# Evaluation tools

The public directory contains two executable tools and three shared/package modules. Historical diagnostics requiring private artifacts are excluded.

| File | Usage |
|---|---|
| [nucle_final_evaluation.py](nucle_final_evaluation.py) | Classical test scoring, bootstrap CIs, and checkpoint replay; [commands and inputs](../../docs/RUNNING.md#55-score-lr-dt-majority-and-pos-rule-on-test) |
| [nucle_span_analysis.py](nucle_span_analysis.py) | Optional validation span/POS analysis; [command and inputs](../../docs/RUNNING.md#71-current-validation-slice-analysis) |
| [group_bootstrap.py](group_bootstrap.py) | Shared function for supplied predictions; [Python API example](../../docs/RUNNING.md#72-bootstrap-api-for-supplied-predictions) |
| [metrics.py](metrics.py) | Shared metric functions imported by runners; no standalone job |
| [__init__.py](__init__.py) | Python package marker; no standalone job |

New BERT test scoring uses the [test subcommand of bert_small_experiment.py](../../docs/RUNNING.md#67-score-the-locked-checkpoints-on-test), in `src/training/`. To read published scores and comparisons, open [results/README.md](../../results/README.md).

The [running guide](../../docs/RUNNING.md#70-which-evaluation-files-should-i-run) owns installation and execution commands. Corpus and task artifacts are not distributed; generate inputs using its documented workflows.
