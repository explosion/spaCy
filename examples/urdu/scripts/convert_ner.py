"""Convert Urdu NER JSONL to spaCy DocBin.

Offsets are Python Unicode code-point indices (str indexing). Records that use
UTF-16 or byte offsets must be converted before this script.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import spacy
from spacy.tokens import Doc, DocBin, Span


SCHEMA_HELP = """
Each JSONL record must be:
  {"id": "doc-001", "text": "...", "entities": [{"start": 0, "end": 5, "label": "PER"}]}
Optional: "source_id" for document-level splitting.
A missing "entities" key is not a negative document. Use "entities": [] for that.
"""


class ConversionError(ValueError):
    pass


def _spans_overlap(a: dict, b: dict) -> bool:
    return a["start"] < b["end"] and b["start"] < a["end"]


def _normalize_entity(ent: dict, loc: str, text: str, seen: set) -> None:
    try:
        start, end, label = int(ent["start"]), int(ent["end"]), ent["label"]
    except (KeyError, TypeError, ValueError) as err:
        raise ConversionError(f"{loc}: need integer start/end and label") from err
    if not isinstance(label, str) or not label.strip():
        raise ConversionError(f"{loc}: empty label")
    if not 0 <= start < end <= len(text):
        raise ConversionError(
            f"{loc}: bounds {start}:{end} outside text length {len(text)}"
        )
    key = (start, end, label)
    if key in seen:
        raise ConversionError(f"{loc}: duplicate span {key}")
    seen.add(key)
    ent["start"], ent["end"], ent["label"] = start, end, label


def _reject_overlaps(doc_id: str, entities: list) -> None:
    for i, left in enumerate(entities):
        for right in entities[i + 1 :]:
            if _spans_overlap(left, right):
                raise ConversionError(
                    f"{doc_id}: overlapping entities {left} and {right}; "
                    "standard ner cannot represent nested/overlapping spans. "
                    "Use a span-categorizer setup if that is the actual task."
                )


def validate_record(record: dict[str, Any], line_no: int) -> None:
    doc_id = record.get("id", f"<line {line_no}>")
    if not record.get("id"):
        raise ConversionError(f"{doc_id}: missing id")
    text = record.get("text")
    if not isinstance(text, str):
        raise ConversionError(f"{doc_id}: text must be a string")
    if "entities" not in record:
        raise ConversionError(
            f"{doc_id}: missing entities; use entities=[] for an annotated "
            "negative document"
        )
    entities = record["entities"]
    if not isinstance(entities, list):
        raise ConversionError(f"{doc_id}: entities must be a list")
    seen: set = set()
    for i, ent in enumerate(entities):
        _normalize_entity(ent, f"{doc_id} entity[{i}]", text, seen)
    _reject_overlaps(doc_id, entities)


def record_to_doc(nlp, record: dict[str, Any], *, require_token_alignment: bool) -> Doc:
    doc = nlp.make_doc(record["text"])
    spans: list[Span] = []
    for ent in record["entities"]:
        span = doc.char_span(
            ent["start"],
            ent["end"],
            label=ent["label"],
            alignment_mode="strict",
        )
        if span is None:
            surface = record["text"][ent["start"] : ent["end"]]
            raise ConversionError(
                f"{record['id']}: entity {ent} ({surface!r}) is not aligned "
                f"to token boundaries (strict offsets; not expanded or contracted)"
            )
        spans.append(span)
    doc.ents = spans
    doc.user_data["id"] = record["id"]
    doc.user_data["source_id"] = record.get("source_id", record["id"])
    doc.user_data["negative"] = not spans
    return doc


def _empty_counts() -> dict[str, Any]:
    return {
        "rows": 0,
        "kept": 0,
        "invalid": 0,
        "negatives": 0,
        "spans": 0,
        "labels": Counter(),
        "sources": Counter(),
    }


def convert_jsonl(
    jsonl_path: Path,
    nlp,
    *,
    skip_invalid: bool,
    require_token_alignment: bool,
) -> tuple[list[Doc], dict[str, Any]]:
    if not jsonl_path.is_file():
        raise ConversionError(f"missing input file: {jsonl_path}")
    counts = _empty_counts()
    docs: list[Doc] = []
    with jsonl_path.open(encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            counts["rows"] += 1
            try:
                record = json.loads(raw)
                validate_record(record, line_no)
                doc = record_to_doc(
                    nlp,
                    record,
                    require_token_alignment=require_token_alignment,
                )
                docs.append(doc)
                counts["kept"] += 1
                counts["spans"] += len(doc.ents)
                if not doc.ents:
                    counts["negatives"] += 1
                for ent in doc.ents:
                    counts["labels"][ent.label_] += 1
                counts["sources"][doc.user_data["source_id"]] += 1
            except (json.JSONDecodeError, ConversionError) as err:
                counts["invalid"] += 1
                loc = f"{jsonl_path.name}:{line_no}"
                if skip_invalid:
                    print(f"skip {loc}: {err}", file=sys.stderr)
                    continue
                raise ConversionError(f"{loc}: {err}") from err
    if counts["rows"] == 0:
        raise ConversionError(f"{jsonl_path}: no JSONL records")
    if counts["kept"] == 0:
        raise ConversionError(
            f"{jsonl_path}: no valid documents (rows={counts['rows']} "
            f"invalid={counts['invalid']})"
        )
    return docs, counts


def write_docbin(docs: Iterable[Doc], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    docbin = DocBin(docs=list(docs), store_user_data=True)
    docbin.to_disk(out_path)


def format_counts(counts: dict[str, Any]) -> str:
    labels = (
        ",".join(f"{name}:{n}" for name, n in sorted(counts["labels"].items()))
        or "none"
    )
    sources = ",".join(sorted(counts["sources"])) or "none"
    return (
        f"kept={counts['kept']} invalid={counts['invalid']} "
        f"rows={counts['rows']} negatives={counts['negatives']} "
        f"spans={counts['spans']} labels={labels} sources={sources}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__ + SCHEMA_HELP)
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--lang", default="ur")
    parser.add_argument("--skip-invalid", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    nlp = spacy.blank(args.lang)
    docs, counts = convert_jsonl(
        args.jsonl,
        nlp,
        skip_invalid=args.skip_invalid,
        require_token_alignment=True,
    )
    write_docbin(docs, args.out)
    print(f"wrote {args.out} {format_counts(counts)}")


if __name__ == "__main__":
    main()
