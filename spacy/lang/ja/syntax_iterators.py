from typing import Union, Iterator

from ...symbols import NOUN, PROPN, PRON, VERB
from ...tokens import Doc, Span


# TODO: this can probably be pruned a bit
# fmt: off
labels = ["nsubj", "nmod", "ddoclike", "nsubjpass", "pcomp", "pdoclike", "doclike", "obl", "dative", "appos", "attr", "ROOT"]
# fmt: on


def noun_chunks(doclike: Union[Doc, Span]) -> Iterator[Span]:
    """Detect base noun phrases from a dependency parse. Works on Doc and Span."""
    doc = doclike.doc  # Ensure works on both Doc and Span.
    np_deps = [doc.vocab.strings.add(label) for label in labels]
    doc.vocab.strings.add("conj")
    np_label = doc.vocab.strings.add("NP")
    seen = set()
    for i, word in enumerate(doclike):
        if word.pos not in (NOUN, PROPN, PRON):
            continue
        # Prevent nested chunks from being produced
        if word.i in seen:
            continue
        if word.dep in np_deps:
            unseen = [w.i for w in word.subtree if w.i not in seen]
            if not unseen:
                continue
            # this takes care of particles etc.
            seen.update(j.i for j in word.subtree)
            # This avoids duplicating embedded clauses
            seen.update(range(word.i + 1))
            # if the head of this is a verb, mark that and rights seen
            # Don't do the subtree as that can hide other phrases
            if word.head.pos == VERB:
                seen.add(word.head.i)
                seen.update(w.i for w in word.head.rights)
            yield unseen[0], word.i + 1, np_label


SYNTAX_ITERATORS = {"noun_chunks": noun_chunks}
