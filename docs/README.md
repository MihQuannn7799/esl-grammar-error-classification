# Documentation

## Suggested reading path

1. Follow [environment setup](RUNNING.md#1-install-the-environment), then run the [synthetic demo](RUNNING.md#3-run-the-synthetic-demonstration) to see the known-span prediction contract.
2. Read [Architecture](ARCHITECTURE.md) for grouping, train-only encoding, and model data flow.
3. Read [Results](RESULTS.md) for model selection, confidence intervals, and limitations.
4. Use [Running the project](RUNNING.md#4-research-data-requirements) for research inputs and training workflows, then follow [LR/DT/Majority/POS test scoring](RUNNING.md#55-score-lr-dt-majority-and-pos-rule-on-test) or [BERT test scoring](RUNNING.md#67-score-the-locked-checkpoints-on-test).

The [file-by-file reference](RUNNING.md#10-file-by-file-reference) is the canonical source for every script command, module API example, individual test command, and configuration/result file. README introduces the project; RUNNING.md owns setup and execution instructions.

For `src/evaluation/`, start with [which files to run or skip](RUNNING.md#70-which-evaluation-files-should-i-run). The public directory contains two runnable tools and three shared/package modules. Historical diagnostics requiring private artifacts are excluded.

## Reports and evidence

| Document | Contents |
|---|---|
| [Final project report](../results/reports/final-report.md) | Full English study, 34 tables, 14 references, methods, findings, and limitations |
| [BERT comparison](../results/reports/bert-comparison.md) | Extended BERT experiment and paired comparison with classical models |
| [Presentation](../results/reports/presentation.md) | Twelve presentation sections with speaker notes |
| [Results index](../results/README.md) | Aggregate CSVs, figures, provenance, and validation metadata |
| [Test scope](../tests/README.md) | Synthetic coverage and expected licensed-fixture skip |
| [Contribution guide](../CONTRIBUTING.md) | Development checks, research integrity, and publication scope |

The public examples demonstrate code behavior. The research reports describe saved study results. Neither a demo score nor a passing synthetic suite is a new NUCLE benchmark or an independent external evaluation.
