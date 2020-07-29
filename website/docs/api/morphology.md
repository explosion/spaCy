---
title: Morphology
tag: class
source: spacy/morphology.pyx
---

Store the possible morphological analyses for a language, and index them by
hash. To save space on each token, tokens only know the hash of their
morphological analysis, so queries of morphological attributes are delegated to
this class.

## Morphology.\_\_init\_\_ {#init tag="method"}

Create a Morphology object using the tag map, lemmatizer and exceptions.

> #### Example
>
> ```python
> from spacy.morphology import Morphology
>
> morphology = Morphology(strings, tag_map, lemmatizer)
> ```

| Name         | Type              | Description                                                                                                |
| ------------ | ----------------- | ---------------------------------------------------------------------------------------------------------- |
| `strings`    | `StringStore`     | The string store.                                                                                          |
| `tag_map`    | `Dict[str, Dict]` | The tag map.                                                                                               |
| `lemmatizer` | `Lemmatizer`      | The lemmatizer.                                                                                            |
| `exc`        | `Dict[str, Dict]` | A dictionary of exceptions in the format `{tag: {orth: {"POS": "X", "Feat1": "Val1, "Feat2": "Val2", ...}` |

## Morphology.add {#add tag="method"}

Insert a morphological analysis in the morphology table, if not already present.
The morphological analysis may be provided in the UD FEATS format as a string or
in the tag map dictionary format. Returns the hash of the new analysis.

> #### Example
>
> ```python
> feats = "Feat1=Val1|Feat2=Val2"
> hash = nlp.vocab.morphology.add(feats)
> assert hash == nlp.vocab.strings[feats]
> ```

| Name       | Type               | Description                 |
| ---------- | ------------------ | --------------------------- |
| `features` | `Union[Dict, str]` | The morphological features. |

## Morphology.get {#get tag="method"}

> #### Example
>
> ```python
> feats = "Feat1=Val1|Feat2=Val2"
> hash = nlp.vocab.morphology.add(feats)
> assert nlp.vocab.morphology.get(hash) == feats
> ```

Get the FEATS string for the hash of the morphological analysis.

| Name    | Type | Description                             |
| ------- | ---- | --------------------------------------- |
| `morph` | int  | The hash of the morphological analysis. |

## Morphology.load_tag_map {#load_tag_map tag="method"}

Replace the current tag map with the provided tag map.

| Name      | Type              | Description  |
| --------- | ----------------- | ------------ |
| `tag_map` | `Dict[str, Dict]` | The tag map. |

## Morphology.load_morph_exceptions {#load_morph_exceptions tag="method"}

Replace the current morphological exceptions with the provided exceptions.

| Name          | Type              | Description                   |
| ------------- | ----------------- | ----------------------------- |
| `morph_rules` | `Dict[str, Dict]` | The morphological exceptions. |

## Morphology.add_special_case {#add_special_case tag="method"}

Add a special-case rule to the morphological analyzer. Tokens whose tag and orth
match the rule will receive the specified properties.

> #### Example
>
> ```python
> attrs = {"POS": "DET", "Definite": "Def"}
> morphology.add_special_case("DT", "the", attrs)
> ```

| Name       | Type | Description                                    |
| ---------- | ---- | ---------------------------------------------- |
| `tag_str`  | str  | The fine-grained tag.                          |
| `orth_str` | str  | The token text.                                |
| `attrs`    | dict | The features to assign for this token and tag. |

## Morphology.exc {#exc tag="property"}

The current morphological exceptions.

| Name       | Type | Description                                         |
| ---------- | ---- | --------------------------------------------------- |
| **YIELDS** | dict | The current dictionary of morphological exceptions. |

## Morphology.lemmatize {#lemmatize tag="method"}

TODO

## Morphology.feats_to_dict {#feats_to_dict tag="staticmethod"}

Convert a string FEATS representation to a dictionary of features and values in
the same format as the tag map.

> #### Example
>
> ```python
> from spacy.morphology import Morphology
> d = Morphology.feats_to_dict("Feat1=Val1|Feat2=Val2")
> assert d == {"Feat1": "Val1", "Feat2": "Val2"}
> ```

| Name        | Type | Description                                                        |
| ----------- | ---- | ------------------------------------------------------------------ |
| `feats`     | str  | The morphological features in Universal Dependencies FEATS format. |
| **RETURNS** | dict | The morphological features as a dictionary.                        |

## Morphology.dict_to_feats {#dict_to_feats tag="staticmethod"}

Convert a dictionary of features and values to a string FEATS representation.

> #### Example
>
> ```python
> from spacy.morphology import Morphology
> f = Morphology.dict_to_feats({"Feat1": "Val1", "Feat2": "Val2"})
> assert f == "Feat1=Val1|Feat2=Val2"
> ```

| Name         | Type              | Description                                                           |
| ------------ | ----------------- | --------------------------------------------------------------------- |
| `feats_dict` | `Dict[str, Dict]` | The morphological features as a dictionary.                           |
| **RETURNS**  | str               | The morphological features as in Universal Dependencies FEATS format. |

## Attributes {#attributes}

| Name          | Type  | Description                                  |
| ------------- | ----- | -------------------------------------------- |
| `FEATURE_SEP` | `str` | The FEATS feature separator. Default is `|`. |
| `FIELD_SEP`   | `str` | The FEATS field separator. Default is `=`.   |
| `VALUE_SEP`   | `str` | The FEATS value separator. Default is `,`.   |
