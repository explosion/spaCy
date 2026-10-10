"""Convert CoNLL-U syntax files to spaCy DocBin using spaCy's converter.

Urdu treebank forms such as بات_چیت are kept as a single token with an
underscore. That surface is reconstructed treebank text, not recovered
running-text offsets. Empty nodes (IDs containing '.') are dropped by the
upstream converter. Multiword token rows (IDs containing '-') are handled by
`--merge-subtokens`.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from spacy.tokens import Doc, DocBin, Span
from spacy.training.converters import conllu_to_docs


def ensure_sentences(doc: Doc) -> bool:
    """Set SENT_START on gold docs if missing. Returns True if injected.

    This annotates the reference Doc. It is not predicted segmentation and
    must not be described as end-to-end sentence splitting.
    """
    if not len(doc):
        return False
    try:
        next(doc.sents)
        return False
    except ValueError:
        doc[0].is_sent_start = True
        for token in doc[1:]:
            token.is_sent_start = False
        return True


def _sentences(doc: Doc) -> list[Span]:
    try:
        return list(doc.sents)
    except ValueError:
        return [doc[:]]


def _require_ann(doc: Doc, names: tuple[str, ...], label: str) -> None:
    for name in names:
        if not doc.has_annotation(name):
            raise ValueError(f"{label}: missing {name} annotation")


def _validate_sentence(tokens: list, doc: Doc, label: str) -> None:
    if not tokens:
        raise ValueError(f"{label}: empty sentence")
    roots = [token for token in tokens if token.dep_ == "ROOT"]
    if len(roots) != 1:
        raise ValueError(f"{label}: expected 1 ROOT, found {len(roots)}")
    start, end = tokens[0].i, tokens[-1].i + 1
    for token in tokens:
        if token.dep_ in ("", "-"):
            raise ValueError(f"{label}: missing dep on token {token.i}")
        if not (start <= token.head.i < end) or not (0 <= token.head.i < len(doc)):
            raise ValueError(f"{label}: head outside sentence for token {token.i}")


def validate_tree(doc: Doc, label: str) -> None:
    _require_ann(doc, ("DEP", "LEMMA", "MORPH"), label)
    for sent in _sentences(doc):
        _validate_sentence(list(sent), doc, label)


def _empty_conllu_counts() -> dict:
    return {
        "kept": 0,
        "invalid": 0,
        "underscore_tokens": 0,
        "sentences": 0,
        "injected_sentence_starts": 0,
        "reconstructed": True,
        "pos": Counter(),
        "deps": Counter(),
    }


def _keep_doc(doc: Doc, conllu_path: Path, injected: bool, counts: dict) -> None:
    counts["underscore_tokens"] += sum("_" in token.text for token in doc)
    counts["sentences"] += len(_sentences(doc))
    if injected:
        counts["injected_sentence_starts"] += 1
    for token in doc:
        if token.pos_:
            counts["pos"][token.pos_] += 1
        if token.dep_:
            counts["deps"][token.dep_] += 1
    doc.user_data["reconstructed"] = True
    doc.user_data["source"] = str(conllu_path)
    doc.user_data["sentence_starts"] = (
        "injected_single_sentence" if injected else "from_treebank"
    )
    counts["kept"] += 1


def convert_conllu(
    conllu_path: Path,
    *,
    n_sents: int,
    merge_subtokens: bool,
    skip_invalid: bool,
) -> tuple[list[Doc], dict]:
    if not conllu_path.is_file():
        raise ValueError(f"missing input file: {conllu_path}")
    text = conllu_path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"{conllu_path}: empty CoNLL-U file")
    docs: list[Doc] = []
    counts = _empty_conllu_counts()
    yielded = 0
    for index, doc in enumerate(
        conllu_to_docs(
            text,
            n_sents=n_sents,
            merge_subtokens=merge_subtokens,
            no_print=True,
        )
    ):
        yielded += 1
        label = f"{conllu_path.name}#{index}"
        injected = ensure_sentences(doc)
        try:
            validate_tree(doc, label)
        except ValueError as err:
            counts["invalid"] += 1
            if skip_invalid:
                print(f"skip {label}: {err}", file=sys.stderr)
                continue
            raise
        _keep_doc(doc, conllu_path, injected, counts)
        docs.append(doc)
    if yielded == 0:
        raise ValueError(f"{conllu_path}: no CoNLL-U sentences")
    if counts["kept"] == 0:
        raise ValueError(
            f"{conllu_path}: no valid documents (invalid={counts['invalid']})"
        )
    return docs, counts


def format_counts(counts: dict) -> str:
    pos = ",".join(f"{name}:{n}" for name, n in sorted(counts["pos"].items())) or "none"
    deps = (
        ",".join(f"{name}:{n}" for name, n in sorted(counts["deps"].items())) or "none"
    )
    return (
        f"kept={counts['kept']} invalid={counts['invalid']} "
        f"sentences={counts['sentences']} "
        f"injected_sentence_starts={counts['injected_sentence_starts']} "
        f"underscore_tokens={counts['underscore_tokens']} "
        f"pos={pos} deps={deps} reconstructed=true"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("conllu", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--n-sents", type=int, default=1)
    parser.add_argument("--merge-subtokens", action="store_true")
    parser.add_argument("--skip-invalid", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    docs, counts = convert_conllu(
        args.conllu,
        n_sents=args.n_sents,
        merge_subtokens=args.merge_subtokens,
        skip_invalid=args.skip_invalid,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    DocBin(docs=docs, store_user_data=True).to_disk(args.out)
    print(f"wrote {args.out} {format_counts(counts)}")
    print(
        "Scores on this corpus are reference-tokenization results, "
        "not raw-text end-to-end evaluation."
    )


if __name__ == "__main__":
    main()
