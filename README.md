# ESL Grammar Error Classification

[![CI](https://github.com/MihQuannn7799/esl-grammar-error-classification/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/MihQuannn7799/esl-grammar-error-classification/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue)](pyproject.toml)
[![Reports: English Markdown](https://img.shields.io/badge/Reports-English%20Markdown-2c7a7b)](results/README.md)

A reproducible machine learning study of **five grammar error types in English learner writing**. The project compares linguistic-feature Logistic Regression and Decision Tree models with a fine-tuned BERT-small classifier.

**Input:** an original sentence and an already known error span. **Output:** ArtOrDet, Prep, Nn, Vform, or SVA. A sentence may contain several annotations; each annotation is a separate classification example. Automatic error detection and correction generation are outside this evaluation.

[Run the demo](#quick-start) | [All file commands](#complete-file-by-file-runbook) | [Architecture](docs/ARCHITECTURE.md) | [Results](docs/RESULTS.md) | [Full report](results/reports/final-report.md) | [All documentation](docs/README.md)

## Results at a glance

Evaluated on the same **2,368 test annotations in 97 connected essay groups**:

| Model | Validation Macro-F1 | Test Macro-F1 | Test accuracy |
|---|---:|---:|---:|
| Majority | 0.1184 | 0.1184 | 0.4206 |
| POS rule | 0.7048 | 0.7106 | 0.7441 |
| Logistic Regression, Full | 0.8067 | **0.8163** | 0.8357 |
| Decision Tree, Full | 0.7879 | 0.7996 | 0.8095 |
| BERT-small, primary seed | **0.8173** | 0.8146 | **0.8438** |

![Test Macro-F1 and paired group-bootstrap confidence intervals](results/figures/benchmark_ci.png)

BERT's three-seed test mean is **0.8182 +/- 0.0038** (sample standard deviation). Its primary seed is fixed before BERT test scoring. The paired BERT-minus-LR difference is **-0.0017, CI95% [-0.0184, 0.0182]**: the evidence does not establish either model as better.

The BERT extension reused a test already seen for the classical experiments, so this is not independent external validation. See the [result interpretation](docs/RESULTS.md) and [full-precision aggregate tables](results/README.md) for confidence intervals, class tradeoffs, ablations, and limitations.

## Quick start

Requires Git and [uv](https://docs.astral.sh/uv/getting-started/installation/). Run from a Git checkout so preparation tests can record a committed HEAD. Initial dependency installation requires network access.

```bash
git clone https://github.com/MihQuannn7799/esl-grammar-error-classification.git
cd esl-grammar-error-classification
uv sync --locked --python 3.13.7
uv run --no-sync python -m examples.synthetic_demo
uv run --no-sync python -m pytest tests -q
```

The demo uses hand-written examples and the actual feature extractor, train-only encoder, and sparse LR. It needs no NUCLE corpus or task checkpoint, writes no result files, and makes no research-performance claim. The base lock installs spaCy and its English model package.

For the complete test suite, including tiny randomly initialized BERT models:

```bash
uv pip install --python .venv -r requirements-bert.txt
uv run --no-sync python -m pytest tests -q
```

The last local full-suite check was **106 passed, 1 skipped**; the skip requires an undistributed licensed corpus fixture. The live badge reports CI status independently. Tests use synthetic inputs and do not download a BERT checkpoint. See [RUNNING.md](docs/RUNNING.md) for training prerequisites.

## What the project demonstrates

- **Data engineering:** SGML parsing, preserved character offsets/provenance, quality checks, and connected-group splitting to reduce content leakage.
- **Feature engineering:** train-only sparse encoding of structure, lexical, POS, morphology, and dependency information; Full has 16,180 columns.
- **Model implementation:** PyTorch sparse multinomial LR with L2/LBFGS and deterministic Gini CART, compared with Majority/POS baselines.
- **Neural experiments:** CLS versus contextual span-mean BERT-small, separate encoder/head learning rates, early stopping, resumable runs, and locked checkpoint selection.
- **Evaluation:** Macro-F1, per-class analysis, incremental/masking/ablation experiments, and 1,000 paired group-bootstrap replicates.

BERT-small has two transformer layers, hidden size 128, and two attention heads. Its input is span-marked text, not the classical feature vector. Full LR already includes sentence-wide dependency information; the comparison is not simply context versus no context.

## Repository structure

```text
src/          Data preparation, features, models, training, and evaluation
examples/     Corpus-free end-to-end demonstration
tests/        Synthetic regression, model, and training-lifecycle tests
configs/      BERT experiment configuration
docs/         Architecture, running instructions, and result interpretation
results/      Aggregate CSVs, figures, and English Markdown reports
.github/      Windows/Linux CI workflow
```

## Explore the work

| Goal | Start here |
|---|---|
| Understand the pipeline and feature encoder | [Architecture](docs/ARCHITECTURE.md) |
| Install, test, or train a new experiment | [Running the project](docs/RUNNING.md) |
| Interpret scores and confidence intervals | [Results and limitations](docs/RESULTS.md) |
| Read the complete study | [Final report: 34 tables and 14 references](results/reports/final-report.md) |
| Inspect the BERT extension | [BERT comparison](results/reports/bert-comparison.md) |
| Present the findings | [Presentation and speaker notes](results/reports/presentation.md) |
| Contribute or run project checks | [Contribution guide](CONTRIBUTING.md) |

## Reproducibility and scope

A fresh checkout supports synthetic tests, the demo, and inspection of saved aggregate results. Full NUCLE reproduction additionally requires independently obtained corpus access, compatible preparation/review inputs, and historical artifacts. Models retain train-fitted weights; validation selects configurations and test is used after locking. Replaying saved predictions is not a new independent evaluation.

The repository excludes corpus text/corrections, row-level predictions, private reviews, checkpoints/vocabularies, caches, report generators, and one-off internal audit/replay helpers. Some retained historical scoring routines require those excluded inputs; follow the public run guide rather than executing them blindly. No pretrained task checkpoint or inference service is distributed.

## Complete file-by-file runbook

This section covers **every Python file and every other public file in this repository**, directly in the README. Execute commands from the repository root. `uv run --no-sync python` uses the environment installed in Quick start, including optional BERT dependencies when needed. The commands below describe how to run each tool; they were not all executed on research data while writing this guide.

### Find the right instructions

A command-line entry point performs a workflow when invoked with `python -m ...`. A shared module exposes functions, classes, or constants for another runner to use; executing that file directly is not a substitute for calling its API. Test modules run through pytest, and data/configuration/document files are read by their consuming tools.

| Files or task | Instructions |
|---|---|
| Public end-to-end example | [A. Public demo](#a-public-demo) |
| Data download, understanding, quality, preparation, comparison, split | [B. Data preparation scripts](#b-data-preparation-scripts) |
| Feature extraction, LR/Tree benchmark and ablations | [C. Features and classical training](#c-features-and-classical-training) |
| Current and historical BERT runners | [D. BERT training](#d-bert-training) |
| Evaluation, replay and diagnostics | [E. Evaluation and diagnostics](#e-evaluation-and-diagnostics) |
| Parsers, boundary helpers, metrics, model classes and package files | [F. Shared modules and actual API examples](#f-shared-modules-and-package-files) |
| Individual test modules | [G. Individual tests](#g-individual-tests) |
| Configuration, reports, CSVs, figures and repository settings | [H. Other files](#h-configuration-documentation-and-result-files) |

The sections are expanded below. In particular, `src/data/nucle_sgml.py`, `parse_nucle.py`, `sentence_boundaries.py`, `boundary_challenges.py`, `constants.py`, and `__init__.py` are shared modules documented in F; the six runnable data scripts are in B. The import checks in F only confirm availability. The following API examples demonstrate actual parsing, conversion, boundary repair, scoring, and model fitting.

### Inputs and execution order

| Level | Required local inputs | What becomes available |
|---|---|---|
| A: public checkout | Git checkout, base dependencies; optional `transformers` for BERT tests | Demo, synthetic tests, library imports, reading reports/results |
| B: authorized research data | NUCLE SGML plus matching annotation CSV, quality audit, overlap-review decisions, source checksum, and a committed HEAD | Preparation and connected-group split |
| C: prepared experiment | Level B outputs; train-only features/encoder for classical models; local pretrained model metadata/files for BERT | Validation training, ablations, locked BERT selection/test |
| H: historical reproduction | Original protocol documents, compatible phase-specific summaries, predictions, checkpoints, manifests, and locks | Fixed-path sensitivity/diagnostic/replay scripts below |

Normal order is **download/restore data -> understanding -> quality review -> preparation -> group split -> features/baselines -> validation training -> lock -> test -> analysis**. Preparation v1 and v2 comparison is optional. The extended BERT runner is the recommended BERT workflow; the five-epoch CLS runner is retained for the historical experiment.

The exact historical review inputs, protocols, row-level predictions, and task checkpoints are not distributed. In particular, `docs/bert_experiment_protocol.md`, `docs/bert_learning_diagnostics_protocol.md`, and `docs/final_evaluation_protocol.md` are required by specific historical scripts but absent from this curated export. Restore genuine inputs in a separate complete research checkout for those stages; do not create empty placeholders or change recorded hashes to bypass checks. Follow [RUNNING.md](docs/RUNNING.md) to prepare a local pretrained `model_source.json` for the current BERT runner.

Use fresh output directories where the implementation requires them. Some fixed-path diagnostics write into `reports/`; do not batch-execute every `.py`. **Do not pass `--help` to scripts without argparse:** `nucle_final_selection.py --help` would start its fitting branch, and the downloader does not interpret a help flag.

### A. Public demo

#### `examples/synthetic_demo.py`

```bash
uv run --no-sync python -m examples.synthetic_demo
```

Needs base dependencies including spaCy's English package. Runs the actual feature extractor, train-only encoder, and LR on hand-written examples; prints predictions and toy metrics. No corpus/checkpoint download and no output files. The toy score is not a NUCLE benchmark.

### B. Data preparation scripts

#### `src/data/data_download.py`

```bash
uv run --no-sync python -m src.data.data_download
```

No CLI options. Explicitly downloads the configured NUCLE SGML URL to `data_set/raw/nucle3.2.sgml`, or skips an existing file. Requires network access and appropriate dataset access; if gated, obtain the source independently and place it at that path. No parsing or splitting occurs here.

#### `src/data/data_understanding.py`

```bash
uv run --no-sync python -m src.data.data_understanding --input data_set/raw/nucle3.2.sgml --csv data_set/interim/nucle_errors.csv --report reports/data_understanding.md
```

Options: `--input`, `--csv`, `--report`. Reads SGML and exports the annotation CSV plus a Markdown overview. Creates parent directories; output files can be replaced if the same paths are reused.

#### `src/data/data_quality.py`

```bash
uv run --no-sync python -m src.data.data_quality --input data_set/raw/nucle3.2.sgml --csv data_set/interim/nucle_errors.csv --output-dir reports --report reports/data_quality.md --release unverified
```

Options: `--input`, `--csv`, `--output-dir`, `--report`, `--release`. Compares source/CSV and writes `nucle_data_quality.json`, `nucle_annotation_audit.csv`, `nucle_duplicate_content.json`, and the requested Markdown report. Use a verified release identifier when available; the example does not infer a release from the filename. This generates audit evidence, not the human review log required by preparation. Reusing output paths can replace files.

#### `src/data/prepare_nucle.py`

```bash
uv run --no-sync python -m src.data.prepare_nucle --source data_set/raw/nucle3.2.sgml --annotations data_set/interim/nucle_errors.csv --audit reports/nucle_annotation_audit.csv --review data_set/interim/nucle_overlap_review_log_all.csv --policy v2 --output data_set/processed/nucle_preparation_v2
```

Options: `--source`, `--annotations`, `--audit`, `--review`, `--output`, `--expected-source-sha256`, `--policy {v1,v2}`. The default expected checksum is the verified historical source checksum. Requires matching review decisions and spaCy 3.8.7; preserves original offsets and rejects incompatible inputs. Creates sample/sentence/provenance JSONL, quality/boundary outputs, summary and hashed manifest in a new directory. It records `git rev-parse HEAD`; it does not split data or train a model.

To build the older policy separately, use the same input arguments and `--policy v1 --output data_set/processed/nucle_preparation_v1`. A different legitimate source requires its own verified checksum and compatible review inputs, not reuse of another dataset's review log.

#### `src/data/compare_preparation.py`

```bash
uv run --no-sync python -m src.data.compare_preparation --old data_set/processed/nucle_preparation_v1 --new data_set/processed/nucle_preparation_v2 --output reports/preparation_comparison_new
```

Options: `--old`, `--new`, `--output`. Requires both full preparation directories and the original SGML, plus `data_set/interim/nucle_boundary_decisions.jsonl`. Reads their source/alignment evidence and writes differences, regression cases, a fresh review packet, selection, and comparison summary. Does not change decisions. Packets contain source material and remain ignored/local. Requires a new output directory.

#### `src/data/group_split_nucle.py`

```bash
uv run --no-sync python -m src.data.group_split_nucle --source data_set/raw/nucle3.2.sgml --prepared data_set/processed/nucle_preparation_v2 --duplicate-report reports/nucle_duplicate_content.json --output data_set/split/nucle_group_split --seed 20261013
```

Options: `--source`, `--prepared`, `--duplicate-report`, `--output`, `--seed`. Requires source, complete preparation, and duplicate evidence. Writes essay-to-group mappings, grouping decisions/policy, sample split manifest, summary, and hashes. Keeps connected groups in one partition and refuses an existing output.

### C. Features and classical training

#### `src/features/nucle_pos.py`

```bash
uv run --no-sync python -m src.features.nucle_pos --prepared data_set/processed/nucle_preparation_v2 --split data_set/split/nucle_group_split --output reports/nucle_pos_baseline_v1
```

Options: `--prepared`, `--split`, `--output`. Requires prepared samples, group split, and the spaCy English parser. Learns the train POS-signature baseline and evaluates validation; writes summary, train POS/label counts, and validation predictions. Keep its canonical output path when using the historical slice-analysis script below.

#### `src/features/nucle_features.py`

```bash
uv run --no-sync python -m src.features.nucle_features --prepared data_set/processed/nucle_preparation_v2 --split data_set/split/nucle_group_split --output data_set/features/nucle_features_v1
```

Options: `--prepared`, `--split`, `--output`. Extracts S/L/P/M/D from original sentences and fits vocabulary/column ordering on train only. Writes `features.jsonl`, `targets.jsonl`, `encoder.json`, and `manifest.json`. The artifact name ends in `v1` although the main inputs use preparation v2. Features/targets are local derived data, not public result CSVs.

#### `src/training/nucle_benchmark.py`

```bash
uv run --no-sync python -m src.training.nucle_benchmark --features data_set/features/nucle_features_v1 --split data_set/split/nucle_group_split --output reports/nucle_feature_benchmark_solver_v2
```

Options: `--features`, `--split`, `--output`. Requires encoded features/targets/encoder and split metadata. Searches Full LR/Tree grids using train/validation, then writes selected metrics, timing, and validation predictions. It does not perform final locked test scoring. Its saved validation predictions are inputs to historical thread/sensitivity diagnostics.

#### `src/training/nucle_ablation.py`

```bash
uv run --no-sync python -m src.training.nucle_ablation --features data_set/features/nucle_features_v1 --split data_set/split/nucle_group_split --output reports/nucle_feature_ablation_v1
```

Options: `--features`, `--split`, `--output`, repeatable `--variant`. By default runs all six historical variants. A restricted example is `--variant S+L`; quote a variant name containing spaces if one is added later. Masked variants additionally read the canonical preparation directory and original parses. Writes run summaries and validation predictions; this is not the final 52-fit evaluation stage. Preserve its canonical path for downstream historical readers.

#### `src/training/nucle_final_selection.py` (historical, fixed paths)

```bash
uv run --no-sync python -m src.training.nucle_final_selection
uv run --no-sync python -m src.training.nucle_final_selection --freeze
```

The first command performs 40 added grid fits plus 12 historical refits, reconstructs encoders, and writes checkpoints/validation evidence under `reports/final_evaluation/`. The second separately freezes inputs/checkpoints into `lock.json`/`lock.sha256`; run it only after reviewing selection output. Requires canonical features/preparation/split, `reports/nucle_feature_ablation_v1/` summaries/predictions, historical POS evidence, and the genuine `docs/final_evaluation_protocol.md`.

The fitting branch refuses an existing final-evaluation directory; freeze refuses an existing lock. There is no general `--output` or `--help` parser. The public export cannot satisfy an original research lock merely by copying aggregate results.

### D. BERT training

#### `src/training/bert_small_experiment.py` (recommended)

Needs `transformers`, prepared v2 samples, the fixed split, and local pretrained files referenced by `reports/contextual_model_validation/model_source.json`. The [pretrained setup instructions](docs/RUNNING.md#6-run-a-new-bert-small-experiment) create that metadata; the runner itself uses local files only. Configuration is [configs/bert_small_training.json](configs/bert_small_training.json).

```bash
uv run --no-sync python -m src.training.bert_small_experiment check --config configs/bert_small_training.json
uv run --no-sync python -m src.training.bert_small_experiment train --config configs/bert_small_training.json --output reports/bert_new
uv run --no-sync python -m src.training.bert_small_experiment train --config configs/bert_small_training.json --output reports/bert_new --resume
uv run --no-sync python -m src.training.bert_small_experiment select --experiment reports/bert_new
uv run --no-sync python -m src.training.bert_small_experiment test --selection reports/bert_new/selection.json --output reports/bert_new/test
```

Run `--resume` only to continue an interrupted, unlocked experiment, not as a required step after a successful train. Subcommands/options:

| Subcommand | Options | Behavior/output |
|---|---|---|
| `check` | `--config` | Validate train/validation inputs and small forwards; no training |
| `train` | `--config`, required `--output`, optional `--resume` | Histories, learning curves, best checkpoints, validation predictions, summaries, resumable optimizer state |
| `select` | required `--experiment` | Require all declared seeds/runs, choose mean validation Macro-F1, fix primary, create `selection.json` and hash lock |
| `test` | required `--selection`, required `--output` | Verify lock/checkpoints, then score selected seeds on test; write summary, class metrics and per-sample predictions locally |

Use train/validation for development; selection locks before test. Test refuses an existing output, never refits train+validation, and does not choose the best test seed. The default config is 12 runs, up to 20 epochs each; it is not a fast smoke test. Copy the config and use a separate output for a declared pilot.

#### `src/training/bert_span_classifier.py` (historical CLS)

```bash
uv run --no-sync python -m src.training.bert_span_classifier --pilot
uv run --no-sync python -m src.training.bert_span_classifier --train
```

Choose exactly one of `--pilot` or `--train` per invocation. Requires v2 samples/split and local pretrained metadata/files. `--pilot` runs 20 train batches and writes timing/tokenization information to `reports/contextual_model_validation/bert/pilot.json`; it performs optimization steps but is not the full benchmark. `--train` additionally requires the original `docs/bert_experiment_protocol.md`, runs the historical five-epoch search, and writes per-run checkpoint/history/predictions plus `selection.json`. It has no test path or configurable output flag and rejects a completed selection. Prefer the extended runner for a new experiment.

### E. Evaluation and diagnostics

These tools need the named local experiment artifacts. Public aggregate CSVs under `results/` are for inspection and do not substitute for excluded row-level predictions, checkpoints, or original protocol/lock records.

#### `src/evaluation/nucle_span_analysis.py`

```bash
uv run --no-sync python -m src.evaluation.nucle_span_analysis --output reports/span_analysis_new
```

Only option: `--output`. Requires canonical v2 preparation/split, `reports/nucle_pos_baseline_v1/` and `reports/nucle_feature_ablation_v1/` validation predictions/summaries, split summary, and essay-group mapping. Writes `summary.json`/`metrics.csv` for span, pair, and POS slices. Refuses an existing output and does not fit models or score test.

#### `src/evaluation/nucle_final_evaluation.py` (historical lock required)

Choose the appropriate stage; these are three supported positional modes, not argparse flags:

```bash
uv run --no-sync python -m src.evaluation.nucle_final_evaluation score
uv run --no-sync python -m src.evaluation.nucle_final_evaluation bootstrap
uv run --no-sync python -m src.evaluation.nucle_final_evaluation replay
```

- `score`: after a valid final-selection lock, read canonical preparation/features/encoders/checkpoints and score 2,368 test examples. Writes test-start/completion records, encoded test inputs, predictions, and subset metrics under `reports/final_evaluation/`. Refuses an already started/scored test.
- `bootstrap`: read locked saved test predictions; write group weights, CI/contrast JSON and aggregate result CSVs. No fitting; can replace these derived files at its fixed paths.
- `replay`: read saved encoded test inputs/checkpoints and compare against recorded predictions, then write `checkpoint_replay.json`. It checks frozen inference, not a new training run.

All modes verify the original lock. The public curated tree lacks original private inputs and differs from historical locked source, so a fresh clone cannot pass that lock. Restore a complete compatible research workspace rather than editing the lock or suppressing checks. There is no shared `--output`/`--help` interface.

#### `src/evaluation/bert_final_analysis.py`

```bash
uv run --no-sync python -m src.evaluation.bert_final_analysis --experiment reports/bert_small_experiment --output reports/bert_analysis_new
```

Options: `--experiment`, `--output`. Requires a complete locked/tested extended BERT experiment plus compatible classical `reports/final_evaluation/` predictions, scoring/hash records, bootstrap results/weight array, and `reports/evaluation_followup/reviewed_overall_results.csv`. Corpus access and canonical preparation are additionally required by its private audit-packet step. It verifies saved predictions/checkpoints, produces model/class/grid/seed/paired tables and figures, and creates local private audit outputs. It does not train or generate new checkpoint predictions. Output must not exist; its full workflow cannot run using public aggregates alone. Shared `scores`/bootstrap/selection helpers are also exercised by synthetic tests.

#### `src/evaluation/bert_checkpoint_verification.py` (historical CLS)

```bash
uv run --no-sync python -m src.evaluation.bert_checkpoint_verification
```

No CLI options. Requires the old CLS `reports/contextual_model_validation/bert/selection.json`, selected checkpoint/tokenizer directories, their saved validation predictions, preparation/split, and local model metadata. Re-evaluates train/validation to assert saved validation predictions match; writes `checkpoint_replay.json` at that fixed location, possibly replacing it. It does not access test or fit weights. This loader is for old CLS checkpoints, not the extended span-mean wrapper; the current runner performs its own checkpoint replay checks.

#### `src/evaluation/bert_learning_diagnostics.py` (historical train-only probes)

```bash
uv run --no-sync python -m src.evaluation.bert_learning_diagnostics
```

No CLI options. Requires the old BERT selection/primary checkpoint, original pretrained files, v2 samples/split, and genuine `docs/bert_learning_diagnostics_protocol.md`. `reports/bert_learning_diagnostics/` must not exist. Creates selected train IDs, input/gradient/marker checks, small-set training histories/checkpoints/summary and replay evidence. It performs train-only optimization on 100 selected examples; it is not the full-corpus benchmark and does not compute validation/test scores.

#### `src/evaluation/bert_target_pair_probe.py`

```bash
uv run --no-sync python -m src.evaluation.bert_target_pair_probe
```

No CLI options. Requires canonical train samples/split and the old CLS primary checkpoint/selection. Uses the already existing `reports/bert_learning_diagnostics/` directory and writes `same_sentence_pairs.json`, refusing an existing file. Inspects up to 50 same-sentence, different-target train pairs with the fixed checkpoint. No training, validation/test scoring, or reselection.

#### `src/evaluation/preprocessing_sensitivity_audit.py`

```bash
uv run --no-sync python -m src.evaluation.preprocessing_sensitivity_audit
```

No CLI options. Requires complete v1/v2 samples using the same IDs, the canonical grouped split, spaCy, and original benchmark validation predictions at `reports/nucle_feature_benchmark_solver_v2/validation_predictions.csv`. Fits fixed-configuration LR/POS for each preparation on train and evaluates validation, checking offsets/alignment. Creates a new `reports/contextual_model_validation/audit/` directory with v1/v2 predictions, summary, and a private case packet. It refuses an existing directory; test is not scored.

#### `src/evaluation/logistic_thread_sensitivity.py`

```bash
uv run --no-sync python -m src.evaluation.logistic_thread_sensitivity
```

No CLI options. Requires canonical features/encoder/split, original benchmark validation predictions, and the preceding sensitivity run's `v2_validation_predictions.csv`. Refits the fixed LR at four and ten CPU threads on train, compares validation predictions, and writes `reports/contextual_model_validation/audit/thread_diagnostic.json`, potentially replacing it. This is a numerical-sensitivity probe, not a different test score or a reason to replace the published baseline.

### F. Shared modules and package files

These files do not have standalone main programs. Running `python file.py` would only define objects or constants and does not perform the intended pipeline. Import them from the associated runner. The commands in the table below are import checks only: package imports exit without output, while selected checks print an API name or metadata. The actual-use examples after the table perform synthetic parsing, conversion, scoring, and fitting. BERT's wrapper requires the optional dependency.

| File | Role / actual use | Import/smoke command |
|---|---|---|
| [examples/__init__.py](examples/__init__.py) | Examples package marker | `uv run --no-sync python -c "import examples"` |
| [src/__init__.py](src/__init__.py) | Root package marker | `uv run --no-sync python -c "import src"` |
| [src/data/__init__.py](src/data/__init__.py) | Data package marker | `uv run --no-sync python -c "import src.data"` |
| [src/data/boundary_challenges.py](src/data/boundary_challenges.py) | Known boundary-case IDs/policy metadata; used by preparation | `uv run --no-sync python -c "from src.data.boundary_challenges import BOUNDARY_CHALLENGES; print(len(BOUNDARY_CHALLENGES))"` |
| [src/data/constants.py](src/data/constants.py) | Shared paths and fixed target label order | `uv run --no-sync python -c "from src.data.constants import TARGET_LABELS; print(TARGET_LABELS)"` |
| [src/data/nucle_sgml.py](src/data/nucle_sgml.py) | SGML parser and document/annotation records; real parsing needs an authorized source | `uv run --no-sync python -c "from src.data.nucle_sgml import load_nucle; print(load_nucle.__name__)"` |
| [src/data/parse_nucle.py](src/data/parse_nucle.py) | Document-to-annotation DataFrame and span reconstruction helpers | `uv run --no-sync python -c "from src.data.parse_nucle import documents_to_dataframe; print(documents_to_dataframe.__name__)"` |
| [src/data/sentence_boundaries.py](src/data/sentence_boundaries.py) | Text-only boundary repair rules; called by preparation | `uv run --no-sync python -c "from src.data.sentence_boundaries import rule_metadata; print(rule_metadata.__name__)"` |
| [src/evaluation/__init__.py](src/evaluation/__init__.py) | Evaluation package marker | `uv run --no-sync python -c "import src.evaluation"` |
| [src/evaluation/metrics.py](src/evaluation/metrics.py) | Fixed five-class metrics; requires aligned label sequences for scoring | `uv run --no-sync python -c "from src.evaluation.metrics import scores; print(scores.__name__)"` |
| [src/features/__init__.py](src/features/__init__.py) | Feature package marker | `uv run --no-sync python -c "import src.features"` |
| [src/models/__init__.py](src/models/__init__.py) | Model package marker | `uv run --no-sync python -c "import src.models"` |
| [src/models/bert_span_readout.py](src/models/bert_span_readout.py) | BERT CLS/span-mean wrapper; actual forward needs a model and token tensors | `uv run --no-sync python -c "from src.models.bert_span_readout import BertReadout; print(BertReadout.__name__)"` |
| [src/models/nucle_logistic.py](src/models/nucle_logistic.py) | Sparse LR optimizer; actual fitting needs encoded features and train labels | `uv run --no-sync python -c "from src.models.nucle_logistic import fit_logistic; print(fit_logistic.__name__)"` |
| [src/models/nucle_tree.py](src/models/nucle_tree.py) | Deterministic Gini Tree; fit/predict methods take encoded rows | `uv run --no-sync python -c "from src.models.nucle_tree import GiniTree; print(GiniTree.__name__)"` |
| [src/training/__init__.py](src/training/__init__.py) | Training package marker | `uv run --no-sync python -c "import src.training"` |

The runnable feature and training scripts above import these shared modules. For full input-to-prediction usage, run `examples/synthetic_demo.py` rather than treating an import smoke test as model evaluation.


#### Actual use: SGML parser and annotation DataFrame

After installing the base dependencies, start Python from the repository root:

```bash
uv run --no-sync python
```

Paste each Python example below into that interpreter. These examples use synthetic text or in-memory values, do not require NUCLE, and do not write dataset or result files. Leave Python with `exit()` before running another shell command.

This example calls both `src/data/nucle_sgml.py` and `src/data/parse_nucle.py`, rather than merely importing them:

```python
from src.data.nucle_sgml import NucleSGMLParser
from src.data.parse_nucle import documents_to_dataframe

source = (
    '<DOC nid="demo"><TEXT><P>They was happy.</P></TEXT>'
    '<ANNOTATION><MISTAKE start_par="0" start_off="5" end_par="0" end_off="8">'
    '<TYPE>SVA</TYPE><CORRECTION>were</CORRECTION>'
    '</MISTAKE></ANNOTATION></DOC>'
)
parser = NucleSGMLParser()
parser.feed(source)
parser.close()
frame = documents_to_dataframe(parser.documents)
print(frame[["annotation_id", "error_span", "error_type", "valid_offset"]].to_string(index=False))
```

Expected: one annotation, ID `0`, span `was`, label `SVA`, and a valid offset. The parser produces document/annotation objects; the converter produces a DataFrame. For an authorized real SGML file, import `Path` from `pathlib` and `load_nucle` from `src.data.nucle_sgml`, then call `load_nucle(Path("data_set/raw/nucle3.2.sgml"))` to supply documents to the same converter. To export the actual CSV and understanding report, use the `data_understanding.py` command in B.

#### Actual use: sentence-boundary helper

`src/data/sentence_boundaries.py` expects a spaCy Doc with sentence boundaries, not a filename:

```python
import spacy
from src.data.sentence_boundaries import repaired_starts

nlp = spacy.blank("en")
nlp.add_pipe("sentencizer")
doc = nlp("First sentence. Second sentence.")
print(repaired_starts(doc))
```

Expected starts: `[0, 16]`, measured as Python character offsets. For complete v1/v2 sample construction, use `prepare_nucle.py`; this helper alone does not build the dataset. The boundary-case metadata and path/label constants have import-and-inspect commands in the table above.

#### Actual use: five-class metrics

`src/evaluation/metrics.py` takes aligned true/predicted label sequences:

```python
from src.evaluation.metrics import scores

truth = ["ArtOrDet", "Prep", "Nn", "Vform", "SVA"]
prediction = ["ArtOrDet", "Prep", "Nn", "SVA", "SVA"]
result = scores(truth, prediction)
print(result["accuracy"])
print(result["macro_f1"])
print(result["per_label"]["SVA"])
```

Expected accuracy: `0.8`; Macro-F1: approximately `0.733333`. SVA precision is `0.5`, recall is `1.0`, and F1 is approximately `0.666667`. This computes metrics from supplied labels; it does not generate model predictions.

#### Actual use: tree model API

`src/models/nucle_tree.py` consumes sparse feature dictionaries and integer class indices:

```python
from src.data.constants import TARGET_LABELS
from src.models.nucle_tree import GiniTree

rows = [{0: 1.0}, {0: 2.0}, {0: 8.0}, {0: 9.0}]
labels = [0, 0, 4, 4]
tree = GiniTree(
    max_depth=2,
    min_samples_leaf=1,
    balanced=False,
    numeric_features={0},
).fit(rows, labels)
indices = tree.predict([{0: 1.5}, {0: 8.5}])
print([TARGET_LABELS[i] for i in indices])
```

Expected: `["ArtOrDet", "SVA"]`. The numeric feature is deliberately synthetic; this checks the fitting/prediction API and is not a grammar benchmark.

#### Actual use: LR, encoder, and BERT wrapper through their callers

After leaving the Python interpreter, run the existing end-to-end example to exercise `TrainOnlyEncoder` and `fit_logistic` with synthetic sentence/span inputs:

```bash
uv run --no-sync python -m examples.synthetic_demo
```

For research LR/Tree training, use `src.training.nucle_benchmark` or `src.training.nucle_ablation` in C with their required prepared features. These runners construct the inputs and call the library models; there is no independent `nucle_logistic.py` training CLI.

For `src/models/bert_span_readout.py`, install the optional BERT dependencies, then exercise actual forwards, span masks, and gradients using the existing tiny-model tests:

```bash
uv run --no-sync python -m pytest tests/test_bert_readout.py -q
```

The tests create random tiny BERT models without downloading pretrained checkpoints. Real training calls the wrapper from `src.training.bert_small_experiment` in D. The wrapper cannot perform a useful standalone forward without a base model, marker IDs, and token tensors. Package `__init__.py` files only establish importable packages; their import checks are the appropriate standalone check.


### G. Individual tests

Use pytest, not `python tests/test_*.py`: these modules define tests but have no test-running main function. The aggregate command is `uv run --no-sync python -m pytest tests -q`. Install `requirements-bert.txt` for all BERT-related coverage. A licensed-fixture skip is expected in a public checkout.

| Test file | Individual command | Coverage / requirement |
|---|---|---|
| [tests/test_bert_final_analysis.py](tests/test_bert_final_analysis.py) | `uv run --no-sync python -m pytest tests/test_bert_final_analysis.py -q` | Paired group bootstrap and deterministic audit-selection helpers; no research packets. |
| [tests/test_bert_readout.py](tests/test_bert_readout.py) | `uv run --no-sync python -m pytest tests/test_bert_readout.py -q` | Tiny random BERT, target masks, gradients, padding; needs transformers. |
| [tests/test_bert_small_experiment.py](tests/test_bert_small_experiment.py) | `uv run --no-sync python -m pytest tests/test_bert_small_experiment.py -q` | Synthetic train/resume/validation-selection/lock/test lifecycle; needs transformers. |
| [tests/test_bert_span_classifier.py](tests/test_bert_span_classifier.py) | `uv run --no-sync python -m pytest tests/test_bert_span_classifier.py -q` | Synthetic WordPiece tokenizer, cropping, offsets, no label/correction leakage; needs transformers. |
| [tests/test_boundary_challenges.py](tests/test_boundary_challenges.py) | `uv run --no-sync python -m pytest tests/test_boundary_challenges.py -q` | Real licensed boundary fixture; expected module skip when undistributed fixture is absent. |
| [tests/test_datadownload.py](tests/test_datadownload.py) | `uv run --no-sync python -m pytest tests/test_datadownload.py -q` | Mocked download/retry/partial-file cleanup; no network download. |
| [tests/test_final_evaluation.py](tests/test_final_evaluation.py) | `uv run --no-sync python -m pytest tests/test_final_evaluation.py -q` | Fixed-label metrics, whole-group resampling, encoder serialization, feature removal, locks. |
| [tests/test_nucle_benchmark.py](tests/test_nucle_benchmark.py) | `uv run --no-sync python -m pytest tests/test_nucle_benchmark.py -q` | Sparse tree, metrics, train/validation loader isolation, benchmark timing. |
| [tests/test_nucle_features.py](tests/test_nucle_features.py) | `uv run --no-sync python -m pytest tests/test_nucle_features.py -q` | Synthetic extraction, train-only vocabulary, leakage rejection, offset mismatch. |
| [tests/test_nucle_preparation.py](tests/test_nucle_preparation.py) | `uv run --no-sync python -m pytest tests/test_nucle_preparation.py -q` | Synthetic preparation, boundaries, offsets/review provenance and no-overwrite; requires committed Git HEAD. |
| [tests/test_nucle_quality.py](tests/test_nucle_quality.py) | `uv run --no-sync python -m pytest tests/test_nucle_quality.py -q` | Synthetic quality flags, overlaps, duplicate detection and source/CSV agreement. |
| [tests/test_nucle_understanding.py](tests/test_nucle_understanding.py) | `uv run --no-sync python -m pytest tests/test_nucle_understanding.py -q` | Synthetic SGML parsing, missing corrections, span checks and canonical paths. |
| [tests/test_preparation_alignment.py](tests/test_preparation_alignment.py) | `uv run --no-sync python -m pytest tests/test_preparation_alignment.py -q` | Synthetic v1/v2 token alignment and partial-token flags. |
| [tests/test_sentence_boundaries.py](tests/test_sentence_boundaries.py) | `uv run --no-sync python -m pytest tests/test_sentence_boundaries.py -q` | Synthetic boundary rules and explicit policy versions. |

Read [tests/README.md](tests/README.md) for test scope. Tests do not recreate the NUCLE research run, acquire corpus permissions, or adjudicate gold labels.

### H. Configuration, documentation, and result files

These files are consumed by a tool or viewed as artifacts; they are not standalone Python scripts. Dataset-derived inputs used by training live under ignored `data_set/` and `reports/`, not in the public aggregate result files.

| File | How to run, consume, or view it |
|---|---|
| [.editorconfig](.editorconfig) | Read automatically by compatible editors; formatting settings, not an executable. |
| [.gitattributes](.gitattributes) | Read automatically by Git for text/binary and line-ending handling. |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | Runs on GitHub after pushes/PRs, or Actions -> CI -> Run workflow; tests/demo on Windows/Linux. |
| [.gitignore](.gitignore) | Read automatically by Git to exclude local/private artifacts; not a data-processing script. |
| [.python-version](.python-version) | Read by Python/uv tooling; the documented commands explicitly select Python 3.13.7. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Read development, test, data-handling, and experiment contribution instructions. |
| [README.md](README.md) | Read this landing page and complete runbook on GitHub; no execution. |
| [configs/bert_small_training.json](configs/bert_small_training.json) | Pass to `src.training.bert_small_experiment check/train --config ...`; declares paths, expected split sizes, grid, seeds, and training settings. |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Read data flow, encoder/model design, and reproducibility boundaries. |
| [docs/README.md](docs/README.md) | Open the documentation index for a suggested reading order. |
| [docs/RESULTS.md](docs/RESULTS.md) | Read result interpretation, paired CIs, class tradeoffs, and limitations. |
| [docs/RUNNING.md](docs/RUNNING.md) | Read environment setup, local pretrained model preparation, and research-stage prerequisites. |
| [pyproject.toml](pyproject.toml) | Install the declared project/dev dependencies with `uv sync --locked --python 3.13.7`. |
| [pytest.ini](pytest.ini) | Automatically loaded by `python -m pytest`; sets repository import path and test directory. |
| [requirements-bert.txt](requirements-bert.txt) | Install with `uv pip install --python .venv -r requirements-bert.txt`; optional BERT package pin. |
| [results/README.md](results/README.md) | Open the index for published aggregate results and report provenance. |
| [results/classical_ablations.csv](results/classical_ablations.csv) | View all 20 classical/baseline pipeline names, CIs and aliases. |
| [results/confusions.csv](results/confusions.csv) | View aggregate off-diagonal error counts; not individual examples. |
| [results/figures/benchmark_ci.png](results/figures/benchmark_ci.png) | View the published test-F1/CI plot; no execution. |
| [results/figures/paired_differences.png](results/figures/paired_differences.png) | View paired difference intervals; no execution. |
| [results/figures/per_class_f1.png](results/figures/per_class_f1.png) | View published class-specific F1; no execution. |
| [results/figures/primary_learning_curve.png](results/figures/primary_learning_curve.png) | View primary BERT train/validation curves; no execution. |
| [results/overall_results.csv](results/overall_results.csv) | View in GitHub or a CSV reader: headline model metrics and CIs. |
| [results/paired_differences.csv](results/paired_differences.csv) | View paired BERT-primary model differences and CIs. |
| [results/per_class_metrics.csv](results/per_class_metrics.csv) | View per-model/class precision, recall, F1, support. |
| [results/reports/bert-comparison.md](results/reports/bert-comparison.md) | Read the extended BERT comparison and interpretation; no execution. |
| [results/reports/final-report.md](results/reports/final-report.md) | Read the complete English study with 34 tables and 14 references; no report generator required. |
| [results/reports/presentation.md](results/reports/presentation.md) | Read the 12 English presentation sections and speaker notes. |
| [results/seed_results.csv](results/seed_results.csv) | View selected BERT seed/checkpoint outcomes and primary designation. |
| [results/validation_grid.csv](results/validation_grid.csv) | View BERT configuration means and sample standard deviations. |
| [tests/README.md](tests/README.md) | Read test inputs, optional dependencies, expected skips, and Git HEAD requirement. |
| [uv.lock](uv.lock) | Consumed by the same locked uv installation; not runnable Python and not the historical model-selection lock. |



## Attribution

An academic team project using NUCLE: Dahlmeier, Ng, and Wu (2013), *Building a Large Annotated Corpus of Learner English: The NUS Corpus of Learner English*. Obtain the dataset separately under its applicable terms.

Individual contributions are not inferred from module ownership. Quân, Duy, and Công are assigned six cases each in the 18-case validation audit. The team has reviewed and finalized all 40 BERT/LR case reviews and all 22 consolidated review decisions, confirmed on 1 November 2026. The reports retain unresolved data concerns and methodological limitations; gold labels and model scores are unchanged.
