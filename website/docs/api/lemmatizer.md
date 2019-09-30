---
title: Lemmatizer
teaser: Assign the base forms of words
tag: class
source: spacy/lemmatizer.py
---

The `Lemmatizer` supports simple part-of-speech-sensitive suffix rules and
lookup tables.

## Lemmatizer.\_\_init\_\_ {#init tag="method"}

Create a `Lemmatizer`.

> #### Example
>
> ```python
> from spacy.lemmatizer import Lemmatizer
> lemmatizer = Lemmatizer()
> ```

| Name         | Type          | Description                                                |
| ------------ | ------------- | ---------------------------------------------------------- |
| `index`      | dict / `None` | Inventory of lemmas in the language.                       |
| `exceptions` | dict / `None` | Mapping of string forms to lemmas that bypass the `rules`. |
| `rules`      | dict / `None` | List of suffix rewrite rules.                              |
| `lookup`     | dict / `None` | Lookup table mapping string to their lemmas.               |
| **RETURNS**  | `Lemmatizer`  | The newly created object.                                  |

## Lemmatizer.\_\_call\_\_ {#call tag="method"}

Lemmatize a string.

> #### Example
>
> ```python
> from spacy.lemmatizer import Lemmatizer
> from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
> lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)
> lemmas = lemmatizer(u"ducks", u"NOUN")
> assert lemmas == [u"duck"]
> ```

| Name         | Type          | Description                                                                                              |
| ------------ | ------------- | -------------------------------------------------------------------------------------------------------- |
| `string`     | unicode       | The string to lemmatize, e.g. the token text.                                                            |
| `univ_pos`   | unicode / int | The token's universal part-of-speech tag.                                                                |
| `morphology` | dict / `None` | Morphological features following the [Universal Dependencies](http://universaldependencies.org/) scheme. |
| **RETURNS**  | list          | The available lemmas for the string.                                                                     |

## Lemmatizer.lookup {#lookup tag="method" new="2"}

Look up a lemma in the lookup table, if available. If no lemma is found, the
original string is returned. Languages can provide a
[lookup table](/usage/adding-languages#lemmatizer) via the `lemma_lookup`
variable, set on the individual `Language` class.

> #### Example
>
> ```python
> lookup = {u"going": u"go"}
> lemmatizer = Lemmatizer(lookup=lookup)
> assert lemmatizer.lookup(u"going") == u"go"
> ```

| Name        | Type    | Description                                                       |
| ----------- | ------- | ----------------------------------------------------------------- |
| `string`    | unicode | The string to look up.                                            |
| **RETURNS** | unicode | The lemma if the string was found, otherwise the original string. |

## Lemmatizer.is_base_form {#is_base_form tag="method"}

Check whether we're dealing with an uninflected paradigm, so we can avoid
lemmatization entirely.

> #### Example
>
> ```python
> pos = "verb"
> morph = {"VerbForm": "inf"}
> is_base_form = lemmatizer.is_base_form(pos, morph)
> assert is_base_form == True
> ```

| Name         | Type          | Description                                                                             |
| ------------ | ------------- | --------------------------------------------------------------------------------------- |
| `univ_pos`   | unicode / int | The token's universal part-of-speech tag.                                               |
| `morphology` | dict          | The token's morphological features.                                                     |
| **RETURNS**  | bool          | Whether the token's part-of-speech tag and morphological features describe a base form. |

## Attributes {#attributes}

| Name                                      | Type          | Description                                                |
| ----------------------------------------- | ------------- | ---------------------------------------------------------- |
| `index`                                   | dict / `None` | Inventory of lemmas in the language.                       |
| `exc`                                     | dict / `None` | Mapping of string forms to lemmas that bypass the `rules`. |
| `rules`                                   | dict / `None` | List of suffix rewrite rules.                              |
| `lookup_table` <Tag variant="new">2</Tag> | dict / `None` | The lemma lookup table, if available.                      |
