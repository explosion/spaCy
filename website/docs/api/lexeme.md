---
title: Lexeme
teaser: An entry in the vocabulary
tag: class
source: spacy/lexeme.pyx
---

A `Lexeme` has no string context – it's a word type, as opposed to a word token.
It therefore has no part-of-speech tag, dependency parse, or lemma (if
lemmatization depends on the part-of-speech tag).

## Lexeme.\_\_init\_\_ {#init tag="method"}

Create a `Lexeme` object.

| Name        | Type     | Description                   |
| ----------- | -------- | ----------------------------- |
| `vocab`     | `Vocab`  | The parent vocabulary.        |
| `orth`      | int      | The orth id of the lexeme.    |
| **RETURNS** | `Lexeme` | The newly constructed object. |

## Lexeme.set_flag {#set_flag tag="method"}

Change the value of a boolean flag.

> #### Example
>
> ```python
> COOL_FLAG = nlp.vocab.add_flag(lambda text: False)
> nlp.vocab["spaCy"].set_flag(COOL_FLAG, True)
> ```

| Name      | Type | Description                          |
| --------- | ---- | ------------------------------------ |
| `flag_id` | int  | The attribute ID of the flag to set. |
| `value`   | bool | The new value of the flag.           |

## Lexeme.check_flag {#check_flag tag="method"}

Check the value of a boolean flag.

> #### Example
>
> ```python
> is_my_library = lambda text: text in ["spaCy", "Thinc"]
> MY_LIBRARY = nlp.vocab.add_flag(is_my_library)
> assert nlp.vocab["spaCy"].check_flag(MY_LIBRARY) == True
> ```

| Name        | Type | Description                            |
| ----------- | ---- | -------------------------------------- |
| `flag_id`   | int  | The attribute ID of the flag to query. |
| **RETURNS** | bool | The value of the flag.                 |

## Lexeme.similarity {#similarity tag="method" model="vectors"}

Compute a semantic similarity estimate. Defaults to cosine over vectors.

> #### Example
>
> ```python
> apple = nlp.vocab["apple"]
> orange = nlp.vocab["orange"]
> apple_orange = apple.similarity(orange)
> orange_apple = orange.similarity(apple)
> assert apple_orange == orange_apple
> ```

| Name        | Type  | Description                                                                                  |
| ----------- | ----- | -------------------------------------------------------------------------------------------- |
| other       | -     | The object to compare with. By default, accepts `Doc`, `Span`, `Token` and `Lexeme` objects. |
| **RETURNS** | float | A scalar similarity score. Higher is more similar.                                           |

## Lexeme.has_vector {#has_vector tag="property" model="vectors"}

A boolean value indicating whether a word vector is associated with the lexeme.

> #### Example
>
> ```python
> apple = nlp.vocab["apple"]
> assert apple.has_vector
> ```

| Name        | Type | Description                                    |
| ----------- | ---- | ---------------------------------------------- |
| **RETURNS** | bool | Whether the lexeme has a vector data attached. |

## Lexeme.vector {#vector tag="property" model="vectors"}

A real-valued meaning representation.

> #### Example
>
> ```python
> apple = nlp.vocab["apple"]
> assert apple.vector.dtype == "float32"
> assert apple.vector.shape == (300,)
> ```

| Name        | Type                                     | Description                                           |
| ----------- | ---------------------------------------- | ----------------------------------------------------- |
| **RETURNS** | `numpy.ndarray[ndim=1, dtype='float32']` | A 1D numpy array representing the lexeme's semantics. |

## Lexeme.vector_norm {#vector_norm tag="property" model="vectors"}

The L2 norm of the lexeme's vector representation.

> #### Example
>
> ```python
> apple = nlp.vocab["apple"]
> pasta = nlp.vocab["pasta"]
> apple.vector_norm  # 7.1346845626831055
> pasta.vector_norm  # 7.759851932525635
> assert apple.vector_norm != pasta.vector_norm
> ```

| Name        | Type  | Description                               |
| ----------- | ----- | ----------------------------------------- |
| **RETURNS** | float | The L2 norm of the vector representation. |

## Attributes {#attributes}

