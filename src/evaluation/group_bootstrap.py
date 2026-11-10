"""Paired group-bootstrap metrics for caller-supplied labels and predictions.

Import group_bootstrap from Python; no research files or checkpoints are read.
"""

import numpy as np

from src.evaluation.metrics import LABELS


def group_bootstrap(metadata, predictions, groups, weights):
    """Fixed five-class F1, using the exact same group resamples for all models."""
    group_index = {name: i for i, name in enumerate(groups)}
    label_index = {name: i for i, name in enumerate(LABELS)}
    if set(group_index) != {row["group_id"] for row in metadata}:
        raise ValueError("Group set differs from historical bootstrap")
    if weights.ndim != 2 or weights.shape[1] != len(groups):
        raise ValueError("Invalid bootstrap weight shape")
    distributions = {}
    for name, pred in predictions.items():
        if len(pred) != len(metadata):
            raise ValueError("Predictions do not align with metadata")
        matrices = np.zeros((len(groups), len(LABELS), len(LABELS)), dtype=np.int64)
        for row, label in zip(metadata, pred, strict=True):
            matrices[group_index[row["group_id"]], label_index[row["error_type"]], label_index[label]] += 1
        boot = (weights @ matrices.reshape(len(groups), -1)).reshape(-1, len(LABELS), len(LABELS))
        diagonal = np.diagonal(boot, axis1=1, axis2=2)
        denominator = boot.sum(1) + boot.sum(2)
        distributions[name] = np.divide(2 * diagonal, denominator, out=np.zeros_like(diagonal, dtype=float),
                                         where=denominator > 0).mean(1)
    return distributions
