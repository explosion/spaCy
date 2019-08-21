---
title: Vectors
teaser: Store, save and load word vectors
tag: class
source: spacy/vectors.pyx
new: 2
---

Vectors data is kept in the `Vectors.data` attribute, which should be an
instance of `numpy.ndarray` (for CPU vectors) or `cupy.ndarray` (for GPU
vectors). Multiple keys can be mapped to the same vector, and not all of the
rows in the table need to be assigned – so `vectors.n_keys` may be greater or
smaller than `vectors.shape[0]`.

## Vectors.\_\_init\_\_ {#init tag="method"}

Create a new vector store. You can set the vector values and keys directly on
initialization, or supply a `shape` keyword argument to create an empty table
you can add vectors to later.

> #### Example
>
> ```python
> from spacy.vectors import Vectors
>
> empty_vectors = Vectors(shape=(10000, 300))
>
> data = numpy.zeros((3, 300), dtype='f')
> keys = [u"cat", u"dog", u"rat"]
> vectors = Vectors(data=data, keys=keys)
> ```

| Name        | Type                               | Description                                                                                                                                                        |
| ----------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `data`      | `ndarray[ndim=1, dtype='float32']` | The vector data.                                                                                                                                                   |
| `keys`      | iterable                           | A sequence of keys aligned with the data.                                                                                                                          |
| `shape`     | tuple                              | Size of the table as `(n_entries, n_columns)`, the number of entries and number of columns. Not required if you're initializing the object with `data` and `keys`. |
| **RETURNS** | `Vectors`                          | The newly created object.                                                                                                                                          |

## Vectors.\_\_getitem\_\_ {#getitem tag="method"}

Get a vector by key. If the key is not found in the table, a `KeyError` is
raised.

> #### Example
>
> ```python
> cat_id = nlp.vocab.strings[u"cat"]
> cat_vector = nlp.vocab.vectors[cat_id]
> assert cat_vector == nlp.vocab[u"cat"].vector
> ```

| Name    | Type                               | Description                    |
| ------- | ---------------------------------- | ------------------------------ |
| `key`   | int                                | The key to get the vector for. |
| returns | `ndarray[ndim=1, dtype='float32']` | The vector for the key.        |

## Vectors.\_\_setitem\_\_ {#setitem tag="method"}

Set a vector for the given key.

> #### Example
>
> ```python
> cat_id = nlp.vocab.strings[u"cat"]
> vector = numpy.random.uniform(-1, 1, (300,))
> nlp.vocab.vectors[cat_id] = vector
> ```

| Name     | Type                               | Description                    |
| -------- | ---------------------------------- | ------------------------------ |
| `key`    | int                                | The key to set the vector for. |
| `vector` | `ndarray[ndim=1, dtype='float32']` | The vector to set.             |

## Vectors.\_\_iter\_\_ {#iter tag="method"}

Iterate over the keys in the table.

> #### Example
>
> ```python
> for key in nlp.vocab.vectors:
>    print(key, nlp.vocab.strings[key])
> ```

| Name       | Type | Description         |
| ---------- | ---- | ------------------- |
| **YIELDS** | int  | A key in the table. |

## Vectors.\_\_len\_\_ {#len tag="method"}

Return the number of vectors in the table.

> #### Example
>
> ```python
> vectors = Vectors(shape=(3, 300))
> assert len(vectors) == 3
> ```

| Name        | Type | Description                         |
| ----------- | ---- | ----------------------------------- |
| **RETURNS** | int  | The number of vectors in the table. |

## Vectors.\_\_contains\_\_ {#contains tag="method"}

Check whether a key has been mapped to a vector entry in the table.

> #### Example
>
> ```python
> cat_id = nlp.vocab.strings[u"cat"]
> nlp.vectors.add(cat_id, numpy.random.uniform(-1, 1, (300,)))
> assert cat_id in vectors
> ```

| Name        | Type | Description                         |
| ----------- | ---- | ----------------------------------- |
| `key`       | int  | The key to check.                   |
| **RETURNS** | bool | Whether the key has a vector entry. |

## Vectors.add {#add tag="method"}

Add a key to the table, optionally setting a vector value as well. Keys can be
mapped to an existing vector by setting `row`, or a new vector can be added.
When adding unicode keys, keep in mind that the `Vectors` class itself has no
[`StringStore`](/api/stringstore), so you have to store the hash-to-string
mapping separately. If you need to manage the strings, you should use the
`Vectors` via the [`Vocab`](/api/vocab) class, e.g. `vocab.vectors`.

