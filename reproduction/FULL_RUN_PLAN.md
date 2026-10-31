# Proposed full HotpotQA / LinUCB campaign

**User approved a $5 total allowance on October 30, 2026,
separate from the initial $1 smoke allowance.** Execution state is recorded
in `results/hotpotqa-full-linucb/status.json` on DSMLP.

The allowance covers all stages below together, including retries. It is a
ceiling, not a cost prediction or guarantee that every stage will complete.
If the next request cannot fit, the process stops before sending it. Failed,
timed-out or unaccounted requests keep their maximum reservations. Verified
successful responses are settled using reported prompt/output tokens. The
ledger persists under the campaign directory across restarts and stages.
Do not delete it or create another campaign to reset an exhausted allowance.

## Scope

- Original HotpotQA fullwiki loader: 500 training and 500 validation questions.
- Original secondary corpus construction, retrieval settings and prompt files.
- GPT-4o-mini; output ceiling 16,384, matching the model's documented maximum.
- Two LinUCB training epochs, alpha=2, original reward/budget settings.
- Fixed Python hash seed 0; four CPU threads; GTX 1080 Ti.
- Original source retained. Apply the documented training-variable fix to the
  executed in-memory copy; record source hash and fix in each stage plan.
- Maximum 50,000 API attempts; text-only OpenAI chat completions, at most
  three completions per request (for evaluation), at most 32 KiB request input.
- The guard uses $0.15 / $0.60 per million input/output tokens. It counts cached
  tokens at the undiscounted rate conservatively. No other models are allowed.

## Stage order and outputs

1. Baseline: answers, upstream EM matcher outcomes, diagnosis, latency, VRAM.
2. Train: two passes over 500 training examples; saved LinUCB policy.
3. Repair: evaluate learned policy on 500 validation examples.
4. Metrics: RAGAS baseline relevance and faithfulness.
5. Metrics-repaired: RAGAS repaired relevance and faithfulness.

Each stage is checked before proceeding. Save logs, stage exit codes, plans,
environment details, dataset/model revisions where accessible, output tables,
the trained policy and budget ledger. An interrupted training script is not
automatically resumable: its source starts fresh training. Inspect it before
any rerun and preserve the shared spending ledger.

Reference values are in PROTOCOL.md. Compare only full-size results against
the paper. Report remaining runtime/model/version differences. Thompson
Sampling, FEVER and ablations are outside this first full campaign.

## Preview inside the compute container

```sh
.venv/bin/python reproduction/full_run.py baseline \
  --campaign results/hotpotqa-full-linucb --budget-usd 5 --dry-run
```

This preview makes no API calls or model downloads. After the campaign budget
is approved, run each stage with that same campaign path and budget, without
`--dry-run`. The API key must be loaded privately from its existing file.
The existing `job.sh` full-size shortcuts are disabled to prevent unguarded
execution; the guarded full runner is the only prepared full-size entry point.

Simulated spending-control tests cover rejection,
output caps, persistent reservations, sync/async requests, successful token
settlement, multiple completions, changed allowances, failures and an exhausted allowance. No full-size paid run was
used to test these controls.

## Recovery after request ceiling

The baseline and both training epochs completed. Repair stopped at the original
10,000-attempt ceiling with $0.53801295 accounted for, including unsettled
reservations. Increase only the technical attempt ceiling to 50,000 to finish
the same authorized stages. The original $5 ledger, request count and monetary
limit are retained; completed stages are skipped. No new campaign is created.
