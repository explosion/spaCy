# coding: utf8
from __future__ import unicode_literals

import numpy
from collections import OrderedDict
import msgpack
import msgpack_numpy
msgpack_numpy.patch()
cimport numpy as np
from thinc.neural.util import get_array_module
from thinc.neural._classes.model import Model

from .strings cimport StringStore
from .compat import basestring_, path2str
from . import util


cdef class Vectors:
    """Store, save and load word vectors.

    Vectors data is kept in the vectors.data attribute, which should be an
    instance of numpy.ndarray (for CPU vectors) or cupy.ndarray
    (for GPU vectors). `vectors.key2row` is a dictionary mapping word hashes to
    rows in the vectors.data table.
    
    Multiple keys can be mapped to the same vector, so len(keys) may be greater
    (but not smaller) than data.shape[0].
    """
    cdef public object data
    cdef readonly StringStore strings
    cdef public object key2row
    cdef public object keys
    cdef public int _i_key
    cdef public int _i_vec

    def __init__(self, strings, width=0, data=None):
        """Create a new vector store. To keep the vector table empty, pass
        `width=0`. You can also create the vector table and add vectors one by
        one, or set the vector values directly on initialisation.

        strings (StringStore or list): List of strings or StringStore that maps
            strings to hash values, and vice versa.
        width (int): Number of dimensions.
        data (numpy.ndarray): The vector data.
        RETURNS (Vectors): The newly created object.
        """
        if isinstance(strings, StringStore):
            self.strings = strings
        else:
            self.strings = StringStore()
            for string in strings:
                self.strings.add(string)
        if data is not None:
            self.data = numpy.asarray(data, dtype='f')
        else:
            self.data = numpy.zeros((len(self.strings), width), dtype='f')
        self._i_key = 0
        self._i_vec = 0
        self.key2row = {}
        self.keys = numpy.zeros((self.data.shape[0],), dtype='uint64')
        if data is not None:
            for i, string in enumerate(self.strings):
                if i >= self.data.shape[0]:
                    break
                self.add(self.strings[string], vector=self.data[i])

    def __reduce__(self):
        return (Vectors, (self.strings, self.data))

    def __getitem__(self, key):
        """Get a vector by key. If key is a string, it is hashed to an integer
        ID using the vectors.strings table. If the integer key is not found in
        the table, a KeyError is raised.

        key (unicode / int): The key to get the vector for.
        RETURNS (numpy.ndarray): The vector for the key.
        """
        if isinstance(key, basestring):
            key = self.strings[key]
        i = self.key2row[key]
        if i is None:
            raise KeyError(key)
        else:
            return self.data[i]

    def __setitem__(self, key, vector):
        """Set a vector for the given key. If key is a string, it is hashed
        to an integer ID using the vectors.strings table.

        key (unicode / int): The key to set the vector for.
        vector (numpy.ndarray): The vector to set.
        """
        if isinstance(key, basestring):
            key = self.strings.add(key)
        i = self.key2row[key]
        self.data[i] = vector

    def __iter__(self):
        """Yield vectors from the table.

        YIELDS (numpy.ndarray): A vector.
        """
        yield from self.data

    def __len__(self):
        """Return the number of vectors that have been assigned.

        RETURNS (int): The number of vectors in the data.
        """
        return self._i_vec

    def __contains__(self, key):
        """Check whether a key has a vector entry in the table.

        key (unicode / int): The key to check.
        RETURNS (bool): Whether the key has a vector entry.
        """
        if isinstance(key, basestring_):
            key = self.strings[key]
        return key in self.key2row

    def add(self, key, *, vector=None, row=None):
        """Add a key to the table. Keys can be mapped to an existing vector
        by setting `row`, or a new vector can be added.

        key (unicode / int): The key to add.
        vector (numpy.ndarray / None): A vector to add for the key.
        row (int / None): The row-number of a vector to map the key to.
        """
        if isinstance(key, basestring_):
            key = self.strings.add(key)
        if row is None and key in self.key2row:
            row = self.key2row[key]
        elif row is None:
            row = self._i_vec
            self._i_vec += 1
        if row >= self.data.shape[0]:
            self.data.resize((row*2, self.data.shape[1]))
        if key not in self.key2row:
            if self._i_key >= self.keys.shape[0]:
                self.keys.resize((self._i_key*2,))
                self.keys[self._i_key] = key
                self._i_key += 1

        self.key2row[key] = row
        if vector is not None:
            self.data[row] = vector
        return row

    def items(self):
        """Iterate over `(string key, vector)` pairs, in order.

        YIELDS (tuple): A key/vector pair.
        """
        for i, key in enumerate(self.keys):
            string = self.strings[key]
            row = self.key2row[key]
            yield string, self.data[row]

    @property
    def shape(self):
        """Get `(rows, dims)` tuples of number of rows and number of dimensions
        in the vector table.

        RETURNS (tuple): A `(rows, dims)` pair.
        """
        return self.data.shape

    def most_similar(self, key):
        # TODO: implement
        raise NotImplementedError

    def from_glove(self, path):
        """Load GloVe vectors from a directory. Assumes binary format,
        that the vocab is in a vocab.txt, and that vectors are named
        vectors.{size}.[fd].bin, e.g. vectors.128.f.bin for 128d float32
        vectors, vectors.300.d.bin for 300d float64 (double) vectors, etc.
        By default GloVe outputs 64-bit vectors.

        path (unicode / Path): The path to load the GloVe vectors from.
        """
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
        """Save the current state to a directory.

        path (unicode / Path): A path to a directory, which will be created if
            it doesn't exists. Either a string or a Path-like object.
        """
        xp = get_array_module(self.data)
        if xp is numpy:
            save_array = lambda arr, file_: xp.save(file_, arr,
                                                    allow_pickle=False)
        else:
            save_array = lambda arr, file_: xp.save(file_, arr)
        serializers = OrderedDict((
            ('vectors', lambda p: save_array(self.data, p.open('wb'))),
            ('keys', lambda p: xp.save(p.open('wb'), self.keys))
        ))
        return util.to_disk(path, serializers, exclude)

    def from_disk(self, path, **exclude):
        """Loads state from a directory. Modifies the object in place and
        returns it.

        path (unicode / Path): Directory path, string or Path-like object.
        RETURNS (Vectors): The modified object.
        """
        def load_keys(path):
            if path.exists():
                self.keys = numpy.load(path2str(path))
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
        """Serialize the current state to a binary string.

        **exclude: Named attributes to prevent from being serialized.
        RETURNS (bytes): The serialized form of the `Vectors` object.
        """
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
        """Load state from a binary string.

        data (bytes): The data to load from.
        **exclude: Named attributes to prevent from being loaded.
        RETURNS (Vectors): The `Vectors` object.
        """
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
