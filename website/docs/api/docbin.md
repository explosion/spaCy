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
### msgpack object structure
{
    "version": str,           # DocBin version number
    "attrs": List[uint64],    # e.g. [TAG, HEAD, ENT_IOB, ENT_TYPE]
    "tokens": bytes,          # Serialized numpy uint64 array with the token data
    "spaces": bytes,          # Serialized numpy boolean array with spaces data
    "lengths": bytes,         # Serialized numpy int32 array with the doc lengths
    "strings": List[str]      # List of unique strings in the token data
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

| Argument          | Description                                                                                                                                                                                                                                                                                         |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `attrs`           | List of attributes to serialize. `ORTH` (hash of token text) and `SPACY` (whether the token is followed by whitespace) are always serialized, so they're not required. Defaults to `("ORTH", "TAG", "HEAD", "DEP", "ENT_IOB", "ENT_TYPE", "ENT_KB_ID", "LEMMA", "MORPH", "POS")`. ~~Iterable[str]~~ |
| `store_user_data` | Whether to write the `Doc.user_data` and the values of custom extension attributes to file/bytes. Defaults to `False`. ~~bool~~                                                                                                                                                                     |
| `docs`            | `Doc` objects to add on initialization. ~~Iterable[Doc]~~                                                                                                                                                                                                                                           |

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

| Argument    | Description                                         |
| ----------- | --------------------------------------------------- |
| **RETURNS** | The number of `Doc`s added to the `DocBin`. ~~int~~ |

## DocBin.add {#add tag="method"}

Add a `Doc`'s annotations to the `DocBin` for serialization.

> #### Example
>
> ```python
> doc_bin = DocBin(attrs=["LEMMA"])
> doc = nlp("This is a document to serialize.")
> doc_bin.add(doc)
> ```

| Argument | Description                      |
| -------- | -------------------------------- |
| `doc`    | The `Doc` object to add. ~~Doc~~ |

## DocBin.get_docs {#get_docs tag="method"}

Recover `Doc` objects from the annotations, using the given vocab.

> #### Example
>
> ```python
> docs = list(doc_bin.get_docs(nlp.vocab))
> ```

| Argument   | Description                 |
| ---------- | --------------------------- |
| `vocab`    | The shared vocab. ~~Vocab~~ |
| **YIELDS** | The `Doc` objects. ~~Doc~~  |

## DocBin.merge {#merge tag="method"}

Extend the annotations of this `DocBin` with the annotations from another. Will
raise an error if the pre-defined `attrs` of the two `DocBin`s don't match.

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

| Argument | Description                                            |
| -------- | ------------------------------------------------------ |
| `other`  | The `DocBin` to merge into the current bin. ~~DocBin~~ |

## DocBin.to_bytes {#to_bytes tag="method"}

Serialize the `DocBin`'s annotations to a bytestring.

> #### Example
>
> ```python
> docs = [nlp("Hello world!")]
> doc_bin = DocBin(docs=docs)
> doc_bin_bytes = doc_bin.to_bytes()
> ```

| Argument    | Description                        |
| ----------- | ---------------------------------- |
| **RETURNS** | The serialized `DocBin`. ~~bytes~~ |

## DocBin.from_bytes {#from_bytes tag="method"}

Deserialize the `DocBin`'s annotations from a bytestring.

> #### Example
>
> ```python
> doc_bin_bytes = doc_bin.to_bytes()
> new_doc_bin = DocBin().from_bytes(doc_bin_bytes)
> ```

| Argument     | Description                      |
| ------------ | -------------------------------- |
| `bytes_data` | The data to load from. ~~bytes~~ |
| **RETURNS**  | The loaded `DocBin`. ~~DocBin~~  |

## DocBin.to_disk {#to_disk tag="method" new="3"}

Save the serialized `DocBin` to a file. Typically uses the `.spacy` extension
and the result can be used as the input data for
[`spacy train`](/api/cli#train).

> #### Example
>
> ```python
> docs = [nlp("Hello world!")]
> doc_bin = DocBin(docs=docs)
> doc_bin.to_disk("./data.spacy")
> ```

| Argument | Description                                                                |
| -------- | -------------------------------------------------------------------------- |
| `path`   | The file path, typically with the `.spacy` extension. ~~Union[str, Path]~~ |

## DocBin.from_disk {#from_disk tag="method" new="3"}

Load a serialized `DocBin` from a file. Typically uses the `.spacy` extension.

> #### Example
>
> ```python
> doc_bin = DocBin().from_disk("./data.spacy")
> ```

| Argument    | Description                                                                |
| ----------- | -------------------------------------------------------------------------- |
| `path`      | The file path, typically with the `.spacy` extension. ~~Union[str, Path]~~ |
| **RETURNS** | The loaded `DocBin`. ~~DocBin~~                                            |
