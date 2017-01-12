# coding: utf-8
from __future__ import unicode_literals

from ...attrs import TAG, DEP, HEAD
from ...serialize.packer import Packer
from ...serialize.bits import BitArray

from ..util import get_doc

import pytest


@pytest.fixture
def text():
    return "the dog jumped"


@pytest.fixture
def text_b():
    return b"the dog jumped"


def test_serialize_char_packer(en_vocab, text_b):
    packer = Packer(en_vocab, [])
    bits = BitArray()
    bits.seek(0)
    byte_str = bytearray(text_b)
    packer.char_codec.encode(byte_str, bits)
    bits.seek(0)
    result = [b''] * len(byte_str)
    packer.char_codec.decode(bits, result)
    assert bytearray(result) == byte_str


def test_serialize_packer_unannotated(en_tokenizer, text):
    packer = Packer(en_tokenizer.vocab, [])
    tokens = en_tokenizer(text)
    assert tokens.text_with_ws == text
    bits = packer.pack(tokens)
    result = packer.unpack(bits)
    assert result.text_with_ws == text


def test_packer_annotated(en_vocab, text):
    heads = [1, 1, 0]
    deps = ['det', 'nsubj', 'ROOT']
    tags = ['DT', 'NN', 'VBD']

    attr_freqs = [
        (TAG, [(en_vocab.strings['NN'], 0.1),
               (en_vocab.strings['DT'], 0.2),
               (en_vocab.strings['JJ'], 0.01),
               (en_vocab.strings['VBD'], 0.05)]),
        (DEP, {en_vocab.strings['det']: 0.2,
               en_vocab.strings['nsubj']: 0.1,
               en_vocab.strings['adj']: 0.05,
               en_vocab.strings['ROOT']: 0.1}.items()),
        (HEAD, {0: 0.05, 1: 0.2, -1: 0.2, -2: 0.1, 2: 0.1}.items())
    ]

    packer = Packer(en_vocab, attr_freqs)
    doc = get_doc(en_vocab, [t for t in text.split()], tags=tags, deps=deps, heads=heads)

    # assert doc.text_with_ws == text
    assert [t.tag_ for t in doc] == tags
    assert [t.dep_ for t in doc] == deps
    assert [(t.head.i-t.i) for t in doc] == heads

    bits = packer.pack(doc)
    result = packer.unpack(bits)

    # assert result.text_with_ws == text
    assert [t.tag_ for t in result] == tags
    assert [t.dep_ for t in result] == deps
    assert [(t.head.i-t.i) for t in result] == heads


def test_packer_bad_chars(en_tokenizer):
    text = "naja gut, is eher bl\xf6d und nicht mit reddit.com/digg.com vergleichbar; vielleicht auf dem weg dahin"
    packer = Packer(en_tokenizer.vocab, [])

    doc = en_tokenizer(text)
    bits = packer.pack(doc)
    result = packer.unpack(bits)
    assert result.string == doc.string


@pytest.mark.models
def test_packer_bad_chars_tags(EN):
    text = "naja gut, is eher bl\xf6d und nicht mit reddit.com/digg.com vergleichbar; vielleicht auf dem weg dahin"
    tags = ['JJ', 'NN', ',', 'VBZ', 'DT', 'NN', 'JJ', 'NN', 'NN',
            'ADD', 'NN', ':', 'NN', 'NN', 'NN', 'NN', 'NN']

    tokens = EN.tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], tags=tags)
    byte_string = doc.to_bytes()
    result = get_doc(tokens.vocab).from_bytes(byte_string)
    assert [t.tag_ for t in result] == [t.tag_ for t in doc]
