---
title: Span
tag: class
source: spacy/tokens/span.pyx
---

A slice from a [`Doc`](/api/doc) object.

## Span.\_\_init\_\_ {#init tag="method"}

Create a `Span` object from the slice `doc[start : end]`.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> span = doc[1:4]
> assert [t.text for t in span] ==  ["it", "back", "!"]
> ```

| Name          | Description                                                                             |
| ------------- | --------------------------------------------------------------------------------------- |
| `doc`         | The parent document. ~~Doc~~                                                            |
| `start`       | The index of the first token of the span. ~~int~~                                       |
| `end`         | The index of the first token after the span. ~~int~~                                    |
| `label`       | A label to attach to the span, e.g. for named entities. ~~Union[str, int]~~             |
| `vector`      | A meaning representation of the span. ~~numpy.ndarray[ndim=1, dtype=float32]~~          |
| `vector_norm` | The L2 norm of the document's vector representation. ~~float~~                          |
| `kb_id`       | A knowledge base ID to attach to the span, e.g. for named entities. ~~Union[str, int]~~ |
| `span_id`     | An ID to associate with the span. ~~Union[str, int]~~                                   |

## Span.\_\_getitem\_\_ {#getitem tag="method"}

Get a `Token` object.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> span = doc[1:4]
> assert span[1].text == "back"
> ```

| Name        | Description                                     |
| ----------- | ----------------------------------------------- |
| `i`         | The index of the token within the span. ~~int~~ |
| **RETURNS** | The token at `span[i]`. ~~Token~~               |

Get a `Span` object.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> span = doc[1:4]
> assert span[1:3].text == "back!"
> ```

| Name        | Description                                       |
| ----------- | ------------------------------------------------- |
| `start_end` | The slice of the span to get. ~~Tuple[int, int]~~ |
| **RETURNS** | The span at `span[start : end]`. ~~Span~~         |

## Span.\_\_iter\_\_ {#iter tag="method"}

Iterate over `Token` objects.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> span = doc[1:4]
> assert [t.text for t in span] == ["it", "back", "!"]
> ```

| Name       | Description                 |
| ---------- | --------------------------- |
| **YIELDS** | A `Token` object. ~~Token~~ |

## Span.\_\_len\_\_ {#len tag="method"}

Get the number of tokens in the span.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> span = doc[1:4]
> assert len(span) == 3
> ```

| Name        | Description                               |
| ----------- | ----------------------------------------- |
| **RETURNS** | The number of tokens in the span. ~~int~~ |

## Span.set_extension {#set_extension tag="classmethod" new="2"}

Define a custom attribute on the `Span` which becomes available via `Span._`.
For details, see the documentation on
[custom attributes](/usage/processing-pipelines#custom-components-attributes).

> #### Example
>
> ```python
> from spacy.tokens import Span
> city_getter = lambda span: any(city in span.text for city in ("New York", "Paris", "Berlin"))
> Span.set_extension("has_city", getter=city_getter)
> doc = nlp("I like New York in Autumn")
> assert doc[1:4]._.has_city
> ```

| Name      | Description                                                                                                                                                                     |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`    | Name of the attribute to set by the extension. For example, `"my_attr"` will be available as `span._.my_attr`. ~~str~~                                                          |
| `default` | Optional default value of the attribute if no getter or method is defined. ~~Optional[Any]~~                                                                                    |
| `method`  | Set a custom method on the object, for example `span._.compare(other_span)`. ~~Optional[Callable[[Span, ...], Any]]~~                                                           |
| `getter`  | Getter function that takes the object and returns an attribute value. Is called when the user accesses the `._` attribute. ~~Optional[Callable[[Span], Any]]~~                  |
| `setter`  | Setter function that takes the `Span` and a value, and modifies the object. Is called when the user writes to the `Span._` attribute. ~~Optional[Callable[[Span, Any], None]]~~ |
| `force`   | Force overwriting existing attribute. ~~bool~~                                                                                                                                  |

## Span.get_extension {#get_extension tag="classmethod" new="2"}

