---
title: GoldParse
teaser: A collection for training annotations
tag: class
source: spacy/gold.pyx
---

## GoldParse.\_\_init\_\_ {#init tag="method"}

Create a `GoldParse`. The [`TextCategorizer`](/api/textcategorizer) component
expects true examples of a label to have the value `1.0`, and negative examples
of a label to have the value `0.0`. Labels not in the dictionary are treated as
missing – the gradient for those labels will be zero.

| Name              | Type        | Description                                                                                                                                                                                                                            |
| ----------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc`             | `Doc`       | The document the annotations refer to.                                                                                                                                                                                                 |
| `words`           | iterable    | A sequence of unicode word strings.                                                                                                                                                                                                    |
| `tags`            | iterable    | A sequence of strings, representing tag annotations.                                                                                                                                                                                   |
| `heads`           | iterable    | A sequence of integers, representing syntactic head offsets.                                                                                                                                                                           |
| `deps`            | iterable    | A sequence of strings, representing the syntactic relation types.                                                                                                                                                                      |
| `entities`        | iterable    | A sequence of named entity annotations, either as BILUO tag strings, or as `(start_char, end_char, label)` tuples, representing the entity positions. If BILUO tag strings, you can specify missing values by setting the tag to None. |
| `cats`            | dict        | Labels for text classification. Each key in the dictionary is a string label for the category and each value is `1.0` (positive) or `0.0` (negative).                                                                                  |
| `links`           | dict        | Labels for entity linking. A dict with `(start_char, end_char)` keys, and the values being dicts with `kb_id:value` entries, representing external KB IDs mapped to either `1.0` (positive) or `0.0` (negative).                       |
| `make_projective` | bool        | Whether to projectivize the dependency tree. Defaults to `False`.                                                                                                                                                                      |
| **RETURNS**       | `GoldParse` | The newly constructed object.                                                                                                                                                                                                          |

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

| Name                                 | Type | Description                                                                                                              |
| ------------------------------------ | ---- | ------------------------------------------------------------------------------------------------------------------------ |
| `words`                              | list | The words.                                                                                                               |
| `tags`                               | list | The part-of-speech tag annotations.                                                                                      |
| `heads`                              | list | The syntactic head annotations.                                                                                          |
| `labels`                             | list | The syntactic relation-type annotations.                                                                                 |
| `ner`                                | list | The named entity annotations as BILUO tags.                                                                              |
| `cand_to_gold`                       | list | The alignment from candidate tokenization to gold tokenization.                                                          |
| `gold_to_cand`                       | list | The alignment from gold tokenization to candidate tokenization.                                                          |
| `cats` <Tag variant="new">2</Tag>    | dict | Keys in the dictionary are string category labels with values `1.0` or `0.0`.                                            |
| `links` <Tag variant="new">2.2</Tag> | dict | Keys in the dictionary are `(start_char, end_char)` triples, and the values are dictionaries with `kb_id:value` entries. |

## Utilities {#util}

### gold.docs_to_json {#docs_to_json tag="function"}

Convert a list of Doc objects into the
[JSON-serializable format](/api/annotation#json-input) used by the
[`spacy train`](/api/cli#train) command. Each input doc will be treated as a
'paragraph' in the output doc.

> #### Example
>
> ```python
> from spacy.gold import docs_to_json
>
> doc = nlp("I like London")
> json_data = docs_to_json([doc])
> ```

| Name        | Type             | Description                                |
| ----------- | ---------------- | ------------------------------------------ |
| `docs`      | iterable / `Doc` | The `Doc` object(s) to convert.            |
| `id`        | int              | ID to assign to the JSON. Defaults to `0`. |
| **RETURNS** | dict             | The data in spaCy's JSON format.           |

### gold.align {#align tag="function"}

Calculate alignment tables between two tokenizations, using the Levenshtein
algorithm. The alignment is case-insensitive.

<Infobox title="Important note" variant="warning">

The current implementation of the alignment algorithm assumes that both
tokenizations add up to the same string. For example, you'll be able to align
`["I", "'", "m"]` and `["I", "'m"]`, which both add up to `"I'm"`, but not
`["I", "'m"]` and `["I", "am"]`.

</Infobox>

> #### Example
>
> ```python
> from spacy.gold import align
>
> bert_tokens = ["obama", "'", "s", "podcast"]
> spacy_tokens = ["obama", "'s", "podcast"]
> alignment = align(bert_tokens, spacy_tokens)
> cost, a2b, b2a, a2b_multi, b2a_multi = alignment
> ```

| Name        | Type  | Description                                                                |
| ----------- | ----- | -------------------------------------------------------------------------- |
| `tokens_a`  | list  | String values of candidate tokens to align.                                |
| `tokens_b`  | list  | String values of reference tokens to align.                                |
| **RETURNS** | tuple | A `(cost, a2b, b2a, a2b_multi, b2a_multi)` tuple describing the alignment. |

The returned tuple contains the following alignment information:

> #### Example
>
> ```python
> a2b = array([0, -1, -1, 2])
> b2a = array([0, 2, 3])
> a2b_multi = {1: 1, 2: 1}
> b2a_multi = {}
> ```
>
> If `a2b[3] == 2`, that means that `tokens_a[3]` aligns to `tokens_b[2]`. If
> there's no one-to-one alignment for a token, it has the value `-1`.

| Name        | Type                                   | Description                                                                                                                                     |
| ----------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `cost`      | int                                    | The number of misaligned tokens.                                                                                                                |
| `a2b`       | `numpy.ndarray[ndim=1, dtype='int32']` | One-to-one mappings of indices in `tokens_a` to indices in `tokens_b`.                                                                          |
| `b2a`       | `numpy.ndarray[ndim=1, dtype='int32']` | One-to-one mappings of indices in `tokens_b` to indices in `tokens_a`.                                                                          |
| `a2b_multi` | dict                                   | A dictionary mapping indices in `tokens_a` to indices in `tokens_b`, where multiple tokens of `tokens_a` align to the same token of `tokens_b`. |
| `b2a_multi` | dict                                   | A dictionary mapping indices in `tokens_b` to indices in `tokens_a`, where multiple tokens of `tokens_b` align to the same token of `tokens_a`. |

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
> doc = nlp("I like London.")
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
> doc = nlp("I like London.")
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
> from spacy.gold import spans_from_biluo_tags
>
> doc = nlp("I like London.")
> tags = ["O", "O", "U-LOC", "O"]
> doc.ents = spans_from_biluo_tags(doc, tags)
> ```

| Name        | Type     | Description                                                                                                                                                                                                                 |
| ----------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc`       | `Doc`    | The document that the BILUO tags refer to.                                                                                                                                                                                  |
| `entities`  | iterable | A sequence of [BILUO](/api/annotation#biluo) tags with each tag describing one token. Each tag string will be of the form of either `""`, `"O"` or `"{action}-{label}"`, where action is one of `"B"`, `"I"`, `"L"`, `"U"`. |
| **RETURNS** | list     | A sequence of `Span` objects with added entity labels.                                                                                                                                                                      |
