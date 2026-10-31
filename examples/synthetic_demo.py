"""Exercise the existing LR pipeline with hand-written, known-span examples.

Run from the repository root: python -m examples.synthetic_demo
No corpus, checkpoint, network request, or output files are used.
This is a wiring demonstration, not an estimate of research performance.
"""
from __future__ import annotations

from collections import Counter

import torch

from src.data.constants import TARGET_LABELS
from src.evaluation.metrics import scores
from src.features.nucle_features import TrainOnlyEncoder, extract_features
from src.features.nucle_pos import load_tagger
from src.models.nucle_logistic import fit_logistic
from src.training.nucle_ablation import sparse_tensor


TRAIN = [
    ("I ate a apple.", "a", "ArtOrDet"),
    ("He bought an book.", "an", "ArtOrDet"),
    ("She is interested on music.", "on", "Prep"),
    ("We depend of public transport.", "of", "Prep"),
    ("I have two book.", "book", "Nn"),
    ("She owns three dog.", "dog", "Nn"),
    ("He can goes home.", "goes", "Vform"),
    ("They enjoy swim together.", "swim", "Vform"),
    ("She walk to school daily.", "walk", "SVA"),
    ("The students is ready.", "is", "SVA"),
]
HOLDOUT = [
    ("She ate a orange.", "a", "ArtOrDet"),
    ("He is interested on science.", "on", "Prep"),
    ("We have four cat.", "cat", "Nn"),
    ("She can walks home.", "walks", "Vform"),
    ("The teachers is ready.", "is", "SVA"),
]


def build_rows(examples, partition, nlp):
    rows, labels = [], []
    for i, (sentence, target, label) in enumerate(examples):
        doc = nlp(sentence)
        token = next(token for token in doc if token.text == target)
        sample = {"sentence": sentence, "error_start": token.idx,
                  "error_end": token.idx + len(target), "error_span": target,
                  "span_kind": "non_empty"}
        features = extract_features(sample, doc)
        rows.append({"sample_id": f"synthetic-{partition}-{i}",
                     "partition": partition, "features": features})
        labels.append(label)
    return rows, labels


def main():
    torch.set_num_threads(1)
    nlp = load_tagger()
    train, train_labels = build_rows(TRAIN, "train", nlp)
    holdout, gold = build_rows(HOLDOUT, "validation", nlp)
    encoder = TrainOnlyEncoder().fit(train)
    train_x = [encoder.transform_one(row["features"]) for row in train]
    holdout_x = [encoder.transform_one(row["features"]) for row in holdout]
    label_index = {label: i for i, label in enumerate(TARGET_LABELS)}
    dimension = len(encoder.feature_names)
    w, b, diagnostics = fit_logistic(
        sparse_tensor(train_x, dimension), [label_index[y] for y in train_labels],
        c_value=1.0, balanced=False, max_iter=100,
    )
    with torch.no_grad():
        logits = torch.sparse.mm(sparse_tensor(holdout_x, dimension), w) + b
        predictions = [TARGET_LABELS[i] for i in logits.argmax(1).tolist()]
    majority = Counter(train_labels).most_common(1)[0][0]
    print("Synthetic demonstration; not NUCLE research performance.")
    print(f"Train={len(train)}; holdout={len(holdout)}; feature columns={dimension}")
    print(f"LR optimizer stopping reason: {diagnostics['termination']}")
    for (sentence, span, _), truth, pred in zip(HOLDOUT, gold, predictions, strict=True):
        print(f"{sentence} | span={span!r} | gold={truth} | prediction={pred}")
    for name, pred in (("Majority", [majority] * len(gold)), ("LR", predictions)):
        result = scores(gold, pred)
        print(f"{name}: accuracy={result['accuracy']:.4f}, macro-F1={result['macro_f1']:.4f}")


if __name__ == "__main__":
    main()
