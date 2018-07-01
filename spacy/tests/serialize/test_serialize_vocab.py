# coding: utf-8
from __future__ import unicode_literals

from ..util import make_tempdir
from ...vocab import Vocab

import pytest


test_strings = [([], []), (['rats', 'are', 'cute'], ['i', 'like', 'rats'])]
test_strings_attrs = [(['rats', 'are', 'cute'], 'Hello')]


@pytest.mark.parametrize('strings1,strings2', test_strings)
def test_serialize_vocab_roundtrip_bytes(strings1,strings2):
    vocab1 = Vocab(strings=strings1)
    vocab2 = Vocab(strings=strings2)
    vocab1_b = vocab1.to_bytes()
    vocab2_b = vocab2.to_bytes()
    if strings1 == strings2:
        assert vocab1_b == vocab2_b
    else:
        assert vocab1_b != vocab2_b
    vocab1 = vocab1.from_bytes(vocab1_b)
    assert vocab1.to_bytes() == vocab1_b
    new_vocab1 = Vocab().from_bytes(vocab1_b)
    assert new_vocab1.to_bytes() == vocab1_b
    assert len(new_vocab1) == len(strings1)
    assert sorted([lex.text for lex in new_vocab1]) == sorted(strings1)


@pytest.mark.parametrize('strings1,strings2', test_strings)
def test_serialize_vocab_roundtrip_disk(strings1,strings2):
    vocab1 = Vocab(strings=strings1)
    vocab2 = Vocab(strings=strings2)
    with make_tempdir() as d:
        file_path1 = d / 'vocab1'
        file_path2 = d / 'vocab2'
        vocab1.to_disk(file_path1)
        vocab2.to_disk(file_path2)
        vocab1_d = Vocab().from_disk(file_path1)
        vocab2_d = Vocab().from_disk(file_path2)
        assert list(vocab1_d) == list(vocab1)
        assert list(vocab2_d) == list(vocab2)
        if strings1 == strings2:
            assert list(vocab1_d) == list(vocab2_d)
        else:
            assert list(vocab1_d) != list(vocab2_d)


@pytest.mark.parametrize('strings,lex_attr', test_strings_attrs)
def test_serialize_vocab_lex_attrs_bytes(strings, lex_attr):
    vocab1 = Vocab(strings=strings)
    vocab2 = Vocab()
    vocab1[strings[0]].norm_ = lex_attr
    assert vocab1[strings[0]].norm_ == lex_attr
    assert vocab2[strings[0]].norm_ != lex_attr
    vocab2 = vocab2.from_bytes(vocab1.to_bytes())
    assert vocab2[strings[0]].norm_ == lex_attr


@pytest.mark.parametrize('strings,lex_attr', test_strings_attrs)
def test_serialize_vocab_lex_attrs_disk(strings, lex_attr):
    vocab1 = Vocab(strings=strings)
    vocab2 = Vocab()
    vocab1[strings[0]].norm_ = lex_attr
    assert vocab1[strings[0]].norm_ == lex_attr
    assert vocab2[strings[0]].norm_ != lex_attr
    with make_tempdir() as d:
        file_path = d / 'vocab'
        vocab1.to_disk(file_path)
        vocab2 = vocab2.from_disk(file_path)
    assert vocab2[strings[0]].norm_ == lex_attr
