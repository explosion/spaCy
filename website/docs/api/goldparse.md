---
title: GoldParse
teaser: A collection for training annotations
tag: class
source: spacy/gold.pyx
---

## GoldParse.\_\_init\_\_ {#init tag="method"}

Create a `GoldParse`. Unlike annotations in `entities`, label annotations in
`cats` can overlap, i.e. a single word can be covered by multiple labelled
spans. The [`TextCategorizer`](/api/textcategorizer) component expects true
examples of a label to have the value `1.0`, and negative examples of a label to
have the value `0.0`. Labels not in the dictionary are treated as missing – the
gradient for those labels will be zero.

| Name        | Type        | Description                                                                                                                                                                                                                            |
| ----------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc`       | `Doc`       | The document the annotations refer to.                                                                                                                                                                                                 |
| `words`     | iterable    | A sequence of unicode word strings.                                                                                                                                                                                                    |
| `tags`      | iterable    | A sequence of strings, representing tag annotations.                                                                                                                                                                                   |
| `heads`     | iterable    | A sequence of integers, representing syntactic head offsets.                                                                                                                                                                           |
| `deps`      | iterable    | A sequence of strings, representing the syntactic relation types.                                                                                                                                                                      |
| `entities`  | iterable    | A sequence of named entity annotations, either as BILUO tag strings, or as `(start_char, end_char, label)` tuples, representing the entity positions. If BILUO tag strings, you can specify missing values by setting the tag to None. |
| `cats`      | dict        | Labels for text classification. Each key in the dictionary may be a string or an int, or a `(start_char, end_char, label)` tuple, indicating that the label is applied to only part of the document (usually a sentence).              |
| **RETURNS** | `GoldParse` | The newly constructed object.                                                                                                                                                                                                          |

## GoldParse.\_\_len\_\_ {#len tag="method"}

Get the number of gold-standard tokens.

| Name        | Type | Description                         |
| ----------- | ---- | ----------------------------------- |
| **RETURNS** | int  | The number of gold-standard tokens. |

## GoldParse.is_projective {#is_projective tag="property"}

Whether the provided syntactic annotations form a projective dependency tree.

| Name        | Type | Description                               |
| ----------- | ---- | ----------------------------------------- |
| **RETURNS** | bool | Whether annotations form projective tree. |

## Attributes {#attributes}

| Name                              | Type | Description                                                                                                                                              |
| --------------------------------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tags`                            | list | The part-of-speech tag annotations.                                                                                                                      |
| `heads`                           | list | The syntactic head annotations.                                                                                                                          |
| `labels`                          | list | The syntactic relation-type annotations.                                                                                                                 |
| `ents`                            | list | The named entity annotations.                                                                                                                            |
| `cand_to_gold`                    | list | The alignment from candidate tokenization to gold tokenization.                                                                                          |
| `gold_to_cand`                    | list | The alignment from gold tokenization to candidate tokenization.                                                                                          |
| `cats` <Tag variant="new">2</Tag> | list | Entries in the list should be either a label, or a `(start, end, label)` triple. The tuple form is used for categories applied to spans of the document. |

## Utilities {#util}

### gold.biluo_tags_from_offsets {#biluo_tags_from_offsets tag="function"}

Encode labelled spans into per-token tags, using the
[BILUO scheme](/api/annotation#biluo) (Begin, In, Last, Unit, Out). Returns a
list of unicode strings, describing the tags. Each tag string will be of the
form of either `""`, `"O"` or `"{action}-{label}"`, where action is one of
`"B"`, `"I"`, `"L"`, `"U"`. The string `"-"` is used where the entity offsets
don't align with the tokenization in the `Doc` object. The training algorithm
will view these as missing values. `O` denotes a non-entity token. `B` denotes
the beginning of a multi-token entity, `I` the inside of an entity of three or
more tokens, and `L` the end of an entity of two or more tokens. `U` denotes a
single-token entity.

> #### Example
>
> ```python
> from spacy.gold import biluo_tags_from_offsets
>
> doc = nlp(u"I like London.")
> entities = [(7, 13, "LOC")]
> tags = biluo_tags_from_offsets(doc, entities)
> assert tags == ["O", "O", "U-LOC", "O"]
> ```

| Name        | Type     | Description                                                                                                                                     |
| ----------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc`       | `Doc`    | The document that the entity offsets refer to. The output tags will refer to the token boundaries within the document.                          |
| `entities`  | iterable | A sequence of `(start, end, label)` triples. `start` and `end` should be character-offset integers denoting the slice into the original string. |
| **RETURNS** | list     | Unicode strings, describing the [BILUO](/api/annotation#biluo) tags.                                                                            |

### gold.offsets_from_biluo_tags {#offsets_from_biluo_tags tag="function"}

Encode per-token tags following the [BILUO scheme](/api/annotation#biluo) into
entity offsets.

> #### Example
>
> ```python
> from spacy.gold import offsets_from_biluo_tags
>
> doc = nlp(u"I like London.")
> tags = ["O", "O", "U-LOC", "O"]
> entities = offsets_from_biluo_tags(doc, tags)
> assert entities == [(7, 13, "LOC")]
> ```

| Name        | Type     | Description                                                                                                                                                                                                                 |
| ----------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc`       | `Doc`    | The document that the BILUO tags refer to.                                                                                                                                                                                  |
| `entities`  | iterable | A sequence of [BILUO](/api/annotation#biluo) tags with each tag describing one token. Each tag string will be of the form of either `""`, `"O"` or `"{action}-{label}"`, where action is one of `"B"`, `"I"`, `"L"`, `"U"`. |
| **RETURNS** | list     | A sequence of `(start, end, label)` triples. `start` and `end` will be character-offset integers denoting the slice into the original string.                                                                               |

### gold.spans_from_biluo_tags {#spans_from_biluo_tags tag="function" new="2.1"}

Encode per-token tags following the [BILUO scheme](/api/annotation#biluo) into
[`Span`](/api/span) objects. This can be used to create entity spans from
token-based tags, e.g. to overwrite the `doc.ents`.

> #### Example
>
> ```python
> from spacy.gold import offsets_from_biluo_tags
>
> doc = nlp(u"I like London.")
> tags = ["O", "O", "U-LOC", "O"]
> doc.ents = spans_from_biluo_tags(doc, tags)
> ```

| Name        | Type     | Description                                                                                                                                                                                                                 |
| ----------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc`       | `Doc`    | The document that the BILUO tags refer to.                                                                                                                                                                                  |
| `entities`  | iterable | A sequence of [BILUO](/api/annotation#biluo) tags with each tag describing one token. Each tag string will be of the form of either `""`, `"O"` or `"{action}-{label}"`, where action is one of `"B"`, `"I"`, `"L"`, `"U"`. |
| **RETURNS** | list     | A sequence of `Span` objects with added entity labels.                                                                                                                                                                      |
