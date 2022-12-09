# coding: utf-8
from __future__ import unicode_literals

import numpy
from spacy.attrs import HEAD, DEP
from spacy.symbols import nsubj, dobj, amod, nmod, conj, cc, root
from spacy.lang.en.syntax_iterators import SYNTAX_ITERATORS

import pytest


from ...util import get_doc


def test_noun_chunks_is_parsed(en_tokenizer):
    """Test that noun_chunks raises Value Error for 'en' language if Doc is not parsed.
    To check this test, we're constructing a Doc
    with a new Vocab here and forcing is_parsed to 'False'
    to make sure the noun chunks don't run.
    """
    doc = en_tokenizer("This is a sentence")
    doc.is_parsed = False
    with pytest.raises(ValueError):
        list(doc.noun_chunks)


def test_en_noun_chunks_not_nested(en_vocab):
    words = ["Peter", "has", "chronic", "command", "and", "control", "issues"]
    heads = [1, 0, 4, 3, -1, -2, -5]
    deps = ["nsubj", "ROOT", "amod", "nmod", "cc", "conj", "dobj"]
    doc = get_doc(en_vocab, words=words, heads=heads, deps=deps)
    doc.from_array(
        [HEAD, DEP],
        numpy.asarray(
            [
                [1, nsubj],
                [0, root],
                [4, amod],
                [3, nmod],
                [numpy.int32(-1).astype(numpy.uint64), cc],
                [numpy.int32(-2).astype(numpy.uint64), conj],
                [numpy.int32(-5).astype(numpy.uint64), dobj],
            ],
            dtype="uint64",
        ),
    )
    doc.noun_chunks_iterator = SYNTAX_ITERATORS["noun_chunks"]
    word_occurred = {}
    for chunk in doc.noun_chunks:
        for word in chunk:
            word_occurred.setdefault(word.text, 0)
            word_occurred[word.text] += 1
    for word, freq in word_occurred.items():
        assert freq == 1, (word, [chunk.text for chunk in doc.noun_chunks])
