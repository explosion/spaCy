---
title: MorphAnalysis
tag: class
source: spacy/tokens/morphanalysis.pyx
---

Stores a single morphological analysis.


## MorphAnalysis.\_\_init\_\_ {#init tag="method"}

Initialize a MorphAnalysis object from a UD FEATS string or a dictionary of
morphological features.

> #### Example
>
> ```python
> from spacy.tokens import MorphAnalysis
> 
> feats = "Feat1=Val1|Feat2=Val2"
> m = MorphAnalysis(nlp.vocab, feats)
> ```

| Name        | Type               | Description                   |
| ----------- | ------------------ | ----------------------------- |
| `vocab`     | `Vocab`            | The vocab.                    |
| `features`  | `Union[Dict, str]` | The morphological features.   |
| **RETURNS** | `MorphAnalysis`    | The newly constructed object. |


## MorphAnalysis.\_\_contains\_\_ {#contains tag="method"}

Whether a feature/value pair is in the analysis.

> #### Example
>
> ```python
> feats = "Feat1=Val1,Val2|Feat2=Val2"
> morph = MorphAnalysis(nlp.vocab, feats)
> assert "Feat1=Val1" in morph
> ```

| Name        | Type  | Description                           |
| ----------- | ----- | ------------------------------------- |
| **RETURNS** | `str` | A feature/value pair in the analysis. |


## MorphAnalysis.\_\_iter\_\_ {#iter tag="method"}

Iterate over the feature/value pairs in the analysis.

> #### Example
>
> ```python
> feats = "Feat1=Val1,Val3|Feat2=Val2"
> morph = MorphAnalysis(nlp.vocab, feats)
> assert list(morph) == ["Feat1=Va1", "Feat1=Val3", "Feat2=Val2"]
> ```

| Name       | Type  | Description                           |
| ---------- | ----- | ------------------------------------- |
| **YIELDS** | `str` | A feature/value pair in the analysis. |


## MorphAnalysis.\_\_len\_\_ {#len tag="method"}

Returns the number of features in the analysis.

> #### Example
>
> ```python
> feats = "Feat1=Val1,Val2|Feat2=Val2"
> morph = MorphAnalysis(nlp.vocab, feats)
> assert len(morph) == 3
> ```

| Name        | Type  | Description                             |
| ----------- | ----- | --------------------------------------- |
| **RETURNS** | `int` | The number of features in the analysis. |


## MorphAnalysis.\_\_str\_\_ {#str tag="method"}

Returns the morphological analysis in the UD FEATS string format.

> #### Example
>
> ```python
> feats = "Feat1=Val1,Val2|Feat2=Val2"
> morph = MorphAnalysis(nlp.vocab, feats)
> assert str(morph) == feats
> ```

| Name        | Type  | Description                      |
| ----------- | ----- | ---------------------------------|
| **RETURNS** | `str` | The analysis in UD FEATS format. |


## MorphAnalysis.get {#get tag="method"}

Retrieve values for a feature by field.

> #### Example
>
> ```python
> feats = "Feat1=Val1,Val2"
> morph = MorphAnalysis(nlp.vocab, feats)
> assert morph.get("Feat1") == ["Val1", "Val2"]
> ```

| Name        | Type   | Description                         |
| ----------- | ------ | ----------------------------------- |
| `field`     | `str`  | The field to retrieve.              |
| **RETURNS** | `list` | A list of the individual features.  |


## MorphAnalysis.to_dict {#to_dict tag="method"}

Produce a dict representation of the analysis, in the same format as the tag
map.

> #### Example
>
> ```python
> feats = "Feat1=Val1,Val2|Feat2=Val2"
> morph = MorphAnalysis(nlp.vocab, feats)
> assert morph.to_dict() == {"Feat1": "Val1,Val2", "Feat2": "Val2"}
> ```

| Name        | Type   | Description                              |
| ----------- | ------ | -----------------------------------------|
| **RETURNS** | `dict` | The dict representation of the analysis. |


## MorphAnalysis.from_id {#from_id tag="classmethod"}

Create a morphological analysis from a given hash ID.

> #### Example
>
> ```python
> feats = "Feat1=Val1|Feat2=Val2"
> hash = nlp.vocab.strings[feats]
> morph = MorphAnalysis.from_id(nlp.vocab, hash)
> assert str(morph) == feats
> ```

| Name    | Type    | Description                      |
| ------- | ------- | -------------------------------- |
| `vocab` | `Vocab` | The vocab.                       |
| `key`   | `int`   | The hash of the features string. |


