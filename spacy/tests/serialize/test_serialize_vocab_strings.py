# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.vocab import Vocab
from spacy.strings import StringStore

from ..util import make_tempdir


test_strings = [([], []), (["rats", "are", "cute"], ["i", "like", "rats"])]
test_strings_attrs = [(["rats", "are", "cute"], "Hello")]


@pytest.mark.parametrize("text", ["rat"])
def test_serialize_vocab(en_vocab, text):
    text_hash = en_vocab.strings.add(text)
    vocab_bytes = en_vocab.to_bytes()
    new_vocab = Vocab().from_bytes(vocab_bytes)
    assert new_vocab.strings[text_hash] == text


@pytest.mark.parametrize("strings1,strings2", test_strings)
def test_serialize_vocab_roundtrip_bytes(strings1, strings2):
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


@pytest.mark.parametrize("strings1,strings2", test_strings)
def test_serialize_vocab_roundtrip_disk(strings1, strings2):
    vocab1 = Vocab(strings=strings1)
    vocab2 = Vocab(strings=strings2)
    with make_tempdir() as d:
        file_path1 = d / "vocab1"
        file_path2 = d / "vocab2"
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


@pytest.mark.parametrize("strings,lex_attr", test_strings_attrs)
def test_serialize_vocab_lex_attrs_bytes(strings, lex_attr):
    vocab1 = Vocab(strings=strings)
    vocab2 = Vocab()
    vocab1[strings[0]].norm_ = lex_attr
    assert vocab1[strings[0]].norm_ == lex_attr
    assert vocab2[strings[0]].norm_ != lex_attr
    vocab2 = vocab2.from_bytes(vocab1.to_bytes())
    assert vocab2[strings[0]].norm_ == lex_attr


@pytest.mark.parametrize("strings,lex_attr", test_strings_attrs)
def test_deserialize_vocab_seen_entries(strings, lex_attr):
    # Reported in #2153
    vocab = Vocab(strings=strings)
    length = len(vocab)
    vocab.from_bytes(vocab.to_bytes())
    assert len(vocab) == length


@pytest.mark.parametrize("strings,lex_attr", test_strings_attrs)
def test_serialize_vocab_lex_attrs_disk(strings, lex_attr):
    vocab1 = Vocab(strings=strings)
    vocab2 = Vocab()
    vocab1[strings[0]].norm_ = lex_attr
    assert vocab1[strings[0]].norm_ == lex_attr
    assert vocab2[strings[0]].norm_ != lex_attr
    with make_tempdir() as d:
        file_path = d / "vocab"
        vocab1.to_disk(file_path)
        vocab2 = vocab2.from_disk(file_path)
    assert vocab2[strings[0]].norm_ == lex_attr


@pytest.mark.parametrize("strings1,strings2", test_strings)
def test_serialize_stringstore_roundtrip_bytes(strings1, strings2):
    sstore1 = StringStore(strings=strings1)
    sstore2 = StringStore(strings=strings2)
    sstore1_b = sstore1.to_bytes()
    sstore2_b = sstore2.to_bytes()
    if strings1 == strings2:
        assert sstore1_b == sstore2_b
    else:
        assert sstore1_b != sstore2_b
    sstore1 = sstore1.from_bytes(sstore1_b)
    assert sstore1.to_bytes() == sstore1_b
    new_sstore1 = StringStore().from_bytes(sstore1_b)
    assert new_sstore1.to_bytes() == sstore1_b
    assert list(new_sstore1) == strings1


@pytest.mark.parametrize("strings1,strings2", test_strings)
def test_serialize_stringstore_roundtrip_disk(strings1, strings2):
    sstore1 = StringStore(strings=strings1)
    sstore2 = StringStore(strings=strings2)
    with make_tempdir() as d:
        file_path1 = d / "strings1"
        file_path2 = d / "strings2"
        sstore1.to_disk(file_path1)
        sstore2.to_disk(file_path2)
        sstore1_d = StringStore().from_disk(file_path1)
        sstore2_d = StringStore().from_disk(file_path2)
        assert list(sstore1_d) == list(sstore1)
        assert list(sstore2_d) == list(sstore2)
        if strings1 == strings2:
            assert list(sstore1_d) == list(sstore2_d)
        else:
            assert list(sstore1_d) != list(sstore2_d)
