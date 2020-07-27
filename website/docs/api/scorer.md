---
title: Scorer
teaser: Compute evaluation scores
tag: class
source: spacy/scorer.py
---

The `Scorer` computes evaluation scores. It's typically created by
[`Language.evaluate`](/api/language#evaluate).

In addition, the `Scorer` provides a number of evaluation methods for evaluating
`Token` and `Doc` attributes.

## Scorer.\_\_init\_\_ {#init tag="method"}

Create a new `Scorer`.

> #### Example
>
> ```python
> from spacy.scorer import Scorer
>
> # default scoring pipeline
> scorer = Scorer()
>
> # provided scoring pipeline
> nlp = spacy.load("en_core_web_sm")
> scorer = Scorer(nlp)
> ```

| Name        | Type     | Description                                                                                                                                                                                                                                                            |
| ----------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nlp`       | Language | The pipeline to use for scoring, where each pipeline component may provide a scoring method. If none is provided, then a default pipeline for the multi-language code `xx` is constructed containing: `senter`, `tagger`, `morphologizer`, `parser`, `ner`, `textcat`. |
| **RETURNS** | `Scorer` | The newly created object.                                                                                                                                                                                                                                              |

## Scorer.score {#score tag="method"}

Calculate the scores for a list of [`Example`](/api/example) objects using the
scoring methods provided by the components in the pipeline.

The returned `Dict` contains the scores provided by the individual pipeline
components. For the scoring methods provided by the `Scorer` and use by the core
pipeline components, the individual score names start with the `Token` or `Doc`
attribute being scored: `token_acc`, `token_p/r/f`, `sents_p/r/f`, `tag_acc`,
`pos_acc`, `morph_acc`, `morph_per_feat`, `lemma_acc`, `dep_uas`, `dep_las`,
`dep_las_per_type`, `ents_p/r/f`, `ents_per_type`, `textcat_macro_auc`,
`textcat_macro_f`.

> #### Example
>
> ```python
> scorer = Scorer()
> scorer.score(examples)
> ```

| Name        | Type                | Description                                                                                   |
| ----------- | ------------------- | --------------------------------------------------------------------------------------------- |
| `examples`  | `Iterable[Example]` | The `Example` objects holding both the predictions and the correct gold-standard annotations. |
| **RETURNS** | `Dict`              | A dictionary of scores.                                                                       |

## Scorer.score_tokenization {#score_tokenization tag="staticmethod"}

Scores the tokenization:

- `token_acc`: # correct tokens / # gold tokens
- `token_p/r/f`: PRF for token character spans

| Name        | Type                | Description                                                                                   |
| ----------- | ------------------- | --------------------------------------------------------------------------------------------- |
| `examples`  | `Iterable[Example]` | The `Example` objects holding both the predictions and the correct gold-standard annotations. |
| **RETURNS** | `Dict`              | A dictionary containing the scores `token_acc/p/r/f`.                                         |

## Scorer.score_token_attr {#score_token_attr tag="staticmethod"}

Scores a single token attribute.

| Name        | Type                | Description                                                                                                                   |
| ----------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `examples`  | `Iterable[Example]` | The `Example` objects holding both the predictions and the correct gold-standard annotations.                                 |
| `attr`      | `str`               | The attribute to score.                                                                                                       |
| `getter`    | `callable`          | Defaults to `getattr`. If provided, `getter(token, attr)` should return the value of the attribute for an individual `Token`. |
| **RETURNS** | `Dict`              | A dictionary containing the score `attr_acc`.                                                                                 |

## Scorer.score_token_attr_per_feat {#score_token_attr_per_feat tag="staticmethod"}

Scores a single token attribute per feature for a token attribute in UFEATS
format.

| Name        | Type                | Description                                                                                                                   |
| ----------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `examples`  | `Iterable[Example]` | The `Example` objects holding both the predictions and the correct gold-standard annotations.                                 |
| `attr`      | `str`               | The attribute to score.                                                                                                       |
| `getter`    | `callable`          | Defaults to `getattr`. If provided, `getter(token, attr)` should return the value of the attribute for an individual `Token`. |
| **RETURNS** | `Dict`              | A dictionary containing the per-feature PRF scores unders the key `attr_per_feat`.                                            |

## Scorer.score_spans {#score_spans tag="staticmethod"}

Returns PRF scores for labeled or unlabeled spans.

| Name        | Type                | Description                                                                                                           |
| ----------- | ------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `examples`  | `Iterable[Example]` | The `Example` objects holding both the predictions and the correct gold-standard annotations.                         |
| `attr`      | `str`               | The attribute to score.                                                                                               |
| `getter`    | `callable`          | Defaults to `getattr`. If provided, `getter(doc, attr)` should return the `Span` objects for an individual `Doc`.     |
| **RETURNS** | `Dict`              | A dictionary containing the PRF scores under the keys `attr_p/r/f` and the per-type PRF scores under `attr_per_type`. |

## Scorer.score_deps {#score_deps tag="staticmethod"}

Calculate the UAS, LAS, and LAS per type scores for dependency parses.

| Name            | Type                | Description                                                                                                                   |
| --------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `examples`      | `Iterable[Example]` | The `Example` objects holding both the predictions and the correct gold-standard annotations.                                 |
| `attr`          | `str`               | The attribute containing the dependency label.                                                                                |
| `getter`        | `callable`          | Defaults to `getattr`. If provided, `getter(token, attr)` should return the value of the attribute for an individual `Token`. |
| `head_attr`     | `str`               | The attribute containing the head token.                                                                                      |
| `head_getter`   | `callable`          | Defaults to `getattr`. If provided, `head_getter(token, attr)` should return the head for an individual `Token`.              |
| `ignore_labels` | `Tuple`             | Labels to ignore while scoring (e.g., `punct`).                                                                               |
| **RETURNS**     | `Dict`              | A dictionary containing the scores: `attr_uas`, `attr_las`, and `attr_las_per_type`.                                          |

## Scorer.score_cats {#score_cats tag="staticmethod"}

Calculate PRF and ROC AUC scores for a doc-level attribute that is a dict
containing scores for each label like `Doc.cats`. The reported overall score
depends on the scorer settings.

| Name             | Type                | Description                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ---------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`       | `Iterable[Example]` | The `Example` objects holding both the predictions and the correct gold-standard annotations.                                                                                                                                                                                                                                                                                                                                                     |
| `attr`           | `str`               | The attribute to score.                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `getter`         | `callable`          | Defaults to `getattr`. If provided, `getter(doc, attr)` should return the cats for an individual `Doc`.                                                                                                                                                                                                                                                                                                                                           |
| labels           | `Iterable[str]`     | The set of possible labels. Defaults to `[]`.                                                                                                                                                                                                                                                                                                                                                                                                     |
| `multi_label`    | `bool`              | Whether the attribute allows multiple labels. Defaults to `True`.                                                                                                                                                                                                                                                                                                                                                                                 |
| `positive_label` | `str`               | The positive label for a binary task with exclusive classes. Defaults to `None`.                                                                                                                                                                                                                                                                                                                                                                  |
| **RETURNS**      | `Dict`              | A dictionary containing the scores, with inapplicable scores as `None`: 1) for all: `attr_score` (one of `attr_f` / `attr_macro_f` / `attr_macro_auc`), `attr_score_desc` (text description of the overall score), `attr_f_per_type`, `attr_auc_per_type`; 2) for binary exclusive with positive label: `attr_p/r/f`; 3) for 3+ exclusive classes, macro-averaged fscore: `attr_macro_f`; 4) for multilabel, macro-averaged AUC: `attr_macro_auc` |
