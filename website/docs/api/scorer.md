---
title: Scorer
teaser: Compute evaluation scores
tag: class
source: spacy/scorer.py
---

The `Scorer` computes evaluation scores. It's typically created by
[`Language.evaluate`](/api/language#evaluate). In addition, the `Scorer`
provides a number of evaluation methods for evaluating [`Token`](/api/token) and
[`Doc`](/api/doc) attributes.

## Scorer.\_\_init\_\_ {#init tag="method"}

Create a new `Scorer`.

> #### Example
>
> ```python
> from spacy.scorer import Scorer
>
> # Default scoring pipeline
> scorer = Scorer()
>
> # Provided scoring pipeline
> nlp = spacy.load("en_core_web_sm")
> scorer = Scorer(nlp)
> ```

| Name               | Description                                                                                                                                                                                                                               |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `nlp`              | The pipeline to use for scoring, where each pipeline component may provide a scoring method. If none is provided, then a default pipeline is constructed using the `default_lang` and `default_pipeline` settings. ~~Optional[Language]~~ |
| `default_lang`     | The language to use for a default pipeline if `nlp` is not provided. Defaults to `xx`. ~~str~~                                                                                                                                            |
| `default_pipeline` | The pipeline components to use for a default pipeline if `nlp` is not provided. Defaults to `("senter", "tagger", "morphologizer", "parser", "ner", "textcat")`. ~~Iterable[string]~~                                                     |
| _keyword-only_     |                                                                                                                                                                                                                                           |
| `\*\*kwargs`       | Any additional settings to pass on to the individual scoring methods. ~~Any~~                                                                                                                                                             |

## Scorer.score {#score tag="method"}

Calculate the scores for a list of [`Example`](/api/example) objects using the
scoring methods provided by the components in the pipeline.

The returned `Dict` contains the scores provided by the individual pipeline
components. For the scoring methods provided by the `Scorer` and used by the
core pipeline components, the individual score names start with the `Token` or
`Doc` attribute being scored:

- `token_acc`, `token_p`, `token_r`, `token_f`
- `sents_p`, `sents_r`, `sents_f`
- `tag_acc`
- `pos_acc`
- `morph_acc`, `morph_micro_p`, `morph_micro_r`, `morph_micro_f`,
  `morph_per_feat`
- `lemma_acc`
- `dep_uas`, `dep_las`, `dep_las_per_type`
- `ents_p`, `ents_r` `ents_f`, `ents_per_type`
- `spans_sc_p`, `spans_sc_r`, `spans_sc_f`
- `cats_score` (depends on config, description provided in `cats_score_desc`),
  `cats_micro_p`, `cats_micro_r`, `cats_micro_f`, `cats_macro_p`,
  `cats_macro_r`, `cats_macro_f`, `cats_macro_auc`, `cats_f_per_type`,
  `cats_auc_per_type`

> #### Example
>
> ```python
> scorer = Scorer()
> scores = scorer.score(examples)
> ```

| Name        | Description                                                                                                         |
| ----------- | ------------------------------------------------------------------------------------------------------------------- |
| `examples`  | The `Example` objects holding both the predictions and the correct gold-standard annotations. ~~Iterable[Example]~~ |
| **RETURNS** | A dictionary of scores. ~~Dict[str, Union[float, Dict[str, float]]]~~                                               |

## Scorer.score_tokenization {#score_tokenization tag="staticmethod" new="3"}

Scores the tokenization:

- `token_acc`: number of correct tokens / number of gold tokens
- `token_p`, `token_r`, `token_f`: precision, recall and F-score for token
  character spans

Docs with `has_unknown_spaces` are skipped during scoring.

> #### Example
>
> ```python
> scores = Scorer.score_tokenization(examples)
> ```

| Name        | Description                                                                                                         |
| ----------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `examples`  | The `Example` objects holding both the predictions and the correct gold-standard annotations. ~~Iterable[Example]~~ |
| **RETURNS** | `Dict`                                                                                                              | A dictionary containing the scores `token_acc`, `token_p`, `token_r`, `token_f`. ~~Dict[str, float]]~~ |

## Scorer.score_token_attr {#score_token_attr tag="staticmethod" new="3"}

Scores a single token attribute. Tokens with missing values in the reference doc
are skipped during scoring.

> #### Example
>
> ```python
> scores = Scorer.score_token_attr(examples, "pos")
> print(scores["pos_acc"])
> ```

