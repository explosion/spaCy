---
title: Vocab
teaser: A storage class for vocabulary and other data shared across a language
tag: class
source: spacy/vocab.pyx
---

The `Vocab` object provides a lookup table that allows you to access
[`Lexeme`](/api/lexeme) objects, as well as the
[`StringStore`](/api/stringstore). It also owns underlying C-data that is shared
between `Doc` objects.

## Vocab.\_\_init\_\_ {#init tag="method"}

Create the vocabulary.

> #### Example
>
> ```python
> from spacy.vocab import Vocab
> vocab = Vocab(strings=["hello", "world"])
> ```

| Name                                        | Description                                                                                                                                                             |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lex_attr_getters`                          | A dictionary mapping attribute IDs to functions to compute them. Defaults to `None`. ~~Optional[Dict[str, Callable[[str], Any]]]~~                                      |
| `strings`                                   | A [`StringStore`](/api/stringstore) that maps strings to hash values, and vice versa, or a list of strings. ~~Union[List[str], StringStore]~~                           |
| `lookups`                                   | A [`Lookups`](/api/lookups) that stores the `lexeme_norm` and other large lookup tables. Defaults to `None`. ~~Optional[Lookups]~~                                      |
| `oov_prob`                                  | The default OOV probability. Defaults to `-20.0`. ~~float~~                                                                                                             |
| `vectors_name` <Tag variant="new">2.2</Tag> | A name to identify the vectors table. ~~str~~                                                                                                                           |
| `writing_system`                            | A dictionary describing the language's writing system. Typically provided by [`Language.Defaults`](/api/language#defaults). ~~Dict[str, Any]~~                          |
| `get_noun_chunks`                           | A function that yields base noun phrases used for [`Doc.noun_chunks`](/api/doc#noun_chunks). ~~Optional[Callable[[Union[Doc, Span], Iterator[Tuple[int, int, int]]]]]~~ |

## Vocab.\_\_len\_\_ {#len tag="method"}

Get the current number of lexemes in the vocabulary.

> #### Example
>
> ```python
> doc = nlp("This is a sentence.")
> assert len(nlp.vocab) > 0
> ```

| Name        | Description                                      |
| ----------- | ------------------------------------------------ |
| **RETURNS** | The number of lexemes in the vocabulary. ~~int~~ |

## Vocab.\_\_getitem\_\_ {#getitem tag="method"}

Retrieve a lexeme, given an int ID or a string. If a previously unseen string is
given, a new lexeme is created and stored.

> #### Example
>
> ```python
> apple = nlp.vocab.strings["apple"]
> assert nlp.vocab[apple] == nlp.vocab["apple"]
> ```

| Name           | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| `id_or_string` | The hash value of a word, or its string. ~~Union[int, str]~~ |
| **RETURNS**    | The lexeme indicated by the given ID. ~~Lexeme~~             |

## Vocab.\_\_iter\_\_ {#iter tag="method"}

Iterate over the lexemes in the vocabulary.

> #### Example
>
> ```python
> stop_words = (lex for lex in nlp.vocab if lex.is_stop)
> ```

| Name       | Description                            |
| ---------- | -------------------------------------- |
| **YIELDS** | An entry in the vocabulary. ~~Lexeme~~ |

## Vocab.\_\_contains\_\_ {#contains tag="method"}

Check whether the string has an entry in the vocabulary. To get the ID for a
given string, you need to look it up in
[`vocab.strings`](/api/vocab#attributes).

> #### Example
>
> ```python
> apple = nlp.vocab.strings["apple"]
> oov = nlp.vocab.strings["dskfodkfos"]
> assert apple in nlp.vocab
> assert oov not in nlp.vocab
> ```

| Name        | Description                                                 |
| ----------- | ----------------------------------------------------------- |
| `string`    | The ID string. ~~str~~                                      |
| **RETURNS** | Whether the string has an entry in the vocabulary. ~~bool~~ |

## Vocab.add_flag {#add_flag tag="method"}

Set a new boolean flag to words in the vocabulary. The `flag_getter` function
will be called over the words currently in the vocab, and then applied to new
words as they occur. You'll then be able to access the flag value on each token,
using `token.check_flag(flag_id)`.

> #### Example
>
> ```python
> def is_my_product(text):
>     products = ["spaCy", "Thinc", "displaCy"]
>     return text in products
>
> MY_PRODUCT = nlp.vocab.add_flag(is_my_product)
> doc = nlp("I like spaCy")
> assert doc[2].check_flag(MY_PRODUCT) == True
> ```

| Name          | Description                                                                                                                                                 |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `flag_getter` | A function that takes the lexeme text and returns the boolean flag value. ~~Callable[[str], bool]~~                                                         |
| `flag_id`     | An integer between `1` and `63` (inclusive), specifying the bit at which the flag will be stored. If `-1`, the lowest available bit will be chosen. ~~int~~ |
| **RETURNS**   | The integer ID by which the flag value can be checked. ~~int~~                                                                                              |

## Vocab.reset_vectors {#reset_vectors tag="method" new="2"}

Drop the current vector table. Because all vectors must be the same width, you
have to call this to change the size of the vectors. Only one of the `width` and
`shape` keyword arguments can be specified.

> #### Example
>
> ```python
> nlp.vocab.reset_vectors(width=300)
> ```

| Name           | Description            |
| -------------- | ---------------------- |
| _keyword-only_ |                        |
| `width`        | The new width. ~~int~~ |
| `shape`        | The new shape. ~~int~~ |

## Vocab.prune_vectors {#prune_vectors tag="method" new="2"}

Reduce the current vector table to `nr_row` unique entries. Words mapped to the
discarded vectors will be remapped to the closest vector among those remaining.
For example, suppose the original table had vectors for the words:
`['sat', 'cat', 'feline', 'reclined']`. If we prune the vector table to, two
rows, we would discard the vectors for "feline" and "reclined". These words
would then be remapped to the closest remaining vector – so "feline" would have
the same vector as "cat", and "reclined" would have the same vector as "sat".
The similarities are judged by cosine. The original vectors may be large, so the
cosines are calculated in minibatches to reduce memory usage.

> #### Example
>
> ```python
> nlp.vocab.prune_vectors(10000)
> assert len(nlp.vocab.vectors) <= 1000
> ```

| Name         | Description                                                                                                                                                                                                                  |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nr_row`     | The number of rows to keep in the vector table. ~~int~~                                                                                                                                                                      |
| `batch_size` | Batch of vectors for calculating the similarities. Larger batch sizes might be faster, while temporarily requiring more memory. ~~int~~                                                                                      |
| **RETURNS**  | A dictionary keyed by removed words mapped to `(string, score)` tuples, where `string` is the entry the removed word was mapped to, and `score` the similarity score between the two words. ~~Dict[str, Tuple[str, float]]~~ |

