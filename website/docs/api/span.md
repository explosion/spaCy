---
title: Span
tag: class
source: spacy/tokens/span.pyx
---

A slice from a [`Doc`](/api/doc) object.

## Span.\_\_init\_\_ {#init tag="method"}

Create a Span object from the `slice doc[start : end]`.

> #### Example
>
> ```python
> doc = nlp(u"Give it back! He pleaded.")
> span = doc[1:4]
> assert [t.text for t in span] ==  [u"it", u"back", u"!"]
> ```

| Name        | Type                                     | Description                                                                                                 |
| ----------- | ---------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `doc`       | `Doc`                                    | The parent document.                                                                                        |
| `start`     | int                                      | The index of the first token of the span.                                                                   |
| `end`       | int                                      | The index of the first token after the span.                                                                |
| `label`     | int / unicode                            | A label to attach to the span, e.g. for named entities. As of v2.1, the label can also be a unicode string. |
| `vector`    | `numpy.ndarray[ndim=1, dtype='float32']` | A meaning representation of the span.                                                                       |
| **RETURNS** | `Span`                                   | The newly constructed object.                                                                               |

## Span.\_\_getitem\_\_ {#getitem tag="method"}

Get a `Token` object.

> #### Example
>
> ```python
> doc = nlp(u"Give it back! He pleaded.")
> span = doc[1:4]
> assert span[1].text == "back"
> ```

| Name        | Type    | Description                             |
| ----------- | ------- | --------------------------------------- |
| `i`         | int     | The index of the token within the span. |
| **RETURNS** | `Token` | The token at `span[i]`.                 |

Get a `Span` object.

> #### Example
>
> ```python
> doc = nlp(u"Give it back! He pleaded.")
> span = doc[1:4]
> assert span[1:3].text == u"back!"
> ```

| Name        | Type   | Description                      |
| ----------- | ------ | -------------------------------- |
| `start_end` | tuple  | The slice of the span to get.    |
| **RETURNS** | `Span` | The span at `span[start : end]`. |

## Span.\_\_iter\_\_ {#iter tag="method"}

Iterate over `Token` objects.

> #### Example
>
> ```python
> doc = nlp(u"Give it back! He pleaded.")
> span = doc[1:4]
> assert [t.text for t in span] == [u"it", u"back", u"!"]
> ```

| Name       | Type    | Description       |
| ---------- | ------- | ----------------- |
| **YIELDS** | `Token` | A `Token` object. |

## Span.\_\_len\_\_ {#len tag="method"}

Get the number of tokens in the span.

> #### Example
>
> ```python
> doc = nlp(u"Give it back! He pleaded.")
> span = doc[1:4]
> assert len(span) == 3
> ```

| Name        | Type | Description                       |
| ----------- | ---- | --------------------------------- |
| **RETURNS** | int  | The number of tokens in the span. |

## Span.set_extension {#set_extension tag="classmethod" new="2"}