| Name             | Description                                                                                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`       | The `Example` objects holding both the predictions and the correct gold-standard annotations. ~~Iterable[Example]~~                                           |
| `attr`           | The attribute to score. ~~str~~                                                                                                                               |
| _keyword-only_   |                                                                                                                                                               |
| `getter`         | Defaults to `getattr`. If provided, `getter(token, attr)` should return the value of the attribute for an individual `Token`. ~~Callable[[Token, str], Any]~~ |
| `missing_values` | Attribute values to treat as missing annotation in the reference annotation. Defaults to `{0, None, ""}`. ~~Set[Any]~~                                        |
| **RETURNS**      | A dictionary containing the score `{attr}_acc`. ~~Dict[str, float]~~                                                                                          |

## Scorer.score_token_attr_per_feat {#score_token_attr_per_feat tag="staticmethod" new="3"}

Scores a single token attribute per feature for a token attribute in the
Universal Dependencies
[FEATS](https://universaldependencies.org/format.html#morphological-annotation)
format. Tokens with missing values in the reference doc are skipped during
scoring.

> #### Example
>
> ```python
> scores = Scorer.score_token_attr_per_feat(examples, "morph")
> print(scores["morph_per_feat"])
> ```

| Name             | Description                                                                                                                                                             |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`       | The `Example` objects holding both the predictions and the correct gold-standard annotations. ~~Iterable[Example]~~                                                     |
| `attr`           | The attribute to score. ~~str~~                                                                                                                                         |
| _keyword-only_   |                                                                                                                                                                         |
| `getter`         | Defaults to `getattr`. If provided, `getter(token, attr)` should return the value of the attribute for an individual `Token`. ~~Callable[[Token, str], Any]~~           |
| `missing_values` | Attribute values to treat as missing annotation in the reference annotation. Defaults to `{0, None, ""}`. ~~Set[Any]~~                                                  |
| **RETURNS**      | A dictionary containing the micro PRF scores under the key `{attr}_micro_p/r/f` and the per-feature PRF scores under `{attr}_per_feat`. ~~Dict[str, Dict[str, float]]~~ |

## Scorer.score_spans {#score_spans tag="staticmethod" new="3"}

Returns PRF scores for labeled or unlabeled spans.

> #### Example
>
> ```python
> scores = Scorer.score_spans(examples, "ents")
> print(scores["ents_f"])
> ```

| Name             | Description                                                                                                                                                                                 |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`       | The `Example` objects holding both the predictions and the correct gold-standard annotations. ~~Iterable[Example]~~                                                                         |
| `attr`           | The attribute to score. ~~str~~                                                                                                                                                             |
| _keyword-only_   |                                                                                                                                                                                             |
| `getter`         | Defaults to `getattr`. If provided, `getter(doc, attr)` should return the `Span` objects for an individual `Doc`. ~~Callable[[Doc, str], Iterable[Span]]~~                                  |
| `has_annotation` | Defaults to `None`. If provided, `has_annotation(doc)` should return whether a `Doc` has annotation for this `attr`. Docs without annotation are skipped for scoring purposes. ~~str~~      |
| `labeled`        | Defaults to `True`. If set to `False`, two spans will be considered equal if their start and end match, irrespective of their label. ~~bool~~                                               |
| `allow_overlap`  | Defaults to `False`. Whether or not to allow overlapping spans. If set to `False`, the alignment will automatically resolve conflicts. ~~bool~~                                             |
| **RETURNS**      | A dictionary containing the PRF scores under the keys `{attr}_p`, `{attr}_r`, `{attr}_f` and the per-type PRF scores under `{attr}_per_type`. ~~Dict[str, Union[float, Dict[str, float]]]~~ |

## Scorer.score_deps {#score_deps tag="staticmethod" new="3"}

Calculate the UAS, LAS, and LAS per type scores for dependency parses. Tokens
with missing values for the `attr` (typically `dep`) are skipped during scoring.

> #### Example
>
> ```python
> def dep_getter(token, attr):
>     dep = getattr(token, attr)
>     dep = token.vocab.strings.as_string(dep).lower()
>     return dep
>
> scores = Scorer.score_deps(
>     examples,
>     "dep",
>     getter=dep_getter,
>     ignore_labels=("p", "punct")
> )
> print(scores["dep_uas"], scores["dep_las"])
> ```

| Name             | Description                                                                                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`       | The `Example` objects holding both the predictions and the correct gold-standard annotations. ~~Iterable[Example]~~                                           |
| `attr`           | The attribute to score. ~~str~~                                                                                                                               |
| _keyword-only_   |                                                                                                                                                               |
| `getter`         | Defaults to `getattr`. If provided, `getter(token, attr)` should return the value of the attribute for an individual `Token`. ~~Callable[[Token, str], Any]~~ |
| `head_attr`      | The attribute containing the head token. ~~str~~                                                                                                              |
| `head_getter`    | Defaults to `getattr`. If provided, `head_getter(token, attr)` should return the head for an individual `Token`. ~~Callable[[Doc, str], Token]~~              |
| `ignore_labels`  | Labels to ignore while scoring (e.g. `"punct"`). ~~Iterable[str]~~                                                                                            |
| `missing_values` | Attribute values to treat as missing annotation in the reference annotation. Defaults to `{0, None, ""}`. ~~Set[Any]~~                                        |
| **RETURNS**      | A dictionary containing the scores: `{attr}_uas`, `{attr}_las`, and `{attr}_las_per_type`. ~~Dict[str, Union[float, Dict[str, float]]]~~                      |

