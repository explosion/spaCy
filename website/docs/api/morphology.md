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

Create a Morphology object.

> #### Example
>
> ```python
> from spacy.morphology import Morphology
>
> morphology = Morphology(strings)
> ```

| Name      | Type          | Description       |
| --------- | ------------- | ----------------- |
| `strings` | `StringStore` | The string store. |

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