Look up a previously registered extension by name. Returns a 4-tuple
`(default, method, getter, setter)` if the extension is registered. Raises a
`KeyError` otherwise.

> #### Example
>
> ```python
> from spacy.tokens import Span
> Span.set_extension("is_city", default=False)
> extension = Span.get_extension("is_city")
> assert extension == (False, None, None, None)
> ```

| Name        | Description                                                                                                                                        |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`      | Name of the extension. ~~str~~                                                                                                                     |
| **RETURNS** | A `(default, method, getter, setter)` tuple of the extension. ~~Tuple[Optional[Any], Optional[Callable], Optional[Callable], Optional[Callable]]~~ |

## Span.has_extension {#has_extension tag="classmethod" new="2"}

Check whether an extension has been registered on the `Span` class.

> #### Example
>
> ```python
> from spacy.tokens import Span
> Span.set_extension("is_city", default=False)
> assert Span.has_extension("is_city")
> ```

| Name        | Description                                         |
| ----------- | --------------------------------------------------- |
| `name`      | Name of the extension to check. ~~str~~             |
| **RETURNS** | Whether the extension has been registered. ~~bool~~ |

## Span.remove_extension {#remove_extension tag="classmethod" new="2.0.12"}

Remove a previously registered extension.

> #### Example
>
> ```python
> from spacy.tokens import Span
> Span.set_extension("is_city", default=False)
> removed = Span.remove_extension("is_city")
> assert not Span.has_extension("is_city")
> ```

| Name        | Description                                                                                                                                                |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`      | Name of the extension. ~~str~~                                                                                                                             |
| **RETURNS** | A `(default, method, getter, setter)` tuple of the removed extension. ~~Tuple[Optional[Any], Optional[Callable], Optional[Callable], Optional[Callable]]~~ |

## Span.char_span {#char_span tag="method" new="2.2.4"}

Create a `Span` object from the slice `span.text[start:end]`. Returns `None` if
the character indices don't map to a valid span.

> #### Example
>
> ```python
> doc = nlp("I like New York")
> span = doc[1:4].char_span(5, 13, label="GPE")
> assert span.text == "New York"
> ```

| Name                                 | Description                                                                               |
| ------------------------------------ | ----------------------------------------------------------------------------------------- |
| `start`                              | The index of the first character of the span. ~~int~~                                     |
| `end`                                | The index of the last character after the span. ~~int~~                                   |
| `label`                              | A label to attach to the span, e.g. for named entities. ~~Union[int, str]~~               |
| `kb_id` <Tag variant="new">2.2</Tag> | An ID from a knowledge base to capture the meaning of a named entity. ~~Union[int, str]~~ |
| `vector`                             | A meaning representation of the span. ~~numpy.ndarray[ndim=1, dtype=float32]~~            |
| **RETURNS**                          | The newly constructed object or `None`. ~~Optional[Span]~~                                |

## Span.similarity {#similarity tag="method" model="vectors"}

Make a semantic similarity estimate. The default estimate is cosine similarity
using an average of word vectors.

> #### Example
>
> ```python
> doc = nlp("green apples and red oranges")
> green_apples = doc[:2]
> red_oranges = doc[3:]
> apples_oranges = green_apples.similarity(red_oranges)
> oranges_apples = red_oranges.similarity(green_apples)
> assert apples_oranges == oranges_apples
> ```

| Name        | Description                                                                                                                      |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `other`     | The object to compare with. By default, accepts `Doc`, `Span`, `Token` and `Lexeme` objects. ~~Union[Doc, Span, Token, Lexeme]~~ |
| **RETURNS** | A scalar similarity score. Higher is more similar. ~~float~~                                                                     |

## Span.get_lca_matrix {#get_lca_matrix tag="method"}

Calculates the lowest common ancestor matrix for a given `Span`. Returns LCA
matrix containing the integer index of the ancestor, or `-1` if no common
ancestor is found, e.g. if span excludes a necessary ancestor.

> #### Example
>
> ```python
> doc = nlp("I like New York in Autumn")
> span = doc[1:4]
> matrix = span.get_lca_matrix()
> # array([[0, 0, 0], [0, 1, 2], [0, 2, 2]], dtype=int32)
> ```

