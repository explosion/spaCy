cimport numpy as np
from libc.stdint cimport uint32_t, uint64_t
from cython.operator cimport dereference as deref
from libcpp.set cimport set as cppset
from murmurhash.mrmr cimport hash128_x64

import functools
import numpy
from typing import cast
import warnings
from enum import Enum
import srsly
from thinc.api import Ops, get_array_module, get_current_ops
from thinc.backends import get_array_ops
from thinc.types import Floats2d

from .strings cimport StringStore

from .strings import get_string_id
from .errors import Errors, Warnings
from . import util


def unpickle_vectors(bytes_data):
    return Vectors().from_bytes(bytes_data)


class Mode(str, Enum):
    default = "default"
    floret = "floret"

    @classmethod
    def values(cls):
        return list(cls.__members__.keys())


cdef class Vectors:
    """Store, save and load word vectors.

    Vectors data is kept in the vectors.data attribute, which should be an
    instance of numpy.ndarray (for CPU vectors) or cupy.ndarray
    (for GPU vectors).

    In the default mode, `vectors.key2row` is a dictionary mapping word hashes
    to rows in the vectors.data table. Multiple keys can be mapped to the same
    vector, and not all of the rows in the table need to be assigned - so
    len(list(vectors.keys())) may be greater or smaller than vectors.shape[0].

    In floret mode, the floret settings (minn, maxn, etc.) are used to
    calculate the vector from the rows corresponding to the key's ngrams.

    DOCS: https://spacy.io/api/vectors
    """
    cdef public object strings
    cdef public object name
    cdef readonly object mode
    cdef public object data
    cdef public object key2row
    cdef cppset[int] _unset
    cdef readonly uint32_t minn
    cdef readonly uint32_t maxn
    cdef readonly uint32_t hash_count
    cdef readonly uint32_t hash_seed
    cdef readonly unicode bow
    cdef readonly unicode eow

    def __init__(self, *, strings=None, shape=None, data=None, keys=None, name=None, mode=Mode.default, minn=0, maxn=0, hash_count=1, hash_seed=0, bow="<", eow=">"):
        """Create a new vector store.

        strings (StringStore): The string store.
        shape (tuple): Size of the table, as (# entries, # columns)
        data (numpy.ndarray or cupy.ndarray): The vector data.
        keys (iterable): A sequence of keys, aligned with the data.
        name (str): A name to identify the vectors table.
        mode (str): Vectors mode: "default" or "floret" (default: "default").
        minn (int): The floret char ngram minn (default: 0).
        maxn (int): The floret char ngram maxn (default: 0).
        hash_count (int): The floret hash count (1-4, default: 1).
        hash_seed (int): The floret hash seed (default: 0).
        bow (str): The floret BOW string (default: "<").
        eow (str): The floret EOW string (default: ">").

        DOCS: https://spacy.io/api/vectors#init
        """
        self.strings = strings
        if self.strings is None:
            self.strings = StringStore()
        self.name = name
        if mode not in Mode.values():
            raise ValueError(
                Errors.E202.format(
                    name="vectors",
                    mode=mode,
                    modes=str(Mode.values())
                )
            )
        self.mode = Mode(mode).value
        self.key2row = {}
        self.minn = minn
        self.maxn = maxn
        self.hash_count = hash_count
        self.hash_seed = hash_seed
        self.bow = bow
        self.eow = eow
        if self.mode == Mode.default:
            if data is None:
                if shape is None:
                    shape = (0,0)
                ops = get_current_ops()
                data = ops.xp.zeros(shape, dtype="f")
                self._unset = cppset[int]({i for i in range(data.shape[0])})
            else:
                self._unset = cppset[int]()
            self.data = data
            if keys is not None:
                for i, key in enumerate(keys):
                    self.add(key, row=i)
        elif self.mode == Mode.floret:
            if maxn < minn:
                raise ValueError(Errors.E863)
            if hash_count < 1 or hash_count >= 5:
                raise ValueError(Errors.E862)
            if data is None:
                raise ValueError(Errors.E864)
            if keys is not None:
                raise ValueError(Errors.E861)
            self.data = data
            self._unset = cppset[int]()

    @property
    def shape(self):
        """Get `(rows, dims)` tuples of number of rows and number of dimensions
        in the vector table.

        RETURNS (tuple): A `(rows, dims)` pair.

        DOCS: https://spacy.io/api/vectors#shape
        """
        return self.data.shape

    @property
    def size(self):
        """The vector size i,e. rows * dims.

        RETURNS (int): The vector size.

        DOCS: https://spacy.io/api/vectors#size
        """
        return self.data.size

    @property
    def is_full(self):
        """Whether the vectors table is full.

        RETURNS (bool): `True` if no slots are available for new keys.

        DOCS: https://spacy.io/api/vectors#is_full
        """
        if self.mode == Mode.floret:
            return True
        return self._unset.size() == 0

    @property
    def n_keys(self):
        """Get the number of keys in the table. Note that this is the number
        of all keys, not just unique vectors.

        RETURNS (int): The number of keys in the table for default vectors.
        For floret vectors, return -1.

        DOCS: https://spacy.io/api/vectors#n_keys
        """
        return len(self.key2row)

    def __reduce__(self):
        return (unpickle_vectors, (self.to_bytes(),))

    def __getitem__(self, key):
        """Get a vector by key. If the key is not found, a KeyError is raised.

        key (str/int): The key to get the vector for.
        RETURNS (ndarray): The vector for the key.

        DOCS: https://spacy.io/api/vectors#getitem
        """
        if self.mode == Mode.default:
            i = self.key2row.get(get_string_id(key), None)
            if i is None:
                raise KeyError(Errors.E058.format(key=key))
            else:
                return self.data[i]
        elif self.mode == Mode.floret:
            return self.get_batch([key])[0]
        raise KeyError(Errors.E058.format(key=key))

    def __setitem__(self, key, vector):
        """Set a vector for the given key.

        key (str/int): The key to set the vector for.
        vector (ndarray): The vector to set.

        DOCS: https://spacy.io/api/vectors#setitem
        """
        if self.mode == Mode.floret:
            warnings.warn(Warnings.W115.format(method="Vectors.__setitem__"))
            return
        key = get_string_id(key)
        i = self.key2row[key]
        self.data[i] = vector
        if self._unset.count(i):
            self._unset.erase(self._unset.find(i))

    def __iter__(self):
        """Iterate over the keys in the table.

        YIELDS (int): A key in the table.

        DOCS: https://spacy.io/api/vectors#iter
        """
        yield from self.key2row

    def __len__(self):
        """Return the number of vectors in the table.

        RETURNS (int): The number of vectors in the data.

        DOCS: https://spacy.io/api/vectors#len
        """
        return self.data.shape[0]

    def __contains__(self, key):
        """Check whether a key has been mapped to a vector entry in the table.

        key (int): The key to check.
        RETURNS (bool): Whether the key has a vector entry.

        DOCS: https://spacy.io/api/vectors#contains
        """
        if self.mode == Mode.floret:
            return True
        else:
            return key in self.key2row

    def resize(self, shape, inplace=False):
        """Resize the underlying vectors array. If inplace=True, the memory
        is reallocated. This may cause other references to the data to become
        invalid, so only use inplace=True if you're sure that's what you want.

        If the number of vectors is reduced, keys mapped to rows that have been
        deleted are removed. These removed items are returned as a list of
        `(key, row)` tuples.

        shape (tuple): A `(rows, dims)` tuple.
        inplace (bool): Reallocate the memory.
        RETURNS (list): The removed items as a list of `(key, row)` tuples.

        DOCS: https://spacy.io/api/vectors#resize
        """
        if self.mode == Mode.floret:
            warnings.warn(Warnings.W115.format(method="Vectors.resize"))
            return -1
        xp = get_array_module(self.data)
        if inplace:
            if shape[1] != self.data.shape[1]:
                raise ValueError(Errors.E193.format(new_dim=shape[1], curr_dim=self.data.shape[1]))
            if xp == numpy:
                self.data.resize(shape, refcheck=False)
            else:
                raise ValueError(Errors.E192)
        else:
            resized_array = xp.zeros(shape, dtype=self.data.dtype)
            copy_shape = (min(shape[0], self.data.shape[0]), min(shape[1], self.data.shape[1]))
            resized_array[:copy_shape[0], :copy_shape[1]] = self.data[:copy_shape[0], :copy_shape[1]]
            self.data = resized_array
        self._sync_unset()
        removed_items = []
        for key, row in self.key2row.copy().items():
            if row >= shape[0]:
                self.key2row.pop(key)
                removed_items.append((key, row))
        return removed_items

    def keys(self):
        """RETURNS (iterable): A sequence of keys in the table."""
        return self.key2row.keys()

    def values(self):
        """Iterate over vectors that have been assigned to at least one key.

        Note that some vectors may be unassigned, so the number of vectors
        returned may be less than the length of the vectors table.

        YIELDS (ndarray): A vector in the table.

        DOCS: https://spacy.io/api/vectors#values
        """
        for row, vector in enumerate(range(self.data.shape[0])):
            if not self._unset.count(row):
                yield vector

    def items(self):
        """Iterate over `(key, vector)` pairs.

        YIELDS (tuple): A key/vector pair.

        DOCS: https://spacy.io/api/vectors#items
        """
        for key, row in self.key2row.items():
            yield key, self.data[row]

    def find(self, *, key=None, keys=None, row=None, rows=None):
        """Look up one or more keys by row, or vice versa.

        key (Union[int, str]): Find the row that the given key points to.
            Returns int, -1 if missing.
        keys (Iterable[Union[int, str]]): Find rows that the keys point to.
            Returns ndarray.
        row (int): Find the first key that points to the row.
            Returns int.
        rows (Iterable[int]): Find the keys that point to the rows.
            Returns ndarray.
        RETURNS: The requested key, keys, row or rows.
        """
        if self.mode == Mode.floret:
            raise ValueError(
                Errors.E858.format(
                    mode=self.mode,
                    alternative="Use Vectors[key] instead.",
                )
            )
        if sum(arg is None for arg in (key, keys, row, rows)) != 3:
            bad_kwargs = {"key": key, "keys": keys, "row": row, "rows": rows}
            raise ValueError(Errors.E059.format(kwargs=bad_kwargs))
        xp = get_array_module(self.data)
        if key is not None:
            key = get_string_id(key)
            return self.key2row.get(key, -1)
        elif keys is not None:
            keys = [get_string_id(key) for key in keys]
            rows = [self.key2row.get(key, -1.) for key in keys]
            return xp.asarray(rows, dtype="i")
        else:
            row2key = {row: key for key, row in self.key2row.items()}
            if row is not None:
                return row2key[row]
            else:
                results = [row2key[row] for row in rows]
                return xp.asarray(results, dtype="uint64")

    def _get_ngram_hashes(self, unicode s):
        """Calculate up to 4 32-bit hash values with MurmurHash3_x64_128 using
        the floret hash settings.
        key (str): The string key.
        RETURNS: A list of the integer hashes.
        """
        # MurmurHash3_x64_128 returns an array of 2 uint64_t values.
        cdef uint64_t[2] out
        chars = s.encode("utf8")
        cdef char* utf8_string = chars
        hash128_x64(utf8_string, len(chars), self.hash_seed, &out)
        rows = [
            out[0] & 0xffffffffu,
            out[0] >> 32,
            out[1] & 0xffffffffu,
            out[1] >> 32,
        ]
        return rows[:min(self.hash_count, 4)]

    def _get_ngrams(self, unicode key):
        """Get all padded ngram strings using the ngram settings.
        key (str): The string key.
        RETURNS: A list of the ngram strings for the padded key.
        """
        key = self.bow + key + self.eow
        ngrams = [key] + [
            key[start:start+ngram_size]
            for ngram_size in range(self.minn, self.maxn + 1)
            for start in range(0, len(key) - ngram_size + 1)
        ]
        return ngrams

    def get_batch(self, keys):
        """Get the vectors for the provided keys efficiently as a batch.
        keys (Iterable[Union[int, str]]): The keys.
        RETURNS: The requested vectors from the vector table.
        """
        ops = get_array_ops(self.data)
        if self.mode == Mode.default:
            rows = self.find(keys=keys)
            vecs = self.data[rows]
        elif self.mode == Mode.floret:
            keys = [self.strings.as_string(key) for key in keys]
            if sum(len(key) for key in keys) == 0:
                return ops.xp.zeros((len(keys), self.data.shape[1]))
            unique_keys = tuple(set(keys))
            row_index = {key: i for i, key in enumerate(unique_keys)}
            rows = [row_index[key] for key in keys]
            indices = []
            lengths = []
            for key in unique_keys:
                if key == "":
                    ngram_rows = []
                else:
                    ngram_rows = [
                        h % self.data.shape[0]
                        for ngram in self._get_ngrams(key)
                        for h in self._get_ngram_hashes(ngram)
                    ]
                indices.extend(ngram_rows)
                lengths.append(len(ngram_rows))
            indices = ops.asarray(indices, dtype="int32")
            lengths = ops.asarray(lengths, dtype="int32")
            vecs = ops.reduce_mean(cast(Floats2d, self.data[indices]), lengths)
            vecs = vecs[rows]
        return ops.as_contig(vecs)

    def add(self, key, *, vector=None, row=None):
        """Add a key to the table. Keys can be mapped to an existing vector
        by setting `row`, or a new vector can be added.

        key (int): The key to add.
        vector (ndarray / None): A vector to add for the key.
        row (int / None): The row number of a vector to map the key to.
        RETURNS (int): The row the vector was added to.

        DOCS: https://spacy.io/api/vectors#add
        """
        if self.mode == Mode.floret:
            warnings.warn(Warnings.W115.format(method="Vectors.add"))
            return -1
        # use int for all keys and rows in key2row for more efficient access
        # and serialization
        key = int(get_string_id(key))
        if row is not None:
            row = int(row)
        if row is None and key in self.key2row:
            row = self.key2row[key]
        elif row is None:
            if self.is_full:
                raise ValueError(Errors.E060.format(rows=self.data.shape[0],
                                                    cols=self.data.shape[1]))
            row = deref(self._unset.begin())
        if row < self.data.shape[0]:
            self.key2row[key] = row
        else:
            raise ValueError(Errors.E197.format(row=row, key=key))
        if vector is not None:
            xp = get_array_module(self.data)
            vector = xp.asarray(vector)
            self.data[row] = vector
        if self._unset.count(row):
            self._unset.erase(self._unset.find(row))
        return row

    def most_similar(self, queries, *, batch_size=1024, n=1, sort=True):
        """For each of the given vectors, find the n most similar entries
        to it, by cosine.

        Queries are by vector. Results are returned as a `(keys, best_rows,
        scores)` tuple. If `queries` is large, the calculations are performed in
        chunks, to avoid consuming too much memory. You can set the `batch_size`
        to control the size/space trade-off during the calculations.

        queries (ndarray): An array with one or more vectors.
        batch_size (int): The batch size to use.
        n (int): The number of entries to return for each query.
        sort (bool): Whether to sort the n entries returned by score.
        RETURNS (tuple): The most similar entries as a `(keys, best_rows, scores)`
            tuple.
        """
        if self.mode == Mode.floret:
            raise ValueError(Errors.E858.format(
                mode=self.mode,
                alternative="",
            ))
        xp = get_array_module(self.data)
        filled = sorted(list({row for row in self.key2row.values()}))
        if len(filled) < n:
            raise ValueError(Errors.E198.format(n=n, n_rows=len(filled)))
        filled = xp.asarray(filled)

        norms = xp.linalg.norm(self.data[filled], axis=1, keepdims=True)
        norms[norms == 0] = 1
        vectors = self.data[filled] / norms

        best_rows = xp.zeros((queries.shape[0], n), dtype='i')
        scores = xp.zeros((queries.shape[0], n), dtype='f')
        # Work in batches, to avoid memory problems.
        for i in range(0, queries.shape[0], batch_size):
            batch = queries[i : i+batch_size]
            batch_norms = xp.linalg.norm(batch, axis=1, keepdims=True)
            batch_norms[batch_norms == 0] = 1
            batch /= batch_norms
            # batch   e.g. (1024, 300)
            # vectors e.g. (10000, 300)
            # sims    e.g. (1024, 10000)
            sims = xp.dot(batch, vectors.T)
            best_rows[i:i+batch_size] = xp.argpartition(sims, -n, axis=1)[:,-n:]
            scores[i:i+batch_size] = xp.partition(sims, -n, axis=1)[:,-n:]

            if sort and n >= 2:
                sorted_index = xp.arange(scores.shape[0])[:,None][i:i+batch_size],xp.argsort(scores[i:i+batch_size], axis=1)[:,::-1]
                scores[i:i+batch_size] = scores[sorted_index]
                best_rows[i:i+batch_size] = best_rows[sorted_index]

        for i, j in numpy.ndindex(best_rows.shape):
            best_rows[i, j] = filled[best_rows[i, j]]
        # Round values really close to 1 or -1
        scores = xp.around(scores, decimals=4, out=scores)
        # Account for numerical error we want to return in range -1, 1
        scores = xp.clip(scores, a_min=-1, a_max=1, out=scores)
        row2key = {row: key for key, row in self.key2row.items()}

        numpy_rows = get_current_ops().to_numpy(best_rows)
        keys = xp.asarray(
            [[row2key[row] for row in numpy_rows[i] if row in row2key]
                    for i in range(len(queries)) ], dtype="uint64")
        return (keys, best_rows, scores)

    def to_ops(self, ops: Ops):
        self.data = ops.asarray(self.data)

    def _get_cfg(self):
        if self.mode == Mode.default:
            return {
                "mode": Mode(self.mode).value,
            }
        elif self.mode == Mode.floret:
            return {
                "mode": Mode(self.mode).value,
                "minn": self.minn,
                "maxn": self.maxn,
                "hash_count": self.hash_count,
                "hash_seed": self.hash_seed,
                "bow": self.bow,
                "eow": self.eow,
            }

    def _set_cfg(self, cfg):
        self.mode = Mode(cfg.get("mode", Mode.default)).value
        self.minn = cfg.get("minn", 0)
        self.maxn = cfg.get("maxn", 0)
        self.hash_count = cfg.get("hash_count", 0)
        self.hash_seed = cfg.get("hash_seed", 0)
        self.bow = cfg.get("bow", "<")
        self.eow = cfg.get("eow", ">")

    def to_disk(self, path, *, exclude=tuple()):
        """Save the current state to a directory.

        path (str / Path): A path to a directory, which will be created if
            it doesn't exists.

        DOCS: https://spacy.io/api/vectors#to_disk
        """
        xp = get_array_module(self.data)
        if xp is numpy:
            save_array = lambda arr, file_: xp.save(file_, arr, allow_pickle=False)
        else:
            save_array = lambda arr, file_: xp.save(file_, arr)

        def save_vectors(path):
            # the source of numpy.save indicates that the file object is closed after use.
            # but it seems that somehow this does not happen, as ResourceWarnings are raised here.
            # in order to not rely on this, wrap in context manager.
            with path.open("wb") as _file:
                save_array(self.data, _file)

        serializers = {
            "strings": lambda p: self.strings.to_disk(p.with_suffix(".json")),
            "vectors": lambda p: save_vectors(p),
            "key2row": lambda p: srsly.write_msgpack(p, self.key2row),
            "vectors.cfg": lambda p: srsly.write_json(p, self._get_cfg()),
        }
        return util.to_disk(path, serializers, exclude)

    def from_disk(self, path, *, exclude=tuple()):
        """Loads state from a directory. Modifies the object in place and
        returns it.

        path (str / Path): Directory path, string or Path-like object.
        RETURNS (Vectors): The modified object.

        DOCS: https://spacy.io/api/vectors#from_disk
        """
        def load_key2row(path):
            if path.exists():
                self.key2row = srsly.read_msgpack(path)
            for key, row in self.key2row.items():
                if self._unset.count(row):
                    self._unset.erase(self._unset.find(row))

        def load_keys(path):
            if path.exists():
                keys = numpy.load(str(path))
                for i, key in enumerate(keys):
                    self.add(key, row=i)

        def load_vectors(path):
            ops = get_current_ops()
            if path.exists():
                self.data = ops.xp.load(str(path))

        def load_settings(path):
            if path.exists():
                self._set_cfg(srsly.read_json(path))

        serializers = {
            "strings": lambda p: self.strings.from_disk(p.with_suffix(".json")),
            "vectors": load_vectors,
            "keys": load_keys,
            "key2row": load_key2row,
            "vectors.cfg": load_settings,
        }

        util.from_disk(path, serializers, exclude)
        self._sync_unset()
        return self

    def to_bytes(self, *, exclude=tuple()):
        """Serialize the current state to a binary string.

        exclude (list): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized form of the `Vectors` object.

        DOCS: https://spacy.io/api/vectors#to_bytes
        """
        def serialize_weights():
            if hasattr(self.data, "to_bytes"):
                return self.data.to_bytes()
            else:
                return srsly.msgpack_dumps(self.data)

        serializers = {
            "strings": lambda: self.strings.to_bytes(),
            "key2row": lambda: srsly.msgpack_dumps(self.key2row),
            "vectors": serialize_weights,
            "vectors.cfg": lambda: srsly.json_dumps(self._get_cfg()),
        }
        return util.to_bytes(serializers, exclude)

    def from_bytes(self, data, *, exclude=tuple()):
        """Load state from a binary string.

        data (bytes): The data to load from.
        exclude (list): String names of serialization fields to exclude.
        RETURNS (Vectors): The `Vectors` object.

        DOCS: https://spacy.io/api/vectors#from_bytes
        """
        def deserialize_weights(b):
            if hasattr(self.data, "from_bytes"):
                self.data.from_bytes()
            else:
                xp = get_array_module(self.data)
                self.data = xp.asarray(srsly.msgpack_loads(b))

        deserializers = {
            "strings": lambda b: self.strings.from_bytes(b),
            "key2row": lambda b: self.key2row.update(srsly.msgpack_loads(b)),
            "vectors": deserialize_weights,
            "vectors.cfg": lambda b: self._set_cfg(srsly.json_loads(b))
        }
        util.from_bytes(data, deserializers, exclude)
        self._sync_unset()
        return self

    def clear(self):
        """Clear all entries in the vector table.

        DOCS: https://spacy.io/api/vectors#clear
        """
        if self.mode == Mode.floret:
            raise ValueError(Errors.E859)
        self.key2row = {}
        self._sync_unset()

    def _sync_unset(self):
        filled = {row for row in self.key2row.values()}
        self._unset = cppset[int]({row for row in range(self.data.shape[0]) if row not in filled})
