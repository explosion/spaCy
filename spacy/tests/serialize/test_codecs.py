from __future__ import unicode_literals
import pytest

import numpy

from spacy.vocab import Vocab
from spacy.serialize.packer import _BinaryCodec
from spacy.serialize.huffman import HuffmanCodec
from spacy.serialize.bits import BitArray


def test_binary():
    codec = _BinaryCodec()
    bits = BitArray()
    msg = numpy.array([0, 1, 0, 1, 1], numpy.int32)
    codec.encode(msg, bits)
    result = numpy.array([0, 0, 0, 0, 0], numpy.int32)
    bits.seek(0)
    codec.decode(bits, result)
    assert list(msg) == list(result)


def test_attribute():
    freqs = {'the': 10, 'quick': 3, 'brown': 4, 'fox': 1, 'jumped': 5, 'over': 8,
            'lazy': 1, 'dog': 2, '.': 9}
 
    int_map = {'the': 0, 'quick': 1, 'brown': 2, 'fox': 3, 'jumped': 4, 'over': 5,
               'lazy': 6, 'dog': 7, '.': 8}

    codec = HuffmanCodec([(int_map[string], freq) for string, freq in freqs.items()])

    bits = BitArray()
    
    msg = numpy.array([1, 7], dtype=numpy.int32)
    msg_list = list(msg)
    codec.encode(msg, bits)
    result = numpy.array([0, 0], dtype=numpy.int32)
    bits.seek(0)
    codec.decode(bits, result)
    assert msg_list == list(result)


def test_vocab_codec():
    vocab = Vocab()
    lex = vocab['dog']
    lex = vocab['the']
    lex = vocab['jumped']

    codec = HuffmanCodec([(lex.orth, lex.prob) for lex in vocab])

    bits = BitArray()
    
    ids = [vocab[s].orth for s in ('the', 'dog', 'jumped')]
    msg = numpy.array(ids, dtype=numpy.int32)
    msg_list = list(msg)
    codec.encode(msg, bits)
    result = numpy.array(range(len(msg)), dtype=numpy.int32)
    bits.seek(0)
    codec.decode(bits, result)
    assert msg_list == list(result)
