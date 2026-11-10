import numpy as np
import pytest

from src.evaluation.group_bootstrap import group_bootstrap
from src.evaluation.metrics import LABELS, scores


def test_group_bootstrap_matches_explicit_group_expansion():
    metadata = [{"group_id": "a" if i < 5 else "b", "error_type": LABELS[i % 5]} for i in range(10)]
    pred = [row["error_type"] for row in metadata]
    pred[1] = "SVA"
    weights = np.array([[2, 0], [1, 1], [0, 2]])
    distributions = group_bootstrap(metadata, {"model": pred, "same": pred}, ["a", "b"], weights)
    for j, w in enumerate(weights):
        ids = [i for group, n in zip(["a", "b"], w) for _ in range(int(n))
               for i, row in enumerate(metadata) if row["group_id"] == group]
        expected = scores([metadata[i]["error_type"] for i in ids], [pred[i] for i in ids])["macro_f1"]
        assert distributions["model"][j] == pytest.approx(expected)
    assert np.array_equal(distributions["model"], distributions["same"])


def test_bootstrap_rejects_unmatched_groups():
    with pytest.raises(ValueError, match="Group set"):
        group_bootstrap([{"group_id": "a", "error_type": "SVA"}], {"model": ["SVA"]}, ["b"], np.array([[1]]))
