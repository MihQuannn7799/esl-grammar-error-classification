"""Boundary, leakage, source identity and publication checks for preparation."""
import json
import subprocess
import sys

import pytest

from src.data.nucle_sgml import NucleDocument, NucleMistake, load_nucle
from src.data.parse_nucle import documents_to_dataframe
from src.data.data_quality import annotation_review
from src.data.prepare_nucle import (
    build_dataset, canonical, construct_input, digest, export_dataset, file_hash,
    make_nlp, prepare, read_quality_flags, segment_paragraph,
)


@pytest.fixture(scope="module")
def nlp():
    return make_nlp()


@pytest.mark.parametrize("text,expected", [
    ("Dr. Smith arrived. He left.", ["Dr. Smith arrived. ", "He left."]),
    ("The value is 3.14. Fine!", ["The value is 3.14. ", "Fine!"]),
    ("I can't go. She won't.", ["I can't go. ", "She won't."]),
    ('"Go!" (He left.) Next.', ['"Go!" (', 'He left.) ', 'Next.']),
    ("Wait... Fine.", ["Wait... Fine."]),
    ("Wait… Fine.", ["Wait… ", "Fine."]),
    ("a\nb; c: d", ["a\nb; c: d"]),
    ("  Hi.  She go.\t", ["  Hi.  ", "She go.\t"]),
    ("Title without punctuation", ["Title without punctuation"]),
    (" \t\n", []), ("", []),
])
def test_locked_sentence_boundaries(nlp, text, expected):
    assert [s["sentence"] for s in segment_paragraph(text, nlp, policy="nucle-preparation-v1")] == expected


def test_unicode_literal_entities_and_parser_roundtrip(nlp, tmp_path):
    path = tmp_path / "fixture.sgml"
    path.write_bytes('<DOC nid="x"><TEXT><TITLE>Title</TITLE><P>\r\n  Cafe\u0301 😀 &amp; A&A.\tNext  line\r\nend.\r\n</P></TEXT></DOC>'.encode())
    doc = load_nucle(path)[0]
    assert doc.paragraphs == ["Title", "  Cafe\u0301 😀 &amp; A&A.\tNext  line\nend."]
    paragraph = doc.paragraphs[1]
    sentences = segment_paragraph(paragraph, nlp)
    assert "".join(s["sentence"] for s in sentences) == paragraph
    for sentence in sentences:
        for token in sentence["tokens"]:
            assert sentence["sentence"][token["start"]:token["end"]] == token["text"]
    start = paragraph.index("😀")
    item, _, reason = construct_input(paragraph, start, start + 1, sentences)
    assert reason is None and item["error_span"] == "😀"


@pytest.mark.parametrize("start,end,span,alignment,reason", [
    (3, 4, "s", "partial_token", None),
    (0, 5, "Dogs ", "whitespace_edge", None),
    (0, 4, "Dogs", "exact", None),
    (0, 8, "Dogs run", "exact", None),
    (8, 9, ".", "exact", None),
    (4, 5, None, None, "no_token_overlap"),
    (2, 2, None, None, "insertion_inside_token"),
    (4, 4, "", "insertion_boundary", None),
    (0, 0, "", "insertion_boundary", None),
    (9, 9, "", "insertion_boundary", None),
])
def test_alignment(nlp, start, end, span, alignment, reason):
    text = "Dogs run."
    item, sent, actual_reason = construct_input(text, start, end, segment_paragraph(text, nlp))
    assert actual_reason == reason
    assert sent is not None
    if item is not None:
        assert item["error_span"] == span and item["alignment"] == alignment
        if alignment == "partial_token":
            assert item["span_token_indices"] == [0]
            assert item["left_token_indices"] == []
            assert item["right_token_indices"] == [1, 2]
            assert item["cuts_start_token"] and not item["cuts_end_token"]


