# Running the project

For the command, input requirements, output behavior, and library/test usage of **every public file**, use the [complete file-by-file runbook in README](../README.md#complete-file-by-file-runbook). This guide explains the normal end-to-end workflow.

All commands run from a Git checkout at the repository root. Start with `git clone https://github.com/MihQuannn7799/esl-grammar-error-classification.git` and `cd esl-grammar-error-classification`. `uv run --no-sync` uses the environment prepared by the installation step without removing optional packages installed afterward.

## 1. Install the environment

```bash
uv sync --locked --python 3.13.7
```

The base lock installs PyTorch, spaCy 3.8.7, its English model package, and the other classical dependencies. Installation on a new machine needs network access. The historical baseline used Windows, Python 3.13.7, and 10 CPU threads; BERT used 4 threads. Cross-platform bitwise equivalence is not claimed.

Optional BERT dependency:

```bash
uv pip install --python .venv -r requirements-bert.txt
```

No document-export packages are required. No `src/reporting/` package is distributed.

## 2. Run tests without the research corpus

```bash
uv run --no-sync python -m pytest tests -q
```

Tests use hand-written/synthetic SGML, feature dictionaries, and tiny random BERT models. Downloader tests mock HTTP rather than downloading data. Missing `transformers` skips BERT-dependent modules; the real-corpus boundary fixture module is also skipped because its fixture is not distributed. See [test scope](../tests/README.md).

## 3. Run the synthetic demonstration

```bash
uv run --no-sync python -m examples.synthetic_demo
```

This parses hand-written known-span examples, extracts the actual S/L/P/M/D features, fits the actual train-only encoder, trains the actual sparse LR, and prints predictions against a small held-out set. It writes no files. The toy data and scores are not a reproduction of the NUCLE study.

## 4. Research data requirements

Obtain NUCLE independently and meet its applicable access terms. The repository does not supply corpus text, corrections, prepared examples, row-level predictions, vocabularies, or checkpoints. Do not replace a missing reviewed artifact with an empty stub just to bypass a check.

The default research layout is:

```text
data_set/raw/nucle3.2.sgml
data_set/interim/nucle_errors.csv
data_set/interim/nucle_overlap_review_log_all.csv
data_set/processed/nucle_preparation_v2/samples.jsonl
data_set/split/nucle_group_split/split_manifest.csv
data_set/features/nucle_features_v1/
reports/nucle_annotation_audit.csv
reports/nucle_duplicate_content.json
```

These paths are intentionally ignored by Git. The historical preparation expects a specific source checksum and validated audit/review inputs. Exact reconstruction requires those original inputs, not just the downloadable SGML. Filenames do not verify the dataset release.

### Parse and inspect an authorized corpus

These commands generate annotation and quality artifacts locally; they do not replace manual review decisions required later:

```bash
uv run --no-sync python -m src.data.data_understanding --input data_set/raw/nucle3.2.sgml --csv data_set/interim/nucle_errors.csv --report reports/local_data_understanding.md
uv run --no-sync python -m src.data.data_quality --input data_set/raw/nucle3.2.sgml --csv data_set/interim/nucle_errors.csv --output-dir reports --report reports/local_data_quality.md
```

### Prepare and split, only with the required review inputs

```bash
uv run --no-sync python -m src.data.prepare_nucle --policy v2 --output data_set/processed/nucle_preparation_v2
uv run --no-sync python -m src.data.group_split_nucle --prepared data_set/processed/nucle_preparation_v2 --duplicate-report reports/nucle_duplicate_content.json --output data_set/split/nucle_group_split --seed 20261013
```

Preparation and split refuse an already existing output. Work in a fresh experiment checkout; keep original research inputs/results intact. A new source version, changed review decisions, or changed code creates a new experiment rather than a byte-identical historical replay. Preparation records the checkout's Git commit in its manifest.

## 5. Train classical baselines and models

After compatible preparation and split artifacts exist:

```bash
uv run --no-sync python -m src.features.nucle_pos --output reports/pos_new
uv run --no-sync python -m src.features.nucle_features --output data_set/features/nucle_features_v1
uv run --no-sync python -m src.training.nucle_benchmark --features data_set/features/nucle_features_v1 --split data_set/split/nucle_group_split --output reports/benchmark_new
uv run --no-sync python -m src.training.nucle_ablation --features data_set/features/nucle_features_v1 --split data_set/split/nucle_group_split --output reports/ablation_new
```

The benchmark compares Full LR/Tree configurations on validation. Ablation runs the original six feature variants. These steps do not make the published final test scores appear automatically. Final historical selection/evaluation scripts additionally depend on their expected summaries, checkpoints, locks, and private artifacts.

The public [classical ablation CSV](../results/classical_ablations.csv) already contains the saved results of the completed study. View it without retraining or opening a new test evaluation.

## 6. Run a new BERT-small experiment

### Prepare pretrained files locally

The experiment runner loads local files only. With `transformers` installed, the following explicit preparation step downloads the public pretrained model (not the research corpus). Review the model's access/usage terms separately. Save this as a local Python script or execute it in a Python session from the root:

```python
import json
from pathlib import Path
from huggingface_hub import snapshot_download

model = "google/bert_uncased_L-2_H-128_A-2"
revision = "30b0a37ccaaa32f332884b96992754e246e48c5f"
snapshot_download(repo_id=model, revision=revision, local_dir=".cache/bert-small")
path = Path("reports/contextual_model_validation/model_source.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps({"model": model, "revision": revision,
                           "path": ".cache/bert-small"}, indent=2), encoding="utf-8")
```

`configs/bert_small_training.json` expects the preparation/split paths above and this `model_source.json`. Its expected counts must match the declared experiment: 11,052/2,368/2,368. For different data or a pilot, copy the config to a new file and record the design before running; do not alter a running/locked experiment.

### Check, train, select, then test

```bash
uv run --no-sync python -m src.training.bert_small_experiment check --config configs/bert_small_training.json
uv run --no-sync python -m src.training.bert_small_experiment train --config configs/bert_small_training.json --output reports/bert_new
uv run --no-sync python -m src.training.bert_small_experiment select --experiment reports/bert_new
uv run --no-sync python -m src.training.bert_small_experiment test --selection reports/bert_new/selection.json --output reports/bert_new/test
```

- `check` validates inputs and performs small forwards without training.
- `train` uses train/validation; it does not create a test dataset or score test. It saves epoch histories, best checkpoints, and resume state.
- Resume an interrupted, unlocked run with the same `train` command plus `--resume`. Keep the same config, input, code, and environment.
- `select` requires every declared run/seed, selects by mean validation Macro-F1, fixes the primary seed, and locks hashes.
- `test` verifies the lock/checkpoints before test tokenization, scores all selected seeds without backpropagation/refitting, and refuses an existing output directory.

The original grid has 12 runs, up to 20 epochs per run, with patience 4; it is not a quick smoke test. Use synthetic tests/demo for a fast inspection. Do not claim a new run recreates the published score unless inputs, environment, selection rules, and outputs have been checked.

## 7. Evaluation boundaries

Choose configurations/checkpoints with validation, then freeze before test. The published models were not refit on train+validation. The BERT extension reused a test already seen for classical models; preserve that limitation when discussing results.

Paired bootstrap must use the same resampled connected groups for all models. Seed standard deviation and group-bootstrap CI answer different questions and should be reported separately. Aggregate CSVs are sufficient to inspect the published outcome, but recomputing its paired bootstrap requires the excluded row-level predictions and group metadata.

Historical functions such as `verify_lock` check the original source/artifact snapshot. This curated export omits reporting modules and private inputs and therefore cannot satisfy that historical lock. The historical evaluator also has fixed output paths; do not run it blindly or edit stored hashes to bypass guards. A source checkout and passing synthetic tests do not imply full raw-to-test reproduction.

## 8. Continuous integration

The [CI workflow](../.github/workflows/ci.yml) installs the locked base environment and optional BERT dependency, then runs the synthetic suite and corpus-free demo on Windows and Linux. It does not download NUCLE or pretrained task weights, rerun the research benchmark, or adjudicate labels.

To run the same project checks locally:

```bash
uv run --no-sync python -m pytest tests -q -ra
uv run --no-sync python -m examples.synthetic_demo
```
