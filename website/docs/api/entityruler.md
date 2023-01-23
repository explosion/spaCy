---
title: EntityRuler
new: 2.1
teaser: 'Pipeline component for rule-based named entity recognition'
api_string_name: entity_ruler
api_trainable: false
---

<Infobox title="New in v4" variant="warning">

As of spaCy v4, there is no separate `EntityRuler` class. The entity ruler is
implemented as a special case of the `SpanRuler` component.

See the [migration guide](#migrating) below for differences between the v3
`EntityRuler` and v4 `SpanRuler` implementations of the `entity_ruler`
component.

See the [`SpanRuler`](/api/spanruler) API docs for the full API.

</Infobox>

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

## Migrating from v3 {#migrating}

### Loading patterns

Unlike the v3 `EntityRuler`, the `SpanRuler` cannot load patterns on
initialization with `SpanRuler(patterns=patterns)` or directly from a JSONL file
path with `SpanRuler.from_disk(jsonl_path)`. Patterns should be loaded from the
JSONL file separately and then added through
[`SpanRuler.initialize`](/api/spanruler#initialize]) or
[`SpanRuler.add_patterns`](/api/spanruler#add_patterns).

```diff
 ruler = nlp.get_pipe("entity_ruler")
- ruler.from_disk("patterns.jsonl")
+ import srsly
+ patterns = srsly.read_jsonl("patterns.jsonl")
+ ruler.add_patterns(patterns)
```

### Saving patterns

`SpanRuler.to_disk` always saves the full component data to a directory and does
not include an option to save the patterns to a single JSONL file.

```diff
 ruler = nlp.get_pipe("entity_ruler")
- ruler.to_disk("patterns.jsonl")
+ import srsly
+ srsly.write_jsonl("patterns.jsonl", ruler.patterns)
```

### Accessing token and phrase patterns

The separate token patterns and phrase patterns are no longer accessible under
`ruler.token_patterns` or `ruler.phrase_patterns`. You can access the combined
patterns in their original format using the property
[`SpanRuler.patterns`](/api/spanruler#patterns).

### Removing patterns by ID

[`SpanRuler.remove`](/api/spanruler#remove) removes by label rather than ID. To
remove by ID, use [`SpanRuler.remove_by_id`](/api/spanruler#remove_by_id):

```diff
 ruler = nlp.get_pipe("entity_ruler")
- ruler.remove("id")
+ ruler.remove_by_id("id")
```
