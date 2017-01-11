# coding: utf-8
from __future__ import unicode_literals

from ..tokens import Doc
from ..attrs import ORTH, POS, HEAD, DEP


def get_doc(vocab, words=[], tags=None, heads=None, deps=None):
    """Create Doc object from given vocab, words and annotations."""
    tags = tags or [''] * len(words)
    heads = heads or [0] * len(words)
    deps = deps or [''] * len(words)

    doc = Doc(vocab, words=words)
    attrs = doc.to_array([POS, HEAD, DEP])
    for i, (tag, head, dep) in enumerate(zip(tags, heads, deps)):
        attrs[i, 0] = doc.vocab.strings[tag]
        attrs[i, 1] = head
        attrs[i, 2] = doc.vocab.strings[dep]
    doc.from_array([POS, HEAD, DEP], attrs)
    return doc
