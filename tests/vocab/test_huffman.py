from __future__ import unicode_literals
from __future__ import division

import pytest

from spacy.serialize import HuffmanCodec
import numpy

from heapq import heappush, heappop, heapify
from collections import defaultdict


class Vocab(object):
    def __init__(self, freqs):
        freqs['-eol-'] = 5
        total = sum(freqs.values())
        by_freq = freqs.items()
        by_freq.sort(key=lambda item: item[1], reverse=True)
        self.symbols = [sym for sym, freq in by_freq]
        self.probs = numpy.array([item[1] / total for item in by_freq], dtype=numpy.float32)
        self.table = {sym: i for i, sym in enumerate(self.symbols)}
        self.codec = HuffmanCodec(self.probs, self.table['-eol-'])

    def pack(self, message):
        seq = [self.table[sym] for sym in message]
        return self.codec.encode(numpy.array(seq, dtype=numpy.uint32))

    def unpack(self, packed):
        ids = self.codec.decode(packed)
        return [self.symbols[i] for i in ids]

 
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
    
    codec = HuffmanCodec(probs, 9)
    
    py_codes = py_encode(dict(enumerate(probs)))
    py_codes = py_codes.items()
    py_codes.sort()
    assert codec.strings == [c for i, c in py_codes]
    

def test_round_trip():
    freqs = {'the': 10, 'quick': 3, 'brown': 4, 'fox': 1, 'jumped': 5, 'over': 8,
            'lazy': 1, 'dog': 2, '.': 9}
    vocab = Vocab(freqs)

    message = ['the', 'quick', 'brown', 'fox', 'jumped', 'over', 'the',
                'the', 'lazy', 'dog', '.']
    strings = list(vocab.codec.strings)
    codes = {vocab.symbols[i]: strings[i] for i in range(len(vocab.symbols))}
    packed = vocab.pack(message)
    string = b''.join(b'{0:b}'.format(ord(c)).rjust(8, b'0')[::-1] for c in packed.as_bytes())
    for word in message:
        code = codes[word]
        assert string[:len(code)] == code
        string = string[len(code):]
    unpacked = vocab.unpack(packed)
    assert message == unpacked


def test_rosetta():
    txt = u"this is an example for huffman encoding"
    symb2freq = defaultdict(int)
    for ch in txt:
        symb2freq[ch] += 1
    symb2freq['-eol-'] = 1
    by_freq = symb2freq.items()
    by_freq.sort(reverse=True, key=lambda item: item[1])
    symbols = [sym for sym, prob in by_freq]
    probs = numpy.array([prob for sym, prob in by_freq], dtype=numpy.float32)

    codec = HuffmanCodec(probs, symbols.index('-eol-'))
    py_codec = py_encode(symb2freq)

    my_lengths = defaultdict(int)
    py_lengths = defaultdict(int)
    for i, my in enumerate(codec.strings):
        symb = by_freq[i][0]
        my_lengths[len(my)] += by_freq[i][1]
        py_lengths[len(py_codec[symb])] += by_freq[i][1]
    my_exp_len = sum(length * weight for length, weight in my_lengths.items())
    py_exp_len = sum(length * weight for length, weight in py_lengths.items())
    assert my_exp_len == py_exp_len


def test_vocab(EN):
    codec = EN.vocab.codec
    expected_length = 0
    for i, code in enumerate(codec.strings):
        expected_length += len(code) * numpy.exp(EN.vocab[i].prob)
    assert 8 < expected_length < 15


def test_freqs():
    freqs = []
    words = []
    for i, line in enumerate(open('freqs.txt')):
        pieces = line.strip().split()
        if len(pieces) != 2:
           continue
        freq, word = pieces
        freqs.append(int(freq))
    freqs.append(1)
    total = sum(freqs)
    freqs = [(float(f) / total) for f in freqs]
    codec = HuffmanCodec(numpy.array(freqs, dtype=numpy.float32), len(freqs)-1)
    expected_length = 0
    for i, code in enumerate(codec.strings):
        expected_length += len(code) * freqs[i]
    assert 8 < expected_length < 14