Define a custom attribute on the `Span` which becomes available via `Span._`.
For details, see the documentation on
[custom attributes](/usage/processing-pipelines#custom-components-attributes).

> #### Example
>
> ```python
> from spacy.tokens import Span
> city_getter = lambda span: any(city in span.text for city in (u"New York", u"Paris", u"Berlin"))
> Span.set_extension("has_city", getter=city_getter)
> doc = nlp(u"I like New York in Autumn")
> assert doc[1:4]._.has_city
> ```

| Name      | Type     | Description                                                                                                                           |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `name`    | unicode  | Name of the attribute to set by the extension. For example, `'my_attr'` will be available as `span._.my_attr`.                        |
| `default` | -        | Optional default value of the attribute if no getter or method is defined.                                                            |
| `method`  | callable | Set a custom method on the object, for example `span._.compare(other_span)`.                                                          |
| `getter`  | callable | Getter function that takes the object and returns an attribute value. Is called when the user accesses the `._` attribute.            |
| `setter`  | callable | Setter function that takes the `Span` and a value, and modifies the object. Is called when the user writes to the `Span._` attribute. |

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

| Name        | Type    | Description                                                   |
| ----------- | ------- | ------------------------------------------------------------- |
| `name`      | unicode | Name of the extension.                                        |
| **RETURNS** | tuple   | A `(default, method, getter, setter)` tuple of the extension. |

## Span.has_extension {#has_extension tag="classmethod" new="2"}

Check whether an extension has been registered on the `Span` class.

> #### Example
>
> ```python
> from spacy.tokens import Span
> Span.set_extension("is_city", default=False)
> assert Span.has_extension("is_city")
> ```

| Name        | Type    | Description                                |
| ----------- | ------- | ------------------------------------------ |
| `name`      | unicode | Name of the extension to check.            |
| **RETURNS** | bool    | Whether the extension has been registered. |

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

| Name        | Type    | Description                                                           |
| ----------- | ------- | --------------------------------------------------------------------- |
| `name`      | unicode | Name of the extension.                                                |
| **RETURNS** | tuple   | A `(default, method, getter, setter)` tuple of the removed extension. |

## Span.similarity {#similarity tag="method" model="vectors"}

Make a semantic similarity estimate. The default estimate is cosine similarity
using an average of word vectors.

> #### Example
>
> ```python
> doc = nlp(u"green apples and red oranges")
> green_apples = doc[:2]
> red_oranges = doc[3:]
> apples_oranges = green_apples.similarity(red_oranges)
> oranges_apples = red_oranges.similarity(green_apples)
> assert apples_oranges == oranges_apples
> ```

| Name        | Type  | Description                                                                                  |
| ----------- | ----- | -------------------------------------------------------------------------------------------- |
| `other`     | -     | The object to compare with. By default, accepts `Doc`, `Span`, `Token` and `Lexeme` objects. |
| **RETURNS** | float | A scalar similarity score. Higher is more similar.                                           |

## Span.get_lca_matrix {#get_lca_matrix tag="method"}

Calculates the lowest common ancestor matrix for a given `Span`. Returns LCA
matrix containing the integer index of the ancestor, or `-1` if no common
ancestor is found, e.g. if span excludes a necessary ancestor.

> #### Example
>
> ```python
> doc = nlp(u"I like New York in Autumn")
> span = doc[1:4]
> matrix = span.get_lca_matrix()
> # array([[0, 0, 0], [0, 1, 2], [0, 2, 2]], dtype=int32)
> ```

| Name        | Type                                   | Description                                      |
| ----------- | -------------------------------------- | ------------------------------------------------ |
| **RETURNS** | `numpy.ndarray[ndim=2, dtype='int32']` | The lowest common ancestor matrix of the `Span`. |

## Span.to_array {#to_array tag="method" new="2"}

Given a list of `M` attribute IDs, export the tokens to a numpy `ndarray` of
shape `(N, M)`, where `N` is the length of the document. The values will be
32-bit integers.

> #### Example
>
> ```python
> from spacy.attrs import LOWER, POS, ENT_TYPE, IS_ALPHA
> doc = nlp(u"I like New York in Autumn.")
> span = doc[2:3]
> # All strings mapped to integers, for easy export to numpy
> np_array = span.to_array([LOWER, POS, ENT_TYPE, IS_ALPHA])
> ```

| Name        | Type                          | Description                                                                                              |
| ----------- | ----------------------------- | -------------------------------------------------------------------------------------------------------- |
| `attr_ids`  | list                          | A list of attribute ID ints.                                                                             |
| **RETURNS** | `numpy.ndarray[long, ndim=2]` | A feature matrix, with one row per word, and one column per attribute indicated in the input `attr_ids`. |

## Span.merge {#merge tag="method"}

<Infobox title="Deprecation note" variant="danger">

As of v2.1.0, `Span.merge` still works but is considered deprecated. You should
use the new and less error-prone [`Doc.retokenize`](/api/doc#retokenize)
instead.

</Infobox>

Retokenize the document, such that the span is merged into a single token.

> #### Example
>
> ```python
> doc = nlp(u"I like New York in Autumn.")
> span = doc[2:4]
> span.merge()
> assert len(doc) == 6
> assert doc[2].text == u"New York"
> ```

| Name           | Type    | Description                                                                                                               |
| -------------- | ------- | ------------------------------------------------------------------------------------------------------------------------- |
| `**attributes` | -       | Attributes to assign to the merged token. By default, attributes are inherited from the syntactic root token of the span. |
| **RETURNS**    | `Token` | The newly merged token.                                                                                                   |

## Span.ents {#ents tag="property" new="2.0.12" model="ner"}

The named entities in the span. Returns a tuple of named entity `Span` objects,
if the entity recognizer has been applied.

> #### Example
>
> ```python
> doc = nlp(u"Mr. Best flew to New York on Saturday morning.")
> span = doc[0:6]
> ents = list(span.ents)
> assert ents[0].label == 346
> assert ents[0].label_ == "PERSON"
> assert ents[0].text == u"Mr. Best"
> ```

| Name        | Type  | Description                                  |
| ----------- | ----- | -------------------------------------------- |
| **RETURNS** | tuple | Entities in the span, one `Span` per entity. |

## Span.as_doc {#as_doc tag="method"}

Create a new `Doc` object corresponding to the `Span`, with a copy of the data.

> #### Example
>
> ```python
> doc = nlp(u"I like New York in Autumn.")
> span = doc[2:4]
> doc2 = span.as_doc()
> assert doc2.text == u"New York"
> ```

| Name        | Type  | Description                             |
| ----------- | ----- | --------------------------------------- |
| **RETURNS** | `Doc` | A `Doc` object of the `Span`'s content. |

## Span.root {#root tag="property" model="parser"}

The token with the shortest path to the root of the sentence (or the root
itself). If multiple tokens are equally high in the tree, the first token is
taken.

> #### Example
>
> ```python
> doc = nlp(u"I like New York in Autumn.")
> i, like, new, york, in_, autumn, dot = range(len(doc))
> assert doc[new].head.text == u"York"
> assert doc[york].head.text == u"like"
> new_york = doc[new:york+1]
> assert new_york.root.text == u"York"
> ```

| Name        | Type    | Description     |
| ----------- | ------- | --------------- |
| **RETURNS** | `Token` | The root token. |

## Span.conjuncts {#conjuncts tag="property" model="parser"}

A tuple of tokens coordinated to `span.root`.

> #### Example
>
> ```python
> doc = nlp(u"I like apples and oranges")
> apples_conjuncts = doc[2:3].conjuncts
> assert [t.text for t in apples_conjuncts] == [u"oranges"]
> ```

| Name        | Type    | Description             |
| ----------- | ------- | ----------------------- |
| **RETURNS** | `tuple` | The coordinated tokens. |

## Span.lefts {#lefts tag="property" model="parser"}

Tokens that are to the left of the span, whose heads are within the span.

> #### Example
>
> ```python
> doc = nlp(u"I like New York in Autumn.")
> lefts = [t.text for t in doc[3:7].lefts]
> assert lefts == [u"New"]
> ```

| Name       | Type    | Description                          |
| ---------- | ------- | ------------------------------------ |
| **YIELDS** | `Token` | A left-child of a token of the span. |

## Span.rights {#rights tag="property" model="parser"}

Tokens that are to the right of the span, whose heads are within the span.

> #### Example
>
> ```python
> doc = nlp(u"I like New York in Autumn.")
> rights = [t.text for t in doc[2:4].rights]
> assert rights == [u"in"]
> ```

| Name       | Type    | Description                           |
| ---------- | ------- | ------------------------------------- |
| **YIELDS** | `Token` | A right-child of a token of the span. |

## Span.n_lefts {#n_lefts tag="property" model="parser"}

The number of tokens that are to the left of the span, whose heads are within
the span.

> #### Example
>
> ```python
> doc = nlp(u"I like New York in Autumn.")
> assert doc[3:7].n_lefts == 1
> ```

| Name        | Type | Description                      |
| ----------- | ---- | -------------------------------- |
| **RETURNS** | int  | The number of left-child tokens. |

## Span.n_rights {#n_rights tag="property" model="parser"}

The number of tokens that are to the right of the span, whose heads are within
the span.

> #### Example
>
> ```python
> doc = nlp(u"I like New York in Autumn.")
> assert doc[2:4].n_rights == 1
> ```

| Name        | Type | Description                       |
| ----------- | ---- | --------------------------------- |
| **RETURNS** | int  | The number of right-child tokens. |

## Span.subtree {#subtree tag="property" model="parser"}

Tokens within the span and tokens which descend from them.

> #### Example
>
> ```python
> doc = nlp(u"Give it back! He pleaded.")
> subtree = [t.text for t in doc[:3].subtree]
> assert subtree == [u"Give", u"it", u"back", u"!"]
> ```

| Name       | Type    | Description                                       |
| ---------- | ------- | ------------------------------------------------- |
| **YIELDS** | `Token` | A token within the span, or a descendant from it. |

## Span.has_vector {#has_vector tag="property" model="vectors"}

A boolean value indicating whether a word vector is associated with the object.

> #### Example
>
> ```python
> doc = nlp(u"I like apples")
> assert doc[1:].has_vector
> ```

| Name        | Type | Description                                  |
| ----------- | ---- | -------------------------------------------- |
| **RETURNS** | bool | Whether the span has a vector data attached. |

## Span.vector {#vector tag="property" model="vectors"}

A real-valued meaning representation. Defaults to an average of the token
vectors.

> #### Example
>
> ```python
> doc = nlp(u"I like apples")
> assert doc[1:].vector.dtype == "float32"
> assert doc[1:].vector.shape == (300,)
> ```

| Name        | Type                                     | Description                                         |
| ----------- | ---------------------------------------- | --------------------------------------------------- |
| **RETURNS** | `numpy.ndarray[ndim=1, dtype='float32']` | A 1D numpy array representing the span's semantics. |

## Span.vector_norm {#vector_norm tag="property" model="vectors"}

The L2 norm of the span's vector representation.

> #### Example
>
> ```python
> doc = nlp(u"I like apples")
> doc[1:].vector_norm # 4.800883928527915
> doc[2:].vector_norm # 6.895897646384268
> assert doc[1:].vector_norm != doc[2:].vector_norm
> ```

| Name        | Type  | Description                               |
| ----------- | ----- | ----------------------------------------- |
| **RETURNS** | float | The L2 norm of the vector representation. |

## Attributes {#attributes}

| Name           | Type         | Description                                                                                                    |
| -------------- | ------------ | -------------------------------------------------------------------------------------------------------------- |
| `doc`          | `Doc`        | The parent document.                                                                                           |
| `sent`         | `Span`       | The sentence span that this span is a part of.                                                                 |
| `start`        | int          | The token offset for the start of the span.                                                                    |
| `end`          | int          | The token offset for the end of the span.                                                                      |
| `start_char`   | int          | The character offset for the start of the span.                                                                |
| `end_char`     | int          | The character offset for the end of the span.                                                                  |
| `text`         | unicode      | A unicode representation of the span text.                                                                     |
| `text_with_ws` | unicode      | The text content of the span with a trailing whitespace character if the last token has one.                   |
| `orth`         | int          | ID of the verbatim text content.                                                                               |
| `orth_`        | unicode      | Verbatim text content (identical to `Span.text`). Exists mostly for consistency with the other attributes.     |
| `label`        | int          | The span's label.                                                                                              |
| `label_`       | unicode      | The span's label.                                                                                              |
| `lemma_`       | unicode      | The span's lemma.                                                                                              |
| `ent_id`       | int          | The hash value of the named entity the token is an instance of.                                                |
| `ent_id_`      | unicode      | The string ID of the named entity the token is an instance of.                                                 |
| `sentiment`    | float        | A scalar value indicating the positivity or negativity of the span.                                            |
| `_`            | `Underscore` | User space for adding custom [attribute extensions](/usage/processing-pipelines#custom-components-attributes). |
