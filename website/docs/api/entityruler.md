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

## Assigned Attributes {#assigned-attributes}

This component assigns predictions basically the same way as the
[`EntityRecognizer`](/api/entityrecognizer).

Predictions can be accessed under `Doc.ents` as a tuple. Each label will also be
reflected in each underlying token, where it is saved in the `Token.ent_type`
and `Token.ent_iob` fields. Note that by definition each token can only have one
label.

When setting `Doc.ents` to create training data, all the spans must be valid and
non-overlapping, or an error will be thrown.

| Location          | Value                                                             |
| ----------------- | ----------------------------------------------------------------- |
| `Doc.ents`        | The annotated spans. ~~Tuple[Span]~~                              |
| `Token.ent_iob`   | An enum encoding of the IOB part of the named entity tag. ~~int~~ |
| `Token.ent_iob_`  | The IOB part of the named entity tag. ~~str~~                     |
| `Token.ent_type`  | The label part of the named entity tag (hash). ~~int~~            |
| `Token.ent_type_` | The label part of the named entity tag. ~~str~~                   |

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

| Setting               | Description                                                                                                                                                                                   |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `phrase_matcher_attr` | Optional attribute name match on for the internal [`PhraseMatcher`](/api/phrasematcher), e.g. `LOWER` to match on the lowercase token text. Defaults to `None`. ~~Optional[Union[int, str]]~~ |
| `validate`            | Whether patterns should be validated (passed to the `Matcher` and `PhraseMatcher`). Defaults to `False`. ~~bool~~                                                                             |
| `overwrite_ents`      | If existing entities are present, e.g. entities added by the model, overwrite them by matches if necessary. Defaults to `False`. ~~bool~~                                                     |
| `ent_id_sep`          | Separator used internally for entity IDs. Defaults to `"\|\|"`. ~~str~~                                                                                                                       |
| `scorer`              | The scoring method. Defaults to [`spacy.scorer.get_ner_prf`](/api/scorer#get_ner_prf). ~~Optional[Callable]~~                                                                                 |

```python
%%GITHUB_SPACY/spacy/pipeline/entityruler.py
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

| Name                              | Description                                                                                                                                                                                                                           |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nlp`                             | The shared nlp object to pass the vocab to the matchers and process phrase patterns. ~~Language~~                                                                                                                                     |
| `name` <Tag variant="new">3</Tag> | Instance name of the current pipeline component. Typically passed in automatically from the factory when the component is added. Used to disable the current entity ruler while creating phrase patterns with the nlp object. ~~str~~ |
| _keyword-only_                    |                                                                                                                                                                                                                                       |
| `phrase_matcher_attr`             | Optional attribute name match on for the internal [`PhraseMatcher`](/api/phrasematcher), e.g. `LOWER` to match on the lowercase token text. Defaults to `None`. ~~Optional[Union[int, str]]~~                                         |
| `validate`                        | Whether patterns should be validated, passed to Matcher and PhraseMatcher as `validate`. Defaults to `False`. ~~bool~~                                                                                                                |
| `overwrite_ents`                  | If existing entities are present, e.g. entities added by the model, overwrite them by matches if necessary. Defaults to `False`. ~~bool~~                                                                                             |
| `ent_id_sep`                      | Separator used internally for entity IDs. Defaults to `"\|\|"`. ~~str~~                                                                                                                                                               |
| `patterns`                        | Optional patterns to load in on initialization. ~~Optional[List[Dict[str, Union[str, List[dict]]]]]~~                                                                                                                                 |

## EntityRuler.initialize {#initialize tag="method" new="3"}

Initialize the component with data and used before training to load in rules
from a file. This method is typically called by
[`Language.initialize`](/api/language#initialize) and lets you customize
arguments it receives via the
[`[initialize.components]`](/api/data-formats#config-initialize) block in the
config.

> #### Example
>
> ```python
> entity_ruler = nlp.add_pipe("entity_ruler")
> entity_ruler.initialize(lambda: [], nlp=nlp, patterns=patterns)
> ```
>
> ```ini
> ### config.cfg
> [initialize.components.entity_ruler]
>
> [initialize.components.entity_ruler.patterns]
> @readers = "srsly.read_jsonl.v1"
> path = "corpus/entity_ruler_patterns.jsonl
> ```

| Name           | Description                                                                                                                                                          |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `get_examples` | Function that returns gold-standard annotations in the form of [`Example`](/api/example) objects. Not used by the `EntityRuler`. ~~Callable[[], Iterable[Example]]~~ |
| _keyword-only_ |                                                                                                                                                                      |
| `nlp`          | The current `nlp` object. Defaults to `None`. ~~Optional[Language]~~                                                                                                 |
| `patterns`     | The list of patterns. Defaults to `None`. ~~Optional[Sequence[Dict[str, Union[str, List[Dict[str, Any]]]]]]~~                                                        |

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

| Name        | Description                     |
| ----------- | ------------------------------- |
| **RETURNS** | The number of patterns. ~~int~~ |

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

| Name        | Description                                           |
| ----------- | ----------------------------------------------------- |
| `label`     | The label to check. ~~str~~                           |
| **RETURNS** | Whether the entity ruler contains the label. ~~bool~~ |

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

| Name        | Description                                                          |
| ----------- | -------------------------------------------------------------------- |
| `doc`       | The `Doc` object to process, e.g. the `Doc` in the pipeline. ~~Doc~~ |
| **RETURNS** | The modified `Doc` with added entities, if available. ~~Doc~~        |

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

| Name       | Description                                                      |
| ---------- | ---------------------------------------------------------------- |
| `patterns` | The patterns to add. ~~List[Dict[str, Union[str, List[dict]]]]~~ |


## EntityRuler.remove {#remove tag="method" new="3.2.1"}

Remove a pattern by its ID from the entity ruler. A `ValueError` is raised if the ID does not exist.

> #### Example
>
> ```python
> patterns = [{"label": "ORG", "pattern": "Apple", "id": "apple"}]
> ruler = nlp.add_pipe("entity_ruler")
> ruler.add_patterns(patterns)
> ruler.remove("apple")
> ```

| Name       | Description                                                      |
| ---------- | ---------------------------------------------------------------- |
| `id`       | The ID of the pattern rule. ~~str~~ |

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

| Name   | Description                                                                                                                                              |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `path` | A path to a JSONL file or directory, which will be created if it doesn't exist. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |

## EntityRuler.from_disk {#from_disk tag="method"}

Load the entity ruler from a path. Expects either a file containing
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

| Name        | Description                                                                                                   |
| ----------- | ------------------------------------------------------------------------------------------------------------- |
| `path`      | A path to a JSONL file or directory. Paths may be either strings or `Path`-like objects. ~~Union[str, Path]~~ |
| **RETURNS** | The modified `EntityRuler` object. ~~EntityRuler~~                                                            |

## EntityRuler.to_bytes {#to_bytes tag="method"}

Serialize the entity ruler patterns to a bytestring.

> #### Example
>
> ```python
> ruler = nlp.add_pipe("entity_ruler")
> ruler_bytes = ruler.to_bytes()
> ```

| Name        | Description                        |
| ----------- | ---------------------------------- |
| **RETURNS** | The serialized patterns. ~~bytes~~ |

## EntityRuler.from_bytes {#from_bytes tag="method"}

Load the pipe from a bytestring. Modifies the object in place and returns it.

> #### Example
>
> ```python
> ruler_bytes = ruler.to_bytes()
> ruler = nlp.add_pipe("enity_ruler")
> ruler.from_bytes(ruler_bytes)
> ```

| Name         | Description                                        |
| ------------ | -------------------------------------------------- |
| `bytes_data` | The bytestring to load. ~~bytes~~                  |
| **RETURNS**  | The modified `EntityRuler` object. ~~EntityRuler~~ |

## EntityRuler.labels {#labels tag="property"}

All labels present in the match patterns.

| Name        | Description                            |
| ----------- | -------------------------------------- |
| **RETURNS** | The string labels. ~~Tuple[str, ...]~~ |

## EntityRuler.ent_ids {#ent_ids tag="property" new="2.2.2"}

All entity IDs present in the `id` properties of the match patterns.

| Name        | Description                         |
| ----------- | ----------------------------------- |
| **RETURNS** | The string IDs. ~~Tuple[str, ...]~~ |

## EntityRuler.patterns {#patterns tag="property"}

Get all patterns that were added to the entity ruler.

| Name        | Description                                                                              |
| ----------- | ---------------------------------------------------------------------------------------- |
| **RETURNS** | The original patterns, one dictionary per pattern. ~~List[Dict[str, Union[str, dict]]]~~ |

## Attributes {#attributes}

| Name              | Description                                                                                                           |
| ----------------- | --------------------------------------------------------------------------------------------------------------------- |
| `matcher`         | The underlying matcher used to process token patterns. ~~Matcher~~                                                    |
| `phrase_matcher`  | The underlying phrase matcher used to process phrase patterns. ~~PhraseMatcher~~                                      |
| `token_patterns`  | The token patterns present in the entity ruler, keyed by label. ~~Dict[str, List[Dict[str, Union[str, List[dict]]]]~~ |
| `phrase_patterns` | The phrase patterns present in the entity ruler, keyed by label. ~~Dict[str, List[Doc]]~~                             |