def test_sentence_conversion_and_insertion_ties(nlp):
    text = "Hi. She go."
    sentences = segment_paragraph(text, nlp)
    item, _, reason = construct_input(text, 8, 10, sentences)
    assert reason is None
    assert (item["sentence"], item["error_start"], item["error_end"], item["error_span"]) == ("She go.", 4, 6, "go")
    assert construct_input(text, 2, 5, sentences)[2] == "cross_sentence"
    for position, index, offset in [(4, 1, 0), (11, 1, 7), (3, 0, 3)]:
        item, sent, reason = construct_input(text, position, position, sentences)
        assert reason is None and sent["sentence_index"] == index and item["error_start"] == offset
    assert construct_input(text, 0, 4, sentences)[0]["error_span"] == "Hi. "


def dataset_for(nlp, docs):
    frame = documents_to_dataframe(docs)
    flags = {int(aid): [] for aid in frame.annotation_id}
    return build_dataset(docs, frame, flags, "fixture", nlp)


def test_reason_priority_and_full_accounting(nlp):
    doc = NucleDocument("x", ["Dogs run.", " \t", "Hi. She go."], [
        NucleMistake(9, 99, 9, 99, "Other"),
        NucleMistake(0, 99, 1, 0, "Nn"),
        NucleMistake(0, 0, 1, 0, "Nn"),
        NucleMistake(1, 0, 1, 0, "Nn"),
        NucleMistake(2, 2, 2, 5, "Nn"),
        NucleMistake(0, 4, 0, 5, "Nn"),
        NucleMistake(0, 2, 0, 2, "Nn"),
        NucleMistake(0, 0, 0, 4, "Nn"),
    ])
    data = dataset_for(nlp, [doc])
    assert [r["reason"] for r in data["provenance"]] == [
        "label_out_of_scope", "invalid_offset", "cross_paragraph", "empty_paragraph",
        "cross_sentence", "no_token_overlap", "insertion_inside_token", None]
    assert data["summary"]["counts"] == {"all": 8, "target": 7, "out_of_scope": 1, "retained": 1, "not_constructible": 6}
    assert data["samples"][0]["annotation_id"] == 7


def test_overlap_ambiguity_and_no_correction_leakage(nlp):
    docs = [NucleDocument("x", ["Dogs run."], [
        NucleMistake(0, 0, 0, 4, "Nn", "Dog", "comment"),
        NucleMistake(0, 0, 0, 4, "SVA", "changed"),
        NucleMistake(0, 3, 0, 4, "Nn"),
    ])]
    original = dataset_for(nlp, docs)
    assert len(original["samples"]) == 3
    assert all("review_status" not in row for row in original["provenance"])
    assert "review_status" not in original["summary"]
    assert original["summary"]["input_duplicates"]["ambiguous_groups"] == 1
    docs[0].mistakes[0].correction = "entirely different answer"
    docs[0].mistakes[0].comment = "secret"
    docs[0].mistakes[0].error_type = "Prep"
    changed = dataset_for(nlp, docs)
    assert changed["sentences"] == original["sentences"]
    assert changed["samples"][0]["input_sha256"] == original["samples"][0]["input_sha256"]
    assert set(changed["samples"][0]).isdisjoint({"correction", "comment", "review_status", "quality_flags"})


def make_source_artifacts(tmp_path):
    source = tmp_path / "source.sgml"
    source.write_text('<DOC nid="x"><TEXT><P>Dogs run.</P></TEXT><ANNOTATION>'
                      '<MISTAKE start_par="0" start_off="0" end_par="0" end_off="4">'
                      '<TYPE>Nn</TYPE><CORRECTION>Dog</CORRECTION></MISTAKE>'
                      '</ANNOTATION></DOC>', encoding="utf-8")
    frame = documents_to_dataframe(load_nucle(source))
    annotations, audit = [tmp_path / f"{name}.csv" for name in ("annotations", "audit")]
    frame.to_csv(annotations, index=False)
    annotation_review(frame)[0].to_csv(audit, index=False)
    return source, annotations, audit, frame


def test_quality_flags_reject_stale_audit(tmp_path):
    _, _, audit, frame = make_source_artifacts(tmp_path)
    assert read_quality_flags(frame, audit) == {0: []}
    audit.write_text(audit.read_text().replace("Nn", "Prep"))
    with pytest.raises(ValueError, match="Audit CSV"):
        read_quality_flags(frame, audit)


