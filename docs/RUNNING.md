# Running the project

Run all shell commands from the **repository root**, the directory containing `pyproject.toml`, `uv.lock`, and `src/`. Commands below work in PowerShell and Bash without activating a virtual environment. Python code blocks belong in a Python session, not directly in the shell.

Choose the workflow that matches your available inputs:

| Goal | Required inputs | Follow |
|---|---|---|
| Try the code or run synthetic tests | Git checkout and installed dependencies | Sections 1–3 |
| Prepare the research corpus | Your local NUCLE SGML file | Section 4 |
| Train classical models on train/validation | Section 4 outputs and the base environment | Section 5 |
| Train, select, and test a new BERT experiment | Section 4 outputs, BERT dependencies, and local pretrained weights | Section 6 |
| Run diagnostics or inspect historical tools | The specific experiment artifacts listed for each tool | Section 7 |
| Find a file's CLI, API, test, or artifact usage | See each entry's requirements | Section 10 |

The public checkout contains code, synthetic examples/tests, and saved aggregate results. It does not contain NUCLE text, prepared samples, fitted vocabularies, row-level research predictions, or task checkpoints. Passing tests or running the demo does not reproduce the published NUCLE scores.

## 1. Install the environment

Install Git and [uv](https://docs.astral.sh/uv/getting-started/installation/), then open a shell at the repository root. Use a Git clone with a committed `HEAD`: preparation records the commit, and its integration tests also need that metadata.

### 1.1. Install the base dependencies

```shell
uv sync --locked --python 3.13.7
```

This creates the repository's `.venv` and installs the locked project dependencies plus the default dev group, including pytest. The base environment includes PyTorch, spaCy 3.8.7, and `en_core_web_sm` 3.8.0. Initial installation needs network access. The Python patch version above is explicit; `.python-version` itself specifies only `3.13`.

### 1.2. Add BERT support when needed

Skip this step for classical training and the demo. Install it for BERT training or BERT-dependent tests:

```shell
uv pip install --python .venv -r requirements-bert.txt
```

`requirements-bert.txt` pins `transformers==4.57.6`; its additional transitive dependencies are not all pinned by the base lock. Run project commands with `uv run --no-sync` after installing it. A later `uv sync` can remove packages outside the base lock; reinstall this optional requirement if you sync again.

### 1.3. Verify the interpreter and spaCy model

```shell
uv run --no-sync python -c "import sys, spacy; print(sys.version); print(spacy.__version__); print(spacy.load('en_core_web_sm').meta['version'])"
```

Expected: Python 3.13.7, spaCy 3.8.7, and model version 3.8.0. The checks below use this environment; no separate report-generation environment is needed.

## 2. Run tests without the research corpus

```shell
uv run --no-sync python -m pytest tests -q -ra
```

The tests use synthetic SGML, features, and tiny locally initialized BERT models. Downloader tests mock HTTP. BERT-dependent tests skip when `transformers` is absent; the real NUCLE boundary-fixture module skips when its excluded fixture is absent. Installing the optional BERT requirement enables those BERT tests without downloading pretrained weights.

Use [tests/README.md](../tests/README.md) for scope and [individual test commands](#g-individual-tests) to run one module. A passing synthetic suite checks code behavior; it does not run the research benchmark.

## 3. Run the synthetic demonstration

```shell
uv run --no-sync python -m examples.synthetic_demo
```

The demo uses hand-written sentences with known error spans, the real S/L/P/M/D feature extractor, a train-fitted encoder, and sparse Logistic Regression. It prints held-out toy predictions and metrics, and writes no files. It needs the base spaCy model, but neither NUCLE nor BERT weights.

## 4. Research data requirements

For research training, complete the steps below in order. Use a new experiment checkout or unused output paths: preparation and split refuse existing output directories. Keep corpus text and derived artifacts under the ignored `data_set/` and `reports/` directories; published aggregate CSVs under `results/` are not training inputs.

### 4.1. Place the source file and verify its identity

Obtain NUCLE under its applicable access terms and place the SGML file at:

```text
data_set/raw/nucle3.2.sgml
```

If you want to use the repository's downloader instead, run it explicitly:

```shell
uv run --no-sync python -m src.data.data_download
```

The downloader fetches its configured URL or skips an existing file. It has no command-line options, does not verify the source checksum, and does not establish the dataset release from its filename. If access fails, obtain the file separately and place it at the path above.

Print the actual checksum:

```shell
uv run --no-sync python -c "from pathlib import Path; import hashlib; print(hashlib.sha256(Path('data_set/raw/nucle3.2.sgml').read_bytes()).hexdigest())"
```

The default preparation command expects this source SHA-256:

```text
8441a60060730bdc6af1e79a064c68441ecb24a66da91ea2aab0061a64a130ac
```

The research split runner also requires exactly **1,397 essays**. Although preparation accepts `--expected-source-sha256` for another verified source, changing that argument alone does not adapt the complete workflow to another dataset. A checksum or inventory mismatch needs investigation before continuing.

### 4.2. Export annotations

```shell
uv run --no-sync python -m src.data.data_understanding --input data_set/raw/nucle3.2.sgml --csv data_set/interim/nucle_errors.csv --report reports/data_understanding.md
```

This parses the SGML and writes the annotation CSV and overview. Check that both output files exist. It does not construct training sentences or split the dataset. Reusing these output filenames replaces them.

### 4.3. Generate quality and duplicate evidence

```shell
uv run --no-sync python -m src.data.data_quality --input data_set/raw/nucle3.2.sgml --csv data_set/interim/nucle_errors.csv --output-dir reports --report reports/nucle_data_quality.md --release unverified
```

Read `reports/nucle_data_quality.md`. In `reports/nucle_data_quality.json`, check that `csv_comparison.status` is `match`. The command also creates `nucle_annotation_audit.csv` and `nucle_duplicate_content.json` under `reports/`; the next two stages consume those files. `--release unverified` records that no release identifier has been established; use a verified identifier when you have one. Reusing output filenames replaces them.

### 4.4. Prepare known-span samples

```shell
uv run --no-sync python -m src.data.prepare_nucle --source data_set/raw/nucle3.2.sgml --annotations data_set/interim/nucle_errors.csv --audit reports/nucle_annotation_audit.csv --output data_set/processed/nucle_preparation
```

The default policy is `v2`, using the text-only boundary repairs. Preparation validates source, annotation CSV, and quality-audit inputs. It needs no private overlap-review log or `--review` argument. The quality audit can contain review fields, but preparation does not copy overlap-review statuses into the prepared records.

Check `data_set/processed/nucle_preparation/` for `samples.jsonl`, `sentences.jsonl`, `provenance.jsonl`, `summary.json`, `manifest.json`, and `manifest.sha256`. The manifest records input/code hashes and Git `HEAD`, with schema version 3. This stage does not split data or fit a model.

The `v1`/`v2` policy identifiers describe algorithms; they are separate from artifact directory names. Only an optional preprocessing-sensitivity experiment needs the old policy: repeat the command above with `--policy v1 --output data_set/processed/nucle_preparation_legacy`. Keep the normal preparation unchanged for the main workflow.

### 4.5. Split connected groups

```shell
uv run --no-sync python -m src.data.group_split_nucle --source data_set/raw/nucle3.2.sgml --prepared data_set/processed/nucle_preparation --duplicate-report reports/nucle_duplicate_content.json --output data_set/split/nucle_group_split --seed 20261013
```

This groups related essays/model inputs and assigns each connected group to one partition. Inspect **`data_set/split/nucle_group_split/split_summary.json`** for `partitions`, sample counts, and label counts. Other outputs include `split_manifest.csv`, `essay_groups.csv`, grouping evidence, and `manifest.json`. The split directory does not contain a file named `summary.json`.

The saved study used 11,052 train, 2,368 validation, and 2,368 test samples. These counts are also declared in the supplied BERT config. Check your generated split rather than assuming those values; changed data, policy, or split settings define a different experiment.

### 4.6. Choose the training branch

Both branches start from `data_set/processed/nucle_preparation/samples.jsonl` and `data_set/split/nucle_group_split/split_manifest.csv`:

- For POS, LR, Tree, and feature ablations, continue with section 5.
- For BERT, continue with section 6. Classical feature extraction and classical model training are not BERT prerequisites.

## 5. Train classical baselines and models

Complete section 4 and install the base environment first. Keep the canonical paths below when running the full ablations or fixed-path diagnostics. POS baseline fitting is independent of feature extraction; both are needed by some later diagnostics.

### 5.1. Fit the POS baseline

```shell
uv run --no-sync python -m src.features.nucle_pos --prepared data_set/processed/nucle_preparation --split data_set/split/nucle_group_split --output reports/nucle_pos_baseline
```

This fits POS-signature label rules on train and evaluates validation. Inspect `reports/nucle_pos_baseline/summary.json`: validation scores are under `pos_rule_validation` and `majority_baseline_validation`. The directory also contains `pos_by_label_train.csv` and `validation_predictions.csv`. This stage does not parse or score the test partition.

### 5.2. Extract features and fit the encoder

```shell
uv run --no-sync python -m src.features.nucle_features --prepared data_set/processed/nucle_preparation --split data_set/split/nucle_group_split --output data_set/features/nucle_features
```

This parses sentences and writes encoded `features.jsonl`, `targets.jsonl`, `encoder.json`, and `manifest.json`. The vocabulary and column order are fitted on train only; the fixed encoder then transforms all partitions, including test. Feature extraction therefore processes test sentences, but it does not train on them or compute test performance.

Inspect the manifest's `partition_counts` and `feature_dimension`, and the encoder's `fit_partition`, which must be `train`. These outputs are the inputs to the next two steps.

### 5.3. Train the full LR and Decision Tree benchmark

```shell
uv run --no-sync python -m src.training.nucle_benchmark --features data_set/features/nucle_features --split data_set/split/nucle_group_split --output reports/nucle_feature_benchmark
```

This fits 8 LR configurations and 12 Tree configurations on train and evaluates validation, alongside the majority baseline. It selects eligible configurations by validation Macro-F1; a non-converged LR candidate is reported but cannot be selected.

Read `reports/nucle_feature_benchmark/summary.json` for `selected_by_validation`, grid `results`, convergence information, and `timing`. A null LR selection means no LR candidate met the convergence guard. `validation_predictions.csv` contains majority, chosen LR, and chosen Tree predictions.

This command saves validation evidence, not reusable LR/Tree task checkpoints or final test scores. It does not offer `--resume` or a test mode.

### 5.4. Train feature ablations

```shell
uv run --no-sync python -m src.training.nucle_ablation --features data_set/features/nucle_features --split data_set/split/nucle_group_split --output reports/nucle_feature_ablation
```

By default, this searches LR and Tree grids for all six declared variants: `S+L`, `S+L+P`, `S+L+P+M`, `S+L+P+M+D`, `Full_mask_span_lexical`, and `S+P+M+D_nonlexical`. Check `reports/nucle_feature_ablation/summary.json` for `selected_by_validation`, `variant_feature_counts`, `fit_count`, and grid results. Predictions are in `validation_predictions.csv`.

The masked variant reparses train/validation samples from the **fixed** `data_set/processed/nucle_preparation/` directory and fits its own masked encoder. The CLI has no `--prepared` option. Changing `--features` or `--split` does not change that preparation path.

For an optional single-variant pilot, use a separate output directory:

```shell
uv run --no-sync python -m src.training.nucle_ablation --features data_set/features/nucle_features --split data_set/split/nucle_group_split --variant S+L --output reports/nucle_ablation_pilot
```

A partial pilot does not supply the complete six-variant evidence required by historical final selection. Classical training here ends with validation summaries and predictions. The separate historical checkpoint/freeze/test tools have additional requirements in section 7.

## 6. Run a new BERT-small experiment

Use `src.training.bert_small_experiment` for a new experiment. It accepts prepared known-span sentences directly, with CLS or span-mean readout. Complete section 4 and install the optional BERT requirement in section 1 first.

### 6.1. Review the configuration

Open [configs/bert_small_training.json](../configs/bert_small_training.json). It declares the sample path, split path, pretrained-source metadata path, and expected counts. Compare its `expected_counts` with `split_summary.json` before running.

The default grid is 2 readouts × 1 encoder learning rate × 2 head learning rates × 3 seeds = **12 runs**. Each allows up to 20 epochs with patience 4. Defaults include batch size 32, maximum length 128, CPU device, and 4 threads. The config supports `cpu`, `cuda`, and `auto`; CUDA needs a compatible PyTorch build and available hardware.

For a pilot, copy the config to a separate local JSON file, reduce its grid/epochs, and choose a separate experiment output. Use the copied filename in both `check` and `train`. Do not change sample counts just to bypass a data mismatch. The runner requires all five labels in each requested partition, even for a pilot.

Relative paths in the BERT config and its `model_source.json` resolve from the repository root, not the config file's directory. The saved experiment config contains absolute paths, so moving a trained experiment to another checkout can invalidate its inputs.

### 6.2. Prepare local pretrained files

The runner uses local files only; it does not download missing weights. Start Python from the repository root:

```shell
uv run --no-sync python
```

Paste this Python block to download the pinned public pretrained snapshot and write its source metadata:

```python
import json
from pathlib import Path
from huggingface_hub import snapshot_download

model = "google/bert_uncased_L-2_H-128_A-2"
revision = "30b0a37ccaaa32f332884b96992754e246e48c5f"
snapshot_download(repo_id=model, revision=revision, local_dir=".cache/bert-small")
metadata = Path("reports/contextual_model_validation/model_source.json")
metadata.parent.mkdir(parents=True, exist_ok=True)
metadata.write_text(
    json.dumps({"model": model, "revision": revision, "path": ".cache/bert-small"}, indent=2),
    encoding="utf-8",
)
```

Enter `exit()` to return to the shell. Confirm `.cache/bert-small/` contains the model/tokenizer files and that `model_source.json` exists at the path in your config. These are starting weights; task checkpoints are created later by training. Preserve the source directory and metadata throughout the run.

### 6.3. Run preflight checks

```shell
uv run --no-sync python -m src.training.bert_small_experiment check --config configs/bert_small_training.json
```

This validates partition IDs/counts, checks available grouping metadata, tokenizes train/validation, and runs two-example forwards for the configured readouts. It prints data audits and the number of planned runs. It performs no training or test scoring. Resolve reported file, count, class, or tokenizer errors before proceeding.

### 6.4. Train the grid

Use an output directory that does not already exist:

```shell
uv run --no-sync python -m src.training.bert_small_experiment train --config configs/bert_small_training.json --output reports/bert_new
```

The runner trains on train, evaluates train/validation, and selects each run's best checkpoint using validation. `reports/bert_new/` contains `manifest.json`, `config.json`, and `data_audit.json`. Each completed run contains `history.json`, `history.csv`, `learning_curves.png`, `best/`, `best_metrics.json`, `validation_predictions.csv`, `last.pt`, and `summary.json`.

Inspect the learning curves and each run's `best_epoch`, `stop_reason`, and validation metrics. Completion requires a summary for every declared run. No test metrics are produced at this step.

### 6.5. Resume an interrupted run only when necessary

Skip this step if training finished. To continue an interrupted experiment at the same output path:

```shell
uv run --no-sync python -m src.training.bert_small_experiment train --config configs/bert_small_training.json --output reports/bert_new --resume
```

Resume checks configuration, input/pretrained hashes, tracked training code, and the recorded environment against the saved manifest. It restores saved training state where available and verifies/skips completed runs. Keep the same inputs, code, environment, and paths. Selection locks prevent further resumed training. Intentional changes require a new experiment directory.

### 6.6. Select by validation and lock the result

After all declared runs finish:

```shell
uv run --no-sync python -m src.training.bert_small_experiment select --experiment reports/bert_new
```

Selection requires all declared runs and unchanged tracked training code. It chooses the configuration with highest mean best-checkpoint validation Macro-F1 across seeds; declared grid order breaks ties. The first configured seed is primary, independently of test performance. Inspect `selection.json` for the ranking and selected runs; `selection.sha256` records its checksum, and the selection records the chosen checkpoint hashes.

### 6.7. Score the locked checkpoints on test

```shell
uv run --no-sync python -m src.training.bert_small_experiment test --selection reports/bert_new/selection.json --output reports/bert_new/test
```

This verifies the selection, saved manifest, tracked training code, data/metadata hashes, and chosen checkpoint files before test scoring. It evaluates every seed of the selected configuration without refitting. Read `reports/bert_new/test/summary.json` for test Macro-F1/accuracy means and seed standard deviations, and `per_class_metrics.csv` for label-level scores. Per-run test metrics/predictions remain local. The test output directory must not already exist.

Seed standard deviation measures training-seed variation; it is not a group-bootstrap confidence interval. The standalone BERT workflow does not require classical checkpoints and does not run the historical cross-model analysis automatically.

## 7. Evaluation boundaries

Choose configurations with validation, lock the choice, then score test. The published study did not refit on train+validation. The BERT extension reused a test split already seen during classical evaluation; its results are not independent external validation. Read [RESULTS.md](RESULTS.md) for interpretation and [results/README.md](../results/README.md) for saved aggregate evidence.

### 7.1. Current validation slice analysis

After the POS baseline and the complete ablation run, you can inspect span/POS slices:

```shell
uv run --no-sync python -m src.evaluation.nucle_span_analysis --output reports/nucle_span_diagnostics
```

Its input paths are fixed: canonical preparation/split, `reports/nucle_pos_baseline/`, and `reports/nucle_feature_ablation/`. It reads `split_summary.json` and `essay_groups.csv` as well as predictions/summaries. It writes `summary.json` and `metrics.csv` to a new output directory, without training or test scoring. Its only CLI option is `--output`.

### 7.2. Historical selection and evaluation

These are separate tools for a complete research workspace. They are not required by sections 4–6, and a public clone lacks some required protocols/evidence. Old locks record their original source/artifact paths and hashes; a newly prepared dataset or a directory rename does not make it compatible with an old lock.

| Tool | Invocation after `uv run --no-sync python -m` | Required evidence and behavior |
|---|---|---|
| Classical final selection | `src.training.nucle_final_selection` | Canonical features/preparation/split, complete POS/ablation evidence, and genuine `docs/final_evaluation_protocol.md`. Performs 40 new grid fits and 12 prior-configuration refits, requires prediction replay, and creates checkpoints plus selection evidence under `reports/final_evaluation/`. It creates the checkpoints; pre-existing final checkpoints or locks are not inputs to this fitting stage. |
| Freeze classical selection | `src.training.nucle_final_selection --freeze` | Completed, reviewed selection outputs; creates `lock.json`/`lock.sha256`. Run separately after selection. |
| Classical test | `src.evaluation.nucle_final_evaluation score` | Compatible frozen selection, code, and inputs; scores exactly 2,368 test samples once at its fixed paths. |
| Classical bootstrap | `src.evaluation.nucle_final_evaluation bootstrap` | Valid lock and saved classical test predictions; writes group-resampling weights, confidence intervals, and aggregate tables. Can replace those derived outputs. |
| Classical checkpoint replay | `src.evaluation.nucle_final_evaluation replay` | Valid lock, checkpoints, saved test encodings/predictions; verifies frozen inference and writes `checkpoint_replay.json`. |
| Historical five-epoch CLS pilot | `src.training.bert_span_classifier --pilot` | Canonical preparation/split and local pretrained metadata/files; optimizes up to 20 train batches and writes `reports/contextual_model_validation/bert/pilot.json`. |
| Historical five-epoch CLS search | `src.training.bert_span_classifier --train` | Same inputs plus genuine `docs/bert_experiment_protocol.md`; writes historical run checkpoints, validation histories/predictions, and selection. It has no test mode. |
| Historical CLS replay | `src.evaluation.bert_checkpoint_verification` | Historical CLS selection/checkpoints, tokenizer/pretrained files, canonical data; verifies validation predictions and re-evaluates train/validation. This is not the current span-mean checkpoint loader. |
| Historical learning probes | `src.evaluation.bert_learning_diagnostics` | Historical CLS artifacts and genuine `docs/bert_learning_diagnostics_protocol.md`; train-only 100-example optimization/gradient probes in a new `reports/bert_learning_diagnostics/` directory. |
| Same-sentence target probe | `src.evaluation.bert_target_pair_probe` | Historical CLS primary checkpoint, train samples/split, and an existing diagnostics directory; writes `same_sentence_pairs.json`, refusing to replace that file. |
| Preprocessing sensitivity | `src.evaluation.preprocessing_sensitivity_audit` | Old-policy/current preparations with matching IDs, canonical split, and benchmark validation predictions. Refits train-only LR/POS and evaluates validation; creates `reports/contextual_model_validation/audit/`, including `legacy_validation_predictions.csv` and `validation_predictions.csv`. |
| LR thread sensitivity | `src.evaluation.logistic_thread_sensitivity` | Canonical features/split, benchmark predictions, and the preceding audit's `validation_predictions.csv`; refits train-only LR with 4/10 threads and writes `thread_diagnostic.json`. |

The downloader, classical final-selection runner, positional classical evaluator, and fixed-path probes do not share an argparse interface. Use only the invocations documented for them: for example, passing `--help` to `nucle_final_selection` starts its fitting branch.

### 7.3. Historical BERT/classical analysis

`src.evaluation.bert_final_analysis` is an analysis tool, not an extra BERT training step. It requires the tested BERT experiment, compatible classical lock/test predictions, bootstrap weights/results, `reports/evaluation_followup/reviewed_overall_results.csv`, and source samples for its private audit. A new BERT run or public aggregate CSVs alone do not supply those inputs.

In a compatible complete research workspace, use the same BERT experiment path that was tested:

```shell
uv run --no-sync python -m src.evaluation.bert_final_analysis --experiment reports/bert_new --output reports/bert_analysis_new
```

It verifies saved evidence and writes tables, figures, paired group-bootstrap comparisons, and a local private audit packet to a new output directory. It does not run checkpoint inference or train models. Original paired bootstrap comparisons require row-level predictions and matching group IDs; the public aggregate tables cannot reconstruct them.

## 8. Continuous integration

The [CI workflow](../.github/workflows/ci.yml) runs on Windows and Linux. It checks the checkout against `HEAD`, installs the base environment and optional BERT requirement, then runs the synthetic suite and demo. Use the live GitHub Actions run to check its status.

CI does not obtain NUCLE, download pretrained research weights, or rerun the full research benchmark. A local verification run and a CI run are separate results.

## 9. Clean checkout and line endings

Text files use LF as configured by `.gitattributes`; no global Git line-ending change is required. Check local changes with:

```shell
git status --short
```

Before retrying a failed stage, use its actual error to choose the next action:

| Symptom | What to check |
|---|---|
| `src` import fails or files are not found | Run from the repository root using the module commands shown above. |
| Missing spaCy/model dependency | Complete section 1; use the repository environment rather than an unrelated Python installation. |
| `No module named transformers` | Install the optional BERT requirement after the most recent base sync. |
| Source checksum or CSV/audit mismatch | Check the original source; regenerate understanding and quality evidence from that same source before preparation. |
| Missing split summary | The split filename is `split_summary.json`; `summary.json` belongs to other stages. |
| Output directory already exists | Keep the recorded run. For a new experiment, choose new output paths; for interrupted BERT training, use the unchanged config/output with `--resume`. Classical runners have no resume mode. |
| Custom paths break the masked ablation or a diagnostic | Those tools include fixed input paths. Use canonical paths in a separate experiment checkout; changing `--output` alone cannot redirect their inputs. |
| BERT count/class/group check fails | Compare prepared IDs and `split_summary.json` with the chosen config. Confirm partition membership and all five labels; do not suppress the guard. |
| Resume or lock verification fails | Check saved config, paths, code, environment, and hashes. Preserve the original experiment; intentional changes need a new run. |
| Historical protocol/checkpoint/evidence is missing | Use the current workflows or restore the genuine matching research artifacts. Placeholder files do not satisfy the checks. |

New output paths are for new experiments, not a way to retune against an already scored test. Preserve historical experiments with their original checkout, inputs, and locks. New preparation manifests record their current code/input snapshot; they do not claim compatibility with an old research lock.

## 10. File-by-file reference

Runnable modules are listed below with their options and the workflow that explains inputs/outputs. The shared-module examples, individual tests, and non-executable artifact index follow. Each normal workflow command appears at its point of use above.

### A. Public demo

[`examples/synthetic_demo.py`](../examples/synthetic_demo.py) runs with the command in [section 3](#3-run-the-synthetic-demonstration); it has no CLI options and produces no files.

### B. Data preparation scripts

| File | CLI options | Instructions |
|---|---|---|
| [data_download.py](../src/data/data_download.py) | None | [4.1](#41-place-the-source-file-and-verify-its-identity) |
| [data_understanding.py](../src/data/data_understanding.py) | `--input`, `--csv`, `--report` | [4.2](#42-export-annotations) |
| [data_quality.py](../src/data/data_quality.py) | `--input`, `--csv`, `--output-dir`, `--report`, `--release` | [4.3](#43-generate-quality-and-duplicate-evidence) |
| [prepare_nucle.py](../src/data/prepare_nucle.py) | `--source`, `--annotations`, `--audit`, `--output`, `--expected-source-sha256`, `--policy {v1,v2}` | [4.4](#44-prepare-known-span-samples) |
| [group_split_nucle.py](../src/data/group_split_nucle.py) | `--source`, `--prepared`, `--duplicate-report`, `--output`, `--seed` | [4.5](#45-split-connected-groups) |

### C. Features and classical training

| File | CLI options | Instructions |
|---|---|---|
| [nucle_pos.py](../src/features/nucle_pos.py) | `--prepared`, `--split`, `--output` | [5.1](#51-fit-the-pos-baseline) |
| [nucle_features.py](../src/features/nucle_features.py) | `--prepared`, `--split`, `--output` | [5.2](#52-extract-features-and-fit-the-encoder) |
| [nucle_benchmark.py](../src/training/nucle_benchmark.py) | `--features`, `--split`, `--output` | [5.3](#53-train-the-full-lr-and-decision-tree-benchmark) |
| [nucle_ablation.py](../src/training/nucle_ablation.py) | `--features`, `--split`, `--output`, repeatable `--variant` | [5.4](#54-train-feature-ablations) |
| [nucle_final_selection.py](../src/training/nucle_final_selection.py) | Fixed-path fitting or `--freeze`; no argparse help | [7.2](#72-historical-selection-and-evaluation) |

### D. BERT training

[`bert_small_experiment.py`](../src/training/bert_small_experiment.py) is the current runner; follow [section 6](#6-run-a-new-bert-small-experiment).

| Subcommand | Options |
|---|---|
| `check` | `--config` (defaults to the supplied config) |
| `train` | `--config`, required `--output`, optional `--resume` |
| `select` | Required `--experiment` |
| `test` | Required `--selection`, required `--output` |

[`bert_span_classifier.py`](../src/training/bert_span_classifier.py) is the historical runner: choose exactly one of `--pilot` or `--train`; see [7.2](#72-historical-selection-and-evaluation). Its checkpoints and selection format differ from the current runner's.

### E. Evaluation and diagnostics

| File | Interface | Instructions |
|---|---|---|
| [nucle_span_analysis.py](../src/evaluation/nucle_span_analysis.py) | `--output` | [7.1](#71-current-validation-slice-analysis) |
| [nucle_final_evaluation.py](../src/evaluation/nucle_final_evaluation.py) | Positional `score`, `bootstrap`, or `replay`; fixed paths | [7.2](#72-historical-selection-and-evaluation) |
| [bert_checkpoint_verification.py](../src/evaluation/bert_checkpoint_verification.py) | No CLI options; fixed paths | [7.2](#72-historical-selection-and-evaluation) |
| [bert_learning_diagnostics.py](../src/evaluation/bert_learning_diagnostics.py) | No CLI options; fixed paths | [7.2](#72-historical-selection-and-evaluation) |
| [bert_target_pair_probe.py](../src/evaluation/bert_target_pair_probe.py) | No CLI options; fixed paths | [7.2](#72-historical-selection-and-evaluation) |
| [preprocessing_sensitivity_audit.py](../src/evaluation/preprocessing_sensitivity_audit.py) | No CLI options; fixed paths | [7.2](#72-historical-selection-and-evaluation) |
| [logistic_thread_sensitivity.py](../src/evaluation/logistic_thread_sensitivity.py) | No CLI options; fixed paths | [7.2](#72-historical-selection-and-evaluation) |
| [bert_final_analysis.py](../src/evaluation/bert_final_analysis.py) | `--experiment`, `--output` | [7.3](#73-historical-bertclassical-analysis) |

### F. Shared modules and package files

These files do not have standalone main programs. Running `python file.py` would only define objects or constants and does not perform the intended pipeline. Import them from the associated runner. The commands in the table below are import checks only: package imports exit without output, while selected checks print an API name or metadata. The actual-use examples after the table perform synthetic parsing, conversion, scoring, and fitting. BERT's wrapper requires the optional dependency.

| File | Role / actual use | Import/smoke command |
|---|---|---|
| [examples/__init__.py](../examples/__init__.py) | Examples package marker | `uv run --no-sync python -c "import examples"` |
| [src/__init__.py](../src/__init__.py) | Root package marker | `uv run --no-sync python -c "import src"` |
| [src/data/__init__.py](../src/data/__init__.py) | Data package marker | `uv run --no-sync python -c "import src.data"` |
| [src/data/boundary_challenges.py](../src/data/boundary_challenges.py) | Known boundary-case IDs/policy metadata; used by preparation | `uv run --no-sync python -c "from src.data.boundary_challenges import BOUNDARY_CHALLENGES; print(len(BOUNDARY_CHALLENGES))"` |
| [src/data/constants.py](../src/data/constants.py) | Shared paths and fixed target label order | `uv run --no-sync python -c "from src.data.constants import TARGET_LABELS; print(TARGET_LABELS)"` |
| [src/data/nucle_sgml.py](../src/data/nucle_sgml.py) | SGML parser and document/annotation records; real parsing needs an authorized source | `uv run --no-sync python -c "from src.data.nucle_sgml import load_nucle; print(load_nucle.__name__)"` |
| [src/data/parse_nucle.py](../src/data/parse_nucle.py) | Document-to-annotation DataFrame and span reconstruction helpers | `uv run --no-sync python -c "from src.data.parse_nucle import documents_to_dataframe; print(documents_to_dataframe.__name__)"` |
| [src/data/sentence_boundaries.py](../src/data/sentence_boundaries.py) | Text-only boundary repair rules; called by preparation | `uv run --no-sync python -c "from src.data.sentence_boundaries import rule_metadata; print(rule_metadata.__name__)"` |
| [src/evaluation/__init__.py](../src/evaluation/__init__.py) | Evaluation package marker | `uv run --no-sync python -c "import src.evaluation"` |
| [src/evaluation/metrics.py](../src/evaluation/metrics.py) | Fixed five-class metrics; requires aligned label sequences for scoring | `uv run --no-sync python -c "from src.evaluation.metrics import scores; print(scores.__name__)"` |
| [src/features/__init__.py](../src/features/__init__.py) | Feature package marker | `uv run --no-sync python -c "import src.features"` |
| [src/models/__init__.py](../src/models/__init__.py) | Model package marker | `uv run --no-sync python -c "import src.models"` |
| [src/models/bert_span_readout.py](../src/models/bert_span_readout.py) | BERT CLS/span-mean wrapper; actual forward needs a model and token tensors | `uv run --no-sync python -c "from src.models.bert_span_readout import BertReadout; print(BertReadout.__name__)"` |
| [src/models/nucle_logistic.py](../src/models/nucle_logistic.py) | Sparse LR optimizer; actual fitting needs encoded features and train labels | `uv run --no-sync python -c "from src.models.nucle_logistic import fit_logistic; print(fit_logistic.__name__)"` |
| [src/models/nucle_tree.py](../src/models/nucle_tree.py) | Deterministic Gini Tree; fit/predict methods take encoded rows | `uv run --no-sync python -c "from src.models.nucle_tree import GiniTree; print(GiniTree.__name__)"` |
| [src/training/__init__.py](../src/training/__init__.py) | Training package marker | `uv run --no-sync python -c "import src.training"` |

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

Expected: one annotation, ID `0`, span `was`, label `SVA`, and a valid offset. The parser produces document/annotation objects; the converter produces a DataFrame. For an authorized real SGML file, import `Path` from `pathlib` and `load_nucle` from `src.data.nucle_sgml`, then call `load_nucle(Path("data_set/raw/nucle3.2.sgml"))` to supply documents to the same converter. To export the actual CSV and understanding report, use the command in [step 4.2](#42-export-annotations).

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

After leaving the Python interpreter, use the [demo command in section 3](#3-run-the-synthetic-demonstration) to exercise `TrainOnlyEncoder` and `fit_logistic` with synthetic sentence/span inputs.

For research LR/Tree training, use `src.training.nucle_benchmark` or `src.training.nucle_ablation` in [section 5](#5-train-classical-baselines-and-models) with their required prepared features. These runners construct the inputs and call the library models; there is no independent `nucle_logistic.py` training CLI.

For `src/models/bert_span_readout.py`, install the optional BERT dependencies, then use the individual command for [tests/test_bert_readout.py in G](#g-individual-tests) to exercise forwards, span masks, and gradients.

The tests create random tiny BERT models without downloading pretrained checkpoints. Real training calls the wrapper from `src.training.bert_small_experiment` in [section 6](#6-run-a-new-bert-small-experiment). The wrapper cannot perform a useful standalone forward without a base model, marker IDs, and token tensors. Package `__init__.py` files only establish importable packages; their import checks are the appropriate standalone check.

### G. Individual tests

Use pytest, not `python tests/test_*.py`: these modules define tests but have no test-running main function. The aggregate command is in [section 2](#2-run-tests-without-the-research-corpus). Install `requirements-bert.txt` for all BERT-related coverage. A licensed-fixture skip is expected in a public checkout.

| Test file | Individual command | Coverage / requirement |
|---|---|---|
| [tests/test_bert_final_analysis.py](../tests/test_bert_final_analysis.py) | `uv run --no-sync python -m pytest tests/test_bert_final_analysis.py -q` | Paired group bootstrap and deterministic audit-selection helpers; no research packets. |
| [tests/test_bert_readout.py](../tests/test_bert_readout.py) | `uv run --no-sync python -m pytest tests/test_bert_readout.py -q` | Tiny random BERT, target masks, gradients, padding; needs transformers. |
| [tests/test_bert_small_experiment.py](../tests/test_bert_small_experiment.py) | `uv run --no-sync python -m pytest tests/test_bert_small_experiment.py -q` | Synthetic train/resume/validation-selection/lock/test lifecycle; needs transformers. |
| [tests/test_bert_span_classifier.py](../tests/test_bert_span_classifier.py) | `uv run --no-sync python -m pytest tests/test_bert_span_classifier.py -q` | Synthetic WordPiece tokenizer, cropping, offsets, no label/correction leakage; needs transformers. |
| [tests/test_boundary_challenges.py](../tests/test_boundary_challenges.py) | `uv run --no-sync python -m pytest tests/test_boundary_challenges.py -q` | Real licensed boundary fixture; expected module skip when undistributed fixture is absent. |
| [tests/test_datadownload.py](../tests/test_datadownload.py) | `uv run --no-sync python -m pytest tests/test_datadownload.py -q` | Mocked download/retry/partial-file cleanup; no network download. |
| [tests/test_final_evaluation.py](../tests/test_final_evaluation.py) | `uv run --no-sync python -m pytest tests/test_final_evaluation.py -q` | Fixed-label metrics, whole-group resampling, encoder serialization, feature removal, locks. |
| [tests/test_nucle_benchmark.py](../tests/test_nucle_benchmark.py) | `uv run --no-sync python -m pytest tests/test_nucle_benchmark.py -q` | Sparse tree, metrics, train/validation loader isolation, benchmark timing. |
| [tests/test_nucle_features.py](../tests/test_nucle_features.py) | `uv run --no-sync python -m pytest tests/test_nucle_features.py -q` | Synthetic extraction, train-only vocabulary, leakage rejection, offset mismatch. |
| [tests/test_nucle_preparation.py](../tests/test_nucle_preparation.py) | `uv run --no-sync python -m pytest tests/test_nucle_preparation.py -q` | Synthetic preparation without a review log, CLI/API use, source/audit validation and no-overwrite; requires committed Git HEAD. |
| [tests/test_nucle_quality.py](../tests/test_nucle_quality.py) | `uv run --no-sync python -m pytest tests/test_nucle_quality.py -q` | Synthetic quality flags, overlaps, duplicate detection and source/CSV agreement. |
| [tests/test_nucle_understanding.py](../tests/test_nucle_understanding.py) | `uv run --no-sync python -m pytest tests/test_nucle_understanding.py -q` | Synthetic SGML parsing, missing corrections, span checks and canonical paths. |
| [tests/test_preparation_alignment.py](../tests/test_preparation_alignment.py) | `uv run --no-sync python -m pytest tests/test_preparation_alignment.py -q` | Synthetic token alignment and partial-token flags, including rejection of corrupted samples. |
| [tests/test_sentence_boundaries.py](../tests/test_sentence_boundaries.py) | `uv run --no-sync python -m pytest tests/test_sentence_boundaries.py -q` | Synthetic boundary rules and explicit policy versions. |

Read [tests/README.md](../tests/README.md) for test scope. Tests do not recreate the NUCLE research run, acquire corpus permissions, or adjudicate gold labels.

### H. Configuration, documentation, and result files

These files are consumed by a tool or viewed as artifacts; they are not standalone Python scripts. Dataset-derived inputs used by training live under ignored `data_set/` and `reports/`, not in the public aggregate result files.

| File | How to run, consume, or view it |
|---|---|
| [.editorconfig](../.editorconfig) | Read automatically by compatible editors; formatting settings, not an executable. |
| [.gitattributes](../.gitattributes) | Read automatically by Git for text/binary and line-ending handling. |
| [.github/workflows/ci.yml](../.github/workflows/ci.yml) | Runs on GitHub after pushes/PRs, or Actions -> CI -> Run workflow; tests/demo on Windows/Linux. |
| [.gitignore](../.gitignore) | Read automatically by Git to exclude local/private artifacts; not a data-processing script. |
| [.python-version](../.python-version) | Read by Python/uv tooling; the documented commands explicitly select Python 3.13.7. |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Read development, test, data-handling, and experiment contribution instructions. |
| [README.md](../README.md) | Project overview and navigation; execution instructions are maintained in this guide. |
| [configs/bert_small_training.json](../configs/bert_small_training.json) | Pass to `src.training.bert_small_experiment check/train --config ...`; declares paths, expected split sizes, grid, seeds, and training settings. |
| [docs/ARCHITECTURE.md](ARCHITECTURE.md) | Read data flow, encoder/model design, and reproducibility boundaries. |
| [docs/README.md](README.md) | Open the documentation index for a suggested reading order. |
| [docs/RESULTS.md](RESULTS.md) | Read result interpretation, paired CIs, class tradeoffs, and limitations. |
| [docs/RUNNING.md](RUNNING.md) | Setup, ordered workflows, CLI reference, API examples, and research-input requirements. |
| [pyproject.toml](../pyproject.toml) | Declares project/dev dependencies; install them using [section 1](#1-install-the-environment). |
| [pytest.ini](../pytest.ini) | Automatically loaded by `python -m pytest`; sets repository import path and test directory. |
| [requirements-bert.txt](../requirements-bert.txt) | Optional BERT package pin; use its install command in [section 1](#1-install-the-environment). |
| [results/README.md](../results/README.md) | Open the index for published aggregate results and report provenance. |
| [results/classical_ablations.csv](../results/classical_ablations.csv) | View all 20 classical/baseline pipeline names, CIs and aliases. |
| [results/confusions.csv](../results/confusions.csv) | View aggregate off-diagonal error counts; not individual examples. |
| [results/figures/benchmark_ci.png](../results/figures/benchmark_ci.png) | View the published test-F1/CI plot; no execution. |
| [results/figures/paired_differences.png](../results/figures/paired_differences.png) | View paired difference intervals; no execution. |
| [results/figures/per_class_f1.png](../results/figures/per_class_f1.png) | View published class-specific F1; no execution. |
| [results/figures/primary_learning_curve.png](../results/figures/primary_learning_curve.png) | View primary BERT train/validation curves; no execution. |
| [results/overall_results.csv](../results/overall_results.csv) | View in GitHub or a CSV reader: headline model metrics and CIs. |
| [results/paired_differences.csv](../results/paired_differences.csv) | View paired BERT-primary model differences and CIs. |
| [results/per_class_metrics.csv](../results/per_class_metrics.csv) | View per-model/class precision, recall, F1, support. |
| [results/reports/bert-comparison.md](../results/reports/bert-comparison.md) | Read the extended BERT comparison and interpretation; no execution. |
| [results/reports/final-report.md](../results/reports/final-report.md) | Read the complete English study; no report generator required. |
| [results/reports/presentation.md](../results/reports/presentation.md) | Read the 12 English presentation sections and speaker notes. |
| [results/seed_results.csv](../results/seed_results.csv) | View selected BERT seed/checkpoint outcomes and primary designation. |
| [results/validation_grid.csv](../results/validation_grid.csv) | View BERT configuration means and sample standard deviations. |
| [tests/README.md](../tests/README.md) | Read test inputs, optional dependencies, expected skips, and Git HEAD requirement. |
| [uv.lock](../uv.lock) | Consumed by the same locked uv installation; not runnable Python and not the historical model-selection lock. |
