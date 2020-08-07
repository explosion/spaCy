---
title: EntityRuler
tag: class
source: spacy/pipeline/entityruler.py
new: 2.1
teaser: 'Pipeline component for rule-based named entity recognition'
api_string_name: entity_ruler
api_trainable: false
---

The entity ruler lets you add spans to the [`Doc.ents`](/api/doc#ents) using
token-based rules or exact phrase matches. It can be combined with the
statistical [`EntityRecognizer`](/api/entityrecognizer) to boost accuracy, or
used on its own to implement a purely rule-based entity recognition system. For
usage examples, see the docs on
[rule-based entity recognition](/usage/rule-based-matching#entityruler).

## Config and implementation {#config}

The default config is defined by the pipeline component factory and describes
how the component should be configured. You can override its settings via the
`config` argument on [`nlp.add_pipe`](/api/language#add_pipe) or in your
[`config.cfg` for training](/usage/training#config).

> #### Example
>
> ```python
> config = {
>    "phrase_matcher_attr": None,
>    "validate": True,
>    "overwrite_ents": False,
>    "ent_id_sep": "||",
> }
> nlp.add_pipe("entity_ruler", config=config)
> ```

| Setting               | Type | Description                                                                                                                                 | Default |
| --------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| `phrase_matcher_attr` | str  | Optional attribute name match on for the internal [`PhraseMatcher`](/api/phrasematcher), e.g. `LOWER` to match on the lowercase token text. | `None`  |
| `validate`            | bool | Whether patterns should be validated (passed to the `Matcher` and `PhraseMatcher`).                                                         | `False` |
| `overwrite_ents`      | bool | If existing entities are present, e.g. entities added by the model, overwrite them by matches if necessary.                                 | `False` |
| `ent_id_sep`          | str  | Separator used internally for entity IDs.                                                                                                   | `"||"`  |

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/entityruler.py
```

## EntityRuler.\_\_init\_\_ {#init tag="method"}

Initialize the entity ruler. If patterns are supplied here, they need to be a
list of dictionaries with a `"label"` and `"pattern"` key. A pattern can either
be a token pattern (list) or a phrase pattern (string). For example:
`{"label": "ORG", "pattern": "Apple"}`.

> #### Example
>
> ```python
> # Construction via add_pipe
> ruler = nlp.add_pipe("entity_ruler")
>
> # Construction from class
> from spacy.pipeline import EntityRuler
> ruler = EntityRuler(nlp, overwrite_ents=True)
> ```

| Name                              | Type       | Description                                                                                                                                                                                                                   |
| --------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nlp`                             | `Language` | The shared nlp object to pass the vocab to the matchers and process phrase patterns.                                                                                                                                          |
| `name` <Tag variant="new">3</Tag> | str        | Instance name of the current pipeline component. Typically passed in automatically from the factory when the component is added. Used to disable the current entity ruler while creating phrase patterns with the nlp object. |
| _keyword-only_                    |            |                                                                                                                                                                                                                               |
| `phrase_matcher_attr`             | int / str  | Optional attribute name match on for the internal [`PhraseMatcher`](/api/phrasematcher), e.g. `LOWER` to match on the lowercase token text. Defaults to `None`.                                                               |
| `validate`                        | bool       | Whether patterns should be validated, passed to Matcher and PhraseMatcher as `validate`. Defaults to `False`.                                                                                                                 |
| `overwrite_ents`                  | bool       | If existing entities are present, e.g. entities added by the model, overwrite them by matches if necessary. Defaults to `False`.                                                                                              |
| `ent_id_sep`                      | str        | Separator used internally for entity IDs. Defaults to `"||"`.                                                                                                                                                                 |
| `patterns`                        | iterable   | Optional patterns to load in on initialization.                                                                                                                                                                               |

## EntityRuler.\_\len\_\_ {#len tag="method"}

The number of all patterns added to the entity ruler.

> #### Example
>
> ```python
> ruler = nlp.add_pipe("entity_ruler")
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
> ruler = nlp.add_pipe("entity_ruler")
> ruler.add_patterns([{"label": "ORG", "pattern": "Apple"}])
> assert "ORG" in ruler
> assert not "PERSON" in ruler
> ```

| Name        | Type | Description                                  |
| ----------- | ---- | -------------------------------------------- |
| `label`     | str  | The label to check.                          |
| **RETURNS** | bool | Whether the entity ruler contains the label. |

## EntityRuler.\_\_call\_\_ {#call tag="method"}

Find matches in the `Doc` and add them to the `doc.ents`. Typically, this
happens automatically after the component has been added to the pipeline using
[`nlp.add_pipe`](/api/language#add_pipe). If the entity ruler was initialized
with `overwrite_ents=True`, existing entities will be replaced if they overlap
with the matches. When matches overlap in a Doc, the entity ruler prioritizes
longer patterns over shorter, and if equal the match occuring first in the Doc
is chosen.

> #### Example
>
> ```python
> ruler = nlp.add_pipe("entity_ruler")
> ruler.add_patterns([{"label": "ORG", "pattern": "Apple"}])
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
> ruler = nlp.add_pipe("entity_ruler")
> ruler.add_patterns(patterns)
> ```

| Name       | Type | Description          |
| ---------- | ---- | -------------------- |
| `patterns` | list | The patterns to add. |

## EntityRuler.to_disk {#to_disk tag="method"}

Save the entity ruler patterns to a directory. The patterns will be saved as
newline-delimited JSON (JSONL). If a file with the suffix `.jsonl` is provided,
only the patterns are saved as JSONL. If a directory name is provided, a
`patterns.jsonl` and `cfg` file with the component configuration is exported.

> #### Example
>
> ```python
> ruler = nlp.add_pipe("entity_ruler")
> ruler.to_disk("/path/to/patterns.jsonl")  # saves patterns only
> ruler.to_disk("/path/to/entity_ruler")    # saves patterns and config
> ```

| Name   | Type         | Description                                                                                                                         |
| ------ | ------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| `path` | str / `Path` | A path to a JSONL file or directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |

## EntityRuler.from_disk {#from_disk tag="method"}

Load the entity ruler from a file. Expects either a file containing
newline-delimited JSON (JSONL) with one entry per line, or a directory
containing a `patterns.jsonl` file and a `cfg` file with the component
configuration.

> #### Example
>
> ```python
> ruler = nlp.add_pipe("entity_ruler")
> ruler.from_disk("/path/to/patterns.jsonl")  # loads patterns only
> ruler.from_disk("/path/to/entity_ruler")    # loads patterns and config
> ```

| Name        | Type          | Description                                                                              |
| ----------- | ------------- | ---------------------------------------------------------------------------------------- |
| `path`      | str / `Path`  | A path to a JSONL file or directory. Paths may be either strings or `Path`-like objects. |
| **RETURNS** | `EntityRuler` | The modified `EntityRuler` object.                                                       |

## EntityRuler.to_bytes {#to_bytes tag="method"}

Serialize the entity ruler patterns to a bytestring.

> #### Example
>
> ```python
> ruler = nlp.add_pipe("entity_ruler")
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
> ruler = nlp.add_pipe("enity_ruler")
> ruler.from_bytes(ruler_bytes)
> ```

| Name         | Type          | Description                        |
| ------------ | ------------- | ---------------------------------- |
| `bytes_data` | bytes         | The bytestring to load.            |
| **RETURNS**  | `EntityRuler` | The modified `EntityRuler` object. |

## EntityRuler.labels {#labels tag="property"}

All labels present in the match patterns.

| Name        | Type  | Description        |
| ----------- | ----- | ------------------ |
| **RETURNS** | tuple | The string labels. |

## EntityRuler.ent_ids {#labels tag="property" new="2.2.2"}

All entity ids present in the match patterns `id` properties.

| Name        | Type  | Description         |
| ----------- | ----- | ------------------- |
| **RETURNS** | tuple | The string ent_ids. |

## EntityRuler.patterns {#patterns tag="property"}

Get all patterns that were added to the entity ruler.

| Name        | Type | Description                                        |
| ----------- | ---- | -------------------------------------------------- |
| **RETURNS** | list | The original patterns, one dictionary per pattern. |

## Attributes {#attributes}

| Name              | Type                                  | Description                                                      |
| ----------------- | ------------------------------------- | ---------------------------------------------------------------- |
| `matcher`         | [`Matcher`](/api/matcher)             | The underlying matcher used to process token patterns.           |
| `phrase_matcher`  | [`PhraseMatcher`](/api/phrasematcher) | The underlying phrase matcher, used to process phrase patterns.  |
| `token_patterns`  | dict                                  | The token patterns present in the entity ruler, keyed by label.  |
| `phrase_patterns` | dict                                  | The phrase patterns present in the entity ruler, keyed by label. |
