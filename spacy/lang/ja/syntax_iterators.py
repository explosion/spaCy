# coding: utf8
from __future__ import unicode_literals

from spacy.symbols import NOUN, PROPN, PRON


def noun_chunks(obj):
    """
    Detect base noun phrases from a dependency parse. Works on both Doc and Span.
    """
    doc = obj.doc  # Ensure works on both Doc and Span.
    np_label = doc.vocab.strings.add('NP')
    start = -1
    for i, word in enumerate(obj):
        if word.pos in (NOUN, PROPN, PRON):
            if start < 0:
                start = i
        elif start >= 0:
            yield start, i, np_label
            start = -1
    if start >= 0:
        yield start, len(doc), np_label


SYNTAX_ITERATORS = {
    'noun_chunks': noun_chunks
}
