"""Verify committed full-run evidence offline using only Python's standard library."""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / 'results/hotpotqa-full-linucb'


def check(condition, message):
    if not condition:
        raise SystemExit('FAIL: ' + message)


def main():
    state = json.loads((CAMPAIGN / 'status.json').read_text())
    check(state['state'] == 'completed', 'Campaign not completed')
    for stage in ('baseline', 'train', 'repair', 'metrics', 'metrics-repaired'):
        check((CAMPAIGN / (stage + '.done')).is_file(), stage + ' completion marker missing')
        check((CAMPAIGN / (stage + '.exit-code')).read_text().strip() == '0', stage + ' failed')
    for stage, name in (('baseline', 'failure_statistics.csv'),
                        ('repair', 'bandit_eval_dataset.csv')):
        with (CAMPAIGN / 'files_hotpotqa_v' / name).open() as stream:
            rows = list(csv.DictReader(stream, delimiter='\t'))
        check(len(rows) == 500, stage + ' expected 500 rows')
        correct = sum(row['EM'].lower() == 'true' for row in rows)
        summary = json.loads((CAMPAIGN / (stage + '-summary.json')).read_text())
        check(math.isclose(correct / 5, summary['upstream_em_percent']), stage + ' EM mismatch')
        print(f'{stage}: {correct}/500 scorer-credited; upstream EM {correct / 5:.1f}%')
    for stage in ('metrics', 'metrics-repaired'):
        rows = []
        for path in sorted(CAMPAIGN.glob(stage + '-ragas-*.csv')):
            with path.open() as stream:
                rows.extend(csv.DictReader(stream))
        check(len(rows) == 500, stage + ' expected 500 metric rows')
        summary = json.loads((CAMPAIGN / (stage + '-summary.json')).read_text())
        for column in ('answer_relevancy', 'faithfulness'):
            scores = [float(row[column]) for row in rows]
            check(all(math.isfinite(score) for score in scores), stage + ' non-finite score')
            mean = sum(scores) / len(scores)
            check(math.isclose(mean, summary['means'][column], abs_tol=1e-10), stage + ' mean mismatch')
            print(f'{stage} {column}: {100 * mean:.4f}% ({len(scores)} scores)')
    ledger = json.loads((CAMPAIGN / 'budget.json').read_text())
    check(ledger['limit_nanodollars'] == 5_000_000_000, 'Original $5 cap changed')
    check(0 <= ledger['successful_usage_nanodollars'] <= ledger['reserved_nanodollars']
          <= ledger['limit_nanodollars'], 'Budget accounting invalid')
    print(f"Accounted campaign amount: ${ledger['reserved_nanodollars'] / 1e9:.8f} (not a billing statement)")
    manifest = json.loads((ROOT / 'reproduction/upstream-files.json').read_text())
    for name, expected in manifest['sha256'].items():
        check(hashlib.sha256((ROOT / 'D2R-RAG' / name).read_bytes()).hexdigest() == expected,
              'Upstream source changed: ' + name)
    print(f"Pinned upstream snapshot verified: {len(manifest['sha256'])} files")
    check((ROOT / 'artifacts/full-linucb-policy.pkl.gz').is_file(), 'Trained checkpoint missing')
    print('PASS: Completed scope and committed result evidence verified. No paid calls were made.')


if __name__ == '__main__':
    main()
