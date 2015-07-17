from __future__ import unicode_literals
import pytest

import numpy

from spacy.vocab import Vocab
from spacy.serialize.packer import _BinaryCodec
from spacy.serialize.packer import make_vocab_codec
from spacy.serialize.packer import _AttributeCodec
from spacy.serialize.bits import BitArray


def test_binary():
    codec = _BinaryCodec()
    bits = BitArray()
    msg = numpy.array([0, 1, 0, 1, 1], numpy.int32)
    codec.encode(msg, bits)
    result = numpy.array([0, 0, 0, 0, 0], numpy.int32)
    codec.decode(iter(bits), result)
    assert list(msg) == list(result)


def test_attribute():
    freqs = {'the': 10, 'quick': 3, 'brown': 4, 'fox': 1, 'jumped': 5, 'over': 8,
            'lazy': 1, 'dog': 2, '.': 9}
 
    int_map = {'the': 0, 'quick': 1, 'brown': 2, 'fox': 3, 'jumped': 4, 'over': 5,
               'lazy': 6, 'dog': 7, '.': 8}

    codec = _AttributeCodec([(int_map[string], freq) for string, freq in freqs.items()])

    bits = BitArray()
    
    msg = numpy.array([1, 7], dtype=numpy.int32)
    msg_list = list(msg)
    codec.encode(msg, bits)
    result = numpy.array([0, 0], dtype=numpy.int32)
    codec.decode(bits, result)
    assert msg_list == list(result)


def test_vocab_codec():
    def get_lex_props(string, prob):
        return {
            'flags': 0,
            'length': len(string),
            'orth': string,
            'lower': string, 
            'norm': string,
            'shape': string,
            'prefix': string[0],
            'suffix': string[-3:],
            'cluster': 0,
            'prob': prob,
            'sentiment': 0
        }

    vocab = Vocab()
    vocab['dog'] = get_lex_props('dog', 0.001)
    vocab['the'] = get_lex_props('the', 0.05)
    vocab['jumped'] = get_lex_props('jumped', 0.005)

    codec = make_vocab_codec(vocab)

    bits = BitArray()
    
    ids = [vocab[s].id for s in ('the', 'dog', 'jumped')]
    msg = numpy.array(ids, dtype=numpy.int32)
    msg_list = list(msg)
    codec.encode(msg, bits)
    result = numpy.array(range(len(msg)), dtype=numpy.int32)
    codec.decode(bits, result)
    assert msg_list == list(result)
