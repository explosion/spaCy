---
title: Cython Classes
menu:
  - ['Doc', 'doc']
  - ['Token', 'token']
  - ['Span', 'span']
  - ['Lexeme', 'lexeme']
  - ['Vocab', 'vocab']
  - ['StringStore', 'stringstore']
---

## Doc {#doc tag="cdef class" source="spacy/tokens/doc.pxd"}

The `Doc` object holds an array of [`TokenC`](/api/cython-structs#tokenc)
structs.

<Infobox variant="warning">

This section documents the extra C-level attributes and methods that can't be
accessed from Python. For the Python documentation, see [`Doc`](/api/doc).

</Infobox>

### Attributes {#doc_attributes}

| Name         | Type         | Description                                                                               |
| ------------ | ------------ | ----------------------------------------------------------------------------------------- |
| `mem`        | `cymem.Pool` | A memory pool. Allocated memory will be freed once the `Doc` object is garbage collected. |
| `vocab`      | `Vocab`      | A reference to the shared `Vocab` object.                                                 |
| `c`          | `TokenC*`    | A pointer to a [`TokenC`](/api/cython-structs#tokenc) struct.                             |
| `length`     | `int`        | The number of tokens in the document.                                                     |
| `max_length` | `int`        | The underlying size of the `Doc.c` array.                                                 |

### Doc.push_back {#doc_push_back tag="method"}

Append a token to the `Doc`. The token can be provided as a
[`LexemeC`](/api/cython-structs#lexemec) or
[`TokenC`](/api/cython-structs#tokenc) pointer, using Cython's
[fused types](http://cython.readthedocs.io/en/latest/src/userguide/fusedtypes.html).

> #### Example
>
> ```python
> from spacy.tokens cimport Doc
> from spacy.vocab cimport Vocab
>
> doc = Doc(Vocab())
> lexeme = doc.vocab.get(u'hello')
> doc.push_back(lexeme, True)
> assert doc.text == u'hello '
> ```

| Name         | Type            | Description                               |
| ------------ | --------------- | ----------------------------------------- |
| `lex_or_tok` | `LexemeOrToken` | The word to append to the `Doc`.          |
| `has_space`  | `bint`          | Whether the word has trailing whitespace. |

## Token {#token tag="cdef class" source="spacy/tokens/token.pxd"}

A Cython class providing access and methods for a
[`TokenC`](/api/cython-structs#tokenc) struct. Note that the `Token` object does
not own the struct. It only receives a pointer to it.

<Infobox variant="warning">

This section documents the extra C-level attributes and methods that can't be
accessed from Python. For the Python documentation, see [`Token`](/api/token).

</Infobox>

### Attributes {#token_attributes}

| Name    | Type      | Description                                                   |
| ------- | --------- | ------------------------------------------------------------- |
| `vocab` | `Vocab`   | A reference to the shared `Vocab` object.                     |
| `c`     | `TokenC*` | A pointer to a [`TokenC`](/api/cython-structs#tokenc) struct. |
| `i`     | `int`     | The offset of the token within the document.                  |
| `doc`   | `Doc`     | The parent document.                                          |

### Token.cinit {#token_cinit tag="method"}

Create a `Token` object from a `TokenC*` pointer.

> #### Example
>
> ```python
> token = Token.cinit(&doc.c[3], doc, 3)
> ```

| Name        | Type      | Description                                                  |
| ----------- | --------- | ------------------------------------------------------------ |
| `vocab`     | `Vocab`   | A reference to the shared `Vocab`.                           |
| `c`         | `TokenC*` | A pointer to a [`TokenC`](/api/cython-structs#tokenc)struct. |
| `offset`    | `int`     | The offset of the token within the document.                 |
| `doc`       | `Doc`     | The parent document.                                         |
| **RETURNS** | `Token`   | The newly constructed object.                                |

## Span {#span tag="cdef class" source="spacy/tokens/span.pxd"}

A Cython class providing access and methods for a slice of a `Doc` object.

<Infobox variant="warning">

This section documents the extra C-level attributes and methods that can't be
accessed from Python. For the Python documentation, see [`Span`](/api/span).

</Infobox>

### Attributes {#span_attributes}

| Name         | Type                                   | Description                                             |
| ------------ | -------------------------------------- | ------------------------------------------------------- |
| `doc`        | `Doc`                                  | The parent document.                                    |
| `start`      | `int`                                  | The index of the first token of the span.               |
| `end`        | `int`                                  | The index of the first token after the span.            |
| `start_char` | `int`                                  | The index of the first character of the span.           |
| `end_char`   | `int`                                  | The index of the last character of the span.            |
| `label`      | <Abbr title="uint64_t">`attr_t`</Abbr> | A label to attach to the span, e.g. for named entities. |

## Lexeme {#lexeme tag="cdef class" source="spacy/lexeme.pxd"}

A Cython class providing access and methods for an entry in the vocabulary.

<Infobox variant="warning">

This section documents the extra C-level attributes and methods that can't be
accessed from Python. For the Python documentation, see [`Lexeme`](/api/lexeme).

</Infobox>

### Attributes {#lexeme_attributes}

| Name    | Type                                   | Description                                                     |
| ------- | -------------------------------------- | --------------------------------------------------------------- |
| `c`     | `LexemeC*`                             | A pointer to a [`LexemeC`](/api/cython-structs#lexemec) struct. |
| `vocab` | `Vocab`                                | A reference to the shared `Vocab` object.                       |
| `orth`  | <Abbr title="uint64_t">`attr_t`</Abbr> | ID of the verbatim text content.                                |

## Vocab {#vocab tag="cdef class" source="spacy/vocab.pxd"}

A Cython class providing access and methods for a vocabulary and other data
shared across a language.

<Infobox variant="warning">

This section documents the extra C-level attributes and methods that can't be
accessed from Python. For the Python documentation, see [`Vocab`](/api/vocab).

</Infobox>

### Attributes {#vocab_attributes}

| Name      | Type          | Description                                                                                 |
| --------- | ------------- | ------------------------------------------------------------------------------------------- |
| `mem`     | `cymem.Pool`  | A memory pool. Allocated memory will be freed once the `Vocab` object is garbage collected. |
| `strings` | `StringStore` | A `StringStore` that maps string to hash values and vice versa.                             |
| `length`  | `int`         | The number of entries in the vocabulary.                                                    |

### Vocab.get {#vocab_get tag="method"}

Retrieve a [`LexemeC*`](/api/cython-structs#lexemec) pointer from the
vocabulary.

> #### Example
>
> ```python
> lexeme = vocab.get(vocab.mem, u'hello')
> ```

| Name        | Type             | Description                                                                                 |
| ----------- | ---------------- | ------------------------------------------------------------------------------------------- |
| `mem`       | `cymem.Pool`     | A memory pool. Allocated memory will be freed once the `Vocab` object is garbage collected. |
| `string`    | unicode          | The string of the word to look up.                                                          |
| **RETURNS** | `const LexemeC*` | The lexeme in the vocabulary.                                                               |

### Vocab.get_by_orth {#vocab_get_by_orth tag="method"}

Retrieve a [`LexemeC*`](/api/cython-structs#lexemec) pointer from the
vocabulary.

> #### Example
>
> ```python
> lexeme = vocab.get_by_orth(doc[0].lex.norm)
> ```

| Name        | Type                                   | Description                                                                                 |
| ----------- | -------------------------------------- | ------------------------------------------------------------------------------------------- |
| `mem`       | `cymem.Pool`                           | A memory pool. Allocated memory will be freed once the `Vocab` object is garbage collected. |
| `orth`      | <Abbr title="uint64_t">`attr_t`</Abbr> | ID of the verbatim text content.                                                            |
| **RETURNS** | `const LexemeC*`                       | The lexeme in the vocabulary.                                                               |

## StringStore {#stringstore tag="cdef class" source="spacy/strings.pxd"}

A lookup table to retrieve strings by 64-bit hashes.

<Infobox variant="warning">

This section documents the extra C-level attributes and methods that can't be
accessed from Python. For the Python documentation, see
[`StringStore`](/api/stringstore).

</Infobox>

### Attributes {#stringstore_attributes}

| Name   | Type                                                   | Description                                                                                      |
| ------ | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| `mem`  | `cymem.Pool`                                           | A memory pool. Allocated memory will be freed once the`StringStore` object is garbage collected. |
| `keys` | <Abbr title="vector[uint64_t]">`vector[hash_t]`</Abbr> | A list of hash values in the `StringStore`.                                                      |
