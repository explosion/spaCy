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

| Name    | Description                        |
| ------- | ---------------------------------- |
| `vocab` | The parent vocabulary. ~~Vocab~~   |
| `orth`  | The orth id of the lexeme. ~~int~~ |

## Lexeme.set_flag {#set_flag tag="method"}

Change the value of a boolean flag.

> #### Example
>
> ```python
> COOL_FLAG = nlp.vocab.add_flag(lambda text: False)
> nlp.vocab["spaCy"].set_flag(COOL_FLAG, True)
> ```

| Name      | Description                                  |
| --------- | -------------------------------------------- |
| `flag_id` | The attribute ID of the flag to set. ~~int~~ |
| `value`   | The new value of the flag. ~~bool~~          |

## Lexeme.check_flag {#check_flag tag="method"}

Check the value of a boolean flag.

> #### Example
>
> ```python
> is_my_library = lambda text: text in ["spaCy", "Thinc"]
> MY_LIBRARY = nlp.vocab.add_flag(is_my_library)
> assert nlp.vocab["spaCy"].check_flag(MY_LIBRARY) == True
> ```

| Name        | Description                                    |
| ----------- | ---------------------------------------------- |
| `flag_id`   | The attribute ID of the flag to query. ~~int~~ |
| **RETURNS** | The value of the flag. ~~bool~~                |

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

| Name        | Description                                                                                                                      |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------- |
| other       | The object to compare with. By default, accepts `Doc`, `Span`, `Token` and `Lexeme` objects. ~~Union[Doc, Span, Token, Lexeme]~~ |
| **RETURNS** | A scalar similarity score. Higher is more similar. ~~float~~                                                                     |

## Lexeme.has_vector {#has_vector tag="property" model="vectors"}

A boolean value indicating whether a word vector is associated with the lexeme.

> #### Example
>
> ```python
> apple = nlp.vocab["apple"]
> assert apple.has_vector
> ```

| Name        | Description                                             |
| ----------- | ------------------------------------------------------- |
| **RETURNS** | Whether the lexeme has a vector data attached. ~~bool~~ |

## Lexeme.vector {#vector tag="property" model="vectors"}

A real-valued meaning representation.

> #### Example
>
> ```python
> apple = nlp.vocab["apple"]
> assert apple.vector.dtype == "float32"
> assert apple.vector.shape == (300,)
> ```

| Name        | Description                                                                                      |
| ----------- | ------------------------------------------------------------------------------------------------ |
| **RETURNS** | A 1-dimensional array representing the lexeme's vector. ~~numpy.ndarray[ndim=1, dtype=float32]~~ |

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

| Name        | Description                                         |
| ----------- | --------------------------------------------------- |
| **RETURNS** | The L2 norm of the vector representation. ~~float~~ |

## Attributes {#attributes}

