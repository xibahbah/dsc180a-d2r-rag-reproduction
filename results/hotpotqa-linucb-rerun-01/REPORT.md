# HotpotQA / LinUCB repeat run

The repeat run finished on November 5, 2026 at 9:11 PM Pacific after about 8 hours 11 minutes on a DSMLP GTX 1080 Ti. It used the same protocol as the first run, including GPT-4o-mini, 500 training questions, two LinUCB epochs, and 500 evaluation questions. All five stages completed.

| Metric | First baseline | First repaired | Repeat baseline | Repeat repaired |
|---|---:|---:|---:|---:|
| Authors' answer score | 35.4% (177/500) | 39.8% (199/500) | 35.8% (179/500) | 40.4% (202/500) |
| Answer relevance | 28.40% | 31.71% | 27.89% | 30.45% |
| Faithfulness | 69.17% | 71.40% | 69.21% | 71.28% |

The gain under the authors' answer scorer was 4.4 percentage points in the first run and 4.6 in the repeat. The scorer uses normalized answer containment. These two runs give a repeatability check for this configuration. They do not establish variation across controlled training seeds or match individual answers across runs.

The repeat run's API ledger accounted for $1.21884525 against a separate $3.40 cap. Successful token usage was also estimated at $1.21884525. These are runner records, not an invoice.

The accompanying files contain the 500-question baseline and repair tables, both sets of per-question RAGAS scores, stage summaries and completion markers, plans, and the ledger. The saved policy and raw logs are available in the DSMLP run folder and local backup.

See the [original run report](../hotpotqa-full-linucb/REPORT.md) and [reproduction protocol](../../reproduction/PROTOCOL.md).
