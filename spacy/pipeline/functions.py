# coding: utf8
from __future__ import unicode_literals

from ..matcher import Matcher


# TODO: replace doc.merge with doc.retokenize


def merge_noun_chunks(doc):
    """Merge noun chunks into a single token.

    doc (Doc): The Doc object.
    RETURNS (Doc): The Doc object with merged noun chunks.
    """
    if not doc.is_parsed:
        return doc
    spans = [
        (np.start_char, np.end_char, np.root.tag, np.root.dep) for np in doc.noun_chunks
    ]
    for start, end, tag, dep in spans:
        doc.merge(start, end, tag=tag, dep=dep)
    return doc


def merge_entities(doc):
    """Merge entities into a single token.

    doc (Doc): The Doc object.
    RETURNS (Doc): The Doc object with merged noun entities.
    """
    spans = [
        (e.start_char, e.end_char, e.root.tag, e.root.dep, e.label) for e in doc.ents
    ]
    for start, end, tag, dep, ent_type in spans:
        doc.merge(start, end, tag=tag, dep=dep, ent_type=ent_type)
    return doc


def merge_subtokens(doc, label="subtok"):
    merger = Matcher(doc.vocab)
    merger.add("SUBTOK", None, [{"DEP": label, "op": "+"}])
    matches = merger(doc)
    spans = [doc[start : end + 1] for _, start, end in matches]
    offsets = [(span.start_char, span.end_char) for span in spans]
    for start_char, end_char in offsets:
        doc.merge(start_char, end_char)
    return doc
