# Published aggregate results

These files were copied from the completed research artifacts for portfolio review. CSV values and selected figures/PDFs retain their original saved contents; no research model was retrained during export.

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

## Final research PDFs

- [Final project report, Vietnamese](reports/bao_cao_tong_ket_NUCLE.pdf)
- [BERT comparison, Vietnamese](reports/BERT_comparison_report.pdf)
- [Presentation, Vietnamese](reports/NUCLE_presentation.pdf)

These PDFs retain their research-era content and may mention private artifact paths or reporting modules absent from this export. For commands available in this repository, follow [RUNNING.md](../docs/RUNNING.md), not historical PDF paths. The English [results guide](../docs/RESULTS.md) summarizes the current interpretation and limitations.

No CSV here contains per-sample inputs/predictions, essay text, correction text, or private review notes. New experiment outputs belong under the ignored `reports/` tree, not in this saved aggregate snapshot.

[validation.json](validation.json) records the export's test/demo checks and environment. [export_manifest.json](export_manifest.json) identifies each published file with its SHA-256 and Git blob SHA; it describes this curated export, not the historical research lock.
