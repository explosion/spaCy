# cython: profile=True
from __future__ import unicode_literals

from libc.stdint cimport uint32_t
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
    char_weights = {b' ': 0.0}
    cdef unicode string
    cdef unicode char
    for orth, addr in vocab._by_orth.items():
        lex = <LexemeC*>addr
        string = vocab.strings[lex.orth]
        for char in string:
            char_weights.setdefault(char, 0.0)
            char_weights[char] += c_exp(lex.prob)
        char_weights[u' '] += c_exp(lex.prob)
    return char_weights.items()


cdef class Packer:
    def __init__(self, Vocab vocab, attr_freqs):
        self.vocab = vocab
        self.orth_codec = HuffmanCodec(_gen_orths(vocab))
        self.char_codec = HuffmanCodec(_gen_chars(vocab))
        
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
        cdef BitArray bits = BitArray()
        cdef uint32_t length = len(doc.string)
        bits.extend(length, 32)
        self._char_encode(doc, bits)
        array = doc.to_array(self.attrs)
        for i, codec in enumerate(self._codecs):
            codec.encode(array[:, i], bits)
        return bits

    def unpack(self, BitArray bits):
        bits.seek(0)
        cdef uint32_t length = bits.read32()
        doc = self._char_decode(bits, length)

        array = numpy.zeros(shape=(len(doc), len(self._codecs)), dtype=numpy.int32)
        for i, codec in enumerate(self._codecs):
            codec.decode(bits, array[:, i])

        doc.from_array(self.attrs, array)
        return doc

    def _char_encode(self, Doc doc, BitArray bits):
        cdef unicode string = doc.string
        self.char_codec.encode(string, bits)
        for token in doc:
            for i in range(len(token)-1):
                bits.append(False)
            bits.append(True)
            if token.whitespace_:
                bits.append(False)

    def _char_decode(self, BitArray bits, n):
        chars = [u''] * n
        self.char_codec.decode(bits, chars)

        cdef unicode string = u''.join(chars)
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
