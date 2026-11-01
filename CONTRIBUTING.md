# Contributing

## Start from the public workflow

Read the [architecture](docs/ARCHITECTURE.md) and follow the [canonical running guide](docs/RUNNING.md): install the base and optional BERT dependencies in section 1, run the synthetic suite in section 2, and run the demo in section 3. Use a Git checkout and the recorded Python version. Installation and execution commands are maintained there rather than duplicated here.

The licensed boundary fixture is intentionally absent. Do not add corpus excerpts to make its test stop skipping. Synthetic BERT tests use local random models, not downloaded pretrained weights.

## Keep changes reviewable

1. Create a focused branch and explain the problem or behavior being changed.
2. Keep algorithms, configuration changes, and documentation edits easy to distinguish.
3. Run the checks relevant to the change; add regression tests for substantive behavior changes rather than tests that merely repeat implementation.
4. Describe the resulting behavior, evidence, and remaining limitations in the pull request.

The CI workflow runs the full synthetic suite and demo on Windows and Linux. A passing suite validates those checks, not exact historical benchmark reproduction.

## Data and experiments

- Use original hand-written or synthetic examples in public tests and documentation.
- Keep NUCLE text, corrections, private packets, per-sample predictions, encoders, and task checkpoints out of Git. New experiment outputs belong under ignored `reports/` or `runs/` paths.
- Fit feature vocabularies and model parameters on train only. Choose configurations with validation, then lock before test.
- Record new experiments separately. Do not replace published results with a better test seed, tune against the observed test, or silently relabel difficult examples.
- Report training-seed standard deviation separately from connected-group bootstrap CI.

## Results and documentation

English Markdown reports are maintained under `results/reports/`. `results/*.csv` and figures are saved research evidence; changing their presentation must not alter numerical conclusions or imply new training. Keep relative links working and update the documentation index when adding a guide.

## Attribution

Describe your actual contribution and how you verified it. Disclose material AI assistance. Do not infer a person's authorship from a module name, shared result, or generated explanation. Dataset access terms are separate from this repository's source and documentation.