## Vocab.get_vector {#get_vector tag="method" new="2"}

Retrieve a vector for a word in the vocabulary. Words can be looked up by string
or hash value. If no vectors data is loaded, a `ValueError` is raised. If `minn`
is defined, then the resulting vector uses [FastText](https://fasttext.cc/)'s
subword features by average over n-grams of `orth` (introduced in spaCy `v2.1`).

> #### Example
>
> ```python
> nlp.vocab.get_vector("apple")
> nlp.vocab.get_vector("apple", minn=1, maxn=5)
> ```

| Name                                | Description                                                                                                            |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `orth`                              | The hash value of a word, or its unicode string. ~~Union[int, str]~~                                                   |
| `minn` <Tag variant="new">2.1</Tag> | Minimum n-gram length used for FastText's n-gram computation. Defaults to the length of `orth`. ~~int~~                |
| `maxn` <Tag variant="new">2.1</Tag> | Maximum n-gram length used for FastText's n-gram computation. Defaults to the length of `orth`. ~~int~~                |
| **RETURNS**                         | A word vector. Size and shape are determined by the `Vocab.vectors` instance. ~~numpy.ndarray[ndim=1, dtype=float32]~~ |

## Vocab.set_vector {#set_vector tag="method" new="2"}

Set a vector for a word in the vocabulary. Words can be referenced by string or
hash value.

> #### Example
>
> ```python
> nlp.vocab.set_vector("apple", array([...]))
> ```

| Name     | Description                                                          |
| -------- | -------------------------------------------------------------------- |
| `orth`   | The hash value of a word, or its unicode string. ~~Union[int, str]~~ |
| `vector` | The vector to set. ~~numpy.ndarray[ndim=1, dtype=float32]~~          |

## Vocab.has_vector {#has_vector tag="method" new="2"}

Check whether a word has a vector. Returns `False` if no vectors are loaded.
Words can be looked up by string or hash value.

> #### Example
>
> ```python
> if nlp.vocab.has_vector("apple"):
>     vector = nlp.vocab.get_vector("apple")
> ```

| Name        | Description                                                          |
| ----------- | -------------------------------------------------------------------- |
| `orth`      | The hash value of a word, or its unicode string. ~~Union[int, str]~~ |
| **RETURNS** | Whether the word has a vector. ~~bool~~                              |

## Vocab.to_disk {#to_disk tag="method" new="2"}

Save the current state to a directory.

> #### Example
>
> ```python
> nlp.vocab.to_disk("/path/to/vocab")
> ```

| Name           | Description                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path`         | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                                                            |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~                                                |

## Vocab.from_disk {#from_disk tag="method" new="2"}

Loads state from a directory. Modifies the object in place and returns it.

> #### Example
>
> ```python
> from spacy.vocab import Vocab
> vocab = Vocab().from_disk("/path/to/vocab")
> ```

| Name           | Description                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `path`         | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                 |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~     |
| **RETURNS**    | The modified `Vocab` object. ~~Vocab~~                                                          |

## Vocab.to_bytes {#to_bytes tag="method"}

Serialize the current state to a binary string.

> #### Example
>
> ```python
> vocab_bytes = nlp.vocab.to_bytes()
> ```

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The serialized form of the `Vocab` object. ~~Vocab~~                                        |

## Vocab.from_bytes {#from_bytes tag="method"}

Load state from a binary string.

> #### Example
>
> ```python
> from spacy.vocab import Vocab
> vocab_bytes = nlp.vocab.to_bytes()
> vocab = Vocab()
> vocab.from_bytes(vocab_bytes)
> ```

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| `bytes_data`   | The data to load from. ~~bytes~~                                                            |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The `Vocab` object. ~~Vocab~~                                                               |

## Attributes {#attributes}

> #### Example
>
> ```python
> apple_id = nlp.vocab.strings["apple"]
> assert type(apple_id) == int
> PERSON = nlp.vocab.strings["PERSON"]
> assert type(PERSON) == int
> ```

| Name                                           | Description                                                                                                                                                            |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `strings`                                      | A table managing the string-to-int mapping. ~~StringStore~~                                                                                                            |
| `vectors` <Tag variant="new">2</Tag>           | A table associating word IDs to word vectors. ~~Vectors~~                                                                                                              |
| `vectors_length`                               | Number of dimensions for each word vector. ~~int~~                                                                                                                     |
| `lookups`                                      | The available lookup tables in this vocab. ~~Lookups~~                                                                                                                 |
| `writing_system` <Tag variant="new">2.1</Tag>  | A dict with information about the language's writing system. ~~Dict[str, Any]~~                                                                                        |
| `get_noun_chunks` <Tag variant="new">3.0</Tag> | A function that yields base noun phrases used for [`Doc.noun_chunks`](/ap/doc#noun_chunks). ~~Optional[Callable[[Union[Doc, Span], Iterator[Tuple[int, int, int]]]]]~~ |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = vocab.to_bytes(exclude=["strings", "vectors"])
> vocab.from_disk("./vocab", exclude=["strings"])
> ```

| Name      | Description                                           |
| --------- | ----------------------------------------------------- |
| `strings` | The strings in the [`StringStore`](/api/stringstore). |
| `vectors` | The word vectors, if available.                       |
| `lookups` | The lookup tables, if available.                      |
