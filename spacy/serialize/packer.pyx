from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t
from libc.math cimport exp as c_exp
from libcpp.queue cimport priority_queue
from libcpp.pair cimport pair

from cymem.cymem cimport Address, Pool
from preshed.maps cimport PreshMap

from ..attrs cimport ID, SPACY, TAG, HEAD, DEP, ENT_IOB, ENT_TYPE
from ..tokens.doc cimport Doc
from ..vocab cimport Vocab
from ..typedefs cimport attr_t
from .bits cimport BitArray
from .huffman cimport HuffmanCodec

from os import path
import numpy

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


def make_vocab_codec(Vocab vocab):
    cdef int length = len(vocab)
    cdef Address mem = Address(length, sizeof(float))
    probs = <float*>mem.ptr
    cdef int i
    for i in range(length):
        probs[i] = <float>c_exp(vocab.lexemes[i].prob)
    cdef float[:] cv_probs = <float[:len(vocab)]>probs
    return HuffmanCodec(cv_probs)


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


cdef class _AttributeCodec:
    cdef Pool mem
    cdef attr_t* _keys
    cdef dict _map
    cdef HuffmanCodec _codec

    def __init__(self, freqs):
        self.mem = Pool()
        cdef attr_t key
        cdef float count
        cdef pair[float, attr_t] item

        cdef priority_queue[pair[float, attr_t]] items

        for key, count in freqs:
            item.first = count
            item.second = key
            items.push(item)
        weights = numpy.ndarray(shape=(len(freqs),), dtype=numpy.float32)
        self._keys = <attr_t*>self.mem.alloc(len(freqs), sizeof(attr_t))
        self._map = {}
        cdef int i = 0
        while not items.empty():
            item = items.top()
            # We put freq first above, for sorting
            self._keys[i] = item.second
            weights[i] = item.first
            self._map[self._keys[i]] = i
            items.pop()
            i += 1
        self._codec = HuffmanCodec(weights)

    def encode(self, attr_t[:] msg, BitArray dest):
        cdef int i
        for i in range(len(msg)):
            msg[i] = self._map[msg[i]]
        self._codec.encode(msg, dest)

    def decode(self, BitArray bits, attr_t[:] dest):
        cdef int i
        self._codec.decode(bits, dest)
        for i in range(len(dest)):
            dest[i] = <attr_t>self._keys[dest[i]]


cdef class Packer:
    def __init__(self, Vocab vocab, list_of_attr_freqs):
        self.vocab = vocab
        codecs = []
        attrs = []

        for attr, freqs in list_of_attr_freqs:
            if attr == ID:
                codecs.append(make_vocab_codec(vocab))
            elif attr == SPACY:
                codecs.append(_BinaryCodec())
            else:
                codecs.append(_AttributeCodec(freqs))
            attrs.append(attr)
        self._codecs = tuple(codecs)
        self.attrs = tuple(attrs)

    def pack(self, Doc doc):
        array = doc.to_array(self.attrs)
        cdef BitArray bits = BitArray()
        cdef uint32_t length = 3
        #cdef uint32_t length = len(doc)
        #bits.extend(length, 32)
        for i, codec in enumerate(self._codecs):
            codec.encode(array[:, i], bits)
        return bits

    def unpack(self, BitArray bits):
        bits.seek(0)
        #cdef uint32_t length = bits.read32()
        cdef uint32_t length = 3
        array = numpy.zeros(shape=(length, len(self._codecs)), dtype=numpy.int32)
        for i, codec in enumerate(self._codecs):
            codec.decode(bits, array[:, i])
        doc = Doc.from_ids(self.vocab, array[:, 0], array[:, 1])
        doc.from_array(self.attrs, array)
        return doc
