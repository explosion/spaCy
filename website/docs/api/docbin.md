---
title: DocBin
tag: class
new: 2.2
teaser: Pack Doc objects for binary serialization
source: spacy/tokens/_serialize.py
---

The `DocBin` class lets you efficiently serialize the information from a
collection of `Doc` objects. You can control which information is serialized by
passing a list of attribute IDs, and optionally also specify whether the user
data is serialized. The `DocBin` is faster and produces smaller data sizes than
pickle, and allows you to deserialize without executing arbitrary Python code. A
notable downside to this format is that you can't easily extract just one
document from the `DocBin`. The serialization format is gzipped msgpack, where
the msgpack object has the following structure:

```python
### msgpack object strcutrue
{
    "attrs": List[uint64],    # e.g. [TAG, HEAD, ENT_IOB, ENT_TYPE]
    "tokens": bytes,          # Serialized numpy uint64 array with the token data
    "spaces": bytes,          # Serialized numpy boolean array with spaces data
    "lengths": bytes,         # Serialized numpy int32 array with the doc lengths
    "strings": List[unicode]  # List of unique strings in the token data
}
```

Strings for the words, tags, labels etc are represented by 64-bit hashes in the
token data, and every string that occurs at least once is passed via the strings
object. This means the storage is more efficient if you pack more documents
together, because you have less duplication in the strings. For usage examples,
see the docs on [serializing `Doc` objects](/usage/saving-loading#docs).

## DocBin.\_\_init\_\_ {#init tag="method"}

Create a `DocBin` object to hold serialized annotations.

> #### Example
>
> ```python
> from spacy.tokens import DocBin
> doc_bin = DocBin(attrs=["ENT_IOB", "ENT_TYPE"])
> ```

| Argument          | Type     | Description                                                                                                                                                                                |
| ----------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `attrs`           | list     | List of attributes to serialize. `orth` (hash of token text) and `spacy` (whether the token is followed by whitespace) are always serialized, so they're not required. Defaults to `None`. |
| `store_user_data` | bool     | Whether to include the `Doc.user_data` and the values of custom extension attributes. Defaults to `False`.                                                                                 |
| **RETURNS**       | `DocBin` | The newly constructed object.                                                                                                                                                              |

## DocBin.\_\len\_\_ {#len tag="method"}

Get the number of `Doc` objects that were added to the `DocBin`.

> #### Example
>
> ```python
> doc_bin = DocBin(attrs=["LEMMA"])
> doc = nlp("This is a document to serialize.")
> doc_bin.add(doc)
> assert len(doc_bin) == 1
> ```

| Argument    | Type | Description                                 |
| ----------- | ---- | ------------------------------------------- |
| **RETURNS** | int  | The number of `Doc`s added to the `DocBin`. |

## DocBin.add {#add tag="method"}

Add a `Doc`'s annotations to the `DocBin` for serialization.

> #### Example
>
> ```python
> doc_bin = DocBin(attrs=["LEMMA"])
> doc = nlp("This is a document to serialize.")
> doc_bin.add(doc)
> ```

| Argument | Type  | Description              |
| -------- | ----- | ------------------------ |
| `doc`    | `Doc` | The `Doc` object to add. |

## DocBin.get_docs {#get_docs tag="method"}

Recover `Doc` objects from the annotations, using the given vocab.

> #### Example
>
> ```python
> docs = list(doc_bin.get_docs(nlp.vocab))
> ```

| Argument   | Type    | Description        |
| ---------- | ------- | ------------------ |
| `vocab`    | `Vocab` | The shared vocab.  |
| **YIELDS** | `Doc`   | The `Doc` objects. |

## DocBin.merge {#merge tag="method"}

Extend the annotations of this `DocBin` with the annotations from another. Will
raise an error if the pre-defined attrs of the two `DocBin`s don't match.

> #### Example
>
> ```python
> doc_bin1 = DocBin(attrs=["LEMMA", "POS"])
> doc_bin1.add(nlp("Hello world"))
> doc_bin2 = DocBin(attrs=["LEMMA", "POS"])
> doc_bin2.add(nlp("This is a sentence"))
> doc_bin1.merge(doc_bin2)
> assert len(doc_bin1) == 2
> ```

| Argument | Type     | Description                                 |
| -------- | -------- | ------------------------------------------- |
| `other`  | `DocBin` | The `DocBin` to merge into the current bin. |

## DocBin.to_bytes {#to_bytes tag="method"}

Serialize the `DocBin`'s annotations to a bytestring.

> #### Example
>
> ```python
> doc_bin = DocBin(attrs=["DEP", "HEAD"])
> doc_bin_bytes = doc_bin.to_bytes()
> ```

| Argument    | Type  | Description              |
| ----------- | ----- | ------------------------ |
| **RETURNS** | bytes | The serialized `DocBin`. |

## DocBin.from_bytes {#from_bytes tag="method"}

Deserialize the `DocBin`'s annotations from a bytestring.

> #### Example
>
> ```python
> doc_bin_bytes = doc_bin.to_bytes()
> new_doc_bin = DocBin().from_bytes(doc_bin_bytes)
> ```

| Argument     | Type     | Description            |
| ------------ | -------- | ---------------------- |
| `bytes_data` | bytes    | The data to load from. |
| **RETURNS**  | `DocBin` | The loaded `DocBin`.   |