> #### Example
>
> ```python
> vector = numpy.random.uniform(-1, 1, (300,))
> cat_id = nlp.vocab.strings[u"cat"]
> nlp.vocab.vectors.add(cat_id, vector=vector)
> nlp.vocab.vectors.add(u"dog", row=0)
> ```

| Name        | Type                               | Description                                           |
| ----------- | ---------------------------------- | ----------------------------------------------------- |
| `key`       | unicode / int                      | The key to add.                                       |
| `vector`    | `ndarray[ndim=1, dtype='float32']` | An optional vector to add for the key.                |
| `row`       | int                                | An optional row number of a vector to map the key to. |
| **RETURNS** | int                                | The row the vector was added to.                      |

## Vectors.resize {#resize tag="method"}

Resize the underlying vectors array. If `inplace=True`, the memory is
reallocated. This may cause other references to the data to become invalid, so
only use `inplace=True` if you're sure that's what you want. If the number of
vectors is reduced, keys mapped to rows that have been deleted are removed.
These removed items are returned as a list of `(key, row)` tuples.

> #### Example
>
> ```python
> removed = nlp.vocab.vectors.resize((10000, 300))
> ```

| Name        | Type  | Description                                                          |
| ----------- | ----- | -------------------------------------------------------------------- |
| `shape`     | tuple | A `(rows, dims)` tuple describing the number of rows and dimensions. |
| `inplace`   | bool  | Reallocate the memory.                                               |
| **RETURNS** | list  | The removed items as a list of `(key, row)` tuples.                  |

## Vectors.keys {#keys tag="method"}

A sequence of the keys in the table.

> #### Example
>
> ```python
> for key in nlp.vocab.vectors.keys():
>     print(key, nlp.vocab.strings[key])
> ```

| Name        | Type     | Description |
| ----------- | -------- | ----------- |
| **RETURNS** | iterable | The keys.   |

## Vectors.values {#values tag="method"}

Iterate over vectors that have been assigned to at least one key. Note that some
vectors may be unassigned, so the number of vectors returned may be less than
the length of the vectors table.

> #### Example
>
> ```python
> for vector in nlp.vocab.vectors.values():
>     print(vector)
> ```

| Name       | Type                               | Description            |
| ---------- | ---------------------------------- | ---------------------- |
| **YIELDS** | `ndarray[ndim=1, dtype='float32']` | A vector in the table. |

## Vectors.items {#items tag="method"}

Iterate over `(key, vector)` pairs, in order.

> #### Example
>
> ```python
> for key, vector in nlp.vocab.vectors.items():
>    print(key, nlp.vocab.strings[key], vector)
> ```

| Name       | Type  | Description                      |
| ---------- | ----- | -------------------------------- |
| **YIELDS** | tuple | `(key, vector)` pairs, in order. |

## Vectors.find (#find tag="method")

Look up one or more keys by row, or vice versa.

> #### Example
>
> ```python
> row = nlp.vocab.vectors.find(key=u"cat")
> rows = nlp.vocab.vectors.find(keys=[u"cat", u"dog"])
> key = nlp.vocab.vectors.find(row=256)
> keys = nlp.vocab.vectors.find(rows=[18, 256, 985])
> ```

| Name        | Type                                  | Description                                                              |
| ----------- | ------------------------------------- | ------------------------------------------------------------------------ |
| `key`       | unicode / int                         | Find the row that the given key points to. Returns int, `-1` if missing. |
| `keys`      | iterable                              | Find rows that the keys point to. Returns `ndarray`.                     |
| `row`       | int                                   | Find the first key that points to the row. Returns int.                  |
| `rows`      | iterable                              | Find the keys that point to the rows. Returns ndarray.                   |
| **RETURNS** | The requested key, keys, row or rows. |

## Vectors.shape {#shape tag="property"}

Get `(rows, dims)` tuples of number of rows and number of dimensions in the
vector table.

> #### Example
>
> ```python
> vectors = Vectors(shape(1, 300))
> vectors.add(u"cat", numpy.random.uniform(-1, 1, (300,)))
> rows, dims = vectors.shape
> assert rows == 1
> assert dims == 300
> ```

| Name        | Type  | Description            |
| ----------- | ----- | ---------------------- |
| **RETURNS** | tuple | A `(rows, dims)` pair. |

## Vectors.size {#size tag="property"}