| Name                                         | Description                                                                                                                                                                                                                                                          |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`                                      | The lexeme's vocabulary. ~~Vocab~~                                                                                                                                                                                                                                   |
| `text`                                       | Verbatim text content. ~~str~~                                                                                                                                                                                                                                       |
| `orth`                                       | ID of the verbatim text content. ~~int~~                                                                                                                                                                                                                             |
| `orth_`                                      | Verbatim text content (identical to `Lexeme.text`). Exists mostly for consistency with the other attributes. ~~str~~                                                                                                                                                 |
| `rank`                                       | Sequential ID of the lexeme's lexical type, used to index into tables, e.g. for word vectors. ~~int~~                                                                                                                                                                |
| `flags`                                      | Container of the lexeme's binary flags. ~~int~~                                                                                                                                                                                                                      |
| `norm`                                       | The lexeme's norm, i.e. a normalized form of the lexeme text. ~~int~~                                                                                                                                                                                                |
| `norm_`                                      | The lexeme's norm, i.e. a normalized form of the lexeme text. ~~str~~                                                                                                                                                                                                |
| `lower`                                      | Lowercase form of the word. ~~int~~                                                                                                                                                                                                                                  |
| `lower_`                                     | Lowercase form of the word. ~~str~~                                                                                                                                                                                                                                  |
| `shape`                                      | Transform of the word's string, to show orthographic features. Alphabetic characters are replaced by `x` or `X`, and numeric characters are replaced by `d`, and sequences of the same character are truncated after length 4. For example,`"Xxxx"`or`"dd"`. ~~int~~ |
| `shape_`                                     | Transform of the word's string, to show orthographic features. Alphabetic characters are replaced by `x` or `X`, and numeric characters are replaced by `d`, and sequences of the same character are truncated after length 4. For example,`"Xxxx"`or`"dd"`. ~~str~~ |
| `prefix`                                     | Length-N substring from the start of the word. Defaults to `N=1`. ~~int~~                                                                                                                                                                                            |
| `prefix_`                                    | Length-N substring from the start of the word. Defaults to `N=1`. ~~str~~                                                                                                                                                                                            |
| `suffix`                                     | Length-N substring from the end of the word. Defaults to `N=3`. ~~int~~                                                                                                                                                                                              |
| `suffix_`                                    | Length-N substring from the start of the word. Defaults to `N=3`. ~~str~~                                                                                                                                                                                            |
| `is_alpha`                                   | Does the lexeme consist of alphabetic characters? Equivalent to `lexeme.text.isalpha()`. ~~bool~~                                                                                                                                                                    |
| `is_ascii`                                   | Does the lexeme consist of ASCII characters? Equivalent to `[any(ord(c) >= 128 for c in lexeme.text)]`. ~~bool~~                                                                                                                                                     |
| `is_digit`                                   | Does the lexeme consist of digits? Equivalent to `lexeme.text.isdigit()`. ~~bool~~                                                                                                                                                                                   |
| `is_lower`                                   | Is the lexeme in lowercase? Equivalent to `lexeme.text.islower()`. ~~bool~~                                                                                                                                                                                          |
| `is_upper`                                   | Is the lexeme in uppercase? Equivalent to `lexeme.text.isupper()`. ~~bool~~                                                                                                                                                                                          |
| `is_title`                                   | Is the lexeme in titlecase? Equivalent to `lexeme.text.istitle()`. ~~bool~~                                                                                                                                                                                          |
| `is_punct`                                   | Is the lexeme punctuation? ~~bool~~                                                                                                                                                                                                                                  |
| `is_left_punct`                              | Is the lexeme a left punctuation mark, e.g. `(`? ~~bool~~                                                                                                                                                                                                            |
| `is_right_punct`                             | Is the lexeme a right punctuation mark, e.g. `)`? ~~bool~~                                                                                                                                                                                                           |
| `is_space`                                   | Does the lexeme consist of whitespace characters? Equivalent to `lexeme.text.isspace()`. ~~bool~~                                                                                                                                                                    |
| `is_bracket`                                 | Is the lexeme a bracket? ~~bool~~                                                                                                                                                                                                                                    |
| `is_quote`                                   | Is the lexeme a quotation mark? ~~bool~~                                                                                                                                                                                                                             |
| `is_currency` <Tag variant="new">2.0.8</Tag> | Is the lexeme a currency symbol? ~~bool~~                                                                                                                                                                                                                            |
| `like_url`                                   | Does the lexeme resemble a URL? ~~bool~~                                                                                                                                                                                                                             |
| `like_num`                                   | Does the lexeme represent a number? e.g. "10.9", "10", "ten", etc. ~~bool~~                                                                                                                                                                                          |
| `like_email`                                 | Does the lexeme resemble an email address? ~~bool~~                                                                                                                                                                                                                  |
| `is_oov`                                     | Is the lexeme out-of-vocabulary (i.e. does it not have a word vector)? ~~bool~~                                                                                                                                                                                      |
| `is_stop`                                    | Is the lexeme part of a "stop list"? ~~bool~~                                                                                                                                                                                                                        |
| `lang`                                       | Language of the parent vocabulary. ~~int~~                                                                                                                                                                                                                           |
| `lang_`                                      | Language of the parent vocabulary. ~~str~~                                                                                                                                                                                                                           |
| `prob`                                       | Smoothed log probability estimate of the lexeme's word type (context-independent entry in the vocabulary). ~~float~~                                                                                                                                                 |
| `cluster`                                    | Brown cluster ID. ~~int~~                                                                                                                                                                                                                                            |
| `sentiment`                                  | A scalar value indicating the positivity or negativity of the lexeme. ~~float~~                                                                                                                                                                                      |
