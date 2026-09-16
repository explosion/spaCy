"""CPU overfit sanity check for the Urdu NER training path.

Evaluates on the training fixture only. This is not held-out evaluation and
is not a model-quality metric.
"""

from __future__ import annotations

import argparse
import math
import random
import tempfile
from pathlib import Path

import spacy
from spacy.tokens import DocBin
from spacy.training import Example
from spacy.util import fix_random_seed

from convert_ner import convert_jsonl, write_docbin

ROOT = Path(__file__).resolve().parents[1]


def fingerprint(nlp) -> float:
    total = 0.0
    for _, pipe in nlp.pipeline:
        model = getattr(pipe, "model", None)
        if model is None:
            continue
        for node in model.walk():
            for name in node.param_names:
                if node.has_param(name):
                    total += float(node.get_param(name).sum())
    return total


def gold_examples(nlp, docs) -> list[Example]:
    examples = []
    for doc in docs:
        entities = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
        examples.append(
            Example.from_dict(nlp.make_doc(doc.text), {"entities": entities})
        )
    return examples


def run_overfit(
    jsonl: Path,
    *,
    seed: int,
    max_steps: int,
    min_f: float,
) -> dict:
    random.seed(seed)
    fix_random_seed(seed)
    nlp_tok = spacy.blank("ur")
    gold_docs, counts = convert_jsonl(
        jsonl, nlp_tok, skip_invalid=False, require_token_alignment=True
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir) / "overfit.spacy"
        write_docbin(gold_docs, tmp)
        reloaded = list(DocBin().from_disk(tmp).get_docs(nlp_tok.vocab))
    if len(reloaded) != len(gold_docs):
        raise SystemExit("DocBin round-trip dropped documents")
    for original, restored in zip(gold_docs, reloaded, strict=True):
        got = [(e.start_char, e.end_char, e.label_) for e in restored.ents]
        expected = [(e.start_char, e.end_char, e.label_) for e in original.ents]
        if got != expected:
            raise SystemExit(
                f"gold spans changed after serialization: {got} != {expected}"
            )

    nlp = spacy.blank("ur")
    nlp.add_pipe("tok2vec")
    nlp.add_pipe("ner")
    ner = nlp.get_pipe("ner")
    for doc in gold_docs:
        for ent in doc.ents:
            ner.add_label(ent.label_)
    examples = gold_examples(nlp, gold_docs)
    nlp.initialize(get_examples=lambda: examples)
    before = fingerprint(nlp)
    last_losses: dict[str, float] = {}
    for _ in range(max_steps):
        random.shuffle(examples)
        last_losses = {}
        nlp.update(examples, losses=last_losses, drop=0.0)
        if any(not math.isfinite(value) for value in last_losses.values()):
            raise SystemExit(f"non-finite losses: {last_losses}")
    after = fingerprint(nlp)
    if after == before:
        raise SystemExit(f"parameters did not change: {before}")
    scores = nlp.evaluate(examples)
    ents_f = float(scores.get("ents_f", 0.0))
    if ents_f < min_f:
        raise SystemExit(
            f"overfit ents_f={ents_f:.3f} below {min_f} after {max_steps} steps; "
            f"losses={last_losses} (training-set diagnostic, not held-out evaluation)"
        )
    return {
        "ents_f": ents_f,
        "losses": last_losses,
        "before": before,
        "after": after,
        "steps": max_steps,
        "docs": counts["kept"],
        "spans": counts["spans"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "jsonl",
        nargs="?",
        type=Path,
        default=ROOT / "fixtures" / "ner_overfit.jsonl",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-steps", type=int, default=40)
    parser.add_argument("--min-f", type=float, default=1.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_overfit(
        args.jsonl, seed=args.seed, max_steps=args.max_steps, min_f=args.min_f
    )
    print(
        f"overfit_check=pass ents_f={result['ents_f']:.3f} "
        f"steps={result['steps']} docs={result['docs']} spans={result['spans']} "
        f"losses={result['losses']} "
        "(training fixture only; not held-out evaluation)"
    )


if __name__ == "__main__":
    main()