The vector size, i.e. `rows * dims`.

> #### Example
>
> ```python
> vectors = Vectors(shape=(500, 300))
> assert vectors.size == 150000
> ```

| Name        | Type | Description      |
| ----------- | ---- | ---------------- |
| **RETURNS** | int  | The vector size. |

## Vectors.is_full {#is_full tag="property"}

Whether the vectors table is full and has no slots are available for new keys.
If a table is full, it can be resized using
[`Vectors.resize`](/api/vectors#resize).

> #### Example
>
> ```python
> vectors = Vectors(shape=(1, 300))
> vectors.add(u"cat", numpy.random.uniform(-1, 1, (300,)))
> assert vectors.is_full
> ```

| Name        | Type | Description                        |
| ----------- | ---- | ---------------------------------- |
| **RETURNS** | bool | Whether the vectors table is full. |

## Vectors.n_keys {#n_keys tag="property"}

Get the number of keys in the table. Note that this is the number of _all_ keys,
not just unique vectors. If several keys are mapped are mapped to the same
vectors, they will be counted individually.

> #### Example
>
> ```python
> vectors = Vectors(shape=(10, 300))
> assert len(vectors) == 10
> assert vectors.n_keys == 0
> ```

| Name        | Type | Description                          |
| ----------- | ---- | ------------------------------------ |
| **RETURNS** | int  | The number of all keys in the table. |

## Vectors.from_glove {#from_glove tag="method"}

Load [GloVe](https://nlp.stanford.edu/projects/glove/) vectors from a directory.
Assumes binary format, that the vocab is in a `vocab.txt`, and that vectors are
named `vectors.{size}.[fd.bin]`, e.g. `vectors.128.f.bin` for 128d float32
vectors, `vectors.300.d.bin` for 300d float64 (double) vectors, etc. By default
GloVe outputs 64-bit vectors.

> #### Example
>
> ```python
> vectors = Vectors()
> vectors.from_glove("/path/to/glove_vectors")
> ```

| Name   | Type             | Description                              |
| ------ | ---------------- | ---------------------------------------- |
| `path` | unicode / `Path` | The path to load the GloVe vectors from. |

## Vectors.to_disk {#to_disk tag="method"}

Save the current state to a directory.

> #### Example
>
> ```python
> vectors.to_disk("/path/to/vectors")
>
> ```

| Name   | Type             | Description                                                                                                           |
| ------ | ---------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path` | unicode / `Path` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |

## Vectors.from_disk {#from_disk tag="method"}

Loads state from a directory. Modifies the object in place and returns it.

> #### Example
>
> ```python
> vectors = Vectors(StringStore())
> vectors.from_disk("/path/to/vectors")
> ```

| Name        | Type             | Description                                                                |
| ----------- | ---------------- | -------------------------------------------------------------------------- |
| `path`      | unicode / `Path` | A path to a directory. Paths may be either strings or `Path`-like objects. |
| **RETURNS** | `Vectors`        | The modified `Vectors` object.                                             |

## Vectors.to_bytes {#to_bytes tag="method"}

Serialize the current state to a binary string.

> #### Example
>
> ```python
> vectors_bytes = vectors.to_bytes()
> ```

| Name        | Type  | Description                                  |
| ----------- | ----- | -------------------------------------------- |
| **RETURNS** | bytes | The serialized form of the `Vectors` object. |

## Vectors.from_bytes {#from_bytes tag="method"}

Load state from a binary string.

> #### Example
>
> ```python
> fron spacy.vectors import Vectors
> vectors_bytes = vectors.to_bytes()
> new_vectors = Vectors(StringStore())
> new_vectors.from_bytes(vectors_bytes)
> ```

| Name        | Type      | Description            |
| ----------- | --------- | ---------------------- |
| `data`      | bytes     | The data to load from. |
| **RETURNS** | `Vectors` | The `Vectors` object.  |

## Attributes {#attributes}

| Name      | Type                               | Description                                                                     |
| --------- | ---------------------------------- | ------------------------------------------------------------------------------- |
| `data`    | `ndarray[ndim=1, dtype='float32']` | Stored vectors data. `numpy` is used for CPU vectors, `cupy` for GPU vectors.   |
| `key2row` | dict                               | Dictionary mapping word hashes to rows in the `Vectors.data` table.             |
| `keys`    | `ndarray[ndim=1, dtype='float32']` | Array keeping the keys in order, such that `keys[vectors.key2row[key]] == key`. |
