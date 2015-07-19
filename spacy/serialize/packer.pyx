# cython: profile=True
from __future__ import unicode_literals

from libc.stdint cimport uint32_t, int32_t
from libc.stdint cimport uint64_t
from libc.math cimport exp as c_exp
from libcpp.queue cimport priority_queue
from libcpp.pair cimport pair

from ..structs cimport UniStr
from ..strings cimport slice_unicode

from cymem.cymem cimport Address, Pool
from preshed.maps cimport PreshMap
from preshed.counter cimport PreshCounter

from ..attrs cimport ORTH, ID, SPACY, TAG, HEAD, DEP, ENT_IOB, ENT_TYPE
from ..tokens.doc cimport Doc
from ..vocab cimport Vocab
from ..structs cimport LexemeC
from ..typedefs cimport attr_t
from .bits cimport BitArray
from .huffman cimport HuffmanCodec

from os import path
import numpy
from .. import util

cimport cython


# Format
# - Total number of bytes in message (32 bit int) --- handled outside this
# - Number of words (32 bit int)
# - Words, terminating in an EOL symbol, huffman coded ~12 bits per word
# - Spaces 1 bit per word
# - Attributes:
#       POS tag
#       Head offset
#       Dep label
#       Entity IOB
#       Entity tag


cdef class _BinaryCodec:
    def encode(self, attr_t[:] msg, BitArray bits):
        cdef int i
        for i in range(len(msg)):
            bits.append(msg[i])

    def decode(self, BitArray bits, attr_t[:] msg):
        cdef int i = 0 
        for bit in bits:
            msg[i] = bit
            i += 1
            if i == len(msg):
                break


def _gen_orths(Vocab vocab):
    cdef attr_t orth
    cdef size_t addr
    for orth, addr in vocab._by_orth.items():
        lex = <LexemeC*>addr
        yield orth, c_exp(lex.prob)


def _gen_chars(Vocab vocab):
    cdef attr_t orth
    cdef size_t addr
    char_weights = {chr(i): 1e-20 for i in range(256)}
    cdef unicode string
    cdef bytes char
    cdef bytes utf8_str
    for orth, addr in vocab._by_orth.items():
        lex = <LexemeC*>addr
        string = vocab.strings[lex.orth]
        utf8_str = string.encode('utf8')
        for char in utf8_str:
            char_weights.setdefault(char, 0.0)
            char_weights[char] += c_exp(lex.prob)
        char_weights[b' '] += c_exp(lex.prob)
    return char_weights.items()


cdef class Packer:
    def __init__(self, Vocab vocab, attr_freqs, char_freqs=None):
        if char_freqs is None:
            char_freqs = _gen_chars(vocab)
        self.vocab = vocab
        self.orth_codec = HuffmanCodec(_gen_orths(vocab))
        self.char_codec = HuffmanCodec(char_freqs)
        
        codecs = []
        attrs = []
        for attr, freqs in sorted(attr_freqs):
            if attr in (ORTH, ID, SPACY):
                continue
            codecs.append(HuffmanCodec(freqs))
            attrs.append(attr)
        self._codecs = tuple(codecs)
        self.attrs = tuple(attrs)

    @classmethod
    def from_dir(cls, Vocab vocab, data_dir):
        return cls(vocab, util.read_encoding_freqs(data_dir))

    def pack(self, Doc doc):
        orths = [t.orth for t in doc]
        chars = doc.string.encode('utf8')
        # n_bits returns nan for oov words, i.e. can't encode message.
        # So, it's important to write the conditional like this.
        if self.orth_codec.n_bits(orths) < self.char_codec.n_bits(chars, overhead=1):
            bits = self._orth_encode(doc)
        else:
            bits = self._char_encode(doc)
        array = doc.to_array(self.attrs)
        for i, codec in enumerate(self._codecs):
            codec.encode(array[:, i], bits)
        return bits

    def unpack(self, BitArray bits):
        bits.seek(0)
        cdef int32_t length = bits.read32()
        if length >= 0:
            doc = self._orth_decode(bits, length)
        else:
            doc = self._char_decode(bits, -length)

        array = numpy.zeros(shape=(len(doc), len(self._codecs)), dtype=numpy.int32)
        for i, codec in enumerate(self._codecs):
            codec.decode(bits, array[:, i])

        doc.from_array(self.attrs, array)
        return doc

    def _orth_encode(self, Doc doc):
        cdef BitArray bits = BitArray()
        orths = [w.orth for w in doc]
        cdef int32_t length = len(doc)
        bits.extend(length, 32) 
        self.orth_codec.encode(orths, bits)
        for token in doc:
            bits.append(bool(token.whitespace_))
        return bits

    def _orth_decode(self, BitArray bits, n):
        orths = [0] * n
        self.orth_codec.decode(bits, orths)
        orths_and_spaces = zip(orths, bits)
        cdef Doc doc = Doc(self.vocab, orths_and_spaces)
        return doc

    def _char_encode(self, Doc doc):
        cdef BitArray bits = BitArray()
        cdef bytes utf8_str = doc.string.encode('utf8')
        cdef int32_t length = len(utf8_str)
        # Signal chars with negative length
        bits.extend(-length, 32)
        self.char_codec.encode(utf8_str, bits)
        for token in doc:
            for i in range(len(token)-1):
                bits.append(False)
            bits.append(True)
            if token.whitespace_:
                bits.append(False)
        return bits

    def _char_decode(self, BitArray bits, n):
        chars = [b''] * n
        self.char_codec.decode(bits, chars)
        cdef bytes utf8_str = b''.join(chars)

        cdef unicode string = utf8_str.decode('utf8')
        cdef Doc tokens = Doc(self.vocab)
        cdef int i
        cdef int start = 0
        cdef bint is_spacy
        cdef UniStr span
        cdef int length = len(string)
        iter_bits = iter(bits)
        for i in range(length):
            is_end_token = iter_bits.next()
            if is_end_token:
                slice_unicode(&span, string, start, i+1)
                lex = self.vocab.get(tokens.mem, &span)
                is_spacy = (i+1) < length and string[i+1] == u' '
                tokens.push_back(lex, is_spacy)
                start = i + 1 + is_spacy
        return tokens
