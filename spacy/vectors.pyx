from __future__ import unicode_literals
from libc.stdint cimport int32_t, uint64_t
import numpy
from collections import OrderedDict
import msgpack
import msgpack_numpy
msgpack_numpy.patch()
cimport numpy as np
from thinc.neural.util import get_array_module
from thinc.neural._classes.model import Model

from .typedefs cimport attr_t
from .strings cimport StringStore
from . import util
from .compat import basestring_


cdef class Vectors:
    '''Store, save and load word vectors.'''
    cdef public object data
    cdef readonly StringStore strings
    cdef public object key2row
    cdef public object keys
    cdef public int i

    def __init__(self, strings, data_or_width=0):
        self.strings = StringStore()
        if isinstance(data_or_width, int):
            self.data = data = numpy.zeros((len(strings), data_or_width),
                                           dtype='f')
        else:
            data = data_or_width
        self.i = 0
        self.data = data
        self.key2row = {}
        self.keys = np.ndarray((self.data.shape[0],), dtype='uint64')

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
        return self.i

    def __contains__(self, key):
        if isinstance(key, basestring_):
            key = self.strings[key]
        return key in self.key2row

    def add(self, key, vector=None):
        if isinstance(key, basestring_):
            key = self.strings.add(key)
        if key not in self.key2row:
            i = self.i
            if i >= self.keys.shape[0]:
                self.keys.resize((self.keys.shape[0]*2,))
                self.data.resize((self.data.shape[0]*2, self.data.shape[1]))
            self.key2row[key] = self.i
            self.keys[self.i] = key
            self.i += 1
        else:
            i = self.key2row[key]
        if vector is not None:
            self.data[i] = vector
        return i

    def items(self):
        for i, string in enumerate(self.strings):
            yield string, self.data[i]

    @property
    def shape(self):
        return self.data.shape

    def most_similar(self, key):
        raise NotImplementedError

    def from_glove(self, path):
        '''Load GloVe vectors from a directory. Assumes binary format,
        that the vocab is in a vocab.txt, and that vectors are named
        vectors.{size}.[fd].bin, e.g. vectors.128.f.bin for 128d float32
        vectors, vectors.300.d.bin for 300d float64 (double) vectors, etc.
        By default GloVe outputs 64-bit vectors.'''
        path = util.ensure_path(path)
        for name in path.iterdir():
            if name.parts[-1].startswith('vectors'):
                _, dims, dtype, _2 = name.parts[-1].split('.')
                self.width = int(dims)
                break
        else:
            raise IOError("Expected file named e.g. vectors.128.f.bin")
        bin_loc = path / 'vectors.{dims}.{dtype}.bin'.format(dims=dims,
                                                             dtype=dtype)
        with bin_loc.open('rb') as file_:
            self.data = numpy.fromfile(file_, dtype='float64')
            self.data = numpy.ascontiguousarray(self.data, dtype='float32')
        n = 0
        with (path / 'vocab.txt').open('r') as file_:
            for line in file_:
                self.add(line.strip())
                n += 1
        if (self.data.size % self.width) == 0:
            self.data

    def to_disk(self, path, **exclude):
        xp = get_array_module(self.data)
        if xp is numpy:
            save_array = lambda arr, file_: xp.save(file_, arr, allow_pickle=False)
        else:
            save_array = lambda arr, file_: xp.save(file_, arr)
        serializers = OrderedDict((
            ('vectors', lambda p: save_array(self.data, p.open('wb'))),
            ('keys', lambda p: xp.save(p.open('wb'), self.keys))
        ))
        return util.to_disk(path, serializers, exclude)

    def from_disk(self, path, **exclude):
        def load_keys(path):
            if path.exists():
                self.keys = numpy.load(path)
                for i, key in enumerate(self.keys):
                    self.keys[i] = key
                    self.key2row[key] = i

        def load_vectors(path):
            xp = Model.ops.xp
            if path.exists():
                self.data = xp.load(path)

        serializers = OrderedDict((
            ('keys', load_keys),
            ('vectors', load_vectors),
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
            self.keys.resize((len(keys),))
            for i, key in enumerate(keys):
                self.keys[i] = key
                self.key2row[key] = i

        deserializers = OrderedDict((
            ('keys', lambda b: load_keys(msgpack.loads(b))),
            ('vectors', deserialize_weights)
        ))
        util.from_bytes(data, deserializers, exclude)
        return self
