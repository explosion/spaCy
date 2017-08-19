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
    cdef public object key2row
    cdef public object keys

    def __init__(self, strings, data_or_width):
        self.strings = StringStore()
        if isinstance(data_or_width, int):
            self.data = data = numpy.zeros((len(strings), data_or_width),
                                           dtype='f')
        else:
            data = data_or_width
        self.data = data
        self.key2row = {}
        self.keys = np.ndarray((self.data.shape[0],), dtype='uint64') 
        for i, string in enumerate(strings):
            key = self.strings.add(string)
            self.key2row[key] = i
            self.keys[i] = key

    def __reduce__(self):
        return (Vectors, (self.strings, self.data))

    def __getitem__(self, key):
        if isinstance(key, basestring):
            key = self.strings[key]
        i = self.key2row[key]
        if i is None:
            raise KeyError(key)
        else:
            return self.data[i]

    def __setitem__(self, key, vector):
        if isinstance(key, basestring):
            key = self.strings.add(key)
        i = self.key2row[key]
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
        serializers = OrderedDict((
            ('vectors', lambda p: numpy.save(p.open('wb'), self.data)),
            ('strings.json', self.strings.to_disk),
            ('keys', lambda p: numpy.save(p.open('wb'), self.keys)),
        ))
        return util.to_disk(path, serializers, exclude)

    def from_disk(self, path, **exclude):
        def load_keys(path):
            self.keys = numpy.load(path)
            for i, key in enumerate(self.keys):
                self.keys[i] = key
                self.key2row[key] = i

        def load_vectors(path):
            self.data = numpy.load(path)

        serializers = OrderedDict((
            ('keys', load_keys),
            ('vectors', load_vectors),
            ('strings.json', self.strings.from_disk),
        ))
        util.from_disk(path, serializers, exclude)
        return self

    def to_bytes(self, **exclude):
        def serialize_weights():
            if hasattr(self.data, 'to_bytes'):
                return self.data.to_bytes()
            else:
                return msgpack.dumps(self.data)
        serializers = OrderedDict((
            ('keys', lambda: msgpack.dumps(self.keys)),
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

        def load_keys(keys):
            for i, key in enumerate(keys):
                self.keys[i] = key
                self.key2row[key] = i

        deserializers = OrderedDict((
            ('keys', lambda b: load_keys(msgpack.loads(b))),
            ('strings', lambda b: self.strings.from_bytes(b)),
            ('vectors', deserialize_weights)
        ))
        util.from_bytes(deserializers, exclude)
        return self
