from libc.stdint cimport int32_t, uint64_t
import numpy
from collections import OrderedDict
import msgpack
import msgpack_numpy
msgpack_numpy.patch()
from cymem.cymem cimport Pool
cimport numpy as np
from libcpp.vector cimport vector

from .typedefs cimport attr_t
from .strings cimport StringStore
from . import util
from ._cfile cimport CFile

MAX_VEC_SIZE = 10000


cdef class Vectors:
    '''Store, save and load word vectors.'''
    cdef public object data
    cdef readonly StringStore strings
    cdef public object index

    def __init__(self, strings, data_or_width):
        self.strings = StringStore()
        if isinstance(data_or_width, int):
            self.data = data = numpy.zeros((len(strings), data_or_width),
                                           dtype='f')
        else:
            data = data_or_width
        self.data = data
        self.index = {}
        for i, string in enumerate(strings):
            self.index[self.strings.add(string)] = i

    def __reduce__(self):
        return (Vectors, (self.strings, self.data))

    def __getitem__(self, key):
        if isinstance(key, basestring):
            key = self.strings[key]
        i = self.index[key]
        if i is None:
            raise KeyError(key)
        else:
            return self.data[i]

    def __setitem__(self, key, vector):
        if isinstance(key, basestring):
            key = self.strings.add(key)
        i = self.index[key]
        self.data[i] = vector

    def __iter__(self):
        yield from self.data

    def __len__(self):
        return len(self.strings)

    def items(self):
        for i, string in enumerate(self.strings):
            yield string, self.data[i]

    @property
    def shape(self):
        return self.data.shape

    def most_similar(self, key):
        raise NotImplementedError

    def to_disk(self, path, **exclude):
        def serialize_vectors(p):
            write_vectors_to_bin_loc(self.strings, self.key2i, self.data, str(p))

        serializers = OrderedDict((
            ('vec.bin', serialize_vectors),
        ))
        return util.to_disk(serializers, exclude)

    def from_disk(self, path, **exclude):
        def deserialize_vectors(p):
            self.key2i, self.vectors = load_vectors_from_bin_loc(self.strings, str(p))

        serializers = OrderedDict((
            ('vec.bin', deserialize_vectors)
        ))
        return util.to_disk(serializers, exclude)

    def to_bytes(self, **exclude):
        def serialize_weights():
            if hasattr(self.data, 'to_bytes'):
                return self.data.to_bytes()
            else:
                return msgpack.dumps(self.data)

        serializers = OrderedDict((
            ('key2row', lambda: msgpack.dumps(self.key2i)),
            ('strings', lambda: self.strings.to_bytes()),
            ('vectors', serialize_weights)
        ))
        return util.to_bytes(serializers, exclude)

    def from_bytes(self, data, **exclude):
        def deserialize_weights(b):
            if hasattr(self.data, 'from_bytes'):
                self.data.from_bytes()
            else:
                self.data = msgpack.loads(b)

        deserializers = OrderedDict((
            ('key2row', lambda b: self.key2i.update(msgpack.loads(b))),
            ('strings', lambda b: self.strings.from_bytes(b)),
            ('vectors', deserialize_weights)
        ))
        return util.from_bytes(deserializers, exclude)


def write_vectors_to_bin_loc(StringStore strings, dict key2i,
                             np.ndarray vectors, out_loc):

    cdef int32_t vec_len = vectors.shape[1]
    cdef int32_t word_len
    cdef bytes word_str
    cdef char* chars
    cdef uint64_t key
    cdef int32_t i
    cdef float* vec

    cdef CFile out_file = CFile(out_loc, 'wb')
    keys = [(i, key) for (key, i) in key2i.item()]
    keys.sort()
    for i, key in keys:
        vec = <float*>vectors.data[i * vec_len]
        word_str = strings[key].encode('utf8')
        word_len = len(word_str)

        out_file.write_from(&word_len, 1, sizeof(word_len))
        out_file.write_from(&vec_len, 1, sizeof(vec_len))

        chars = <char*>word_str
        out_file.write_from(chars, word_len, sizeof(char))
        out_file.write_from(vec, vec_len, sizeof(float))
    out_file.close()


def load_vectors_from_bin_loc(StringStore strings, loc):
    """
    Load vectors from the location of a binary file.
    Arguments:
        loc (unicode): The path of the binary file to load from.
    Returns:
        vec_len (int): The length of the vectors loaded.
    """
    cdef CFile file_ = CFile(loc, b'rb')
    cdef int32_t word_len
    cdef int32_t vec_len = 0
    cdef int32_t prev_vec_len = 0
    cdef float* vec
    cdef attr_t string_id
    cdef bytes py_word
    cdef vector[float*] vectors
    cdef int line_num = 0
    cdef Pool mem = Pool()
    cdef dict key2i = {}
    while True:
        try:
            file_.read_into(&word_len, sizeof(word_len), 1)
        except IOError:
            break
        file_.read_into(&vec_len, sizeof(vec_len), 1)
        if prev_vec_len != 0 and vec_len != prev_vec_len:
            raise Exception("Mismatched vector sizes")
        if 0 >= vec_len >= MAX_VEC_SIZE:
            raise Exception("Mismatched vector sizes")

        chars = <char*>file_.alloc_read(mem, word_len, sizeof(char))
        vec = <float*>file_.alloc_read(mem, vec_len, sizeof(float))

        key = strings.add(chars[:word_len])
        key2i[key] = vectors.size()
        vectors.push_back(vec)
    numpy_vectors = numpy.zeros((vectors.size(), vec_len), dtype='f')
    for i in range(vectors.size()):
        for j in range(vec_len):
            numpy_vectors[i, j] = vectors[i][j]
    return key2i, numpy_vectors
