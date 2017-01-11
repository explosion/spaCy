# coding: utf-8
from __future__ import unicode_literals

from ...attrs import HEAD, DEP
from ...symbols import nsubj, dobj, amod, nmod, conj, cc, root
from ...syntax.iterators import english_noun_chunks
from ..util import get_doc

import numpy


def test_doc_noun_chunks_not_nested(en_tokenizer):
    text = "Peter has chronic command and control issues"
    heads = [1, 0, 4, 3, -1, -2, -5]
    deps = ['nsubj', 'ROOT', 'amod', 'nmod', 'cc', 'conj', 'dobj']

    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads, deps=deps)

    tokens.from_array(
        [HEAD, DEP],
        numpy.asarray([[1, nsubj], [0, root], [4, amod], [3, nmod], [-1, cc],
                       [-2, conj], [-5, dobj]], dtype='int32'))
    tokens.noun_chunks_iterator = english_noun_chunks
    word_occurred = {}
    for chunk in tokens.noun_chunks:
        for word in chunk:
            word_occurred.setdefault(word.text, 0)
            word_occurred[word.text] += 1
    for word, freq in word_occurred.items():
        assert freq == 1, (word, [chunk.text for chunk in tokens.noun_chunks])
