from __future__ import unicode_literals
import pytest

from spacy.attrs import LEMMA, ORTH, PROB, IS_ALPHA
from spacy.parts_of_speech import NOUN, VERB


def test_neq(en_vocab):
    addr = en_vocab['Hello']
    assert en_vocab['bye'].orth != addr.orth


def test_eq(en_vocab):
    addr = en_vocab['Hello']
    assert en_vocab['Hello'].orth == addr.orth


def test_case_neq(en_vocab):
    addr = en_vocab['Hello']
    assert en_vocab['hello'].orth != addr.orth


def test_punct_neq(en_vocab):
    addr = en_vocab['Hello']
    assert en_vocab['Hello,'].orth != addr.orth


def test_shape_attr(en_vocab):
    example = en_vocab['example']
    assert example.orth != example.shape


def test_symbols(en_vocab):
    assert en_vocab.strings['IS_ALPHA'] == IS_ALPHA
    assert en_vocab.strings['NOUN'] == NOUN
    assert en_vocab.strings['VERB'] == VERB
    assert en_vocab.strings['LEMMA'] == LEMMA
    assert en_vocab.strings['ORTH'] == ORTH
    assert en_vocab.strings['PROB'] == PROB
    