@pytest.mark.parametrize("policy", ["nucle-preparation-v1", "nucle-preparation-v2"])
def test_complete_run_reproducibility_and_no_overwrite(tmp_path, policy):
    source, annotations, audit, _ = make_source_artifacts(tmp_path)
    first, second = tmp_path / "first", tmp_path / "second"
    for output in (first, second):
        prepare(source, annotations, audit, output=output, expected_source_sha256=file_hash(source), policy=policy)
    a = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
    b = json.loads((second / "manifest.json").read_text(encoding="utf-8"))
    assert a["outputs"] == b["outputs"]
    assert a["schema_version"] == 3
    assert set(a["inputs"]) == {"source", "annotations", "audit", "environment_lock"}
    assert all("review_status" not in json.loads(line)
               for line in (first / "provenance.jsonl").read_text().splitlines())
    assert "review_status" not in json.loads((first / "summary.json").read_text())
    assert (first / "manifest.sha256").read_text().strip() == digest(canonical(a).encode())
    for name, expected in a["outputs"].items():
        assert file_hash(first / name) == expected
    before = file_hash(first / "samples.jsonl")
    with pytest.raises(ValueError, match="already exists"):
        prepare(source, annotations, audit, output=first, expected_source_sha256=file_hash(source), policy=policy)
    assert file_hash(first / "samples.jsonl") == before
    with pytest.raises(ValueError, match="Source checksum"):
        prepare(source, annotations, audit, output=tmp_path / "bad", expected_source_sha256="wrong", policy=policy)
    assert not (tmp_path / "bad").exists()
    annotations.write_text(annotations.read_text().replace("Dogs run.", "Cats run."))
    with pytest.raises(ValueError, match="Understanding CSV"):
        prepare(source, annotations, audit, output=tmp_path / "bad", expected_source_sha256=file_hash(source), policy=policy)


def test_changed_input_prevents_publication(tmp_path):
    source = tmp_path / "input"
    source.write_text("changed")
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="Input changed"):
        export_dataset(output, {"samples": [], "summary": {}}, {}, {source: "old-hash"})
    assert not output.exists()


def test_cli_preparation_runs_without_review_log(tmp_path):
    source, annotations, audit, _ = make_source_artifacts(tmp_path)
    output = tmp_path / "cli_prepared"
    result = subprocess.run(
        [sys.executable, "-m", "src.data.prepare_nucle",
         "--source", str(source), "--annotations", str(annotations),
         "--audit", str(audit), "--output", str(output),
         "--expected-source-sha256", file_hash(source)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    rows = [json.loads(line) for line in (output / "samples.jsonl").read_text().splitlines()]
    assert [(row["sentence"], row["error_span"], row["error_type"]) for row in rows] == [
        ("Dogs run.", "Dogs", "Nn")]
    assert "review" not in json.loads((output / "manifest.json").read_text())["inputs"]


def test_compare_preparations_without_overlap_review_metadata(tmp_path, monkeypatch):
    from src.data import compare_preparation

    source, annotations, audit, _ = make_source_artifacts(tmp_path)
    outputs = [tmp_path / "v1", tmp_path / "v2"]
    for output, policy in zip(outputs, ["nucle-preparation-v1", "nucle-preparation-v2"]):
        prepare(source, annotations, audit, output=output,
                expected_source_sha256=file_hash(source), policy=policy)
    # This optional historical comparison has its own boundary-decision input.
    interim = tmp_path / "interim"
    interim.mkdir()
    (interim / "nucle_boundary_decisions.jsonl").write_text(
        json.dumps({"annotation_id": 0, "boundary": "keep", "issue_type": "synthetic"}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(compare_preparation, "DATA_ROOT", tmp_path)
    summary = compare_preparation.compare(
        old=outputs[0], new=outputs[1], output=tmp_path / "comparison", source=source,
    )
    assert summary["mechanical_checked"] == 1
    assert summary["input_changed"] == 0
    assert summary["source_metadata_unchanged"]
