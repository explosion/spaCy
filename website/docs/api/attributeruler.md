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
tags. See the [usage guide](/usage/linguistic-features/#mappings-exceptions) for
examples.

## Config and implementation {#config}

The default config is defined by the pipeline component factory and describes
how the component should be configured. You can override its settings via the
`config` argument on [`nlp.add_pipe`](/api/language#add_pipe) or in your
[`config.cfg` for training](/usage/training#config).

> #### Example
>
> ```python
> config = {"validate": True}
> nlp.add_pipe("attribute_ruler", config=config)
> ```

| Setting    | Description                                                                                   |
| ---------- | --------------------------------------------------------------------------------------------- |
| `validate` | Whether patterns should be validated (passed to the `Matcher`). Defaults to `False`. ~~bool~~ |

```python
%%GITHUB_SPACY/spacy/pipeline/attributeruler.py
```

## AttributeRuler.\_\_init\_\_ {#init tag="method"}

Initialize the attribute ruler.

> #### Example
>
> ```python
> # Construction via add_pipe
> ruler = nlp.add_pipe("attribute_ruler")
> ```

| Name           | Description                                                                                                                                                                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `vocab`        | The shared vocabulary to pass to the matcher. ~~Vocab~~                                                                                                                                                                                                                                    |
| `name`         | Instance name of the current pipeline component. Typically passed in automatically from the factory when the component is added. ~~str~~                                                                                                                                                   |
| _keyword-only_ |                                                                                                                                                                                                                                                                                            |
| `validate`     | Whether patterns should be validated (passed to the [`Matcher`](/api/matcher#init)). Defaults to `False`. ~~bool~~                                                                                                                                                                         |
| `scorer`       | The scoring method. Defaults to [`Scorer.score_token_attr`](/api/scorer#score_token_attr) for the attributes `"tag`", `"pos"`, `"morph"` and `"lemma"` and [`Scorer.score_token_attr_per_feat`](/api/scorer#score_token_attr_per_feat) for the attribute `"morph"`. ~~Optional[Callable]~~ |

## AttributeRuler.\_\_call\_\_ {#call tag="method"}

Apply the attribute ruler to a `Doc`, setting token attributes for tokens
matched by the provided patterns.

| Name        | Description                      |
| ----------- | -------------------------------- |
| `doc`       | The document to process. ~~Doc~~ |
| **RETURNS** | The processed document. ~~Doc~~  |

## AttributeRuler.add {#add tag="method"}

Add patterns to the attribute ruler. The patterns are a list of `Matcher`
patterns and the attributes are a dict of attributes to set on the matched
token. If the pattern matches a span of more than one token, the `index` can be
used to set the attributes for the token at that index in the span. The `index`
may be negative to index from the end of the span.

> #### Example
>
> ```python
> ruler = nlp.add_pipe("attribute_ruler")
> patterns = [[{"TAG": "VB"}]]
> attrs = {"POS": "VERB"}
> ruler.add(patterns=patterns, attrs=attrs)
> ```

| Name       | Description                                                                                                                       |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `patterns` | The `Matcher` patterns to add. ~~Iterable[List[Dict[Union[int, str], Any]]]~~                                                     |
| `attrs`    | The attributes to assign to the target token in the matched span. ~~Dict[str, Any]~~                                              |
| `index`    | The index of the token in the matched span to modify. May be negative to index from the end of the span. Defaults to `0`. ~~int~~ |

## AttributeRuler.add_patterns {#add_patterns tag="method"}

> #### Example
>
> ```python
> ruler = nlp.add_pipe("attribute_ruler")
> patterns = [
>   {
>     "patterns": [[{"TAG": "VB"}]], "attrs": {"POS": "VERB"}
>   },
>   {
>     "patterns": [[{"LOWER": "two"}, {"LOWER": "apples"}]],
>     "attrs": {"LEMMA": "apple"},
>     "index": -1
>   },
> ]
> ruler.add_patterns(patterns)
> ```

Add patterns from a list of pattern dicts. Each pattern dict can specify the
keys `"patterns"`, `"attrs"` and `"index"`, which match the arguments of
[`AttributeRuler.add`](/api/attributeruler#add).

| Name       | Description                                                                |
| ---------- | -------------------------------------------------------------------------- |
| `patterns` | The patterns to add. ~~Iterable[Dict[str, Union[List[dict], dict, int]]]~~ |

## AttributeRuler.patterns {#patterns tag="property"}

Get all patterns that have been added to the attribute ruler in the
`patterns_dict` format accepted by
[`AttributeRuler.add_patterns`](/api/attributeruler#add_patterns).

| Name        | Description                                                                                  |
| ----------- | -------------------------------------------------------------------------------------------- |
| **RETURNS** | The patterns added to the attribute ruler. ~~List[Dict[str, Union[List[dict], dict, int]]]~~ |

## AttributeRuler.initialize {#initialize tag="method"}

Initialize the component with data and used before training to load in rules
from a file. This method is typically called by
[`Language.initialize`](/api/language#initialize) and lets you customize
arguments it receives via the
[`[initialize.components]`](/api/data-formats#config-initialize) block in the
config.

> #### Example
>
> ```python
> ruler = nlp.add_pipe("attribute_ruler")
> ruler.initialize(lambda: [], nlp=nlp, patterns=patterns)
> ```
>
> ```ini
> ### config.cfg
> [initialize.components.attribute_ruler]
>
> [initialize.components.attribute_ruler.patterns]
> @readers = "srsly.read_json.v1"
> path = "corpus/attribute_ruler_patterns.json
> ```

| Name           | Description                                                                                                                                                                                                                                    |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | Function that returns gold-standard annotations in the form of [`Example`](/api/example) objects (the training data). Not used by this component. ~~Callable[[], Iterable[Example]]~~                                                          |
| _keyword-only_ |                                                                                                                                                                                                                                                |
| `nlp`          | The current `nlp` object. Defaults to `None`. ~~Optional[Language]~~                                                                                                                                                                           |
| `patterns`     | A list of pattern dicts with the keys as the arguments to [`AttributeRuler.add`](/api/attributeruler#add) (`patterns`/`attrs`/`index`) to add as patterns. Defaults to `None`. ~~Optional[Iterable[Dict[str, Union[List[dict], dict, int]]]]~~ |
| `tag_map`      | The tag map that maps fine-grained tags to coarse-grained tags and morphological features. Defaults to `None`. ~~Optional[Dict[str, Dict[Union[int, str], Union[int, str]]]]~~                                                                 |
| `morph_rules`  | The morph rules that map token text and fine-grained tags to coarse-grained tags, lemmas and morphological features. Defaults to `None`. ~~Optional[Dict[str, Dict[str, Dict[Union[int, str], Union[int, str]]]]]~~                            |

## AttributeRuler.load_from_tag_map {#load_from_tag_map tag="method"}

Load attribute ruler patterns from a tag map.

| Name      | Description                                                                                                                                      |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `tag_map` | The tag map that maps fine-grained tags to coarse-grained tags and morphological features. ~~Dict[str, Dict[Union[int, str], Union[int, str]]]~~ |

## AttributeRuler.load_from_morph_rules {#load_from_morph_rules tag="method"}

Load attribute ruler patterns from morph rules.

| Name          | Description                                                                                                                                                                           |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `morph_rules` | The morph rules that map token text and fine-grained tags to coarse-grained tags, lemmas and morphological features. ~~Dict[str, Dict[str, Dict[Union[int, str], Union[int, str]]]]~~ |

## AttributeRuler.to_disk {#to_disk tag="method"}

Serialize the pipe to disk.

> #### Example
>
> ```python
> ruler = nlp.add_pipe("attribute_ruler")
> ruler.to_disk("/path/to/attribute_ruler")
> ```

| Name           | Description                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `path`         | A path to a directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                                                            |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~                                                |

## AttributeRuler.from_disk {#from_disk tag="method"}

Load the pipe from disk. Modifies the object in place and returns it.

> #### Example
>
> ```python
> ruler = nlp.add_pipe("attribute_ruler")
> ruler.from_disk("/path/to/attribute_ruler")
> ```

| Name           | Description                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `path`         | A path to a directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| _keyword-only_ |                                                                                                 |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~     |
| **RETURNS**    | The modified `AttributeRuler` object. ~~AttributeRuler~~                                        |

## AttributeRuler.to_bytes {#to_bytes tag="method"}

> #### Example
>
> ```python
> ruler = nlp.add_pipe("attribute_ruler")
> ruler = ruler.to_bytes()
> ```

Serialize the pipe to a bytestring.

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The serialized form of the `AttributeRuler` object. ~~bytes~~                               |

## AttributeRuler.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> ruler_bytes = ruler.to_bytes()
> ruler = nlp.add_pipe("attribute_ruler")
> ruler.from_bytes(ruler_bytes)
> ```

| Name           | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| `bytes_data`   | The data to load from. ~~bytes~~                                                            |
| _keyword-only_ |                                                                                             |
| `exclude`      | String names of [serialization fields](#serialization-fields) to exclude. ~~Iterable[str]~~ |
| **RETURNS**    | The `AttributeRuler` object. ~~AttributeRuler~~                                             |

## Serialization fields {#serialization-fields}

During serialization, spaCy will export several data fields used to restore
different aspects of the object. If needed, you can exclude them from
serialization by passing in the string names via the `exclude` argument.

> #### Example
>
> ```python
> data = ruler.to_disk("/path", exclude=["vocab"])
> ```

| Name       | Description                                                     |
| ---------- | --------------------------------------------------------------- |
| `vocab`    | The shared [`Vocab`](/api/vocab).                               |
| `patterns` | The `Matcher` patterns. You usually don't want to exclude this. |
| `attrs`    | The attributes to set. You usually don't want to exclude this.  |
| `indices`  | The token indices. You usually don't want to exclude this.      |
