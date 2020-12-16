---
title: Cython Structs
teaser: C-language objects that let you group variables together
next: /api/cython-classes
menu:
  - ['TokenC', 'tokenc']
  - ['LexemeC', 'lexemec']
---

## TokenC {#tokenc tag="C struct" source="spacy/structs.pxd"}

Cython data container for the `Token` object.

> #### Example
>
> ```python
> token = &doc.c[3]
> token_ptr = &doc.c[3]
> ```

| Name         | Type                                   | Description                                                                                                                                                                                                                                                                                                                         |
| ------------ | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lex`        | `const LexemeC*`                       | A pointer to the lexeme for the token.                                                                                                                                                                                                                                                                                              |
| `morph`      | `uint64_t`                             | An ID allowing lookup of morphological attributes.                                                                                                                                                                                                                                                                                  |
| `pos`        | `univ_pos_t`                           | Coarse-grained part-of-speech tag.                                                                                                                                                                                                                                                                                                  |
| `spacy`      | `bint`                                 | A binary value indicating whether the token has trailing whitespace.                                                                                                                                                                                                                                                                |
| `tag`        | <Abbr title="uint64_t">`attr_t`</Abbr> | Fine-grained part-of-speech tag.                                                                                                                                                                                                                                                                                                    |
| `idx`        | `int`                                  | The character offset of the token within the parent document.                                                                                                                                                                                                                                                                       |
| `lemma`      | <Abbr title="uint64_t">`attr_t`</Abbr> | Base form of the token, with no inflectional suffixes.                                                                                                                                                                                                                                                                              |
| `sense`      | <Abbr title="uint64_t">`attr_t`</Abbr> | Space for storing a word sense ID, currently unused.                                                                                                                                                                                                                                                                                |
| `head`       | `int`                                  | Offset of the syntactic parent relative to the token.                                                                                                                                                                                                                                                                               |
| `dep`        | <Abbr title="uint64_t">`attr_t`</Abbr> | Syntactic dependency relation.                                                                                                                                                                                                                                                                                                      |
| `l_kids`     | `uint32_t`                             | Number of left children.                                                                                                                                                                                                                                                                                                            |
| `r_kids`     | `uint32_t`                             | Number of right children.                                                                                                                                                                                                                                                                                                           |
| `l_edge`     | `uint32_t`                             | Offset of the leftmost token of this token's syntactic descendants.                                                                                                                                                                                                                                                                 |
| `r_edge`     | `uint32_t`                             | Offset of the rightmost token of this token's syntactic descendants.                                                                                                                                                                                                                                                                |
| `sent_start` | `int`                                  | Ternary value indicating whether the token is the first word of a sentence. `0` indicates a missing value, `-1` indicates `False` and `1` indicates `True`. The default value, 0, is interpreted as no sentence break. Sentence boundary detectors will usually set 0 for all tokens except tokens that follow a sentence boundary. |
| `ent_iob`    | `int`                                  | IOB code of named entity tag. `0` indicates a missing value, `1` indicates `I`, `2` indicates `0` and `3` indicates `B`.                                                                                                                                                                                                            |
| `ent_type`   | <Abbr title="uint64_t">`attr_t`</Abbr> | Named entity type.                                                                                                                                                                                                                                                                                                                  |
| `ent_id`     | <Abbr title="uint64_t">`attr_t`</Abbr> | ID of the entity the token is an instance of, if any. Currently not used, but potentially for coreference resolution.                                                                                                                                                                                                               |

### Token.get_struct_attr {#token_get_struct_attr tag="staticmethod, nogil" source="spacy/tokens/token.pxd"}

Get the value of an attribute from the `TokenC` struct by attribute ID.

> #### Example
>
> ```python
> from spacy.attrs cimport IS_ALPHA
> from spacy.tokens cimport Token
>
> is_alpha = Token.get_struct_attr(&doc.c[3], IS_ALPHA)
> ```

| Name        | Type                                   | Description                                                                            |
| ----------- | -------------------------------------- | -------------------------------------------------------------------------------------- |
| `token`     | `const TokenC*`                        | A pointer to a `TokenC` struct.                                                        |
| `feat_name` | `attr_id_t`                            | The ID of the attribute to look up. The attributes are enumerated in `spacy.typedefs`. |
| **RETURNS** | <Abbr title="uint64_t">`attr_t`</Abbr> | The value of the attribute.                                                            |

### Token.set_struct_attr {#token_set_struct_attr tag="staticmethod, nogil" source="spacy/tokens/token.pxd"}

Set the value of an attribute of the `TokenC` struct by attribute ID.

> #### Example
>
> ```python
> from spacy.attrs cimport TAG
> from spacy.tokens cimport Token
>
> token = &doc.c[3]
> Token.set_struct_attr(token, TAG, 0)
> ```

| Name        | Type                                   | Description                                                                            |
| ----------- | -------------------------------------- | -------------------------------------------------------------------------------------- |
| `token`     | `const TokenC*`                        | A pointer to a `TokenC` struct.                                                        |
| `feat_name` | `attr_id_t`                            | The ID of the attribute to look up. The attributes are enumerated in `spacy.typedefs`. |
| `value`     | <Abbr title="uint64_t">`attr_t`</Abbr> | The value to set.                                                                      |

### token_by_start {#token_by_start tag="function" source="spacy/tokens/doc.pxd"}

Find a token in a `TokenC*` array by the offset of its first character.

> #### Example
>
> ```python
> from spacy.tokens.doc cimport Doc, token_by_start
> from spacy.vocab cimport Vocab
>
> doc = Doc(Vocab(), words=["hello", "world"])
> assert token_by_start(doc.c, doc.length, 6) == 1
> assert token_by_start(doc.c, doc.length, 4) == -1
> ```

| Name         | Type            | Description                                               |
| ------------ | --------------- | --------------------------------------------------------- |
| `tokens`     | `const TokenC*` | A `TokenC*` array.                                        |
| `length`     | `int`           | The number of tokens in the array.                        |
| `start_char` | `int`           | The start index to search for.                            |
| **RETURNS**  | `int`           | The index of the token in the array or `-1` if not found. |

### token_by_end {#token_by_end tag="function" source="spacy/tokens/doc.pxd"}

Find a token in a `TokenC*` array by the offset of its final character.

> #### Example
>
> ```python
> from spacy.tokens.doc cimport Doc, token_by_end
> from spacy.vocab cimport Vocab
>
> doc = Doc(Vocab(), words=["hello", "world"])
> assert token_by_end(doc.c, doc.length, 5) == 0
> assert token_by_end(doc.c, doc.length, 1) == -1
> ```

| Name        | Type            | Description                                               |
| ----------- | --------------- | --------------------------------------------------------- |
| `tokens`    | `const TokenC*` | A `TokenC*` array.                                        |
| `length`    | `int`           | The number of tokens in the array.                        |
| `end_char`  | `int`           | The end index to search for.                              |
| **RETURNS** | `int`           | The index of the token in the array or `-1` if not found. |

### set_children_from_heads {#set_children_from_heads tag="function" source="spacy/tokens/doc.pxd"}

Set attributes that allow lookup of syntactic children on a `TokenC*` array.
This function must be called after making changes to the `TokenC.head`
attribute, in order to make the parse tree navigation consistent.

> #### Example
>
> ```python
> from spacy.tokens.doc cimport Doc, set_children_from_heads
> from spacy.vocab cimport Vocab
>
> doc = Doc(Vocab(), words=["Baileys", "from", "a", "shoe"])
> doc.c[0].head = 0
> doc.c[1].head = 0
> doc.c[2].head = 3
> doc.c[3].head = 1
> set_children_from_heads(doc.c, doc.length)
> assert doc.c[3].l_kids == 1
> ```

| Name     | Type            | Description                        |
| -------- | --------------- | ---------------------------------- |
| `tokens` | `const TokenC*` | A `TokenC*` array.                 |
| `length` | `int`           | The number of tokens in the array. |

## LexemeC {#lexemec tag="C struct" source="spacy/structs.pxd"}

Struct holding information about a lexical type. `LexemeC` structs are usually
owned by the `Vocab`, and accessed through a read-only pointer on the `TokenC`
struct.

> #### Example
>
> ```python
> lex = doc.c[3].lex
> ```

| Name        | Type                                    | Description                                                                                                                |
| ----------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `flags`     | <Abbr title="uint64_t">`flags_t`</Abbr> | Bit-field for binary lexical flag values.                                                                                  |
| `id`        | <Abbr title="uint64_t">`attr_t`</Abbr>  | Usually used to map lexemes to rows in a matrix, e.g. for word vectors. Does not need to be unique, so currently misnamed. |
| `length`    | <Abbr title="uint64_t">`attr_t`</Abbr>  | Number of unicode characters in the lexeme.                                                                                |
| `orth`      | <Abbr title="uint64_t">`attr_t`</Abbr>  | ID of the verbatim text content.                                                                                           |
| `lower`     | <Abbr title="uint64_t">`attr_t`</Abbr>  | ID of the lowercase form of the lexeme.                                                                                    |
| `norm`      | <Abbr title="uint64_t">`attr_t`</Abbr>  | ID of the lexeme's norm, i.e. a normalized form of the text.                                                               |
| `shape`     | <Abbr title="uint64_t">`attr_t`</Abbr>  | Transform of the lexeme's string, to show orthographic features.                                                           |
| `prefix`    | <Abbr title="uint64_t">`attr_t`</Abbr>  | Length-N substring from the start of the lexeme. Defaults to `N=1`.                                                        |
| `suffix`    | <Abbr title="uint64_t">`attr_t`</Abbr>  | Length-N substring from the end of the lexeme. Defaults to `N=3`.                                                          |

### Lexeme.get_struct_attr {#lexeme_get_struct_attr tag="staticmethod, nogil" source="spacy/lexeme.pxd"}

Get the value of an attribute from the `LexemeC` struct by attribute ID.

> #### Example
>
> ```python
> from spacy.attrs cimport IS_ALPHA
> from spacy.lexeme cimport Lexeme
>
> lexeme = doc.c[3].lex
> is_alpha = Lexeme.get_struct_attr(lexeme, IS_ALPHA)
> ```

| Name        | Type                                   | Description                                                                            |
| ----------- | -------------------------------------- | -------------------------------------------------------------------------------------- |
| `lex`       | `const LexemeC*`                       | A pointer to a `LexemeC` struct.                                                       |
| `feat_name` | `attr_id_t`                            | The ID of the attribute to look up. The attributes are enumerated in `spacy.typedefs`. |
| **RETURNS** | <Abbr title="uint64_t">`attr_t`</Abbr> | The value of the attribute.                                                            |

### Lexeme.set_struct_attr {#lexeme_set_struct_attr tag="staticmethod, nogil" source="spacy/lexeme.pxd"}

Set the value of an attribute of the `LexemeC` struct by attribute ID.

> #### Example
>
> ```python
> from spacy.attrs cimport NORM
> from spacy.lexeme cimport Lexeme
>
> lexeme = doc.c[3].lex
> Lexeme.set_struct_attr(lexeme, NORM, lexeme.lower)
> ```

| Name        | Type                                   | Description                                                                            |
| ----------- | -------------------------------------- | -------------------------------------------------------------------------------------- |
| `lex`       | `const LexemeC*`                       | A pointer to a `LexemeC` struct.                                                       |
| `feat_name` | `attr_id_t`                            | The ID of the attribute to look up. The attributes are enumerated in `spacy.typedefs`. |
| `value`     | <Abbr title="uint64_t">`attr_t`</Abbr> | The value to set.                                                                      |

### Lexeme.c_check_flag {#lexeme_c_check_flag tag="staticmethod, nogil" source="spacy/lexeme.pxd"}

Check the value of a binary flag attribute.

> #### Example
>
> ```python
> from spacy.attrs cimport IS_STOP
> from spacy.lexeme cimport Lexeme
>
> lexeme = doc.c[3].lex
> is_stop = Lexeme.c_check_flag(lexeme, IS_STOP)
> ```

| Name        | Type             | Description                                                                     |
| ----------- | ---------------- | ------------------------------------------------------------------------------- |
| `lexeme`    | `const LexemeC*` | A pointer to a `LexemeC` struct.                                                |
| `flag_id`   | `attr_id_t`      | The ID of the flag to look up. The flag IDs are enumerated in `spacy.typedefs`. |
| **RETURNS** | `bint`           | The boolean value of the flag.                                                  |

### Lexeme.c_set_flag {#lexeme_c_set_flag tag="staticmethod, nogil" source="spacy/lexeme.pxd"}

Set the value of a binary flag attribute.

> #### Example
>
> ```python
> from spacy.attrs cimport IS_STOP
> from spacy.lexeme cimport Lexeme
>
> lexeme = doc.c[3].lex
> Lexeme.c_set_flag(lexeme, IS_STOP, 0)
> ```

| Name      | Type             | Description                                                                     |
| --------- | ---------------- | ------------------------------------------------------------------------------- |
| `lexeme`  | `const LexemeC*` | A pointer to a `LexemeC` struct.                                                |
| `flag_id` | `attr_id_t`      | The ID of the flag to look up. The flag IDs are enumerated in `spacy.typedefs`. |
| `value`   | `bint`           | The value to set.                                                               |
