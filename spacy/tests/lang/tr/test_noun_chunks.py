# coding: utf-8
from __future__ import unicode_literals

import numpy
from spacy.attrs import HEAD, DEP
from spacy.symbols import nsubj, obj, iobj, obl, amod, nmod, conj, cc, root
from spacy.lang.tr.syntax_iterators import SYNTAX_ITERATORS

import pytest


from ...util import get_doc


def test_noun_chunks_is_parsed(tr_tokenizer):
    """Test that noun_chunks raises Value Error for 'tr' language if Doc is not parsed.
    To check this test, we're constructing a Doc
    with a new Vocab here and forcing is_parsed to 'False'
    to make sure the noun chunks don't run.
    """
    doc = tr_tokenizer("Dün seni gördüm.")
    doc.is_parsed = False
    with pytest.raises(ValueError):
        list(doc.noun_chunks)

def test_tr_noun_chunks_amod_simple(tr_vocab):
    pass

def test_tr_noun_chunks_nmod_simple(tr_vocab):
    pass

def test_tr_noun_chunks_nmod_two(tr_vocab):
    pass

def test_tr_noun_chunks_nmod_three(tr_vocab):
    pass

def test_tr_noun_chunks_nmod_four(tr_vocab):
    pass

def test_tr_noun_chunks_np_recursive(tr_vocab):
    pass

def test_tr_noun_chunks_not_nested(tr_vocab):
    pass
