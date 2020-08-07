---
title: AttributeRuler
tag: class
source: spacy/pipeline/attributeruler.py
new: 3
teaser: 'Pipeline component for rule-based token attribute assignment'
api_string_name: attribute_ruler
api_trainable: false
---

The attribute ruler lets you set token attributes for tokens identified by
[`Matcher` patterns](/usage/rule-based-matching#matcher). The attribute ruler is
typically used to handle exceptions for token attributes and to map values
between attributes such as mapping fine-grained POS tags to coarse-grained POS
tags.

## Config and implementation {#config}

The default config is defined by the pipeline component factory and describes
how the component should be configured. You can override its settings via the
`config` argument on [`nlp.add_pipe`](/api/language#add_pipe) or in your
[`config.cfg` for training](/usage/training#config).

> #### Example
>
> ```python
> config = {
>    "pattern_dicts": None,
>    "validate": True,
> }
> nlp.add_pipe("attribute_ruler", config=config)
> ```

| Setting         | Type             | Description                                                                                                                             | Default |
| --------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| `pattern_dicts` | `Iterable[dict]` | A list of pattern dicts with the keys as the arguments to [`AttributeRuler.add`](#add) (`patterns`/`attrs`/`index`) to add as patterns. | `None`  |
| `validate`      | bool             | Whether patterns should be validated (passed to the `Matcher`).                                                                         | `False` |

```python
https://github.com/explosion/spaCy/blob/develop/spacy/pipeline/attributeruler.py
```

## AttributeRuler.\_\_init\_\_ {#init tag="method"}

Initialize the attribute ruler. If pattern dicts are supplied here, they need to
be a list of dictionaries with `"patterns"`, `"attrs"`, and optional `"index"`
keys, e.g.:

```python
pattern_dicts = \[
    {"patterns": \[\[{"TAG": "VB"}\]\], "attrs": {"POS": "VERB"}},
    {"patterns": \[\[{"LOWER": "an"}\]\], "attrs": {"LEMMA": "a"}},
\]
```

> #### Example
>
> ```python
> # Construction via add_pipe
> attribute_ruler = nlp.add_pipe("attribute_ruler")
> ```

| Name            | Type              | Description                                                                                                                                                                                                                   |
| --------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`         | `Vocab`           | The shared nlp object to pass the vocab to the matchers and process phrase patterns.                                                                                                                                          |
| `name`          | str               | Instance name of the current pipeline component. Typically passed in automatically from the factory when the component is added. Used to disable the current entity ruler while creating phrase patterns with the nlp object. |
| _keyword-only_  |                   |                                                                                                                                                                                                                               |
| `pattern_dicts` | `Iterable[Dict]]` | Optional patterns to load in on initialization. Defaults to `None`.                                                                                                                                                           |
| `validate`      | bool              | Whether patterns should be validated (passed to the `Matcher`). Defaults to `False`.                                                                                                                                          |

## AttributeRuler.\_\_call\_\_ {#call tag="method"}

Apply the attribute ruler to a Doc, setting token attributes for tokens matched
by the provided patterns.

| Name        | Type  | Description                                                  |
| ----------- | ----- | ------------------------------------------------------------ |
| `doc`       | `Doc` | The `Doc` object to process, e.g. the `Doc` in the pipeline. |
| **RETURNS** | `Doc` | The modified `Doc` with added entities, if available.        |

## AttributeRuler.add {#add tag="method"}

Add patterns to the attribute ruler. The patterns are a list of `Matcher`
patterns and the attributes are a dict of attributes to set on the matched
token. If the pattern matches a span of more than one token, the `index` can be
used to set the attributes for the token at that index in the span. The `index`
may be negative to index from the end of the span.

> #### Example
>
> ```python
> attribute_ruler = nlp.add_pipe("attribute_ruler")
> patterns = [[{"TAG": "VB"}]]
> attrs = {"POS": "VERB"}
> attribute_ruler.add(patterns=patterns, attrs=attrs)
> ```

| Name     | Type                   | Description                                                                                                             |
| -------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| patterns | `Iterable[List[Dict]]` | A list of Matcher patterns.                                                                                             |
| attrs    | dict                   | The attributes to assign to the target token in the matched span.                                                       |
| index    | int                    | The index of the token in the matched span to modify. May be negative to index from the end of the span. Defaults to 0. |

## AttributeRuler.add_patterns {#add_patterns tag="method"}

> #### Example
>
> ```python
> attribute_ruler = nlp.add_pipe("attribute_ruler")
> pattern_dicts = \[
>   {
>     "patterns": \[\[{"TAG": "VB"}\]\],
>     "attrs": {"POS": "VERB"}
>   },
>   {
>     "patterns": \[\[{"LOWER": "two"}, {"LOWER": "apples"}\]\],
>     "attrs": {"LEMMA": "apple"},
>     "index": -1
>   },
> \]
> attribute_ruler.add_patterns(pattern_dicts)
> ```

Add patterns from a list of pattern dicts with the keys as the arguments to
[`AttributeRuler.add`](#add).

| Name            | Type              | Description          |
| --------------- | ----------------- | -------------------- |
| `pattern_dicts` | `Iterable[Dict]]` | The patterns to add. |

## AttributeRuler.patterns {#patterns tag="property"}

Get all patterns that have been added to the attribute ruler in the
`patterns_dict` format accepted by
[`AttributeRuler.add_patterns`](#add_patterns).

| Name        | Type         | Description                                |
| ----------- | ------------ | ------------------------------------------ |
| **RETURNS** | `List[dict]` | The patterns added to the attribute ruler. |

## AttributeRuler.load_from_tag_map {#load_from_tag_map tag="method"}

Load attribute ruler patterns from a tag map.

| Name      | Type | Description                                                                                |
| --------- | ---- | ------------------------------------------------------------------------------------------ |
| `tag_map` | dict | The tag map that maps fine-grained tags to coarse-grained tags and morphological features. |

## AttributeRuler.load_from_morph_rules {#load_from_morph_rules tag="method"}

Load attribute ruler patterns from morph rules.

| Name          | Type | Description                                                                                                          |
| ------------- | ---- | -------------------------------------------------------------------------------------------------------------------- |
| `morph_rules` | dict | The morph rules that map token text and fine-grained tags to coarse-grained tags, lemmas and morphological features. |

## AttributeRuler.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> attribute_ruler = nlp.add_pipe("attribute_ruler")
> attribute_ruler.to_disk("/path/to/attribute_ruler")
> ```

| Name           | Type            | Description                                                                                                           |
| -------------- | --------------- | --------------------------------------------------------------------------------------------------------------------- |
| `path`         | str / `Path`    | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                 |                                                                                                                       |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude.                                             |

## AttributeRuler.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> attribute_ruler = nlp.add_pipe("attribute_ruler")
> attribute_ruler.from_disk("/path/to/attribute_ruler")
> ```

| Name           | Type             | Description                                                                |
| -------------- | ---------------- | -------------------------------------------------------------------------- |
| `path`         | str / `Path`     | A path to a directory. Paths may be either strings or `Path`-like objects. |
| _keyword-only_ |                  |                                                                            |
| `exclude`      | `Iterable[str]`  | String names of [serialization fields](#serialization-fields) to exclude.  |
| **RETURNS**    | `AttributeRuler` | The modified `AttributeRuler` object.                                      |

## AttributeRuler.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> attribute_ruler = nlp.add_pipe("attribute_ruler")
> attribute_ruler_bytes = attribute_ruler.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Type            | Description                                                               |
| -------------- | --------------- | ------------------------------------------------------------------------- |
| _keyword-only_ |                 |                                                                           |
| `exclude`      | `Iterable[str]` | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | bytes           | The serialized form of the `AttributeRuler` object.                       |

## AttributeRuler.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> attribute_ruler_bytes = attribute_ruler.to_bytes()
> attribute_ruler = nlp.add_pipe("attribute_ruler")
> attribute_ruler.from_bytes(attribute_ruler_bytes)
> ```

| Name           | Type             | Description                                                               |
| -------------- | ---------------- | ------------------------------------------------------------------------- |
| `bytes_data`   | bytes            | The data to load from.                                                    |
| _keyword-only_ |                  |                                                                           |
| `exclude`      | `Iterable[str]`  | String names of [serialization fields](#serialization-fields) to exclude. |
| **RETURNS**    | `AttributeRuler` | The `AttributeRuler` object.                                              |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = attribute_ruler.to_disk("/path", exclude=["vocab"])
> ```

| Name       | Description                                                    |
| ---------- | -------------------------------------------------------------- |
| `vocab`    | The shared [`Vocab`](/api/vocab).                              |
| `patterns` | The Matcher patterns. You usually don't want to exclude this.  |
| `attrs`    | The attributes to set. You usually don't want to exclude this. |
| `indices`  | The token indices. You usually don't want to exclude this.     |
