---
title: Vectors
teaser: Store, save and load word vectors
tag: class
source: spacy/vectors.pyx
new: 2
---

Vectors data is kept in the `Vectors.data` attribute, which should be an
instance of `numpy.ndarray` (for CPU vectors) or `cupy.ndarray` (for GPU
vectors).

As of spaCy v3.2, `Vectors` supports two types of vector tables:

- `default`: A standard vector table (as in spaCy v3.1 and earlier) where each
  key is mapped to one row in the vector table. Multiple keys can be mapped to
  the same vector, and not all of the rows in the table need to be assigned – so
  `vectors.n_keys` may be greater or smaller than `vectors.shape[0]`.
- `floret`: Only supports vectors trained with
  [floret](https://github.com/explosion/floret), an extended version of
  [fastText](https://fasttext.cc) that produces compact vector tables by
  combining fastText's subword ngrams with Bloom embeddings. The compact tables
  are similar to the [`HashEmbed`](https://thinc.ai/docs/api-layers#hashembed)
  embeddings already used in many spaCy components. Each word is represented as
  the sum of one or more rows as determined by the settings related to character
  ngrams and the hash table.

## Vectors.\_\_init\_\_ {#init tag="method"}

Create a new vector store. With the default mode, you can set the vector values
and keys directly on initialization, or supply a `shape` keyword argument to
create an empty table you can add vectors to later. In floret mode, the complete
vector data and settings must be provided on initialization and cannot be
modified later.

> #### Example
>
> ```python
> from spacy.vectors import Vectors
>
> empty_vectors = Vectors(shape=(10000, 300))
>
> data = numpy.zeros((3, 300), dtype='f')
> keys = ["cat", "dog", "rat"]
> vectors = Vectors(data=data, keys=keys)
> ```

| Name                                      | Description                                                                                                                                                                            |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| _keyword-only_                            |                                                                                                                                                                                        |
| `strings`                                 | The string store. A new string store is created if one is not provided. Defaults to `None`. ~~Optional[StringStore]~~                                                                  |
| `shape`                                   | Size of the table as `(n_entries, n_columns)`, the number of entries and number of columns. Not required if you're initializing the object with `data` and `keys`. ~~Tuple[int, int]~~ |
| `data`                                    | The vector data. ~~numpy.ndarray[ndim=1, dtype=float32]~~                                                                                                                              |
| `keys`                                    | A sequence of keys aligned with the data. ~~Iterable[Union[str, int]]~~                                                                                                                |
| `name`                                    | A name to identify the vectors table. ~~str~~                                                                                                                                          |
| `mode` <Tag variant="new">3.2</Tag>       | Vectors mode: `"default"` or [`"floret"`](https://github.com/explosion/floret) (default: `"default"`). ~~str~~                                                                         |
| `minn` <Tag variant="new">3.2</Tag>       | The floret char ngram minn (default: `0`). ~~int~~                                                                                                                                     |
| `maxn` <Tag variant="new">3.2</Tag>       | The floret char ngram maxn (default: `0`). ~~int~~                                                                                                                                     |
| `hash_count` <Tag variant="new">3.2</Tag> | The floret hash count. Supported values: 1--4 (default: `1`). ~~int~~                                                                                                                  |
| `hash_seed` <Tag variant="new">3.2</Tag>  | The floret hash seed (default: `0`). ~~int~~                                                                                                                                           |
| `bow` <Tag variant="new">3.2</Tag>        | The floret BOW string (default: `"<"`). ~~str~~                                                                                                                                        |
| `eow` <Tag variant="new">3.2</Tag>        | The floret EOW string (default: `">"`). ~~str~~                                                                                                                                        |

## Vectors.\_\_getitem\_\_ {#getitem tag="method"}

Get a vector by key. If the key is not found in the table, a `KeyError` is
raised.

> #### Example
>
> ```python
> cat_id = nlp.vocab.strings["cat"]
> cat_vector = nlp.vocab.vectors[cat_id]
> assert cat_vector == nlp.vocab["cat"].vector
> ```

| Name        | Description                                                      |
| ----------- | ---------------------------------------------------------------- |
| `key`       | The key to get the vector for. ~~Union[int, str]~~               |
| **RETURNS** | The vector for the key. ~~numpy.ndarray[ndim=1, dtype=float32]~~ |

## Vectors.\_\_setitem\_\_ {#setitem tag="method"}

Set a vector for the given key. Not supported for `floret` mode.

> #### Example
>
> ```python
> cat_id = nlp.vocab.strings["cat"]
> vector = numpy.random.uniform(-1, 1, (300,))
> nlp.vocab.vectors[cat_id] = vector
> ```

| Name     | Description                                                 |
| -------- | ----------------------------------------------------------- |
| `key`    | The key to set the vector for. ~~int~~                      |
| `vector` | The vector to set. ~~numpy.ndarray[ndim=1, dtype=float32]~~ |

## Vectors.\_\_iter\_\_ {#iter tag="method"}

Iterate over the keys in the table. In `floret` mode, the keys table is not
used.

> #### Example
>
> ```python
> for key in nlp.vocab.vectors:
>    print(key, nlp.vocab.strings[key])
> ```

| Name       | Description                 |
| ---------- | --------------------------- |
| **YIELDS** | A key in the table. ~~int~~ |

## Vectors.\_\_len\_\_ {#len tag="method"}

Return the number of vectors in the table.

> #### Example
>
> ```python
> vectors = Vectors(shape=(3, 300))
> assert len(vectors) == 3
> ```

| Name        | Description                                 |
| ----------- | ------------------------------------------- |
| **RETURNS** | The number of vectors in the table. ~~int~~ |

## Vectors.\_\_contains\_\_ {#contains tag="method"}

Check whether a key has been mapped to a vector entry in the table. In `floret`
mode, returns `True` for all keys.

> #### Example
>
> ```python
> cat_id = nlp.vocab.strings["cat"]
> nlp.vocab.vectors.add(cat_id, numpy.random.uniform(-1, 1, (300,)))
> assert cat_id in vectors
> ```

| Name        | Description                                  |
| ----------- | -------------------------------------------- |
| `key`       | The key to check. ~~int~~                    |
| **RETURNS** | Whether the key has a vector entry. ~~bool~~ |

## Vectors.add {#add tag="method"}

Add a key to the table, optionally setting a vector value as well. Keys can be
mapped to an existing vector by setting `row`, or a new vector can be added. Not
supported for `floret` mode.

> #### Example
>
> ```python
> vector = numpy.random.uniform(-1, 1, (300,))
> cat_id = nlp.vocab.strings["cat"]
> nlp.vocab.vectors.add(cat_id, vector=vector)
> nlp.vocab.vectors.add("dog", row=0)
> ```

| Name           | Description                                                                     |
| -------------- | ------------------------------------------------------------------------------- |
| `key`          | The key to add. ~~Union[str, int]~~                                             |
| _keyword-only_ |                                                                                 |
| `vector`       | An optional vector to add for the key. ~~numpy.ndarray[ndim=1, dtype=float32]~~ |
| `row`          | An optional row number of a vector to map the key to. ~~int~~                   |
| **RETURNS**    | The row the vector was added to. ~~int~~                                        |

## Vectors.resize {#resize tag="method"}

Resize the underlying vectors array. If `inplace=True`, the memory is
reallocated. This may cause other references to the data to become invalid, so
only use `inplace=True` if you're sure that's what you want. If the number of
vectors is reduced, keys mapped to rows that have been deleted are removed.
These removed items are returned as a list of `(key, row)` tuples. Not supported
for `floret` mode.

> #### Example
>
> ```python
> removed = nlp.vocab.vectors.resize((10000, 300))
> ```

| Name        | Description                                                                              |
| ----------- | ---------------------------------------------------------------------------------------- |
| `shape`     | A `(rows, dims)` tuple describing the number of rows and dimensions. ~~Tuple[int, int]~~ |
| `inplace`   | Reallocate the memory. ~~bool~~                                                          |
| **RETURNS** | The removed items as a list of `(key, row)` tuples. ~~List[Tuple[int, int]]~~            |

## Vectors.keys {#keys tag="method"}

A sequence of the keys in the table. In `floret` mode, the keys table is not
used.

> #### Example
>
> ```python
> for key in nlp.vocab.vectors.keys():
>     print(key, nlp.vocab.strings[key])
> ```

| Name        | Description                 |
| ----------- | --------------------------- |
| **RETURNS** | The keys. ~~Iterable[int]~~ |

## Vectors.values {#values tag="method"}

Iterate over vectors that have been assigned to at least one key. Note that some
vectors may be unassigned, so the number of vectors returned may be less than
the length of the vectors table. In `floret` mode, the keys table is not used.

> #### Example
>
> ```python
> for vector in nlp.vocab.vectors.values():
>     print(vector)
> ```

| Name       | Description                                                     |
| ---------- | --------------------------------------------------------------- |
| **YIELDS** | A vector in the table. ~~numpy.ndarray[ndim=1, dtype=float32]~~ |

## Vectors.items {#items tag="method"}

Iterate over `(key, vector)` pairs, in order. In `floret` mode, the keys table
is empty.

> #### Example
>
> ```python
> for key, vector in nlp.vocab.vectors.items():
>    print(key, nlp.vocab.strings[key], vector)
> ```

| Name       | Description                                                                           |
| ---------- | ------------------------------------------------------------------------------------- |
| **YIELDS** | `(key, vector)` pairs, in order. ~~Tuple[int, numpy.ndarray[ndim=1, dtype=float32]]~~ |

## Vectors.find {#find tag="method"}

Look up one or more keys by row, or vice versa. Not supported for `floret` mode.

> #### Example
>
> ```python
> row = nlp.vocab.vectors.find(key="cat")
> rows = nlp.vocab.vectors.find(keys=["cat", "dog"])
> key = nlp.vocab.vectors.find(row=256)
> keys = nlp.vocab.vectors.find(rows=[18, 256, 985])
> ```

| Name           | Description                                                                                  |
| -------------- | -------------------------------------------------------------------------------------------- |
| _keyword-only_ |                                                                                              |
| `key`          | Find the row that the given key points to. Returns int, `-1` if missing. ~~Union[str, int]~~ |
| `keys`         | Find rows that the keys point to. Returns `numpy.ndarray`. ~~Iterable[Union[str, int]]~~     |
| `row`          | Find the first key that points to the row. Returns integer. ~~int~~                          |
| `rows`         | Find the keys that point to the rows. Returns `numpy.ndarray`. ~~Iterable[int]~~             |
| **RETURNS**    | The requested key, keys, row or rows. ~~Union[int, numpy.ndarray[ndim=1, dtype=float32]]~~   |

## Vectors.shape {#shape tag="property"}

Get `(rows, dims)` tuples of number of rows and number of dimensions in the
vector table.

> #### Example
>
> ```python
> vectors = Vectors(shape(1, 300))
> vectors.add("cat", numpy.random.uniform(-1, 1, (300,)))
> rows, dims = vectors.shape
> assert rows == 1
> assert dims == 300
> ```

| Name        | Description                                |
| ----------- | ------------------------------------------ |
| **RETURNS** | A `(rows, dims)` pair. ~~Tuple[int, int]~~ |

## Vectors.size {#size tag="property"}

The vector size, i.e. `rows * dims`.

> #### Example
>
> ```python
> vectors = Vectors(shape=(500, 300))
> assert vectors.size == 150000
> ```

| Name        | Description              |
| ----------- | ------------------------ |
| **RETURNS** | The vector size. ~~int~~ |

## Vectors.is_full {#is_full tag="property"}

Whether the vectors table is full and has no slots are available for new keys.
If a table is full, it can be resized using
[`Vectors.resize`](/api/vectors#resize). In `floret` mode, the table is always
full and cannot be resized.

> #### Example
>
> ```python
> vectors = Vectors(shape=(1, 300))
> vectors.add("cat", numpy.random.uniform(-1, 1, (300,)))
> assert vectors.is_full
> ```

| Name        | Description                                 |
| ----------- | ------------------------------------------- |
| **RETURNS** | Whether the vectors table is full. ~~bool~~ |

## Vectors.n_keys {#n_keys tag="property"}

Get the number of keys in the table. Note that this is the number of _all_ keys,
not just unique vectors. If several keys are mapped to the same vectors, they
will be counted individually. In `floret` mode, the keys table is not used.

> #### Example
>
> ```python
> vectors = Vectors(shape=(10, 300))
> assert len(vectors) == 10
> assert vectors.n_keys == 0
> ```

| Name        | Description                                                                   |
| ----------- | ----------------------------------------------------------------------------- |
| **RETURNS** | The number of all keys in the table. Returns `-1` for floret vectors. ~~int~~ |

## Vectors.most_similar {#most_similar tag="method"}

For each of the given vectors, find the `n` most similar entries to it by
cosine. Queries are by vector. Results are returned as a
`(keys, best_rows, scores)` tuple. If `queries` is large, the calculations are
performed in chunks to avoid consuming too much memory. You can set the
`batch_size` to control the size/space trade-off during the calculations. Not
supported for `floret` mode.

> #### Example
>
> ```python
> queries = numpy.asarray([numpy.random.uniform(-1, 1, (300,))])
> most_similar = nlp.vocab.vectors.most_similar(queries, n=10)
> ```

| Name           | Description                                                                                                             |
| -------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `queries`      | An array with one or more vectors. ~~numpy.ndarray~~                                                                    |
| _keyword-only_ |                                                                                                                         |
| `batch_size`   | The batch size to use. Default to `1024`. ~~int~~                                                                       |
| `n`            | The number of entries to return for each query. Defaults to `1`. ~~int~~                                                |
| `sort`         | Whether to sort the entries returned by score. Defaults to `True`. ~~bool~~                                             |
| **RETURNS**    | The most similar entries as a `(keys, best_rows, scores)` tuple. ~~Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]~~ |

## Vectors.get_batch {#get_batch tag="method" new="3.2"}

Get the vectors for the provided keys efficiently as a batch.

> #### Example
>
> ```python
> words = ["cat", "dog"]
> vectors = nlp.vocab.vectors.get_batch(words)
> ```

| Name   | Description                             |
| ------ | --------------------------------------- |
| `keys` | The keys. ~~Iterable[Union[int, str]]~~ |

## Vectors.to_ops {#to_ops tag="method"}

Change the embedding matrix to use different Thinc ops.

> #### Example
>
> ```python
> from thinc.api import NumpyOps
>
> vectors.to_ops(NumpyOps())
>
> ```

| Name  | Description                                              |
| ----- | -------------------------------------------------------- |
| `ops` | The Thinc ops to switch the embedding matrix to. ~~Ops~~ |

## Vectors.to_disk {#to_disk tag="method"}

Save the current state to a directory.

> #### Example
>
> ```python
> vectors.to_disk("/path/to/vectors")
>
> ```

| Name   | Description                                                                                                                                |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |

## Vectors.from_disk {#from_disk tag="method"}

Loads state from a directory. Modifies the object in place and returns it.

> #### Example
>
> ```python
> vectors = Vectors(StringStore())
> vectors.from_disk("/path/to/vectors")
> ```

| Name        | Description                                                                                     |
| ----------- | ----------------------------------------------------------------------------------------------- |
| `path`      | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| **RETURNS** | The modified `Vectors` object. ~~Vectors~~                                                      |

## Vectors.to_bytes {#to_bytes tag="method"}

Serialize the current state to a binary string.

> #### Example
>
> ```python
> vectors_bytes = vectors.to_bytes()
> ```

| Name        | Description                                            |
| ----------- | ------------------------------------------------------ |
| **RETURNS** | The serialized form of the `Vectors` object. ~~bytes~~ |

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

| Name        | Description                       |
| ----------- | --------------------------------- |
| `data`      | The data to load from. ~~bytes~~  |
| **RETURNS** | The `Vectors` object. ~~Vectors~~ |

## Attributes {#attributes}

| Name      | Description                                                                                                                                                          |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `data`    | Stored vectors data. `numpy` is used for CPU vectors, `cupy` for GPU vectors. ~~Union[numpy.ndarray[ndim=1, dtype=float32], cupy.ndarray[ndim=1, dtype=float32]]~~   |
| `key2row` | Dictionary mapping word hashes to rows in the `Vectors.data` table. ~~Dict[int, int]~~                                                                               |
| `keys`    | Array keeping the keys in order, such that `keys[vectors.key2row[key]] == key`. ~~Union[numpy.ndarray[ndim=1, dtype=float32], cupy.ndarray[ndim=1, dtype=float32]]~~ |