| Name        | Description                                                                             |
| ----------- | --------------------------------------------------------------------------------------- |
| **RETURNS** | The lowest common ancestor matrix of the `Span`. ~~numpy.ndarray[ndim=2, dtype=int32]~~ |

## Span.to_array {#to_array tag="method" new="2"}

Given a list of `M` attribute IDs, export the tokens to a numpy `ndarray` of
shape `(N, M)`, where `N` is the length of the document. The values will be
32-bit integers.

> #### Example
>
> ```python
> from spacy.attrs import LOWER, POS, ENT_TYPE, IS_ALPHA
> doc = nlp("I like New York in Autumn.")
> span = doc[2:3]
> # All strings mapped to integers, for easy export to numpy
> np_array = span.to_array([LOWER, POS, ENT_TYPE, IS_ALPHA])
> ```

| Name        | Description                                                                                                                              |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `attr_ids`  | A list of attributes (int IDs or string names) or a single attribute (int ID or string name). ~~Union[int, str, List[Union[int, str]]]~~ |
| **RETURNS** | The exported attributes as a numpy array. ~~Union[numpy.ndarray[ndim=2, dtype=uint64], numpy.ndarray[ndim=1, dtype=uint64]]~~            |

## Span.ents {#ents tag="property" new="2.0.13" model="ner"}

The named entities that fall completely within the span. Returns a tuple of
`Span` objects.

> #### Example
>
> ```python
> doc = nlp("Mr. Best flew to New York on Saturday morning.")
> span = doc[0:6]
> ents = list(span.ents)
> assert ents[0].label == 346
> assert ents[0].label_ == "PERSON"
> assert ents[0].text == "Mr. Best"
> ```

| Name        | Description                                                       |
| ----------- | ----------------------------------------------------------------- |
| **RETURNS** | Entities in the span, one `Span` per entity. ~~Tuple[Span, ...]~~ |

## Span.noun_chunks {#noun_chunks tag="property" model="parser"}

Iterate over the base noun phrases in the span. Yields base noun-phrase `Span`
objects, if the document has been syntactically parsed. A base noun phrase, or
"NP chunk", is a noun phrase that does not permit other NPs to be nested within
it – so no NP-level coordination, no prepositional phrases, and no relative
clauses.

