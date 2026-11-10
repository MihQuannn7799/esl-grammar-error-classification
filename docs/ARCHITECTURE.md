# Architecture and data flow

## Prediction contract

An input consists of the original sentence and a known error span, identified by Python character offsets `[error_start, error_end)`. The slice must equal `error_span`. Output is one of the five labels defined in [constants.py](../src/data/constants.py).

Gold labels supervise training and scoring. Corrections, sample/essay IDs, group membership, and review decisions are not predictors. IDs support joins, grouping, and traceability. Multiple annotations in the same sentence remain separate samples.

## Data preparation and grouping

1. Parse SGML documents and annotations with [nucle_sgml.py](../src/data/nucle_sgml.py).
2. Audit offsets, missing fields, overlaps, duplicates, and source/CSV agreement.
3. Construct sentences and annotation-local offsets with [prepare_nucle.py](../src/data/prepare_nucle.py). Version 2 uses fixed text-only sentence-boundary rules. The public runner validates the source, annotation CSV, and quality audit without a private overlap-review log. It does not add overlap-review statuses to prepared records; new manifests use schema version 3.
4. Connect related essays using duplicate content and exact model-input evidence, then split connected groups with [group_split_nucle.py](../src/data/group_split_nucle.py).

The research split seed was `20261013`: 11,052 train, 2,368 validation, and 2,368 test annotations. There are 1,045/99/97 groups with target samples in those partitions. The corpus contains 15,788 target annotations in 11,272 distinct prepared sentences. Semantic near-duplicate detection was not exhaustive.

## Classical branch

```text
Known-span sentence
    → spaCy POS / morphology / dependency analysis
    → feature dictionary S + L + P + M + D
    → TrainOnlyEncoder
    → sparse numeric vector
    → Logistic Regression or Decision Tree
    → error label
```

| Feature group | Information |
|---|---|
| S | Span structure, length, and position |
| L | Lexical span/context identities and unigram/bigram indicators |
| P | POS signatures and local POS context |
| M | Number, Person, Tense, VerbForm, and missing indicators |
| D | Dependency relations, heads/dependents, distances, and subject information |

The Full representation has 16,180 columns. Lexical context uses up to two tokens on either side, while dependency information comes from parsing the complete sentence. Numeric features retain their original scale. The pooled n-gram channel has a 500-term cap; that cap does not apply to every lexical slot.

[TrainOnlyEncoder](../src/features/nucle_features.py) learns categorical values, vocabularies, and column ordering from train rows only. It rejects other partitions in `fit`, uses unknown columns for unseen values, and rejects forbidden predictor families. Validation and test use the fitted mapping without adding columns.

[Logistic Regression](../src/models/nucle_logistic.py) computes `logits = xW + b`, then chooses the largest logit. Training minimizes weighted mean cross-entropy plus `||W||² / (2*C*n_train)` with PyTorch LBFGS; bias is not regularized. Smaller `C` means stronger regularization. Full selected `C=0.1`, no class weighting. A `change_tolerance` stop is not a guarantee that the gradient tolerance was reached.

[Decision Tree](../src/models/nucle_tree.py) uses deterministic CART splits based on Gini reduction. Full selected depth 8, minimum leaf size 5, no class weighting. In its balanced mode, weights affect impurity, while leaf predictions use the majority raw class count.

## Baselines

- Majority always predicts the train-majority class, ArtOrDet.
- POS rule maps a single ADP signature to Prep and DET to ArtOrDet. Other signatures use their train-majority label; missing/unseen signatures fall back to the overall train majority.

Both baselines are selected without reading validation/test labels into their predictor rules.

## BERT branch

```text
[CLS] left [SPAN_START] target [SPAN_END] right [SEP]
    → BERT-small encoder
    → CLS readout or mean of contextual target states
    → shared pooler / dropout / classification head
    → five logits
```

The checkpoint family is `google/bert_uncased_L-2_H-128_A-2`: 2 layers, hidden size 128, and 2 attention heads. This is not BERT-base. The tokenizer maps text to WordPiece IDs; the neural encoder computes contextual hidden states. BERT does not consume the classical S/L/P/M/D vector.

The [span readout wrapper](../src/models/bert_span_readout.py) averages hidden states strictly inside the target markers. Empty spans fall back to the start-marker state. The 128-token budget preserves the target while cropping context when necessary.

The [extended experiment runner](../src/training/bert_small_experiment.py) supports preflight, train/resume, validation selection/locking, and test. It trains CLS/span-mean × two head learning rates × three seeds, with encoder LR `5e-5`, maximum 20 epochs, and patience 4. Validation selected span mean, head LR `1e-4`; primary seed is `20261013`.

## Evaluation and reproducibility boundaries

[metrics.py](../src/evaluation/metrics.py) uses a fixed five-label Macro-F1 and confusion matrices with true rows/predicted columns. [group_bootstrap.py](../src/evaluation/group_bootstrap.py) computes paired group-bootstrap metrics from supplied predictions without private research files. Models share the same resampled groups in each bootstrap replicate.

The final classical stage contained 40 new grid fits and 12 historical refits. Full-minus-D aliases S+L+P+M; 18 LR/Tree names correspond to 16 distinct LR/Tree checkpoints, plus two baselines.

The original research workflow also included source hashes, locks, review inputs, and replay checks. The portfolio excludes private artifacts and reporting code, so its source tree differs from that historical snapshot. Historical diagnostics, the old CLS training runner, private comparison/report generators, and the one-off raw-to-test replay driver are excluded. Shared metrics/bootstrap, span tokenization, and the current data/training/evaluation workflows remain public and are covered by synthetic tests. Existing experiment locks remain tied to their original source; do not alter old hashes to make a check pass.
