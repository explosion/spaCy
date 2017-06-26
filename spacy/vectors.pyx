import numpy
from collections import OrderedDict
import msgpack
import msgpack_numpy
msgpack_numpy.patch()

from .strings cimport StringStore
from . import util


cdef class Vectors:
    '''Store, save and load word vectors.'''
    cdef public object data
    cdef readonly StringStore strings
    cdef public object key2i

    def __init__(self, strings, data_or_width):
        self.strings = StringStore()
        if isinstance(data_or_width, int):
            self.data = data = numpy.zeros((len(strings), data_or_width),
                                           dtype='f')
        else:
            data = data_or_width
        self.data = data
        self.key2i = {}
        for i, string in enumerate(strings):
            self.key2i[self.strings.add(string)] = i

    def __reduce__(self):
        return (Vectors, (self.strings, self.data))

    def __getitem__(self, key):
        if isinstance(key, basestring):
            key = self.strings[key]
        i = self.key2i[key]
        if i is None:
            raise KeyError(key)
        else:
            return self.data[i]

    def __setitem__(self, key, vector):
        if isinstance(key, basestring):
            key = self.strings.add(key)
        i = self.key2i[key]
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

    def to_disk(self, path):
        raise NotImplementedError

    def from_disk(self, path):
        raise NotImplementedError

    def to_bytes(self, **exclude):
        def serialize_weights():
            if hasattr(self.weights, 'to_bytes'):
                return self.weights.to_bytes()
            else:
                return msgpack.dumps(self.weights)

        serializers = OrderedDict((
            ('strings', lambda: self.strings.to_bytes()),
            ('weights', serialize_weights)
        ))
        return util.to_bytes(serializers, exclude)

    def from_bytes(self, data, **exclude):
        def deserialize_weights(b):
            if hasattr(self.weights, 'from_bytes'):
                self.weights.from_bytes()
            else:
                self.weights = msgpack.loads(b)

        deserializers = OrderedDict((
            ('strings', lambda b: self.strings.from_bytes(b)),
            ('weights', deserialize_weights)
        ))
        return util.from_bytes(deserializers, exclude)