If the `noun_chunk` [syntax iterator](/usage/linguistic-features#language-data)
has not been implemeted for the given language, a `NotImplementedError` is
raised.

> #### Example
>
> ```python
> doc = nlp("A phrase with another phrase occurs.")
> span = doc[3:5]
> chunks = list(span.noun_chunks)
> assert len(chunks) == 1
> assert chunks[0].text == "another phrase"
> ```

| Name       | Description                       |
| ---------- | --------------------------------- |
| **YIELDS** | Noun chunks in the span. ~~Span~~ |

## Span.as_doc {#as_doc tag="method"}

Create a new `Doc` object corresponding to the `Span`, with a copy of the data.

When calling this on many spans from the same doc, passing in a precomputed
array representation of the doc using the `array_head` and `array` args can save
time.

> #### Example
>
> ```python
> doc = nlp("I like New York in Autumn.")
> span = doc[2:4]
> doc2 = span.as_doc()
> assert doc2.text == "New York"
> ```

| Name             | Description                                                                                                          |
| ---------------- | -------------------------------------------------------------------------------------------------------------------- |
| `copy_user_data` | Whether or not to copy the original doc's user data. ~~bool~~                                                        |
| `array_head`     | Precomputed array attributes (headers) of the original doc, as generated by `Doc._get_array_attrs()`. ~~Tuple~~      |
| `array`          | Precomputed array version of the original doc as generated by [`Doc.to_array`](/api/doc#to_array). ~~numpy.ndarray~~ |
| **RETURNS**      | A `Doc` object of the `Span`'s content. ~~Doc~~                                                                      |

## Span.root {#root tag="property" model="parser"}

The token with the shortest path to the root of the sentence (or the root
itself). If multiple tokens are equally high in the tree, the first token is
taken.

> #### Example
>
> ```python
> doc = nlp("I like New York in Autumn.")
> i, like, new, york, in_, autumn, dot = range(len(doc))
> assert doc[new].head.text == "York"
> assert doc[york].head.text == "like"
> new_york = doc[new:york+1]
> assert new_york.root.text == "York"
> ```

| Name        | Description               |
| ----------- | ------------------------- |
| **RETURNS** | The root token. ~~Token~~ |

## Span.conjuncts {#conjuncts tag="property" model="parser"}

A tuple of tokens coordinated to `span.root`.

> #### Example
>
> ```python
> doc = nlp("I like apples and oranges")
> apples_conjuncts = doc[2:3].conjuncts
> assert [t.text for t in apples_conjuncts] == ["oranges"]
> ```

| Name        | Description                                   |
| ----------- | --------------------------------------------- |
| **RETURNS** | The coordinated tokens. ~~Tuple[Token, ...]~~ |

## Span.lefts {#lefts tag="property" model="parser"}

Tokens that are to the left of the span, whose heads are within the span.

> #### Example
>
> ```python
> doc = nlp("I like New York in Autumn.")
> lefts = [t.text for t in doc[3:7].lefts]
> assert lefts == ["New"]
> ```

| Name       | Description                                    |
| ---------- | ---------------------------------------------- |
| **YIELDS** | A left-child of a token of the span. ~~Token~~ |

## Span.rights {#rights tag="property" model="parser"}

Tokens that are to the right of the span, whose heads are within the span.

> #### Example
>
> ```python
> doc = nlp("I like New York in Autumn.")
> rights = [t.text for t in doc[2:4].rights]
> assert rights == ["in"]
> ```

| Name       | Description                                     |
| ---------- | ----------------------------------------------- |
| **YIELDS** | A right-child of a token of the span. ~~Token~~ |

## Span.n_lefts {#n_lefts tag="property" model="parser"}

The number of tokens that are to the left of the span, whose heads are within
the span.

> #### Example
>
> ```python
> doc = nlp("I like New York in Autumn.")
> assert doc[3:7].n_lefts == 1
> ```

| Name        | Description                              |
| ----------- | ---------------------------------------- |
| **RETURNS** | The number of left-child tokens. ~~int~~ |

## Span.n_rights {#n_rights tag="property" model="parser"}

The number of tokens that are to the right of the span, whose heads are within
the span.

> #### Example
>
> ```python
> doc = nlp("I like New York in Autumn.")
> assert doc[2:4].n_rights == 1
> ```

| Name        | Description                               |
| ----------- | ----------------------------------------- |
| **RETURNS** | The number of right-child tokens. ~~int~~ |

## Span.subtree {#subtree tag="property" model="parser"}

Tokens within the span and tokens which descend from them.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> subtree = [t.text for t in doc[:3].subtree]
> assert subtree == ["Give", "it", "back", "!"]
> ```

| Name       | Description                                                 |
| ---------- | ----------------------------------------------------------- |
| **YIELDS** | A token within the span, or a descendant from it. ~~Token~~ |

## Span.has_vector {#has_vector tag="property" model="vectors"}

A boolean value indicating whether a word vector is associated with the object.

> #### Example
>
> ```python
> doc = nlp("I like apples")
> assert doc[1:].has_vector
> ```

| Name        | Description                                           |
| ----------- | ----------------------------------------------------- |
| **RETURNS** | Whether the span has a vector data attached. ~~bool~~ |

## Span.vector {#vector tag="property" model="vectors"}

A real-valued meaning representation. Defaults to an average of the token
vectors.

> #### Example
>
> ```python
> doc = nlp("I like apples")
> assert doc[1:].vector.dtype == "float32"
> assert doc[1:].vector.shape == (300,)
> ```

| Name        | Description                                                                                     |
| ----------- | ----------------------------------------------------------------------------------------------- |
| **RETURNS** | A 1-dimensional array representing the span's vector. ~~`numpy.ndarray[ndim=1, dtype=float32]~~ |

## Span.vector_norm {#vector_norm tag="property" model="vectors"}

The L2 norm of the span's vector representation.

> #### Example
>
> ```python
> doc = nlp("I like apples")
> doc[1:].vector_norm # 4.800883928527915
> doc[2:].vector_norm # 6.895897646384268
> assert doc[1:].vector_norm != doc[2:].vector_norm
> ```

| Name        | Description                                         |
| ----------- | --------------------------------------------------- |
| **RETURNS** | The L2 norm of the vector representation. ~~float~~ |

## Span.sent {#sent tag="property" model="sentences"}

The sentence span that this span is a part of. This property is only available
when [sentence boundaries](/usage/linguistic-features#sbd) have been set on the
document by the `parser`, `senter`, `sentencizer` or some custom function. It
will raise an error otherwise.

If the span happens to cross sentence boundaries, only the first sentence will
be returned. If it is required that the sentence always includes the full span,
the result can be adjusted as such:

```python
sent = span.sent
sent = doc[sent.start : max(sent.end, span.end)]
```

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> span = doc[1:3]
> assert span.sent.text == "Give it back!"
> ```

| Name        | Description                                             |
| ----------- | ------------------------------------------------------- |
| **RETURNS** | The sentence span that this span is a part of. ~~Span~~ |

## Span.sents {#sents tag="property" model="sentences" new="3.2.1"}

Returns a generator over the sentences the span belongs to. This property is
only available when [sentence boundaries](/usage/linguistic-features#sbd) have
been set on the document by the `parser`, `senter`, `sentencizer` or some custom
function. It will raise an error otherwise.

If the span happens to cross sentence boundaries, all sentences the span
overlaps with will be returned.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> span = doc[2:4]
> assert len(span.sents) == 2
> ```

| Name        | Description                                                                |
| ----------- | -------------------------------------------------------------------------- |
| **RETURNS** | A generator yielding sentences this `Span` is a part of ~~Iterable[Span]~~ |

## Attributes {#attributes}

| Name                                    | Description                                                                                                                   |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `doc`                                   | The parent document. ~~Doc~~                                                                                                  |
| `tensor` <Tag variant="new">2.1.7</Tag> | The span's slice of the parent `Doc`'s tensor. ~~numpy.ndarray~~                                                              |
| `start`                                 | The token offset for the start of the span. ~~int~~                                                                           |
| `end`                                   | The token offset for the end of the span. ~~int~~                                                                             |
| `start_char`                            | The character offset for the start of the span. ~~int~~                                                                       |
| `end_char`                              | The character offset for the end of the span. ~~int~~                                                                         |
| `text`                                  | A string representation of the span text. ~~str~~                                                                             |
| `text_with_ws`                          | The text content of the span with a trailing whitespace character if the last token has one. ~~str~~                          |
| `orth`                                  | ID of the verbatim text content. ~~int~~                                                                                      |
| `orth_`                                 | Verbatim text content (identical to `Span.text`). Exists mostly for consistency with the other attributes. ~~str~~            |
| `label`                                 | The hash value of the span's label. ~~int~~                                                                                   |
| `label_`                                | The span's label. ~~str~~                                                                                                     |
| `lemma_`                                | The span's lemma. Equivalent to `"".join(token.text_with_ws for token in span)`. ~~str~~                                      |
| `kb_id`                                 | The hash value of the knowledge base ID referred to by the span. ~~int~~                                                      |
| `kb_id_`                                | The knowledge base ID referred to by the span. ~~str~~                                                                        |
| `ent_id`                                | The hash value of the named entity the root token is an instance of. ~~int~~                                                  |
| `ent_id_`                               | The string ID of the named entity the root token is an instance of. ~~str~~                                                   |
| `id`                                    | The hash value of the span's ID. ~~int~~                                                                                      |
| `id_`                                   | The span's ID. ~~str~~                                                                                                        |
| `sentiment`                             | A scalar value indicating the positivity or negativity of the span. ~~float~~                                                 |
| `_`                                     | User space for adding custom [attribute extensions](/usage/processing-pipelines#custom-components-attributes). ~~Underscore~~ |
