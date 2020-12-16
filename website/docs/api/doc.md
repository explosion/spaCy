---
title: Doc
tag: class
teaser: A container for accessing linguistic annotations.
source: spacy/tokens/doc.pyx
---

A `Doc` is a sequence of [`Token`](/api/token) objects. Access sentences and
named entities, export annotations to numpy arrays, losslessly serialize to
compressed binary strings. The `Doc` object holds an array of
[`TokenC`](/api/cython-structs#tokenc) structs. The Python-level `Token` and
[`Span`](/api/span) objects are views of this array, i.e. they don't own the
data themselves.

## Doc.\_\_init\_\_ {#init tag="method"}

Construct a `Doc` object. The most common way to get a `Doc` object is via the
`nlp` object.

> #### Example
>
> ```python
> # Construction 1
> doc = nlp("Some text")
>
> # Construction 2
> from spacy.tokens import Doc
> words = ["hello", "world", "!"]
> spaces = [True, False, False]
> doc = Doc(nlp.vocab, words=words, spaces=spaces)
> ```

| Name        | Type     | Description                                                                                                                                                         |
| ----------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`     | `Vocab`  | A storage container for lexical types.                                                                                                                              |
| `words`     | iterable | A list of strings to add to the container.                                                                                                                          |
| `spaces`    | iterable | A list of boolean values indicating whether each word has a subsequent space. Must have the same length as `words`, if specified. Defaults to a sequence of `True`. |
| **RETURNS** | `Doc`    | The newly constructed object.                                                                                                                                       |

## Doc.\_\_getitem\_\_ {#getitem tag="method"}

Get a [`Token`](/api/token) object at position `i`, where `i` is an integer.
Negative indexing is supported, and follows the usual Python semantics, i.e.
`doc[-2]` is `doc[len(doc) - 2]`.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> assert doc[0].text == "Give"
> assert doc[-1].text == "."
> span = doc[1:3]
> assert span.text == "it back"
> ```

| Name        | Type    | Description             |
| ----------- | ------- | ----------------------- |
| `i`         | int     | The index of the token. |
| **RETURNS** | `Token` | The token at `doc[i]`.  |

Get a [`Span`](/api/span) object, starting at position `start` (token index) and
ending at position `end` (token index). For instance, `doc[2:5]` produces a span
consisting of tokens 2, 3 and 4. Stepped slices (e.g. `doc[start : end : step]`)
are not supported, as `Span` objects must be contiguous (cannot have gaps). You
can use negative indices and open-ended ranges, which have their normal Python
semantics.

| Name        | Type   | Description                       |
| ----------- | ------ | --------------------------------- |
| `start_end` | tuple  | The slice of the document to get. |
| **RETURNS** | `Span` | The span at `doc[start:end]`.     |

## Doc.\_\_iter\_\_ {#iter tag="method"}

Iterate over `Token` objects, from which the annotations can be easily accessed.

> #### Example
>
> ```python
> doc = nlp("Give it back")
> assert [t.text for t in doc] == ["Give", "it", "back"]
> ```

This is the main way of accessing [`Token`](/api/token) objects, which are the
main way annotations are accessed from Python. If faster-than-Python speeds are
required, you can instead access the annotations as a numpy array, or access the
underlying C data directly from Cython.

| Name       | Type    | Description       |
| ---------- | ------- | ----------------- |
| **YIELDS** | `Token` | A `Token` object. |

## Doc.\_\_len\_\_ {#len tag="method"}

Get the number of tokens in the document.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> assert len(doc) == 7
> ```

| Name        | Type | Description                           |
| ----------- | ---- | ------------------------------------- |
| **RETURNS** | int  | The number of tokens in the document. |

## Doc.set_extension {#set_extension tag="classmethod" new="2"}

Define a custom attribute on the `Doc` which becomes available via `Doc._`. For
details, see the documentation on
[custom attributes](/usage/processing-pipelines#custom-components-attributes).

> #### Example
>
> ```python
> from spacy.tokens import Doc
> city_getter = lambda doc: any(city in doc.text for city in ("New York", "Paris", "Berlin"))
> Doc.set_extension("has_city", getter=city_getter)
> doc = nlp("I like New York")
> assert doc._.has_city
> ```

| Name      | Type     | Description                                                                                                                         |
| --------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `name`    | unicode  | Name of the attribute to set by the extension. For example, `'my_attr'` will be available as `doc._.my_attr`.                       |
| `default` | -        | Optional default value of the attribute if no getter or method is defined.                                                          |
| `method`  | callable | Set a custom method on the object, for example `doc._.compare(other_doc)`.                                                          |
| `getter`  | callable | Getter function that takes the object and returns an attribute value. Is called when the user accesses the `._` attribute.          |
| `setter`  | callable | Setter function that takes the `Doc` and a value, and modifies the object. Is called when the user writes to the `Doc._` attribute. |
| `force`   | bool     | Force overwriting existing attribute.                                                                                               |

## Doc.get_extension {#get_extension tag="classmethod" new="2"}

Look up a previously registered extension by name. Returns a 4-tuple
`(default, method, getter, setter)` if the extension is registered. Raises a
`KeyError` otherwise.

> #### Example
>
> ```python
> from spacy.tokens import Doc
> Doc.set_extension('has_city', default=False)
> extension = Doc.get_extension('has_city')
> assert extension == (False, None, None, None)
> ```

| Name        | Type    | Description                                                   |
| ----------- | ------- | ------------------------------------------------------------- |
| `name`      | unicode | Name of the extension.                                        |
| **RETURNS** | tuple   | A `(default, method, getter, setter)` tuple of the extension. |

## Doc.has_extension {#has_extension tag="classmethod" new="2"}

Check whether an extension has been registered on the `Doc` class.

> #### Example
>
> ```python
> from spacy.tokens import Doc
> Doc.set_extension('has_city', default=False)
> assert Doc.has_extension('has_city')
> ```

| Name        | Type    | Description                                |
| ----------- | ------- | ------------------------------------------ |
| `name`      | unicode | Name of the extension to check.            |
| **RETURNS** | bool    | Whether the extension has been registered. |

## Doc.remove_extension {#remove_extension tag="classmethod" new="2.0.12"}

Remove a previously registered extension.

> #### Example
>
> ```python
> from spacy.tokens import Doc
> Doc.set_extension('has_city', default=False)
> removed = Doc.remove_extension('has_city')
> assert not Doc.has_extension('has_city')
> ```

| Name        | Type    | Description                                                           |
| ----------- | ------- | --------------------------------------------------------------------- |
| `name`      | unicode | Name of the extension.                                                |
| **RETURNS** | tuple   | A `(default, method, getter, setter)` tuple of the removed extension. |

## Doc.char_span {#char_span tag="method" new="2"}

Create a `Span` object from the slice `doc.text[start_idx:end_idx]`. Returns
`None` if the character indices don't map to a valid span using the default mode
`"strict".

> #### Example
>
> ```python
> doc = nlp("I like New York")
> span = doc.char_span(7, 15, label="GPE")
> assert span.text == "New York"
> ```

| Name                                 | Type                                     | Description                                                                                                                                                                                                                                                 |
| ------------------------------------ | ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `start_idx`                          | int                                      | The index of the first character of the span.                                                                                                                                                                                                               |
| `end_idx`                            | int                                      | The index of the last character after the span.                                                                                                                                                                                                             |
| `label`                              | uint64 / unicode                         | A label to attach to the span, e.g. for named entities.                                                                                                                                                                                                     |
| `kb_id` <Tag variant="new">2.2</Tag> | uint64 / unicode                         | An ID from a knowledge base to capture the meaning of a named entity.                                                                                                                                                                                       |
| `vector`                             | `numpy.ndarray[ndim=1, dtype='float32']` | A meaning representation of the span.                                                                                                                                                                                                                       |
| `mode`                               | `str`                                    | How character indices snap to token boundaries. Options: "strict" (no snapping), "inside" (span of all tokens completely within the character span), "outside" (span of all tokens at least partially covered by the character span). Defaults to "strict". |
| **RETURNS**                          | `Span`                                   | The newly constructed object or `None`.                                                                                                                                                                                                                     |

## Doc.similarity {#similarity tag="method" model="vectors"}

Make a semantic similarity estimate. The default estimate is cosine similarity
using an average of word vectors.

> #### Example
>
> ```python
> apples = nlp("I like apples")
> oranges = nlp("I like oranges")
> apples_oranges = apples.similarity(oranges)
> oranges_apples = oranges.similarity(apples)
> assert apples_oranges == oranges_apples
> ```

| Name        | Type  | Description                                                                                  |
| ----------- | ----- | -------------------------------------------------------------------------------------------- |
| `other`     | -     | The object to compare with. By default, accepts `Doc`, `Span`, `Token` and `Lexeme` objects. |
| **RETURNS** | float | A scalar similarity score. Higher is more similar.                                           |

## Doc.count_by {#count_by tag="method"}

Count the frequencies of a given attribute. Produces a dict of
`{attr (int): count (ints)}` frequencies, keyed by the values of the given
attribute ID.

> #### Example
>
> ```python
> from spacy.attrs import ORTH
> doc = nlp("apple apple orange banana")
> assert doc.count_by(ORTH) == {7024L: 1, 119552L: 1, 2087L: 2}
> doc.to_array([ORTH])
> # array([[11880], [11880], [7561], [12800]])
> ```

| Name        | Type | Description                                        |
| ----------- | ---- | -------------------------------------------------- |
| `attr_id`   | int  | The attribute ID                                   |
| **RETURNS** | dict | A dictionary mapping attributes to integer counts. |

## Doc.get_lca_matrix {#get_lca_matrix tag="method"}

Calculates the lowest common ancestor matrix for a given `Doc`. Returns LCA
matrix containing the integer index of the ancestor, or `-1` if no common
ancestor is found, e.g. if span excludes a necessary ancestor.

> #### Example
>
> ```python
> doc = nlp("This is a test")
> matrix = doc.get_lca_matrix()
> # array([[0, 1, 1, 1], [1, 1, 1, 1], [1, 1, 2, 3], [1, 1, 3, 3]], dtype=int32)
> ```

| Name        | Type                                   | Description                                     |
| ----------- | -------------------------------------- | ----------------------------------------------- |
| **RETURNS** | `numpy.ndarray[ndim=2, dtype='int32']` | The lowest common ancestor matrix of the `Doc`. |

## Doc.to_json {#to_json tag="method" new="2.1"}

Convert a Doc to JSON. The format it produces will be the new format for the
[`spacy train`](/api/cli#train) command (not implemented yet). If custom
underscore attributes are specified, their values need to be JSON-serializable.
They'll be added to an `"_"` key in the data, e.g. `"_": {"foo": "bar"}`.

> #### Example
>
> ```python
> doc = nlp("Hello")
> json_doc = doc.to_json()
> ```
>
> #### Result
>
> ```python
> {
>   "text": "Hello",
>   "ents": [],
>   "sents": [{"start": 0, "end": 5}],
>   "tokens": [{"id": 0, "start": 0, "end": 5, "pos": "INTJ", "tag": "UH", "dep": "ROOT", "head": 0}
>   ]
> }
> ```

| Name         | Type | Description                                                                    |
| ------------ | ---- | ------------------------------------------------------------------------------ |
| `underscore` | list | Optional list of string names of custom JSON-serializable `doc._.` attributes. |
| **RETURNS**  | dict | The JSON-formatted data.                                                       |

<Infobox title="Deprecation note" variant="warning">

spaCy previously implemented a `Doc.print_tree` method that returned a similar
JSON-formatted representation of a `Doc`. As of v2.1, this method is deprecated
in favor of `Doc.to_json`. If you need more complex nested representations, you
might want to write your own function to extract the data.

</Infobox>

## Doc.to_array {#to_array tag="method"}

Export given token attributes to a numpy `ndarray`. If `attr_ids` is a sequence
of `M` attributes, the output array will be of shape `(N, M)`, where `N` is the
length of the `Doc` (in tokens). If `attr_ids` is a single attribute, the output
shape will be `(N,)`. You can specify attributes by integer ID (e.g.
`spacy.attrs.LEMMA`) or string name (e.g. 'LEMMA' or 'lemma'). The values will
be 64-bit integers.

Returns a 2D array with one row per token and one column per attribute (when
`attr_ids` is a list), or as a 1D numpy array, with one item per attribute (when
`attr_ids` is a single value).

> #### Example
>
> ```python
> from spacy.attrs import LOWER, POS, ENT_TYPE, IS_ALPHA
> doc = nlp(text)
> # All strings mapped to integers, for easy export to numpy
> np_array = doc.to_array([LOWER, POS, ENT_TYPE, IS_ALPHA])
> np_array = doc.to_array("POS")
> ```

| Name        | Type                                                                               | Description                                                                                  |
| ----------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `attr_ids`  | list or int or string                                                              | A list of attributes (int IDs or string names) or a single attribute (int ID or string name) |
| **RETURNS** | `numpy.ndarray[ndim=2, dtype='uint64']` or `numpy.ndarray[ndim=1, dtype='uint64']` | The exported attributes as a numpy array.                                                    |

## Doc.from_array {#from_array tag="method"}

Load attributes from a numpy array. Write to a `Doc` object, from an `(M, N)`
array of attributes.

> #### Example
>
> ```python
> from spacy.attrs import LOWER, POS, ENT_TYPE, IS_ALPHA
> from spacy.tokens import Doc
> doc = nlp("Hello world!")
> np_array = doc.to_array([LOWER, POS, ENT_TYPE, IS_ALPHA])
> doc2 = Doc(doc.vocab, words=[t.text for t in doc])
> doc2.from_array([LOWER, POS, ENT_TYPE, IS_ALPHA], np_array)
> assert doc[0].pos_ == doc2[0].pos_
> ```

| Name        | Type                                   | Description                                                               |
| ----------- | -------------------------------------- | ------------------------------------------------------------------------- |
| `attrs`     | list                                   | A list of attribute ID ints.                                              |
| `array`     | `numpy.ndarray[ndim=2, dtype='int32']` | The attribute values to load.                                             |
| `exclude`   | list                                   | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS** | `Doc`                                  | Itself.                                                                   |

## Doc.to_disk {#to_disk tag="method" new="2"}

Save the current state to a directory.

> #### Example
>
> ```python
> doc.to_disk("/path/to/doc")
> ```

| Name      | Type             | Description                                                                                                           |
| --------- | ---------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`    | unicode / `Path` | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| `exclude` | list             | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## Doc.from_disk {#from_disk tag="method" new="2"}

Loads state from a directory. Modifies the object in place and returns it.

> #### Example
>
> ```python
> from spacy.tokens import Doc
> from spacy.vocab import Vocab
> doc = Doc(Vocab()).from_disk("/path/to/doc")
> ```

| Name        | Type             | Description                                                                |
| ----------- | ---------------- | -------------------------------------------------------------------------- |
| `path`      | unicode / `Path` | A path to a directory. Paths may be either strings or `Path`-like objects. |
| `exclude`   | list             | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS** | `Doc`            | The modified `Doc` object.                                                 |

## Doc.to_bytes {#to_bytes tag="method"}

Serialize, i.e. export the document contents to a binary string.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> doc_bytes = doc.to_bytes()
> ```

| Name        | Type  | Description                                                               |
| ----------- | ----- | ------------------------------------------------------------------------- |
| `exclude`   | list  | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS** | bytes | A losslessly serialized copy of the `Doc`, including all annotations.     |

## Doc.from_bytes {#from_bytes tag="method"}

Deserialize, i.e. import the document contents from a binary string.

> #### Example
>
> ```python
> from spacy.tokens import Doc
> doc = nlp("Give it back! He pleaded.")
> doc_bytes = doc.to_bytes()
> doc2 = Doc(doc.vocab).from_bytes(doc_bytes)
> assert doc.text == doc2.text
> ```

| Name        | Type  | Description                                                               |
| ----------- | ----- | ------------------------------------------------------------------------- |
| `data`      | bytes | The string to load from.                                                  |
| `exclude`   | list  | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS** | `Doc` | The `Doc` object.                                                         |

## Doc.retokenize {#retokenize tag="contextmanager" new="2.1"}

Context manager to handle retokenization of the `Doc`. Modifications to the
`Doc`'s tokenization are stored, and then made all at once when the context
manager exits. This is much more efficient, and less error-prone. All views of
the `Doc` (`Span` and `Token`) created before the retokenization are
invalidated, although they may accidentally continue to work.

> #### Example
>
> ```python
> doc = nlp("Hello world!")
> with doc.retokenize() as retokenizer:
>     retokenizer.merge(doc[0:2])
> ```

| Name        | Type          | Description      |
| ----------- | ------------- | ---------------- |
| **RETURNS** | `Retokenizer` | The retokenizer. |

### Retokenizer.merge {#retokenizer.merge tag="method"}

Mark a span for merging. The `attrs` will be applied to the resulting token (if
they're context-dependent token attributes like `LEMMA` or `DEP`) or to the
underlying lexeme (if they're context-independent lexical attributes like
`LOWER` or `IS_STOP`). Writable custom extension attributes can be provided as a
dictionary mapping attribute names to values as the `"_"` key.

> #### Example
>
> ```python
> doc = nlp("I like David Bowie")
> with doc.retokenize() as retokenizer:
>     attrs = {"LEMMA": "David Bowie"}
>     retokenizer.merge(doc[2:4], attrs=attrs)
> ```

| Name    | Type   | Description                            |
| ------- | ------ | -------------------------------------- |
| `span`  | `Span` | The span to merge.                     |
| `attrs` | dict   | Attributes to set on the merged token. |

### Retokenizer.split {#retokenizer.split tag="method"}

Mark a token for splitting, into the specified `orths`. The `heads` are required
to specify how the new subtokens should be integrated into the dependency tree.
The list of per-token heads can either be a token in the original document, e.g.
`doc[2]`, or a tuple consisting of the token in the original document and its
subtoken index. For example, `(doc[3], 1)` will attach the subtoken to the
second subtoken of `doc[3]`.

This mechanism allows attaching subtokens to other newly created subtokens,
without having to keep track of the changing token indices. If the specified
head token will be split within the retokenizer block and no subtoken index is
specified, it will default to `0`. Attributes to set on subtokens can be
provided as a list of values. They'll be applied to the resulting token (if
they're context-dependent token attributes like `LEMMA` or `DEP`) or to the
underlying lexeme (if they're context-independent lexical attributes like
`LOWER` or `IS_STOP`).

> #### Example
>
> ```python
> doc = nlp("I live in NewYork")
> with doc.retokenize() as retokenizer:
>     heads = [(doc[3], 1), doc[2]]
>     attrs = {"POS": ["PROPN", "PROPN"],
>              "DEP": ["pobj", "compound"]}
>     retokenizer.split(doc[3], ["New", "York"], heads=heads, attrs=attrs)
> ```

| Name    | Type    | Description                                                                                                 |
| ------- | ------- | ----------------------------------------------------------------------------------------------------------- |
| `token` | `Token` | The token to split.                                                                                         |
| `orths` | list    | The verbatim text of the split tokens. Needs to match the text of the original token.                       |
| `heads` | list    | List of `token` or `(token, subtoken)` tuples specifying the tokens to attach the newly split subtokens to. |
| `attrs` | dict    | Attributes to set on all split tokens. Attribute names mapped to list of per-token attribute values.        |

## Doc.merge {#merge tag="method"}

<Infobox title="Deprecation note" variant="danger">

As of v2.1.0, `Doc.merge` still works but is considered deprecated. You should
use the new and less error-prone [`Doc.retokenize`](/api/doc#retokenize)
instead.

</Infobox>

Retokenize the document, such that the span at `doc.text[start_idx : end_idx]`
is merged into a single token. If `start_idx` and `end_idx` do not mark start
and end token boundaries, the document remains unchanged.

> #### Example
>
> ```python
> doc = nlp("Los Angeles start.")
> doc.merge(0, len("Los Angeles"), "NNP", "Los Angeles", "GPE")
> assert [t.text for t in doc] == ["Los Angeles", "start", "."]
> ```

| Name           | Type    | Description                                                                                                               |
| -------------- | ------- | ------------------------------------------------------------------------------------------------------------------------- |
| `start_idx`    | int     | The character index of the start of the slice to merge.                                                                   |
| `end_idx`      | int     | The character index after the end of the slice to merge.                                                                  |
| `**attributes` | -       | Attributes to assign to the merged token. By default, attributes are inherited from the syntactic root token of the span. |
| **RETURNS**    | `Token` | The newly merged token, or `None` if the start and end indices did not fall at token boundaries                           |

## Doc.ents {#ents tag="property" model="NER"}

The named entities in the document. Returns a tuple of named entity `Span`
objects, if the entity recognizer has been applied.

> #### Example
>
> ```python
> doc = nlp("Mr. Best flew to New York on Saturday morning.")
> ents = list(doc.ents)
> assert ents[0].label == 346
> assert ents[0].label_ == "PERSON"
> assert ents[0].text == "Mr. Best"
> ```

| Name        | Type  | Description                                      |
| ----------- | ----- | ------------------------------------------------ |
| **RETURNS** | tuple | Entities in the document, one `Span` per entity. |

## Doc.noun_chunks {#noun_chunks tag="property" model="parser"}

Iterate over the base noun phrases in the document. Yields base noun-phrase
`Span` objects, if the document has been syntactically parsed. A base noun
phrase, or "NP chunk", is a noun phrase that does not permit other NPs to be
nested within it – so no NP-level coordination, no prepositional phrases, and no
relative clauses.

> #### Example
>
> ```python
> doc = nlp("A phrase with another phrase occurs.")
> chunks = list(doc.noun_chunks)
> assert chunks[0].text == "A phrase"
> assert chunks[1].text == "another phrase"
> ```

| Name       | Type   | Description                  |
| ---------- | ------ | ---------------------------- |
| **YIELDS** | `Span` | Noun chunks in the document. |

## Doc.sents {#sents tag="property" model="parser"}

Iterate over the sentences in the document. Sentence spans have no label. To
improve accuracy on informal texts, spaCy calculates sentence boundaries from
the syntactic dependency parse. If the parser is disabled, the `sents` iterator
will be unavailable.

> #### Example
>
> ```python
> doc = nlp("This is a sentence. Here's another...")
> sents = list(doc.sents)
> assert len(sents) == 2
> assert [s.root.text for s in sents] == ["is", "'s"]
> ```

| Name       | Type   | Description                |
| ---------- | ------ | -------------------------- |
| **YIELDS** | `Span` | Sentences in the document. |

## Doc.has_vector {#has_vector tag="property" model="vectors"}

A boolean value indicating whether a word vector is associated with the object.

> #### Example
>
> ```python
> doc = nlp("I like apples")
> assert doc.has_vector
> ```

| Name        | Type | Description                                      |
| ----------- | ---- | ------------------------------------------------ |
| **RETURNS** | bool | Whether the document has a vector data attached. |

## Doc.vector {#vector tag="property" model="vectors"}

A real-valued meaning representation. Defaults to an average of the token
vectors.

> #### Example
>
> ```python
> doc = nlp("I like apples")
> assert doc.vector.dtype == "float32"
> assert doc.vector.shape == (300,)
> ```

| Name        | Type                                     | Description                                             |
| ----------- | ---------------------------------------- | ------------------------------------------------------- |
| **RETURNS** | `numpy.ndarray[ndim=1, dtype='float32']` | A 1D numpy array representing the document's semantics. |

## Doc.vector_norm {#vector_norm tag="property" model="vectors"}

The L2 norm of the document's vector representation.

> #### Example
>
> ```python
> doc1 = nlp("I like apples")
> doc2 = nlp("I like oranges")
> doc1.vector_norm  # 4.54232424414368
> doc2.vector_norm  # 3.304373298575751
> assert doc1.vector_norm != doc2.vector_norm
> ```

| Name        | Type  | Description                               |
| ----------- | ----- | ----------------------------------------- |
| **RETURNS** | float | The L2 norm of the vector representation. |

## Attributes {#attributes}

| Name                                    | Type         | Description                                                                                                                                                                     |
| --------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `text`                                  | unicode      | A unicode representation of the document text.                                                                                                                                  |
| `text_with_ws`                          | unicode      | An alias of `Doc.text`, provided for duck-type compatibility with `Span` and `Token`.                                                                                           |
| `mem`                                   | `Pool`       | The document's local memory heap, for all C data it owns.                                                                                                                       |
| `vocab`                                 | `Vocab`      | The store of lexical types.                                                                                                                                                     |
| `tensor` <Tag variant="new">2</Tag>     | `ndarray`    | Container for dense vector representations.                                                                                                                                     |
| `cats` <Tag variant="new">2</Tag>       | dict         | Maps a label to a score for categories applied to the document. The label is a string and the score should be a float.                                                          |
| `user_data`                             | -            | A generic storage area, for user custom data.                                                                                                                                   |
| `lang` <Tag variant="new">2.1</Tag>     | int          | Language of the document's vocabulary.                                                                                                                                          |
| `lang_` <Tag variant="new">2.1</Tag>    | unicode      | Language of the document's vocabulary.                                                                                                                                          |
| `is_tagged`                             | bool         | A flag indicating that the document has been part-of-speech tagged. Returns `True` if the `Doc` is empty.                                                                       |
| `is_parsed`                             | bool         | A flag indicating that the document has been syntactically parsed. Returns `True` if the `Doc` is empty.                                                                        |
| `is_sentenced`                          | bool         | A flag indicating that sentence boundaries have been applied to the document. Returns `True` if the `Doc` is empty.                                                             |
| `is_nered` <Tag variant="new">2.1</Tag> | bool         | A flag indicating that named entities have been set. Will return `True` if the `Doc` is empty, or if _any_ of the tokens has an entity tag set, even if the others are unknown. |
| `sentiment`                             | float        | The document's positivity/negativity score, if available.                                                                                                                       |
| `user_hooks`                            | dict         | A dictionary that allows customization of the `Doc`'s properties.                                                                                                               |
| `user_token_hooks`                      | dict         | A dictionary that allows customization of properties of `Token` children.                                                                                                       |
| `user_span_hooks`                       | dict         | A dictionary that allows customization of properties of `Span` children.                                                                                                        |
| `_`                                     | `Underscore` | User space for adding custom [attribute extensions](/usage/processing-pipelines#custom-components-attributes).                                                                  |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = doc.to_bytes(exclude=["text", "tensor"])
> doc.from_disk("./doc.bin", exclude=["user_data"])
> ```

| Name               | Description                                   |
| ------------------ | --------------------------------------------- |
| `text`             | The value of the `Doc.text` attribute.        |
| `sentiment`        | The value of the `Doc.sentiment` attribute.   |
| `tensor`           | The value of the `Doc.tensor` attribute.      |
| `user_data`        | The value of the `Doc.user_data` dictionary.  |
| `user_data_keys`   | The keys of the `Doc.user_data` dictionary.   |
| `user_data_values` | The values of the `Doc.user_data` dictionary. |
