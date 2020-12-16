---
title: Scorer
teaser: Compute evaluation scores
tag: class
source: spacy/scorer.py
---

The `Scorer` computes and stores evaluation scores. It's typically created by
[`Language.evaluate`](/api/language#evaluate).

## Scorer.\_\_init\_\_ {#init tag="method"}

Create a new `Scorer`.

> #### Example
>
> ```python
> from spacy.scorer import Scorer
>
> scorer = Scorer()
> ```

| Name         | Type     | Description                                                  |
| ------------ | -------- | ------------------------------------------------------------ |
| `eval_punct` | bool     | Evaluate the dependency attachments to and from punctuation. |
| **RETURNS**  | `Scorer` | The newly created object.                                    |

## Scorer.score {#score tag="method"}

Update the evaluation scores from a single [`Doc`](/api/doc) /
[`GoldParse`](/api/goldparse) pair.

> #### Example
>
> ```python
> scorer = Scorer()
> scorer.score(doc, gold)
> ```

| Name           | Type        | Description                                                                                                          |
| -------------- | ----------- | -------------------------------------------------------------------------------------------------------------------- |
| `doc`          | `Doc`       | The predicted annotations.                                                                                           |
| `gold`         | `GoldParse` | The correct annotations.                                                                                             |
| `verbose`      | bool        | Print debugging information.                                                                                         |
| `punct_labels` | tuple       | Dependency labels for punctuation. Used to evaluate dependency attachments to punctuation if `eval_punct` is `True`. |

## Properties

| Name                                            | Type  | Description                                                                                                                                               |
| ----------------------------------------------- | ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `token_acc`                                     | float | Tokenization accuracy.                                                                                                                                    |
| `tags_acc`                                      | float | Part-of-speech tag accuracy (fine grained tags, i.e. `Token.tag`).                                                                                        |
| `uas`                                           | float | Unlabelled dependency score.                                                                                                                              |
| `las`                                           | float | Labelled dependency score.                                                                                                                                |
| `ents_p`                                        | float | Named entity accuracy (precision).                                                                                                                        |
| `ents_r`                                        | float | Named entity accuracy (recall).                                                                                                                           |
| `ents_f`                                        | float | Named entity accuracy (F-score).                                                                                                                          |
| `ents_per_type` <Tag variant="new">2.1.5</Tag>  | dict  | Scores per entity label. Keyed by label, mapped to a dict of `p`, `r` and `f` scores.                                                                     |
| `textcat_score` <Tag variant="new">2.2</Tag>    | float | F-score on positive label for binary exclusive, macro-averaged F-score for 3+ exclusive, macro-averaged AUC ROC score for multilabel (`-1` if undefined). |
| `textcats_per_cat` <Tag variant="new">2.2</Tag> | dict  | Scores per textcat label, keyed by label.                                                                                                                 |
| `las_per_type` <Tag variant="new">2.2.3</Tag>   | dict  | Labelled dependency scores, keyed by label.                                                                                                               |
| `scores`                                        | dict  | All scores, keyed by type.                                                                                                                                |
