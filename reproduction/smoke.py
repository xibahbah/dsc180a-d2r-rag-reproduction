"""Run upstream baseline on two questions, isolated from reproduction outputs.

This deliberately reduced dataset is an integration check, not a paper result.
It still calls the paid API and may download full underlying dataset shards.
"""
from pathlib import Path
import argparse
import os
import sys

# Set before NumPy/PyTorch imports to avoid oversubscribing the DSMLP CPUs.
for variable in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
                 'NUMEXPR_NUM_THREADS'):
    os.environ[variable] = '4'


def main():
    from budget_guard import install
    install(Path(__file__).resolve().parents[1] / 'results/smoke-budget.json')
    import datasets
    repo = Path(__file__).resolve().parents[1] / "D2R-RAG"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output')
    parser.add_argument('--stage', choices=['baseline', 'train', 'repair'], default='baseline')
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=args.stage != 'baseline')
    if not (output / 'src').exists():
        (output / "src").symlink_to(repo / "src", target_is_directory=True)
    (output / "files_hotpotqa_v").mkdir(exist_ok=True)
    (output / "files_hotpotqa_t").mkdir(exist_ok=True)
    original_loader = datasets.load_dataset

    def limited_loader(path, *args, **kwargs):
        if path != "hotpotqa/hotpot_qa":
            raise ValueError("Smoke runner only supports upstream HotpotQA")
        requested = kwargs["split"]
        split = requested.split("[", 1)[0]
        size = 5 if "100000" in requested else 2
        kwargs["split"] = f"{split}[:{size}]"
        return original_loader(path, *args, **kwargs)

    datasets.load_dataset = limited_loader
    os.chdir(output)
    script = {'baseline': 'experiments/analysis_shortanswer.py',
              'train': 'src/train_shortanswer.py',
              'repair': 'experiments/analysis_shortanswer_patched.py'}[args.stage]
    # The training script otherwise references params_updates before assignment
    # if the first example is diagnosed NO_FAILURE. Apply this control-flow fix
    # to the in-memory smoke copy only; retain the authors' source unchanged.
    source = (repo / script).read_text()
    if args.stage == 'train':
        target = '        for row in tqdm.tqdm(dataset):\n'
        if source.count(target) != 1:
            raise RuntimeError('Training source changed; review smoke compatibility fix')
        source = source.replace(target, target + '            params_updates = {}\n')
    sys.argv = [str(repo / script), "hotpotqa"]
    print(f"SMOKE ONLY ({args.stage}): 2 questions per split; secondary contexts from 5 examples.")
    exec(compile(source, sys.argv[0], 'exec'), {'__name__': '__main__', '__file__': sys.argv[0]})


if __name__ == "__main__":
    main()
