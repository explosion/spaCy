# cython: profile=True
from __future__ import unicode_literals

from libc.stdint cimport uint32_t, int32_t
from libc.stdint cimport uint64_t
from libc.math cimport exp as c_exp
from libcpp.queue cimport priority_queue
from libcpp.pair cimport pair

from cymem.cymem cimport Address, Pool
from preshed.maps cimport PreshMap
from preshed.counter cimport PreshCounter
import json

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
    char_weights = {i: 1e-20 for i in range(256)}
    cdef unicode string
    cdef bytes char
    cdef bytes utf8_str
    for orth, addr in vocab._by_orth.items():
        lex = <LexemeC*>addr
        string = vocab.strings[lex.orth]
        utf8_str = string.encode('utf8')
        for char in utf8_str:
            char_weights.setdefault(ord(char), 0.0)
            char_weights[ord(char)] += c_exp(lex.prob)
        char_weights[ord(' ')] += c_exp(lex.prob)
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

    def pack(self, Doc doc):
        if len(doc) == 0:
            return b''
        bits = self._orth_encode(doc)
        if bits is None:
            bits = self._char_encode(doc)
        cdef int i
        if self.attrs:
            array = doc.to_array(self.attrs)
            for i, codec in enumerate(self._codecs):
                codec.encode(array[:, i], bits)
        return bits.as_bytes()

    def unpack(self, data):
        doc = Doc(self.vocab)
        self.unpack_into(data, doc)
        return doc

    def unpack_into(self, byte_string, Doc doc):
        if byte_string == b'':
            return None
        bits = BitArray(byte_string)
        bits.seek(0)
        cdef int32_t length = bits.read32()
        if length >= 0:
            self._orth_decode(bits, length, doc)
        else:
            self._char_decode(bits, -length, doc)
        array = numpy.zeros(shape=(len(doc), len(self._codecs)), dtype=numpy.int32)
        for i, codec in enumerate(self._codecs):
            codec.decode(bits, array[:, i])
        doc.from_array(self.attrs, array)
        return doc

    def _orth_encode(self, Doc doc):
        for t in doc:
            if t.is_oov:
                return None
        cdef BitArray bits = BitArray()
        cdef int32_t length = len(doc)
        bits.extend(length, 32) 
        orths = doc.to_array([ORTH])
        n_bits = self.orth_codec.encode_int32(orths[:, 0], bits)
        if n_bits == 0:
            return None
        for token in doc:
            bits.append(bool(token.whitespace_))
        return bits

    def _char_encode(self, Doc doc):
        cdef bytes utf8_str = doc.string.encode('utf8')
        cdef BitArray bits = BitArray()
        cdef int32_t length = len(utf8_str)
        # Signal chars with negative length
        bits.extend(-length, 32)
        self.char_codec.encode(bytearray(utf8_str), bits)
        cdef int i, j
        for i in range(doc.length):
            for j in range(doc.c[i].lex.length-1):
                bits.append(False)
            bits.append(True)
            if doc.c[i].spacy:
                bits.append(False)
        return bits

    def _orth_decode(self, BitArray bits, int32_t n, Doc doc):
        cdef attr_t[:] orths = numpy.ndarray(shape=(n,), dtype=numpy.int32)
        self.orth_codec.decode_int32(bits, orths)
        cdef int i
        cdef bint space
        spaces = iter(bits)
        for i in range(n):
            orth = orths[i]
            space = next(spaces)
            lex = self.vocab.get_by_orth(doc.mem, orth)
            doc.push_back(lex, space)
        return doc

    def _char_decode(self, BitArray bits, int32_t n_bytes, Doc doc):
        cdef bytearray utf8_str = bytearray(n_bytes)
        self.char_codec.decode(bits, utf8_str)

        cdef unicode string = utf8_str.decode('utf8')
        cdef int start = 0
        cdef bint is_spacy
        cdef int n_unicode_chars = len(string)
        cdef int i = 0
        cdef bint is_end_token
        for is_end_token in bits:
            if is_end_token:
                span = string[start:i+1]
                lex = self.vocab.get(doc.mem, span)
                is_spacy = (i+1) < n_unicode_chars and string[i+1] == u' '
                doc.push_back(lex, is_spacy)
                start = i + 1 + is_spacy
            i += 1
            if i >= n_unicode_chars:
                break
        return doc
