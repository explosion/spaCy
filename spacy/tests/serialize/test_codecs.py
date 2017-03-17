# coding: utf-8
from __future__ import unicode_literals

from ...serialize.packer import _BinaryCodec
from ...serialize.huffman import HuffmanCodec
from ...serialize.bits import BitArray

import numpy
import pytest


def test_serialize_codecs_binary():
    codec = _BinaryCodec()
    bits = BitArray()
    array = numpy.array([0, 1, 0, 1, 1], numpy.int32)
    codec.encode(array, bits)
    result = numpy.array([0, 0, 0, 0, 0], numpy.int32)
    bits.seek(0)
    codec.decode(bits, result)
    assert list(array) == list(result)


def test_serialize_codecs_attribute():
    freqs = {'the': 10, 'quick': 3, 'brown': 4, 'fox': 1, 'jumped': 5,
             'over': 8, 'lazy': 1, 'dog': 2, '.': 9}
    int_map = {'the': 0, 'quick': 1, 'brown': 2, 'fox': 3, 'jumped': 4,
               'over': 5, 'lazy': 6, 'dog': 7, '.': 8}

    codec = HuffmanCodec([(int_map[string], freq) for string, freq in freqs.items()])
    bits = BitArray()
    array = numpy.array([1, 7], dtype=numpy.int32)
    codec.encode(array, bits)
    result = numpy.array([0, 0], dtype=numpy.int32)
    bits.seek(0)
    codec.decode(bits, result)
    assert list(array) == list(result)


def test_serialize_codecs_vocab(en_vocab):
    words = ["the", "dog", "jumped"]
    for word in words:
        _ = en_vocab[word]
    codec = HuffmanCodec([(lex.orth, lex.prob) for lex in en_vocab])
    bits = BitArray()
    ids = [en_vocab[s].orth for s in words]
    array = numpy.array(ids, dtype=numpy.int32)
    codec.encode(array, bits)
    result = numpy.array(range(len(array)), dtype=numpy.int32)
    bits.seek(0)
    codec.decode(bits, result)
    assert list(array) == list(result)