| Name                                         | Type    | Description                                                                                                                                                                                                                                                  |
| -------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `vocab`                                      | `Vocab` | The lexeme's vocabulary.                                                                                                                                                                                                                                     |
| `text`                                       | unicode | Verbatim text content.                                                                                                                                                                                                                                       |
| `orth`                                       | int     | ID of the verbatim text content.                                                                                                                                                                                                                             |
| `orth_`                                      | unicode | Verbatim text content (identical to `Lexeme.text`). Exists mostly for consistency with the other attributes.                                                                                                                                                 |
| `rank`                                       | int     | Sequential ID of the lexemes's lexical type, used to index into tables, e.g. for word vectors.                                                                                                                                                               |
| `flags`                                      | int     | Container of the lexeme's binary flags.                                                                                                                                                                                                                      |
| `norm`                                       | int     | The lexemes's norm, i.e. a normalized form of the lexeme text.                                                                                                                                                                                               |
| `norm_`                                      | unicode | The lexemes's norm, i.e. a normalized form of the lexeme text.                                                                                                                                                                                               |
| `lower`                                      | int     | Lowercase form of the word.                                                                                                                                                                                                                                  |
| `lower_`                                     | unicode | Lowercase form of the word.                                                                                                                                                                                                                                  |
| `shape`                                      | int     | Transform of the words's string, to show orthographic features. Alphabetic characters are replaced by `x` or `X`, and numeric characters are replaced by d`, and sequences of the same character are truncated after length 4. For example,`"Xxxx"`or`"dd"`. |
| `shape_`                                     | unicode | Transform of the word's string, to show orthographic features. Alphabetic characters are replaced by `x` or `X`, and numeric characters are replaced by d`, and sequences of the same character are truncated after length 4. For example,`"Xxxx"`or`"dd"`.  |
| `prefix`                                     | int     | Length-N substring from the start of the word. Defaults to `N=1`.                                                                                                                                                                                            |
| `prefix_`                                    | unicode | Length-N substring from the start of the word. Defaults to `N=1`.                                                                                                                                                                                            |
| `suffix`                                     | int     | Length-N substring from the end of the word. Defaults to `N=3`.                                                                                                                                                                                              |
| `suffix_`                                    | unicode | Length-N substring from the start of the word. Defaults to `N=3`.                                                                                                                                                                                            |
| `is_alpha`                                   | bool    | Does the lexeme consist of alphabetic characters? Equivalent to `lexeme.text.isalpha()`.                                                                                                                                                                     |
| `is_ascii`                                   | bool    | Does the lexeme consist of ASCII characters? Equivalent to `[any(ord(c) >= 128 for c in lexeme.text)]`.                                                                                                                                                      |
| `is_digit`                                   | bool    | Does the lexeme consist of digits? Equivalent to `lexeme.text.isdigit()`.                                                                                                                                                                                    |
| `is_lower`                                   | bool    | Is the lexeme in lowercase? Equivalent to `lexeme.text.islower()`.                                                                                                                                                                                           |
| `is_upper`                                   | bool    | Is the lexeme in uppercase? Equivalent to `lexeme.text.isupper()`.                                                                                                                                                                                           |
| `is_title`                                   | bool    | Is the lexeme in titlecase? Equivalent to `lexeme.text.istitle()`.                                                                                                                                                                                           |
| `is_punct`                                   | bool    | Is the lexeme punctuation?                                                                                                                                                                                                                                   |
| `is_left_punct`                              | bool    | Is the lexeme a left punctuation mark, e.g. `(`?                                                                                                                                                                                                             |
| `is_right_punct`                             | bool    | Is the lexeme a right punctuation mark, e.g. `)`?                                                                                                                                                                                                            |
| `is_space`                                   | bool    | Does the lexeme consist of whitespace characters? Equivalent to `lexeme.text.isspace()`.                                                                                                                                                                     |
| `is_bracket`                                 | bool    | Is the lexeme a bracket?                                                                                                                                                                                                                                     |
| `is_quote`                                   | bool    | Is the lexeme a quotation mark?                                                                                                                                                                                                                              |
| `is_currency` <Tag variant="new">2.0.8</Tag> | bool    | Is the lexeme a currency symbol?                                                                                                                                                                                                                             |
| `like_url`                                   | bool    | Does the lexeme resemble a URL?                                                                                                                                                                                                                              |
| `like_num`                                   | bool    | Does the lexeme represent a number? e.g. "10.9", "10", "ten", etc.                                                                                                                                                                                           |
| `like_email`                                 | bool    | Does the lexeme resemble an email address?                                                                                                                                                                                                                   |
| `is_oov`                                     | bool    | Does the lexeme have a word vector?                                                                                                                                                                                                                          |
| `is_stop`                                    | bool    | Is the lexeme part of a "stop list"?                                                                                                                                                                                                                         |
| `lang`                                       | int     | Language of the parent vocabulary.                                                                                                                                                                                                                           |
| `lang_`                                      | unicode | Language of the parent vocabulary.                                                                                                                                                                                                                           |
| `prob`                                       | float   | Smoothed log probability estimate of the lexeme's word type (context-independent entry in the vocabulary).                                                                                                                                                   |
| `cluster`                                    | int     | Brown cluster ID.                                                                                                                                                                                                                                            |
| `sentiment`                                  | float   | A scalar value indicating the positivity or negativity of the lexeme.                                                                                                                                                                                        |
