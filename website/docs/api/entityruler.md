---
title: EntityRuler
new: 2.1
teaser: 'Pipeline component for rule-based named entity recognition'
api_string_name: entity_ruler
api_trainable: false
---

<Infobox title="New in v4" variant="warning">

As of spaCy v4, there is no separate `EntityRuler` class. The entity ruler is
implemented as a special case of the `SpanRuler` component. See the
[`SpanRuler`](/api/spanruler) API docs for the full API.

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
