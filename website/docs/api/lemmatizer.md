---
title: Lemmatizer
teaser: Assign the base forms of words
tag: class
source: spacy/lemmatizer.py
---

The `Lemmatizer` supports simple part-of-speech-sensitive suffix rules and
lookup tables.

## Lemmatizer.\_\_init\_\_ {#init tag="method"}

Initialize a `Lemmatizer`. Typically, this happens under the hood within spaCy
when a `Language` subclass and its `Vocab` is initialized.

> #### Example
>
> ```python
> from spacy.lemmatizer import Lemmatizer
> from spacy.lookups import Lookups
> lookups = Lookups()
> lookups.add_table("lemma_rules", {"noun": [["s", ""]]})
> lemmatizer = Lemmatizer(lookups)
> ```
>
> For examples of the data format, see the
> [`spacy-lookups-data`](https://github.com/explosion/spacy-lookups-data) repo.

| Name                                   | Type                      | Description                                                                                                               |
| -------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `lookups` <Tag variant="new">2.2</Tag> | [`Lookups`](/api/lookups) | The lookups object containing the (optional) tables `"lemma_rules"`, `"lemma_index"`, `"lemma_exc"` and `"lemma_lookup"`. |
| **RETURNS**                            | `Lemmatizer`              | The newly created object.                                                                                                 |

<Infobox title="Deprecation note" variant="danger">

As of v2.2, the lemmatizer is initialized with a [`Lookups`](/api/lookups)
object containing tables for the different components. This makes it easier for
spaCy to share and serialize rules and lookup tables via the `Vocab`, and allows
users to modify lemmatizer data at runtime by updating `nlp.vocab.lookups`.

```diff
- lemmatizer = Lemmatizer(rules=lemma_rules)
+ lemmatizer = Lemmatizer(lookups)
```

</Infobox>

## Lemmatizer.\_\_call\_\_ {#call tag="method"}

Lemmatize a string.

> #### Example
>
> ```python
> from spacy.lemmatizer import Lemmatizer
> from spacy.lookups import Lookups
> lookups = Lookups()
> lookups.add_table("lemma_rules", {"noun": [["s", ""]]})
> lemmatizer = Lemmatizer(lookups)
> lemmas = lemmatizer("ducks", "NOUN")
> assert lemmas == ["duck"]
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
[lookup table](/usage/adding-languages#lemmatizer) via the `Lookups`.

> #### Example
>
> ```python
> lookups = Lookups()
> lookups.add_table("lemma_lookup", {"going": "go"})
> assert lemmatizer.lookup("going") == "go"
> ```

| Name        | Type    | Description                                                                                                 |
| ----------- | ------- | ----------------------------------------------------------------------------------------------------------- |
| `string`    | unicode | The string to look up.                                                                                      |
| `orth`      | int     | Optional hash of the string to look up. If not set, the string will be used and hashed. Defaults to `None`. |
| **RETURNS** | unicode | The lemma if the string was found, otherwise the original string.                                           |

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

| Name                                   | Type                      | Description                                                     |
| -------------------------------------- | ------------------------- | --------------------------------------------------------------- |
| `lookups` <Tag variant="new">2.2</Tag> | [`Lookups`](/api/lookups) | The lookups object containing the rules and data, if available. |
