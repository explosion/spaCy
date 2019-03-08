---
title: EntityRuler
tag: class
source: spacy/pipeline/entityruler.py
new: 2.1
---

The EntityRuler lets you add spans to the [`Doc.ents`](/api/doc#ents) using
token-based rules or exact phrase matches. It can be combined with the
statistical [`EntityRecognizer`](/api/entityrecognizer) to boost accuracy, or
used on its own to implement a purely rule-based entity recognition system.
After initialization, the component is typically added to the processing
pipeline using [`nlp.add_pipe`](/api/language#add_pipe).

## EntityRuler.\_\_init\_\_ {#init tag="method"}

Initialize the entity ruler. If patterns are supplied here, they need to be a
list of dictionaries with a `"label"` and `"pattern"` key. A pattern can either
be a token pattern (list) or a phrase pattern (string). For example:
`{'label': 'ORG', 'pattern': 'Apple'}`.

> #### Example
>
> ```python
> # Construction via create_pipe
> ruler = nlp.create_pipe("entityruler")
>
> # Construction from class
> from spacy.pipeline import EntityRuler
> ruler = EntityRuler(nlp, overwrite_ents=True)
> ```

| Name             | Type          | Description                                                                                                                                           |
| ---------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nlp`            | `Language`    | The shared nlp object to pass the vocab to the matchers and process phrase patterns.                                                                  |
| `patterns`       | iterable      | Optional patterns to load in.                                                                                                                         |
| `overwrite_ents` | bool          | If existing entities are present, e.g. entities added by the model, overwrite them by matches if necessary. Defaults to `False`.                      |
| `**cfg`          | -             | Other config parameters. If pipeline component is loaded as part of a model pipeline, this will include all keyword arguments passed to `spacy.load`. |
| **RETURNS**      | `EntityRuler` | The newly constructed object.                                                                                                                         |

## EntityRuler.\_\len\_\_ {#len tag="method"}

The number of all patterns added to the entity ruler.

> #### Example
>
> ```python
> ruler = EntityRuler(nlp)
> assert len(ruler) == 0
> ruler.add_patterns([{"label": "ORG", "pattern": "Apple"}])
> assert len(ruler) == 1
> ```

| Name        | Type | Description             |
| ----------- | ---- | ----------------------- |
| **RETURNS** | int  | The number of patterns. |

## EntityRuler.\_\_contains\_\_ {#contains tag="method"}

Whether a label is present in the patterns.

> #### Example
>
> ```python
> ruler = EntityRuler(nlp)
> ruler.add_patterns([{"label": "ORG", "pattern": "Apple"}])
> assert "ORG" in ruler
> assert not "PERSON" in ruler
> ```

| Name        | Type    | Description                                  |
| ----------- | ------- | -------------------------------------------- |
| `label`     | unicode | The label to check.                          |
| **RETURNS** | bool    | Whether the entity ruler contains the label. |

## EntityRuler.\_\_call\_\_ {#call tag="method"}

Find matches in the `Doc` and add them to the `doc.ents`. Typically, this
happens automatically after the component has been added to the pipeline using
[`nlp.add_pipe`](/api/language#add_pipe). If the entity ruler was initialized
with `overwrite_ents=True`, existing entities will be replaced if they overlap
with the matches.

> #### Example
>
> ```python
> ruler = EntityRuler(nlp)
> ruler.add_patterns([{"label": "ORG", "pattern": "Apple"}])
> nlp.add_pipe(ruler)
>
> doc = nlp("A text about Apple.")
> ents = [(ent.text, ent.label_) for ent in doc.ents]
> assert ents == [("Apple", "ORG")]
> ```

| Name        | Type  | Description                                                  |
| ----------- | ----- | ------------------------------------------------------------ |
| `doc`       | `Doc` | The `Doc` object to process, e.g. the `Doc` in the pipeline. |
| **RETURNS** | `Doc` | The modified `Doc` with added entities, if available.        |

## EntityRuler.add_patterns {#add_patterns tag="method"}

Add patterns to the entity ruler. A pattern can either be a token pattern (list
of dicts) or a phrase pattern (string). For more details, see the usage guide on
[rule-based matching](/usage/rule-based-matching).

> #### Example
>
> ```python
> patterns = [
>     {"label": "ORG", "pattern": "Apple"},
>     {"label": "GPE", "pattern": [{"lower": "san"}, {"lower": "francisco"}]}
> ]
> ruler = EntityRuler(nlp)
> ruler.add_patterns(patterns)
> ```

| Name       | Type | Description          |
| ---------- | ---- | -------------------- |
| `patterns` | list | The patterns to add. |

## EntityRuler.to_disk {#to_disk tag="method"}

Save the entity ruler patterns to a directory. The patterns will be saved as
newline-delimited JSON (JSONL).

> #### Example
>
> ```python
> ruler = EntityRuler(nlp)
> ruler.to_disk("/path/to/rules.jsonl")
> ```

| Name   | Type             | Description                                                                                                      |
| ------ | ---------------- | ---------------------------------------------------------------------------------------------------------------- |
| `path` | unicode / `Path` | A path to a file, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |

## EntityRuler.from_disk {#from_disk tag="method"}

Load the entity ruler from a file. Expects a file containing newline-delimited
JSON (JSONL) with one entry per line.

> #### Example
>
> ```python
> ruler = EntityRuler(nlp)
> ruler.from_disk("/path/to/rules.jsonl")
> ```

| Name        | Type             | Description                                                                 |
| ----------- | ---------------- | --------------------------------------------------------------------------- |
| `path`      | unicode / `Path` | A path to a JSONL file. Paths may be either strings or `Path`-like objects. |
| **RETURNS** | `EntityRuler`    | The modified `EntityRuler` object.                                          |

## EntityRuler.to_bytes {#to_bytes tag="method"}

Serialize the entity ruler patterns to a bytestring.

> #### Example
>
> ```python
> ruler = EntityRuler(nlp)
> ruler_bytes = ruler.to_bytes()
> ```

| Name        | Type  | Description              |
| ----------- | ----- | ------------------------ |
| **RETURNS** | bytes | The serialized patterns. |

## EntityRuler.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> ruler_bytes = ruler.to_bytes()
> ruler = EntityRuler(nlp)
> ruler.from_bytes(ruler_bytes)
> ```

| Name             | Type          | Description                        |
| ---------------- | ------------- | ---------------------------------- |
| `patterns_bytes` | bytes         | The bytestring to load.            |
| **RETURNS**      | `EntityRuler` | The modified `EntityRuler` object. |

## EntityRuler.labels {#labels tag="property"}

All labels present in the match patterns.

| Name        | Type  | Description        |
| ----------- | ----- | ------------------ |
| **RETURNS** | tuple | The string labels. |

## EntityRuler.patterns {#patterns tag="property"}

Get all patterns that were added to the entity ruler.

| Name        | Type | Description                                        |
| ----------- | ---- | -------------------------------------------------- |
| **RETURNS** | list | The original patterns, one dictionary per pattern. |

## Attributes {#attributes}

| Name              | Type                                  | Description                                                      |
| ----------------- | ------------------------------------- | ---------------------------------------------------------------- |
| `matcher`         | [`Matcher`](/api/matcher)             | The underlying matcher used to process token patterns.           |
| `phrase_matcher`  | [`PhraseMatcher`](/api/phtasematcher) | The underlying phrase matcher, used to process phrase patterns.  |
| `token_patterns`  | dict                                  | The token patterns present in the entity ruler, keyed by label.  |
| `phrase_patterns` | dict                                  | The phrase patterns present in the entity ruler, keyed by label. |
