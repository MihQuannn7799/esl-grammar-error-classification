# ESL Grammar Error Classification

[![CI](https://github.com/MihQuannn7799/esl-grammar-error-classification/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/MihQuannn7799/esl-grammar-error-classification/actions/workflows/ci.yml)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue)](pyproject.toml)
[![Reports: English Markdown](https://img.shields.io/badge/Reports-English%20Markdown-2c7a7b)](results/README.md)

A reproducible machine learning study of **five grammar error types in English learner writing**. The project compares linguistic-feature Logistic Regression and Decision Tree models with a fine-tuned BERT-small classifier.

**Input:** an original sentence and an already known error span. **Output:** ArtOrDet, Prep, Nn, Vform, or SVA. A sentence may contain several annotations; each annotation is a separate classification example. Automatic error detection and correction generation are outside this evaluation.

[Get started](#quick-start) | [All file commands](docs/RUNNING.md#10-file-by-file-reference) | [Architecture](docs/ARCHITECTURE.md) | [Results](docs/RESULTS.md) | [Full report](results/reports/final-report.md) | [All documentation](docs/README.md)

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

Clone the repository and enter its root:

```bash
git clone https://github.com/MihQuannn7799/esl-grammar-error-classification.git
cd esl-grammar-error-classification
```

Continue in the [running guide](docs/RUNNING.md), which owns all installation and execution commands:

1. [Install the environment](docs/RUNNING.md#1-install-the-environment), including the optional BERT dependency when needed.
2. [Run the synthetic demonstration](docs/RUNNING.md#3-run-the-synthetic-demonstration), which needs no NUCLE corpus or task checkpoint.
3. [Run the tests](docs/RUNNING.md#2-run-tests-without-the-research-corpus).

The demo uses hand-written examples and the actual feature extractor, train-only encoder, and sparse LR. It writes no result files and makes no research-performance claim. CI runs synthetic checks on Windows and Linux; its badge reports current status.

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
| Score LR, DT, Majority, and POS rule on test | [Classical checkpoint, freeze, test, and bootstrap workflow](docs/RUNNING.md#55-score-lr-dt-majority-and-pos-rule-on-test) |
| Find a command or usage example for a specific file | [File-by-file reference](docs/RUNNING.md#10-file-by-file-reference) |
| Interpret scores and confidence intervals | [Results and limitations](docs/RESULTS.md) |
| Read the complete study | [Final report: 34 tables and 14 references](results/reports/final-report.md) |
| Inspect the BERT extension | [BERT comparison](results/reports/bert-comparison.md) |
| Present the findings | [Presentation and speaker notes](results/reports/presentation.md) |
| Contribute or run project checks | [Contribution guide](CONTRIBUTING.md) |

## Reproducibility and scope

A fresh checkout supports synthetic tests, the demo, and inspection of saved aggregate results. New NUCLE preparation requires independently obtained corpus access and matching annotation/quality artifacts; it does not require a private overlap-review log. Exact historical evaluation additionally needs the original research artifacts and locks. Models retain train-fitted weights; validation selects configurations and test is used after locking. Replaying saved predictions is not a new independent evaluation.

The repository excludes corpus text/corrections, row-level predictions, private reviews, checkpoints/vocabularies, caches, report generators, and one-off internal audit/replay helpers. Some retained historical scoring routines require those excluded inputs; follow the public run guide rather than executing them blindly. No pretrained task checkpoint or inference service is distributed.

## Complete file-by-file runbook

The [file-by-file reference in RUNNING.md](docs/RUNNING.md#10-file-by-file-reference) covers every public file: runnable scripts, shared modules, tests, configuration, reports, and result artifacts. It includes inputs, outputs, real API examples, and historical-reproduction requirements.

README is the project overview and navigation page. RUNNING.md is the single source for setup and execution instructions; changing a command only requires updating that guide.

## Attribution

An academic team project using NUCLE: Dahlmeier, Ng, and Wu (2013), *Building a Large Annotated Corpus of Learner English: The NUS Corpus of Learner English*. Obtain the dataset separately under its applicable terms.
