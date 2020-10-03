# coding: utf-8
from __future__ import unicode_literals

import numpy
from spacy.attrs import HEAD, DEP
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
    words = ["sarı", "kedi"]
    heads = [1, 0]
    deps = ["amod", "ROOT"]
    pos = ["ADJ", "NOUN"]
    doc = get_doc(tr_vocab, words=words, pos=pos, heads=heads, deps=deps)
    doc.noun_chunks_iterator = SYNTAX_ITERATORS["noun_chunks"]
    chunks = [chunk.text for chunk in doc.noun_chunks]
    assert chunks == ["sarı kedi"]

def test_tr_noun_chunks_nmod_simple(tr_vocab):
    words = ["arkadaşımın", "kedisi"]
    heads = [1, 0]
    deps = ["nmod", "ROOT"]
    pos = ["NOUN", "NOUN"]
    doc = get_doc(tr_vocab, words=words, pos=pos, heads=heads, deps=deps)
    doc.noun_chunks_iterator = SYNTAX_ITERATORS["noun_chunks"]
    chunks = [chunk.text for chunk in doc.noun_chunks]
    assert chunks == ["arkadaşımın kedisi"]

def test_tr_noun_chunks_determiner_simple(tr_vocab):
    words = ["O", "kedi"]
    heads = [1, 0]
    deps = ["det", "ROOT"]
    pos = ["DET", "NOUN"]
    doc = get_doc(tr_vocab, words=words, pos=pos, heads=heads, deps=deps)
    doc.noun_chunks_iterator = SYNTAX_ITERATORS["noun_chunks"]
    chunks = [chunk.text for chunk in doc.noun_chunks]
    assert chunks == ["O kedi"]

def test_tr_noun_chunks_one_det_one_adj_simple(tr_vocab):
    words = ["O", "sarı", "kedi"]
    heads = [2, 1, 0]
    deps = ["det", "amod", "ROOT"]
    pos = ["DET", "ADJ", "NOUN"]
    doc = get_doc(tr_vocab, words=words, pos=pos, heads=heads, deps=deps)
    doc.noun_chunks_iterator = SYNTAX_ITERATORS["noun_chunks"]
    chunks = [chunk.text for chunk in doc.noun_chunks]
    assert chunks == ["O sarı kedi"]

def test_tr_noun_chunks_two_adjs_simple(tr_vocab):
    words = ["beyaz", "tombik", "kedi"]
    heads = [2, 1, 0]
    deps = ["amod", "amod", "ROOT"]
    pos = ["ADJ", "ADJ", "NOUN"]
    doc = get_doc(tr_vocab, words=words, pos=pos, heads=heads, deps=deps)
    doc.noun_chunks_iterator = SYNTAX_ITERATORS["noun_chunks"]
    chunks = [chunk.text for chunk in doc.noun_chunks]
    assert chunks == ["beyaz tombik kedi"]


def test_tr_noun_chunks_one_det_two_adjs_simple(tr_vocab):
    words = ["o", "beyaz", "tombik", "kedi"]
    heads = [3, 2, 1, 0]
    deps = ["det", "amod", "amod", "ROOT"]
    pos = ["DET", "ADJ", "ADJ", "NOUN"]
    doc = get_doc(tr_vocab, words=words, pos=pos, heads=heads, deps=deps)
    doc.noun_chunks_iterator = SYNTAX_ITERATORS["noun_chunks"]
    chunks = [chunk.text for chunk in doc.noun_chunks]
    assert chunks == ["o beyaz tombik kedi"]

def test_tr_noun_chunks_nmod_two(tr_vocab):
    words = ["kızın", "saçının", "rengi"]
    heads = [1, 1, 0]
    deps = ["nmod", "nmod", "ROOT"]
    pos = ["NOUN", "NOUN", "NOUN"]
    doc = get_doc(tr_vocab, words=words, pos=pos, heads=heads, deps=deps)
    doc.noun_chunks_iterator = SYNTAX_ITERATORS["noun_chunks"]
    chunks = [chunk.text for chunk in doc.noun_chunks]
    assert chunks == ["kızın saçının rengi"]

def test_tr_noun_chunks_nmod_three(tr_vocab):
    words = ["güney", "Afrika", "ülkelerinden", "Mozambik"]
    heads = [1, 1, 1, 0]
    deps = ["nmod", "nmod", "nmod", "ROOT"]
    pos = ["NOUN", "PROPN", "NOUN", "PROPN"]
    doc = get_doc(tr_vocab, words=words, pos=pos, heads=heads, deps=deps)
    doc.noun_chunks_iterator = SYNTAX_ITERATORS["noun_chunks"]
    chunks = [chunk.text for chunk in doc.noun_chunks]
    assert chunks == ["güney Afrika ülkelerinden Mozambik"]

def test_tr_noun_chunks_acl_simple(tr_vocab):
    words = ["bahçesi", "olan", "okul"]
    heads = [2, -1, 0]
    deps = ["acl", "cop", "ROOT"]
    pos = ["NOUN", "AUX", "NOUN"]
    doc = get_doc(tr_vocab, words=words, pos=pos, heads=heads, deps=deps)
    doc.noun_chunks_iterator = SYNTAX_ITERATORS["noun_chunks"]
    chunks = [chunk.text for chunk in doc.noun_chunks]
    assert chunks == ["bahçesi olan okul"]

def test_tr_noun_chunks_np_recursive(tr_vocab):
    pass

def test_tr_noun_chunks_not_nested(tr_vocab):
    pass
