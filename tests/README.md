# Tests

From the repository root, after installing the base environment:

```bash
uv run --no-sync python -m pytest tests -q
```

The tests cover parsing, offset preservation, sentence boundaries, train-only feature encoding, LR/Tree behavior, fixed-label metrics, bootstrap alignment, and BERT training/selection/resume guards.

| Area | Inputs and requirements |
|---|---|
| Parser, quality, preparation, features, models | Hand-written/synthetic examples; base spaCy/model dependencies |
| HTTP downloader | Mock HTTP responses; no corpus download |
| BERT tokenizer/readout/lifecycle | Tiny local vocabulary and randomly initialized model; optional `transformers` dependency |
| Real NUCLE boundary regression | Licensed local fixture, intentionally not distributed; module skips when unavailable |

Enable BERT tests with:

```bash
uv pip install --python .venv -r requirements-bert.txt
uv run --no-sync python -m pytest tests -q
```

The test suite does not require corpus access, pretrained research checkpoints, or report generation. It does not rerun the research benchmark or independently adjudicate gold labels. See `results/validation.json` for the checks run while preparing this export, when present; the test count from an older research snapshot is not a result for a new environment.

Use a Git checkout with a committed HEAD: preparation records `git rev-parse HEAD` in its provenance, including in one synthetic integration test. A ZIP extraction without Git metadata does not satisfy that requirement.
