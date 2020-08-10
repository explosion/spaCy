---
title: Token
teaser: An individual token — i.e. a word, punctuation symbol, whitespace, etc.
tag: class
source: spacy/tokens/token.pyx
---

## Token.\_\_init\_\_ {#init tag="method"}

Construct a `Token` object.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> token = doc[0]
> assert token.text == "Give"
> ```

| Name     | Type    | Description                                 |
| -------- | ------- | ------------------------------------------- |
| `vocab`  | `Vocab` | A storage container for lexical types.      |
| `doc`    | `Doc`   | The parent document.                        |
| `offset` | int     | The index of the token within the document. |

## Token.\_\_len\_\_ {#len tag="method"}

The number of unicode characters in the token, i.e. `token.text`.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> token = doc[0]
> assert len(token) == 4
> ```

| Name        | Type | Description                                    |
| ----------- | ---- | ---------------------------------------------- |
| **RETURNS** | int  | The number of unicode characters in the token. |

## Token.set_extension {#set_extension tag="classmethod" new="2"}

Define a custom attribute on the `Token` which becomes available via `Token._`.
For details, see the documentation on
[custom attributes](/usage/processing-pipelines#custom-components-attributes).

> #### Example
>
> ```python
> from spacy.tokens import Token
> fruit_getter = lambda token: token.text in ("apple", "pear", "banana")
> Token.set_extension("is_fruit", getter=fruit_getter)
> doc = nlp("I have an apple")
> assert doc[3]._.is_fruit
> ```

| Name      | Type     | Description                                                                                                                             |
| --------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `name`    | str      | Name of the attribute to set by the extension. For example, `"my_attr"` will be available as `token._.my_attr`.                         |
| `default` | -        | Optional default value of the attribute if no getter or method is defined.                                                              |
| `method`  | callable | Set a custom method on the object, for example `token._.compare(other_token)`.                                                          |
| `getter`  | callable | Getter function that takes the object and returns an attribute value. Is called when the user accesses the `._` attribute.              |
| `setter`  | callable | Setter function that takes the `Token` and a value, and modifies the object. Is called when the user writes to the `Token._` attribute. |
| `force`   | bool     | Force overwriting existing attribute.                                                                                                   |

## Token.get_extension {#get_extension tag="classmethod" new="2"}

Look up a previously registered extension by name. Returns a 4-tuple
`(default, method, getter, setter)` if the extension is registered. Raises a
`KeyError` otherwise.

> #### Example
>
> ```python
> from spacy.tokens import Token
> Token.set_extension("is_fruit", default=False)
> extension = Token.get_extension("is_fruit")
> assert extension == (False, None, None, None)
> ```

| Name        | Type  | Description                                                   |
| ----------- | ----- | ------------------------------------------------------------- |
| `name`      | str   | Name of the extension.                                        |
| **RETURNS** | tuple | A `(default, method, getter, setter)` tuple of the extension. |

## Token.has_extension {#has_extension tag="classmethod" new="2"}

Check whether an extension has been registered on the `Token` class.

> #### Example
>
> ```python
> from spacy.tokens import Token
> Token.set_extension("is_fruit", default=False)
> assert Token.has_extension("is_fruit")
> ```

| Name        | Type | Description                                |
| ----------- | ---- | ------------------------------------------ |
| `name`      | str  | Name of the extension to check.            |
| **RETURNS** | bool | Whether the extension has been registered. |

## Token.remove_extension {#remove_extension tag="classmethod" new=""2.0.11""}

Remove a previously registered extension.

> #### Example
>
> ```python
> from spacy.tokens import Token
> Token.set_extension("is_fruit", default=False)
> removed = Token.remove_extension("is_fruit")
> assert not Token.has_extension("is_fruit")
> ```

| Name        | Type  | Description                                                           |
| ----------- | ----- | --------------------------------------------------------------------- |
| `name`      | str   | Name of the extension.                                                |
| **RETURNS** | tuple | A `(default, method, getter, setter)` tuple of the removed extension. |

## Token.check_flag {#check_flag tag="method"}

Check the value of a boolean flag.

> #### Example
>
> ```python
> from spacy.attrs import IS_TITLE
> doc = nlp("Give it back! He pleaded.")
> token = doc[0]
> assert token.check_flag(IS_TITLE) == True
> ```

| Name        | Type | Description                            |
| ----------- | ---- | -------------------------------------- |
| `flag_id`   | int  | The attribute ID of the flag to check. |
| **RETURNS** | bool | Whether the flag is set.               |

## Token.similarity {#similarity tag="method" model="vectors"}

Compute a semantic similarity estimate. Defaults to cosine over vectors.

> #### Example
>
> ```python
> apples, _, oranges = nlp("apples and oranges")
> apples_oranges = apples.similarity(oranges)
> oranges_apples = oranges.similarity(apples)
> assert apples_oranges == oranges_apples
> ```

| Name        | Type  | Description                                                                                  |
| ----------- | ----- | -------------------------------------------------------------------------------------------- |
| other       | -     | The object to compare with. By default, accepts `Doc`, `Span`, `Token` and `Lexeme` objects. |
| **RETURNS** | float | A scalar similarity score. Higher is more similar.                                           |

## Token.nbor {#nbor tag="method"}

Get a neighboring token.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> give_nbor = doc[0].nbor()
> assert give_nbor.text == "it"
> ```

| Name        | Type    | Description                                                 |
| ----------- | ------- | ----------------------------------------------------------- |
| `i`         | int     | The relative position of the token to get. Defaults to `1`. |
| **RETURNS** | `Token` | The token at position `self.doc[self.i+i]`.                 |

## Token.is_ancestor {#is_ancestor tag="method" model="parser"}

Check whether this token is a parent, grandparent, etc. of another in the
dependency tree.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> give = doc[0]
> it = doc[1]
> assert give.is_ancestor(it)
> ```

| Name        | Type    | Description                                           |
| ----------- | ------- | ----------------------------------------------------- |
| descendant  | `Token` | Another token.                                        |
| **RETURNS** | bool    | Whether this token is the ancestor of the descendant. |

## Token.ancestors {#ancestors tag="property" model="parser"}

The rightmost token of this token's syntactic descendants.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> it_ancestors = doc[1].ancestors
> assert [t.text for t in it_ancestors] == ["Give"]
> he_ancestors = doc[4].ancestors
> assert [t.text for t in he_ancestors] == ["pleaded"]
> ```

| Name       | Type    | Description                                                           |
| ---------- | ------- | --------------------------------------------------------------------- |
| **YIELDS** | `Token` | A sequence of ancestor tokens such that `ancestor.is_ancestor(self)`. |

## Token.conjuncts {#conjuncts tag="property" model="parser"}

A tuple of coordinated tokens, not including the token itself.

> #### Example
>
> ```python
> doc = nlp("I like apples and oranges")
> apples_conjuncts = doc[2].conjuncts
> assert [t.text for t in apples_conjuncts] == ["oranges"]
> ```

| Name        | Type    | Description             |
| ----------- | ------- | ----------------------- |
| **RETURNS** | `tuple` | The coordinated tokens. |

## Token.children {#children tag="property" model="parser"}

A sequence of the token's immediate syntactic children.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> give_children = doc[0].children
> assert [t.text for t in give_children] == ["it", "back", "!"]
> ```

| Name       | Type    | Description                                 |
| ---------- | ------- | ------------------------------------------- |
| **YIELDS** | `Token` | A child token such that `child.head==self`. |

## Token.lefts {#lefts tag="property" model="parser"}

The leftward immediate children of the word, in the syntactic dependency parse.

> #### Example
>
> ```python
> doc = nlp("I like New York in Autumn.")
> lefts = [t.text for t in doc[3].lefts]
> assert lefts == ["New"]
> ```

| Name       | Type    | Description                |
| ---------- | ------- | -------------------------- |
| **YIELDS** | `Token` | A left-child of the token. |

## Token.rights {#rights tag="property" model="parser"}

The rightward immediate children of the word, in the syntactic dependency parse.

> #### Example
>
> ```python
> doc = nlp("I like New York in Autumn.")
> rights = [t.text for t in doc[3].rights]
> assert rights == ["in"]
> ```

| Name       | Type    | Description                 |
| ---------- | ------- | --------------------------- |
| **YIELDS** | `Token` | A right-child of the token. |

## Token.n_lefts {#n_lefts tag="property" model="parser"}

The number of leftward immediate children of the word, in the syntactic
dependency parse.

> #### Example
>
> ```python
> doc = nlp("I like New York in Autumn.")
> assert doc[3].n_lefts == 1
> ```

| Name        | Type | Description                      |
| ----------- | ---- | -------------------------------- |
| **RETURNS** | int  | The number of left-child tokens. |

## Token.n_rights {#n_rights tag="property" model="parser"}

The number of rightward immediate children of the word, in the syntactic
dependency parse.

> #### Example
>
> ```python
> doc = nlp("I like New York in Autumn.")
> assert doc[3].n_rights == 1
> ```

| Name        | Type | Description                       |
| ----------- | ---- | --------------------------------- |
| **RETURNS** | int  | The number of right-child tokens. |

## Token.subtree {#subtree tag="property" model="parser"}

A sequence containing the token and all the token's syntactic descendants.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> give_subtree = doc[0].subtree
> assert [t.text for t in give_subtree] == ["Give", "it", "back", "!"]
> ```

| Name       | Type    | Description                                                                |
| ---------- | ------- | -------------------------------------------------------------------------- |
| **YIELDS** | `Token` | A descendant token such that `self.is_ancestor(token)` or `token == self`. |

## Token.is_sent_start {#is_sent_start tag="property" new="2"}

A boolean value indicating whether the token starts a sentence. `None` if
unknown. Defaults to `True` for the first token in the `Doc`.

> #### Example
>
> ```python
> doc = nlp("Give it back! He pleaded.")
> assert doc[4].is_sent_start
> assert not doc[5].is_sent_start
> ```

| Name        | Type | Description                          |
| ----------- | ---- | ------------------------------------ |
| **RETURNS** | bool | Whether the token starts a sentence. |

## Token.has_vector {#has_vector tag="property" model="vectors"}

A boolean value indicating whether a word vector is associated with the token.

> #### Example
>
> ```python
> doc = nlp("I like apples")
> apples = doc[2]
> assert apples.has_vector
> ```

| Name        | Type | Description                                   |
| ----------- | ---- | --------------------------------------------- |
| **RETURNS** | bool | Whether the token has a vector data attached. |

## Token.vector {#vector tag="property" model="vectors"}

A real-valued meaning representation.

> #### Example
>
> ```python
> doc = nlp("I like apples")
> apples = doc[2]
> assert apples.vector.dtype == "float32"
> assert apples.vector.shape == (300,)
> ```

| Name        | Type                                     | Description                                          |
| ----------- | ---------------------------------------- | ---------------------------------------------------- |
| **RETURNS** | `numpy.ndarray[ndim=1, dtype="float32"]` | A 1D numpy array representing the token's semantics. |

## Token.vector_norm {#vector_norm tag="property" model="vectors"}

The L2 norm of the token's vector representation.

> #### Example
>
> ```python
> doc = nlp("I like apples and pasta")
> apples = doc[2]
> pasta = doc[4]
> apples.vector_norm  # 6.89589786529541
> pasta.vector_norm  # 7.759851932525635
> assert apples.vector_norm != pasta.vector_norm
> ```

| Name        | Type  | Description                               |
| ----------- | ----- | ----------------------------------------- |
| **RETURNS** | float | The L2 norm of the vector representation. |

## Attributes {#attributes}

| Name                                         | Type                    | Description                                                                                                                                                                                                                                                    |
| -------------------------------------------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc`                                        | `Doc`                   | The parent document.                                                                                                                                                                                                                                           |
| `lex` <Tag variant="new">3</Tag>             | [`Lexeme`](/api/lexeme) | The underlying lexeme.                                                                                                                                                                                                                                         |
| `sent` <Tag variant="new">2.0.12</Tag>       | [`Span`](/api/span)     | The sentence span that this token is a part of.                                                                                                                                                                                                                |
| `text`                                       | str                     | Verbatim text content.                                                                                                                                                                                                                                         |
| `text_with_ws`                               | str                     | Text content, with trailing space character if present.                                                                                                                                                                                                        |
| `whitespace_`                                | str                     | Trailing space character if present.                                                                                                                                                                                                                           |
| `orth`                                       | int                     | ID of the verbatim text content.                                                                                                                                                                                                                               |
| `orth_`                                      | str                     | Verbatim text content (identical to `Token.text`). Exists mostly for consistency with the other attributes.                                                                                                                                                    |
| `vocab`                                      | `Vocab`                 | The vocab object of the parent `Doc`.                                                                                                                                                                                                                          |
| `tensor` <Tag variant="new">2.1.7</Tag>      | `ndarray`               | The tokens's slice of the parent `Doc`'s tensor.                                                                                                                                                                                                               |
| `head`                                       | `Token`                 | The syntactic parent, or "governor", of this token.                                                                                                                                                                                                            |
| `left_edge`                                  | `Token`                 | The leftmost token of this token's syntactic descendants.                                                                                                                                                                                                      |
| `right_edge`                                 | `Token`                 | The rightmost token of this token's syntactic descendants.                                                                                                                                                                                                     |
| `i`                                          | int                     | The index of the token within the parent document.                                                                                                                                                                                                             |
| `ent_type`                                   | int                     | Named entity type.                                                                                                                                                                                                                                             |
| `ent_type_`                                  | str                     | Named entity type.                                                                                                                                                                                                                                             |
| `ent_iob`                                    | int                     | IOB code of named entity tag. `3` means the token begins an entity, `2` means it is outside an entity, `1` means it is inside an entity, and `0` means no entity tag is set.                                                                                   |
| `ent_iob_`                                   | str                     | IOB code of named entity tag. "B" means the token begins an entity, "I" means it is inside an entity, "O" means it is outside an entity, and "" means no entity tag is set.                                                                                    |
| `ent_kb_id` <Tag variant="new">2.2</Tag>     | int                     | Knowledge base ID that refers to the named entity this token is a part of, if any.                                                                                                                                                                             |
| `ent_kb_id_` <Tag variant="new">2.2</Tag>    | str                     | Knowledge base ID that refers to the named entity this token is a part of, if any.                                                                                                                                                                             |
| `ent_id`                                     | int                     | ID of the entity the token is an instance of, if any. Currently not used, but potentially for coreference resolution.                                                                                                                                          |
| `ent_id_`                                    | str                     | ID of the entity the token is an instance of, if any. Currently not used, but potentially for coreference resolution.                                                                                                                                          |
| `lemma`                                      | int                     | Base form of the token, with no inflectional suffixes.                                                                                                                                                                                                         |
| `lemma_`                                     | str                     | Base form of the token, with no inflectional suffixes.                                                                                                                                                                                                         |
| `norm`                                       | int                     | The token's norm, i.e. a normalized form of the token text. Usually set in the language's [tokenizer exceptions](/usage/adding-languages#tokenizer-exceptions) or [norm exceptions](/usage/adding-languages#norm-exceptions).                                  |
| `norm_`                                      | str                     | The token's norm, i.e. a normalized form of the token text. Usually set in the language's [tokenizer exceptions](/usage/adding-languages#tokenizer-exceptions) or [norm exceptions](/usage/adding-languages#norm-exceptions).                                  |
| `lower`                                      | int                     | Lowercase form of the token.                                                                                                                                                                                                                                   |
| `lower_`                                     | str                     | Lowercase form of the token text. Equivalent to `Token.text.lower()`.                                                                                                                                                                                          |
| `shape`                                      | int                     | Transform of the tokens's string, to show orthographic features. Alphabetic characters are replaced by `x` or `X`, and numeric characters are replaced by `d`, and sequences of the same character are truncated after length 4. For example,`"Xxxx"`or`"dd"`. |
| `shape_`                                     | str                     | Transform of the tokens's string, to show orthographic features. Alphabetic characters are replaced by `x` or `X`, and numeric characters are replaced by `d`, and sequences of the same character are truncated after length 4. For example,`"Xxxx"`or`"dd"`. |
| `prefix`                                     | int                     | Hash value of a length-N substring from the start of the token. Defaults to `N=1`.                                                                                                                                                                             |
| `prefix_`                                    | str                     | A length-N substring from the start of the token. Defaults to `N=1`.                                                                                                                                                                                           |
| `suffix`                                     | int                     | Hash value of a length-N substring from the end of the token. Defaults to `N=3`.                                                                                                                                                                               |
| `suffix_`                                    | str                     | Length-N substring from the end of the token. Defaults to `N=3`.                                                                                                                                                                                               |
| `is_alpha`                                   | bool                    | Does the token consist of alphabetic characters? Equivalent to `token.text.isalpha()`.                                                                                                                                                                         |
| `is_ascii`                                   | bool                    | Does the token consist of ASCII characters? Equivalent to `all(ord(c) < 128 for c in token.text)`.                                                                                                                                                             |
| `is_digit`                                   | bool                    | Does the token consist of digits? Equivalent to `token.text.isdigit()`.                                                                                                                                                                                        |
| `is_lower`                                   | bool                    | Is the token in lowercase? Equivalent to `token.text.islower()`.                                                                                                                                                                                               |
| `is_upper`                                   | bool                    | Is the token in uppercase? Equivalent to `token.text.isupper()`.                                                                                                                                                                                               |
| `is_title`                                   | bool                    | Is the token in titlecase? Equivalent to `token.text.istitle()`.                                                                                                                                                                                               |
| `is_punct`                                   | bool                    | Is the token punctuation?                                                                                                                                                                                                                                      |
| `is_left_punct`                              | bool                    | Is the token a left punctuation mark, e.g. `"("` ?                                                                                                                                                                                                             |
| `is_right_punct`                             | bool                    | Is the token a right punctuation mark, e.g. `")"` ?                                                                                                                                                                                                            |
| `is_space`                                   | bool                    | Does the token consist of whitespace characters? Equivalent to `token.text.isspace()`.                                                                                                                                                                         |
| `is_bracket`                                 | bool                    | Is the token a bracket?                                                                                                                                                                                                                                        |
| `is_quote`                                   | bool                    | Is the token a quotation mark?                                                                                                                                                                                                                                 |
| `is_currency` <Tag variant="new">2.0.8</Tag> | bool                    | Is the token a currency symbol?                                                                                                                                                                                                                                |
| `like_url`                                   | bool                    | Does the token resemble a URL?                                                                                                                                                                                                                                 |
| `like_num`                                   | bool                    | Does the token represent a number? e.g. "10.9", "10", "ten", etc.                                                                                                                                                                                              |
| `like_email`                                 | bool                    | Does the token resemble an email address?                                                                                                                                                                                                                      |
| `is_oov`                                     | bool                    | Does the token have a word vector?                                                                                                                                                                                                                             |
| `is_stop`                                    | bool                    | Is the token part of a "stop list"?                                                                                                                                                                                                                            |
| `pos`                                        | int                     | Coarse-grained part-of-speech from the [Universal POS tag set](https://universaldependencies.org/docs/u/pos/).                                                                                                                                                 |
| `pos_`                                       | str                     | Coarse-grained part-of-speech from the [Universal POS tag set](https://universaldependencies.org/docs/u/pos/).                                                                                                                                                 |
| `tag`                                        | int                     | Fine-grained part-of-speech.                                                                                                                                                                                                                                   |
| `tag_`                                       | str                     | Fine-grained part-of-speech.                                                                                                                                                                                                                                   |
| `morph`                                      | `MorphAnalysis`         | Morphological analysis.                                                                                                                                                                                                                                        |
| `morph_`                                     | str                     | Morphological analysis in UD FEATS format.                                                                                                                                                                                                                     |
| `dep`                                        | int                     | Syntactic dependency relation.                                                                                                                                                                                                                                 |
| `dep_`                                       | str                     | Syntactic dependency relation.                                                                                                                                                                                                                                 |
| `lang`                                       | int                     | Language of the parent document's vocabulary.                                                                                                                                                                                                                  |
| `lang_`                                      | str                     | Language of the parent document's vocabulary.                                                                                                                                                                                                                  |
| `prob`                                       | float                   | Smoothed log probability estimate of token's word type (context-independent entry in the vocabulary).                                                                                                                                                          |
| `idx`                                        | int                     | The character offset of the token within the parent document.                                                                                                                                                                                                  |
| `sentiment`                                  | float                   | A scalar value indicating the positivity or negativity of the token.                                                                                                                                                                                           |
| `lex_id`                                     | int                     | Sequential ID of the token's lexical type, used to index into tables, e.g. for word vectors.                                                                                                                                                                   |
| `rank`                                       | int                     | Sequential ID of the token's lexical type, used to index into tables, e.g. for word vectors.                                                                                                                                                                   |
| `cluster`                                    | int                     | Brown cluster ID.                                                                                                                                                                                                                                              |
| `_`                                          | `Underscore`            | User space for adding custom [attribute extensions](/usage/processing-pipelines#custom-components-attributes).                                                                                                                                                 |
