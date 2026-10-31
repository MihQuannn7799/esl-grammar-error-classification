# Published aggregate results

These files were copied from the completed research artifacts for portfolio review. CSV values and selected figures retain their original saved contents; no research model was retrained during export.

| File | Contents | Research source |
|---|---|---|
| [overall_results.csv](overall_results.csv) | Five headline models, validation/test F1, accuracy, macro precision/recall, CI | `reports/bert_final_analysis/overall_results.csv` |
| [per_class_metrics.csv](per_class_metrics.csv) | Precision, recall, F1, and support by model/label | `reports/bert_final_analysis/per_class_metrics.csv` |
| [paired_differences.csv](paired_differences.csv) | BERT-primary paired comparisons with CI | `reports/bert_final_analysis/paired_differences.csv` |
| [seed_results.csv](seed_results.csv) | Three selected BERT seeds and primary designation | `reports/bert_final_analysis/seed_results.csv` |
| [validation_grid.csv](validation_grid.csv) | Four BERT configurations summarized across seeds | `reports/bert_final_analysis/validation_grid.csv` |
| [confusions.csv](confusions.csv) | Aggregate off-diagonal confusion counts | `reports/bert_final_analysis/confusions.csv` |
| [classical_ablations.csv](classical_ablations.csv) | Twenty named classical/baseline pipelines, including aliases | `reports/final_evaluation/overall_results.csv` |

The classical ablation table contains Full-minus-D aliases of S+L+P+M; names do not imply distinct fitted checkpoints. Some validation entries in the classical source have historical rounding differences from the later verified headline table. Use `overall_results.csv` for the five-model headline comparison.

## Figures

- [Test Macro-F1 and CI](figures/benchmark_ci.png)
- [Per-class F1](figures/per_class_f1.png)
- [Primary BERT learning curve](figures/primary_learning_curve.png)
- [Paired differences](figures/paired_differences.png)

## English Markdown reports

- [Final project report](reports/final-report.md): translated research narrative, all 34 original tables, 14 references, and selected figures.
- [BERT comparison](reports/bert-comparison.md): the extended experiment, both original quantitative tables, two figures, and interpretation limits.
- [Presentation and speaker notes](reports/presentation.md): all 12 presentation sections in English, including translated speaker notes.

These replace the three Vietnamese PDFs in the current repository tree. Numerical results and conclusions are unchanged; links and code-scope notes are adapted to the curated public export. Historical evidence not included here is described as such. For runnable commands, use [RUNNING.md](../docs/RUNNING.md). The shorter [results guide](../docs/RESULTS.md) remains available alongside the complete reports.

No CSV here contains per-sample inputs/predictions, essay text, correction text, or private review notes. New experiment outputs belong under the ignored `reports/` tree, not in this saved aggregate snapshot.