## Scorer.score_cats {#score_cats tag="staticmethod" new="3"}

Calculate PRF and ROC AUC scores for a doc-level attribute that is a dict
containing scores for each label like `Doc.cats`. The returned dictionary
contains the following scores:

- `{attr}_micro_p`, `{attr}_micro_r` and `{attr}_micro_f`: each instance across
  each label is weighted equally
- `{attr}_macro_p`, `{attr}_macro_r` and `{attr}_macro_f`: the average values
  across evaluations per label
- `{attr}_f_per_type` and `{attr}_auc_per_type`: each contains a dictionary of
  scores, keyed by label
- A final `{attr}_score` and corresponding `{attr}_score_desc` (text
  description)

The reported `{attr}_score` depends on the classification properties:

- **binary exclusive with positive label:** `{attr}_score` is set to the F-score
  of the positive label
- **3+ exclusive classes**, macro-averaged F-score:
  `{attr}_score = {attr}_macro_f`
- **multilabel**, macro-averaged AUC: `{attr}_score = {attr}_macro_auc`

> #### Example
>
> ```python
> labels = ["LABEL_A", "LABEL_B", "LABEL_C"]
> scores = Scorer.score_cats(
>     examples,
>     "cats",
>     labels=labels
> )
> print(scores["cats_macro_auc"])
> ```

| Name             | Description                                                                                                                                        |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `examples`       | The `Example` objects holding both the predictions and the correct gold-standard annotations. ~~Iterable[Example]~~                                |
| `attr`           | The attribute to score. ~~str~~                                                                                                                    |
| _keyword-only_   |                                                                                                                                                    |
| `getter`         | Defaults to `getattr`. If provided, `getter(doc, attr)` should return the cats for an individual `Doc`. ~~Callable[[Doc, str], Dict[str, float]]~~ |
| labels           | The set of possible labels. Defaults to `[]`. ~~Iterable[str]~~                                                                                    |
| `multi_label`    | Whether the attribute allows multiple labels. Defaults to `True`. ~~bool~~                                                                         |
| `positive_label` | The positive label for a binary task with exclusive classes. Defaults to `None`. ~~Optional[str]~~                                                 |
| **RETURNS**      | A dictionary containing the scores, with inapplicable scores as `None`. ~~Dict[str, Optional[float]]~~                                             |

## Scorer.score_links {#score_links tag="staticmethod" new="3"}

Returns PRF for predicted links on the entity level. To disentangle the
performance of the NEL from the NER, this method only evaluates NEL links for
entities that overlap between the gold reference and the predictions.

> #### Example
>
> ```python
> scores = Scorer.score_links(
>     examples,
>     negative_labels=["NIL", ""]
> )
> print(scores["nel_micro_f"])
> ```

| Name              | Description                                                                                                         |
| ----------------- | ------------------------------------------------------------------------------------------------------------------- |
| `examples`        | The `Example` objects holding both the predictions and the correct gold-standard annotations. ~~Iterable[Example]~~ |
| _keyword-only_    |                                                                                                                     |
| `negative_labels` | The string values that refer to no annotation (e.g. "NIL"). ~~Iterable[str]~~                                       |
| **RETURNS**       | A dictionary containing the scores. ~~Dict[str, Optional[float]]~~                                                  |

## get_ner_prf {#get_ner_prf new="3"}

Compute micro-PRF and per-entity PRF scores.

| Name       | Description                                                                                                         |
| ---------- | ------------------------------------------------------------------------------------------------------------------- |
| `examples` | The `Example` objects holding both the predictions and the correct gold-standard annotations. ~~Iterable[Example]~~ |
