"""Offline comparison of saved predictions; not a new experiment or causal audit."""
import collections
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'results/hotpotqa-full-linucb/files_hotpotqa_v'


def main():
    def load(name):
        with (BASE / name).open() as stream:
            return list(csv.DictReader(stream, delimiter='\t'))
    before = load('failure_statistics.csv')
    after = load('bandit_eval_dataset.csv')
    assert len(before) == len(after) == 500
    assert len({row['question'] for row in before}) == 500
    assert [r['question'] for r in before] == [r['question'] for r in after]
    pairs = []
    transitions = collections.Counter()
    for index, (a, b) in enumerate(zip(before, after), 1):
        ac, bc = a['EM'].lower() == 'true', b['EM'].lower() == 'true'
        kind = ('credited' if ac else 'uncredited') + '_to_' + ('credited' if bc else 'uncredited')
        transitions[kind] += 1
        pairs.append(dict(data_row=index, question=a['question'], gold=a['gt_response'],
                          before=a['response'], after=b['response'], before_score=ac,
                          after_score=bc, before_label=a['failure_label'],
                          after_label=b['failure_label'], action=b['action'], params=b['params']))
    prefixes = ['What science fantasy', 'Which performance act', 'Flyboys stars',
                'Were Scott Derrickson', 'What government position']
    examples = [next(p for p in pairs if p['question'].startswith(prefix)) for prefix in prefixes]
    output = dict(note='Saved scorer transitions across separate stochastic runs; not causal repair outcomes.',
                  rows=500, transitions=dict(transitions),
                  after_actions=dict(collections.Counter(r['action'] for r in after)), examples=examples)
    path = ROOT / 'docs/example-analysis.json'
    path.write_text(json.dumps(output, indent=2) + '\n')
    text = ['# Real answer examples and scoring audit', '',
            'Generated from committed tables by `python3 scripts/analyze_examples.py`; no API calls.', '',
            '## What the saved scores show', '',
            '| Saved baseline credit | Saved repaired credit | Cases |', '|---|---|---:|']
    for key, count in sorted(transitions.items()):
        left, right = key.split('_to_')
        text.append(f'| {left} | {right} | {count} |')
    text += ['', '**Interpretation:** 26 newly credited minus 4 newly uncredited = 22 net,',
             'or 4.4 percentage points. These are scorer transitions, not 26 verified fixes.',
             'The repair script generates a new initial answer; it does not consume the saved',
             'baseline answer. The final CSV stores the post-repair diagnosis, so it does not',
             'necessarily explain why that action was originally selected. Action -1 means no repair.', '',
             '## Important metric implementation finding', '',
             'The installed `qa_metrics/em.py` from qa-metrics 0.2.42 was inspected on DSMLP.',
             'It normalizes reference and candidate strings and credits a match when `ref in can`.',
             'This is substring inclusion, not strict equality. The upstream scripts lowercase',
             'answers and call this function. We preserved it for reproduction comparability.',
             'A response can earn credit while declining to answer; see example 2.',
             'No new scores or human labels have been substituted for the authors\' metric.', '']
    for i, p in enumerate(examples, 1):
        text += [f'## Example {i} — data row {p["data_row"]}', '',
                 '**Question:** ' + p['question'], '', '**Gold:** ' + p['gold'], '',
                 '**Baseline response:** ' + p['before'], '',
                 '**Final response in repaired evaluation:** ' + p['after'], '',
                 f'**Saved credit:** {p["before_score"]} → {p["after_score"]}.',
                 f'**Saved diagnosis:** {p["before_label"]} → {p["after_label"]}.',
                 f'**Selected action:** {p["action"]}; update: `{p["params"]}`.', '']
        observations = [
            'The final answer identifies Animorphs, unlike the baseline abstention. This is a plausible substantive improvement; reranking was selected. It is not a controlled causal attribution to diagnosis.',
            'The final response still says the evidence is insufficient, but includes “Badly Drawn Boy.” The containment scorer credits it. Do not present this as an unambiguous successful correction.',
            'The baseline mentions James Franco while also expressing insufficient evidence. Its credit is lost in the final abstention. Both answers deserve semantic review rather than treating the initial credit as definitive correctness.',
            'Both outputs abstain instead of answering yes, yet both are labeled NO_FAILURE and action -1 is recorded. This illustrates a diagnostic blind spot, not an estimated diagnosis-error rate.',
            'Both outputs abstain and the final action is -1. The NO_FAILURE diagnosis does not establish gold-answer correctness.']
        text += ['**Observation:** ' + observations[i-1], '']
    text += ['## Limits', '',
             'These five examples are purposively selected illustrations, not a random audit.',
             'Data-row numbers are 1-based excluding the header. Baseline and repair rows were',
             'joined and checked by exact question text. A clean repair-caused overcorrection',
             'rate would require the same stored initial responses and an explicit changed-answer',
             'definition. Gold strings alone do not establish passage support. No manual judgment',
             'here was used to rewrite the original results.']
    (ROOT / 'docs/EXAMPLE_ANALYSIS.md').write_text('\n'.join(text) + '\n')
    print(json.dumps(dict(transitions), indent=2))
    print('Wrote docs/EXAMPLE_ANALYSIS.md and docs/example-analysis.json')


if __name__ == '__main__':
    main()
