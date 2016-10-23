from __future__ import unicode_literals
from __future__ import division

import pytest

from spacy.serialize.huffman import HuffmanCodec
from spacy.serialize.bits import BitArray
import numpy
import math

from heapq import heappush, heappop, heapify
from collections import defaultdict


def py_encode(symb2freq):
    """Huffman encode the given dict mapping symbols to weights
    From Rosetta Code
    """
    heap = [[wt, [sym, ""]] for sym, wt in symb2freq.items()]
    heapify(heap)
    while len(heap) > 1:
        lo = heappop(heap)
        hi = heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    return dict(heappop(heap)[1:])


def test1():
    probs = numpy.zeros(shape=(10,), dtype=numpy.float32)
    probs[0] = 0.3
    probs[1] = 0.2
    probs[2] = 0.15
    probs[3] = 0.1
    probs[4] = 0.06
    probs[5] = 0.02
    probs[6] = 0.01
    probs[7] = 0.005
    probs[8] = 0.0001
    probs[9] = 0.000001
    
    codec = HuffmanCodec(list(enumerate(probs)))
    
    py_codes = py_encode(dict(enumerate(probs)))
    py_codes = list(py_codes.items())
    py_codes.sort()
    assert codec.strings == [c for i, c in py_codes]


def test_empty():
    codec = HuffmanCodec({})
    assert codec.strings == []
    

def test_round_trip():
    freqs = {'the': 10, 'quick': 3, 'brown': 4, 'fox': 1, 'jumped': 5, 'over': 8,
            'lazy': 1, 'dog': 2, '.': 9}
    codec = HuffmanCodec(freqs.items())

    message = ['the', 'quick', 'brown', 'fox', 'jumped', 'over', 'the',
                'the', 'lazy', 'dog', '.']
    strings = list(codec.strings)
    codes = dict([(codec.leaves[i], strings[i]) for i in range(len(codec.leaves))])
    bits = codec.encode(message)
    string = ''.join('{0:b}'.format(c).rjust(8, '0')[::-1] for c in bits.as_bytes())
    for word in message:
        code = codes[word]
        assert string[:len(code)] == code
        string = string[len(code):]
    unpacked = [0] * len(message)
    bits.seek(0)
    codec.decode(bits, unpacked)
    assert message == unpacked


def test_rosetta():
    txt = u"this is an example for huffman encoding"
    symb2freq = defaultdict(int)
    for ch in txt:
        symb2freq[ch] += 1
    by_freq = list(symb2freq.items())
    by_freq.sort(reverse=True, key=lambda item: item[1])
    symbols = [sym for sym, prob in by_freq]

    codec = HuffmanCodec(symb2freq.items())
    py_codec = py_encode(symb2freq)

    codes = dict([(codec.leaves[i], codec.strings[i]) for i in range(len(codec.leaves))])

    my_lengths = defaultdict(int)
    py_lengths = defaultdict(int)
    for symb, freq in symb2freq.items():
        my = codes[symb]
        my_lengths[len(my)] += freq
        py_lengths[len(py_codec[symb])] += freq
    my_exp_len = sum(length * weight for length, weight in my_lengths.items())
    py_exp_len = sum(length * weight for length, weight in py_lengths.items())
    assert my_exp_len == py_exp_len


@pytest.mark.slow
def test_vocab(EN):
    codec = HuffmanCodec([(w.orth, numpy.exp(w.prob)) for w in EN.vocab])
    expected_length = 0
    for i, code in enumerate(codec.strings):
        leaf = codec.leaves[i]
        expected_length += len(code) * numpy.exp(EN.vocab[leaf].prob)
    assert 8 < expected_length < 15
