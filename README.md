# ESL Grammar Error Classification

Classifying **five grammatical error types at a known error span** in English learner writing, using leakage-aware feature engineering, classical machine learning, and a small fine-tuned BERT model.

This repository presents the modeling code, tests, run guides, and aggregate results of an academic team project. It includes a synthetic example that runs without the research corpus. Report-generation tooling and private research artifacts are excluded.

## Task

```text
Original sentence + known error offsets
                  |
          error-type classifier
                  |
    ArtOrDet / Prep / Nn / Vform / SVA
```

One annotation is one sample; a sentence can produce several samples. This evaluates error-type classification, not automatic error detection or correction generation.

| Label | Meaning | Illustrative error → correction |
|---|---|---|
| ArtOrDet | Article or determiner | `a apple` → `an apple` |
| Prep | Preposition | `interested on music` → `interested in music` |
| Nn | Noun number | `two book` → `two books` |
| Vform | Verb form | `can goes` → `can go` |
| SVA | Subject–verb agreement | `She go every day` → `She goes every day` |

The examples above are illustrative, not quotations from NUCLE.

## Main results

All rows use the same 2,368 test annotations in 97 connected groups. Macro-F1 treats each error type equally.

| Model | Validation Macro-F1 | Test Macro-F1 | Test accuracy | Test F1 95% CI |
|---|---:|---:|---:|---|
| Majority | 0.1184 | 0.1184 | 0.4206 | [0.1104, 0.1279] |
| POS rule | 0.7048 | 0.7106 | 0.7441 | [0.6766, 0.7365] |
| Logistic Regression, Full | 0.8067 | **0.8163** | 0.8357 | [0.7876, 0.8382] |
| Decision Tree, Full | 0.7879 | 0.7996 | 0.8095 | [0.7693, 0.8246] |
| BERT-small, primary seed | **0.8173** | 0.8146 | **0.8438** | [0.7919, 0.8350] |

![Test Macro-F1 and group-bootstrap confidence intervals](results/figures/benchmark_ci.png)

BERT's test Macro-F1 across three seeds is **0.8182 ± 0.0038** (mean ± sample standard deviation). The primary seed was fixed before BERT test scoring and is used for paired comparisons.

**BERT primary − LR: −0.0017, paired CI95% [−0.0184, 0.0182].** This does not establish that either model is better. BERT's higher accuracy comes with weaker SVA F1; aggregate accuracy alone hides that tradeoff.

The BERT extension was performed after classical test results were known, using the same test set. It is an additional comparison, not an independent external evaluation. See [results and limitations](docs/RESULTS.md) and the [full-precision CSVs](results/README.md).

## Engineering and experimental design

- Parse NUCLE SGML and preserve character offsets, annotation identity, and provenance.
- Keep connected groups of related essays in one partition to reduce leakage from shared content.
- Fit a categorical/lexical feature encoder on train only; use fixed columns and unknown-value handling for validation/test.
- Implement sparse multinomial Logistic Regression in PyTorch and a deterministic Gini Decision Tree.
- Compare structure, lexical, POS, morphology, and dependency features through incremental experiments, masking, and ablations.
- Fine-tune BERT-small with CLS/span-mean readouts, separate encoder/head learning rates, checkpoint replay checks, and resumable training.
- Select models using validation; compare saved test predictions with paired bootstrap by connected group.

## Quick start

Run from the repository root. The reference research environment used Python **3.13.7**; the declared supported range is in `pyproject.toml`.

```bash
uv sync --locked --python 3.13.7
uv run --no-sync python -m pytest tests -q
uv run --no-sync python -m examples.synthetic_demo
```

The demo uses hand-written examples, the existing spaCy feature extractor, a train-only encoder, and Logistic Regression. It creates no research artifacts and downloads no corpus or BERT checkpoint. Its metrics are demonstration output, not the research results above. The spaCy English package is installed through the base dependency lock.

Portfolio validation: **106 tests passed, 1 skipped** with the optional BERT dependency present; the synthetic demo also ran successfully. Tests used the existing research environment. A fresh dependency installation was not rerun; see [validation details](results/validation.json).

For BERT tests and training, install the optional dependency before rerunning tests:

```bash
uv pip install --python .venv -r requirements-bert.txt
uv run --no-sync python -m pytest tests -q
```

Without `transformers`, BERT-specific tests are skipped. The licensed real-corpus boundary fixture is not distributed, so its test module is skipped. Other tests use synthetic inputs, and BERT tests use tiny locally initialized models/vocabularies without downloading pretrained weights.

For complete instructions, input requirements, and fresh-output commands, see [Running the project](docs/RUNNING.md). The commands above require network access to install dependencies on a new machine. No inference service or pretrained task checkpoint is distributed.

## Repository map

```text
src/
  data/         SGML parsing, quality checks, preparation, group splitting
  features/     POS baseline and train-only S/L/P/M/D encoding
  models/       Sparse LR, Gini Tree, BERT span readout
  training/     Benchmarks, ablations, selection, BERT train/lock/test
  evaluation/   Metrics, bootstrap, and experiment diagnostics
tests/          Synthetic regression and lifecycle tests
examples/       Corpus-free end-to-end demonstration
configs/        BERT experiment configuration
docs/           Architecture, running instructions, result interpretation
results/        Aggregate CSVs, selected figures, English Markdown reports
```

The former `src/reporting/` package is intentionally absent. Document-export validators that depend on that package are also omitted; ML training, feature extraction, and tests do not import it. The ML source retained from the research project is copied without algorithm changes.

## What can be reproduced?

| Available from this repository | Requires independently supplied research inputs |
|---|---|
| Run synthetic tests and the demonstration | Recreate the NUCLE experiment dataset |
| Inspect algorithms and selected configurations | Rebuild the historical split using its review inputs |
| Inspect aggregate metrics, ablations, figures, and final reports | Replay original predictions/checkpoints or historical lock hashes |
| Train a new experiment after supplying compatible inputs | Reproduce exact research scores in the original environment |

The repository excludes NUCLE text/corrections, row-level predictions, review packets, encoders/vocabularies, model checkpoints, caches, private work logs, old archives, and report generators. Internal post-prediction audit/review helpers and the one-off historical replay driver are omitted. Shared evaluation routines and data-integrity checks used by the experiments/tests remain; historical test-scoring routines still require private artifacts and are not a fresh-clone quick start. Research-era manifests and source hashes are not regenerated to imply that this curated export is the original locked workspace.

## Documentation

- [Architecture and data flow](docs/ARCHITECTURE.md)
- [Installation, testing, and training](docs/RUNNING.md)
- [Results, model selection, and limitations](docs/RESULTS.md)
- [Aggregate files and provenance](results/README.md)
- [Test scope](tests/README.md)
- [Final research report, English Markdown](results/reports/final-report.md)
- [BERT comparison, English Markdown](results/reports/bert-comparison.md)
- [Presentation and speaker notes, English Markdown](results/reports/presentation.md)

## Attribution and assistance

This was an academic team project; this portfolio does not infer individual contributions from the module list. AI tools assisted with code, tests, analysis, and documentation; BERT training/testing commands were run by the project user. Technical checks and AI-assisted language audits do not replace independent expert adjudication of annotations.

Dataset reference: Dahlmeier, Ng, and Wu (2013), *Building a Large Annotated Corpus of Learner English: The NUS Corpus of Learner English*, BEA. Obtain NUCLE separately under its applicable terms; it is not included in this repository.
