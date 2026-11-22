"""Convert pretokenized IOB/BIO JSONL to DocBin.

The surface is reconstructed by joining tokens with single spaces. That is not
original running text. Invalid BIO sequences are rejected.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import spacy
from spacy.tokens import Doc
from spacy.training.iob_utils import biluo_tags_to_spans, iob_to_biluo

from convert_ner import ConversionError, format_counts, write_docbin


def validate_bio(tags: list[str], loc: str) -> None:
    prev = "O"
    for i, tag in enumerate(tags):
        if not isinstance(tag, str) or not tag:
            raise ConversionError(f"{loc}: empty BIO tag at {i}")
        if tag == "O":
            prev = "O"
            continue
        if tag[1:2] != "-" or tag[0] not in {"B", "I"} or not tag[2:]:
            raise ConversionError(f"{loc}: invalid BIO tag {tag!r} at {i}")
        label = tag[2:]
        if tag.startswith("I-") and (prev == "O" or prev[2:] != label):
            raise ConversionError(
                f"{loc}: invalid BIO sequence {tag!r} after {prev!r} at {i}"
            )
        prev = tag


def bio_record_to_doc(nlp, record: dict[str, Any], line_no: int) -> Doc:
    doc_id = record.get("id", f"<line {line_no}>")
    if not record.get("id"):
        raise ConversionError(f"{doc_id}: missing id")
    tokens = record.get("tokens")
    tags = record.get("tags")
    if not isinstance(tokens, list) or not tokens:
        raise ConversionError(f"{doc_id}: tokens must be a non-empty list")
    if not isinstance(tags, list):
        raise ConversionError(f"{doc_id}: tags must be a list")
    if len(tokens) != len(tags):
        raise ConversionError(f"{doc_id}: tokens/tags length mismatch")
    if not all(isinstance(tok, str) and tok for tok in tokens):
        raise ConversionError(f"{doc_id}: tokens must be non-empty strings")
    validate_bio(tags, doc_id)
    spaces = [True] * (len(tokens) - 1) + [False]
    doc = Doc(nlp.vocab, words=tokens, spaces=spaces)
    doc.ents = biluo_tags_to_spans(doc, iob_to_biluo(tags))
    doc.user_data["id"] = record["id"]
    doc.user_data["source_id"] = record.get("source_id", record["id"])
    doc.user_data["reconstructed"] = True
    doc.user_data["negative"] = not doc.ents
    return doc


def convert_bio_jsonl(
    jsonl_path: Path,
    nlp,
    *,
    skip_invalid: bool,
) -> tuple[list[Doc], dict[str, Any]]:
    if not jsonl_path.is_file():
        raise ConversionError(f"missing input file: {jsonl_path}")
    counts = {
        "rows": 0,
        "kept": 0,
        "invalid": 0,
        "negatives": 0,
        "spans": 0,
        "labels": Counter(),
        "sources": Counter(),
    }
    docs: list[Doc] = []
    with jsonl_path.open(encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            counts["rows"] += 1
            try:
                record = json.loads(raw)
                doc = bio_record_to_doc(nlp, record, line_no)
                docs.append(doc)
                counts["kept"] += 1
                counts["spans"] += len(doc.ents)
                if not doc.ents:
                    counts["negatives"] += 1
                for ent in doc.ents:
                    counts["labels"][ent.label_] += 1
                counts["sources"][doc.user_data["source_id"]] += 1
            except (json.JSONDecodeError, ConversionError, ValueError) as err:
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--lang", default="ur")
    parser.add_argument("--skip-invalid", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    nlp = spacy.blank(args.lang)
    docs, counts = convert_bio_jsonl(args.jsonl, nlp, skip_invalid=args.skip_invalid)
    write_docbin(docs, args.out)
    print(f"wrote {args.out} {format_counts(counts)} reconstructed=true")


if __name__ == "__main__":
    main()
