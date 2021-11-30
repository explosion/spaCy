from typing import Optional, Iterable, Dict, Set, List, Any, Callable, Tuple
from typing import TYPE_CHECKING
import numpy as np
from collections import defaultdict

from .training import Example
from .tokens import Token, Doc, Span
from .errors import Errors
from .util import get_lang_class, SimpleFrozenList
from .morphology import Morphology

if TYPE_CHECKING:
    # This lets us add type hints for mypy etc. without causing circular imports
    from .language import Language  # noqa: F401


DEFAULT_PIPELINE = ("senter", "tagger", "morphologizer", "parser", "ner", "textcat")
MISSING_VALUES = frozenset([None, 0, ""])


class PRFScore:
    """A precision / recall / F score."""

    def __init__(
        self,
        *,
        tp: int = 0,
        fp: int = 0,
        fn: int = 0,
    ) -> None:
        self.tp = tp
        self.fp = fp
        self.fn = fn

    def __len__(self) -> int:
        return self.tp + self.fp + self.fn

    def __iadd__(self, other):
        self.tp += other.tp
        self.fp += other.fp
        self.fn += other.fn
        return self

    def __add__(self, other):
        return PRFScore(
            tp=self.tp + other.tp, fp=self.fp + other.fp, fn=self.fn + other.fn
        )

    def score_set(self, cand: set, gold: set) -> None:
        self.tp += len(cand.intersection(gold))
        self.fp += len(cand - gold)
        self.fn += len(gold - cand)

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp + 1e-100)

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn + 1e-100)

    @property
    def fscore(self) -> float:
        p = self.precision
        r = self.recall
        return 2 * ((p * r) / (p + r + 1e-100))

    def to_dict(self) -> Dict[str, float]:
        return {"p": self.precision, "r": self.recall, "f": self.fscore}


class ROCAUCScore:
    """An AUC ROC score. This is only defined for binary classification.
    Use the method is_binary before calculating the score, otherwise it
    may throw an error."""

    def __init__(self) -> None:
        self.golds: List[Any] = []
        self.cands: List[Any] = []
        self.saved_score = 0.0
        self.saved_score_at_len = 0

    def score_set(self, cand, gold) -> None:
        self.cands.append(cand)
        self.golds.append(gold)

    def is_binary(self):
        return len(np.unique(self.golds)) == 2

    @property
    def score(self):
        if not self.is_binary():
            raise ValueError(Errors.E165.format(label=set(self.golds)))
        if len(self.golds) == self.saved_score_at_len:
            return self.saved_score
        self.saved_score = _roc_auc_score(self.golds, self.cands)
        self.saved_score_at_len = len(self.golds)
        return self.saved_score


class Scorer:
    """Compute evaluation scores."""

    def __init__(
        self,
        nlp: Optional["Language"] = None,
        default_lang: str = "xx",
        default_pipeline: Iterable[str] = DEFAULT_PIPELINE,
        **cfg,
    ) -> None:
        """Initialize the Scorer.

        DOCS: https://spacy.io/api/scorer#init
        """
        self.cfg = cfg
        if nlp:
            self.nlp = nlp
        else:
            nlp = get_lang_class(default_lang)()
            for pipe in default_pipeline:
                nlp.add_pipe(pipe)
            self.nlp = nlp

    def score(self, examples: Iterable[Example]) -> Dict[str, Any]:
        """Evaluate a list of Examples.

        examples (Iterable[Example]): The predicted annotations + correct annotations.
        RETURNS (Dict): A dictionary of scores.

        DOCS: https://spacy.io/api/scorer#score
        """
        scores = {}
        if hasattr(self.nlp.tokenizer, "score"):
            scores.update(self.nlp.tokenizer.score(examples, **self.cfg))  # type: ignore
        for name, component in self.nlp.pipeline:
            if hasattr(component, "score"):
                scores.update(component.score(examples, **self.cfg))
        return scores

    @staticmethod
    def score_tokenization(examples: Iterable[Example], **cfg) -> Dict[str, Any]:
        """Returns accuracy and PRF scores for tokenization.
        * token_acc: # correct tokens / # gold tokens
        * token_p/r/f: PRF for token character spans

        examples (Iterable[Example]): Examples to score
        RETURNS (Dict[str, Any]): A dictionary containing the scores
            token_acc/p/r/f.

        DOCS: https://spacy.io/api/scorer#score_tokenization
        """
        acc_score = PRFScore()
        prf_score = PRFScore()
        for example in examples:
            gold_doc = example.reference
            pred_doc = example.predicted
            if gold_doc.has_unknown_spaces:
                continue
            align = example.alignment
            gold_spans = set()
            pred_spans = set()
            for token in gold_doc:
                if token.orth_.isspace():
                    continue
                gold_spans.add((token.idx, token.idx + len(token)))
            for token in pred_doc:
                if token.orth_.isspace():
                    continue
                pred_spans.add((token.idx, token.idx + len(token)))
                if align.x2y.lengths[token.i] != 1:
                    acc_score.fp += 1
                else:
                    acc_score.tp += 1
            prf_score.score_set(pred_spans, gold_spans)
        if len(acc_score) > 0:
            return {
                "token_acc": acc_score.fscore,
                "token_p": prf_score.precision,
                "token_r": prf_score.recall,
                "token_f": prf_score.fscore,
            }
        else:
            return {
                "token_acc": None,
                "token_p": None,
                "token_r": None,
                "token_f": None,
            }

    @staticmethod
    def score_token_attr(
        examples: Iterable[Example],
        attr: str,
        *,
        getter: Callable[[Token, str], Any] = getattr,
        missing_values: Set[Any] = MISSING_VALUES,  # type: ignore[assignment]
        **cfg,
    ) -> Dict[str, Any]:
        """Returns an accuracy score for a token-level attribute.

        examples (Iterable[Example]): Examples to score
        attr (str): The attribute to score.
        getter (Callable[[Token, str], Any]): Defaults to getattr. If provided,
            getter(token, attr) should return the value of the attribute for an
            individual token.
        missing_values (Set[Any]): Attribute values to treat as missing annotation
            in the reference annotation.
        RETURNS (Dict[str, Any]): A dictionary containing the accuracy score
            under the key attr_acc.

        DOCS: https://spacy.io/api/scorer#score_token_attr
        """
        tag_score = PRFScore()
        for example in examples:
            gold_doc = example.reference
            pred_doc = example.predicted
            align = example.alignment
            gold_tags = set()
            missing_indices = set()
            for gold_i, token in enumerate(gold_doc):
                value = getter(token, attr)
                if value not in missing_values:
                    gold_tags.add((gold_i, getter(token, attr)))
                else:
                    missing_indices.add(gold_i)
            pred_tags = set()
            for token in pred_doc:
                if token.orth_.isspace():
                    continue
                if align.x2y.lengths[token.i] == 1:
                    gold_i = align.x2y[token.i].dataXd[0, 0]
                    if gold_i not in missing_indices:
                        pred_tags.add((gold_i, getter(token, attr)))
            tag_score.score_set(pred_tags, gold_tags)
        score_key = f"{attr}_acc"
        if len(tag_score) == 0:
            return {score_key: None}
        else:
            return {score_key: tag_score.fscore}

    @staticmethod
    def score_token_attr_per_feat(
        examples: Iterable[Example],
        attr: str,
        *,
        getter: Callable[[Token, str], Any] = getattr,
        missing_values: Set[Any] = MISSING_VALUES,  # type: ignore[assignment]
        **cfg,
    ) -> Dict[str, Any]:
        """Return micro PRF and PRF scores per feat for a token attribute in
        UFEATS format.

        examples (Iterable[Example]): Examples to score
        attr (str): The attribute to score.
        getter (Callable[[Token, str], Any]): Defaults to getattr. If provided,
            getter(token, attr) should return the value of the attribute for an
            individual token.
        missing_values (Set[Any]): Attribute values to treat as missing
            annotation in the reference annotation.
        RETURNS (dict): A dictionary containing the micro PRF scores under the
            key attr_micro_p/r/f and the per-feat PRF scores under
            attr_per_feat.
        """
        micro_score = PRFScore()
        per_feat = {}
        for example in examples:
            pred_doc = example.predicted
            gold_doc = example.reference
            align = example.alignment
            gold_per_feat: Dict[str, Set] = {}
            missing_indices = set()
            for gold_i, token in enumerate(gold_doc):
                value = getter(token, attr)
                morph = gold_doc.vocab.strings[value]
                if value not in missing_values and morph != Morphology.EMPTY_MORPH:
                    for feat in morph.split(Morphology.FEATURE_SEP):
                        field, values = feat.split(Morphology.FIELD_SEP)
                        if field not in per_feat:
                            per_feat[field] = PRFScore()
                        if field not in gold_per_feat:
                            gold_per_feat[field] = set()
                        gold_per_feat[field].add((gold_i, feat))
                else:
                    missing_indices.add(gold_i)
            pred_per_feat: Dict[str, Set] = {}
            for token in pred_doc:
                if token.orth_.isspace():
                    continue
                if align.x2y.lengths[token.i] == 1:
                    gold_i = align.x2y[token.i].dataXd[0, 0]
                    if gold_i not in missing_indices:
                        value = getter(token, attr)
                        morph = gold_doc.vocab.strings[value]
                        if (
                            value not in missing_values
                            and morph != Morphology.EMPTY_MORPH
                        ):
                            for feat in morph.split(Morphology.FEATURE_SEP):
                                field, values = feat.split(Morphology.FIELD_SEP)
                                if field not in per_feat:
                                    per_feat[field] = PRFScore()
                                if field not in pred_per_feat:
                                    pred_per_feat[field] = set()
                                pred_per_feat[field].add((gold_i, feat))
            for field in per_feat:
                micro_score.score_set(
                    pred_per_feat.get(field, set()), gold_per_feat.get(field, set())
                )
                per_feat[field].score_set(
                    pred_per_feat.get(field, set()), gold_per_feat.get(field, set())
                )
        result: Dict[str, Any] = {}
        if len(micro_score) > 0:
            result[f"{attr}_micro_p"] = micro_score.precision
            result[f"{attr}_micro_r"] = micro_score.recall
            result[f"{attr}_micro_f"] = micro_score.fscore
            result[f"{attr}_per_feat"] = {k: v.to_dict() for k, v in per_feat.items()}
        else:
            result[f"{attr}_micro_p"] = None
            result[f"{attr}_micro_r"] = None
            result[f"{attr}_micro_f"] = None
            result[f"{attr}_per_feat"] = None
        return result

    @staticmethod
    def score_spans(
        examples: Iterable[Example],
        attr: str,
        *,
        getter: Callable[[Doc, str], Iterable[Span]] = getattr,
        has_annotation: Optional[Callable[[Doc], bool]] = None,
        labeled: bool = True,
        allow_overlap: bool = False,
        **cfg,
    ) -> Dict[str, Any]:
        """Returns PRF scores for labeled spans.

        examples (Iterable[Example]): Examples to score
        attr (str): The attribute to score.
        getter (Callable[[Doc, str], Iterable[Span]]): Defaults to getattr. If
            provided, getter(doc, attr) should return the spans for the
            individual doc.
        has_annotation (Optional[Callable[[Doc], bool]]) should return whether a `Doc`
            has annotation for this `attr`. Docs without annotation are skipped for
            scoring purposes.
        labeled (bool): Whether or not to include label information in
            the evaluation. If set to 'False', two spans will be considered
            equal if their start and end match, irrespective of their label.
        allow_overlap (bool): Whether or not to allow overlapping spans.
            If set to 'False', the alignment will automatically resolve conflicts.
        RETURNS (Dict[str, Any]): A dictionary containing the PRF scores under
            the keys attr_p/r/f and the per-type PRF scores under attr_per_type.

        DOCS: https://spacy.io/api/scorer#score_spans
        """
        score = PRFScore()
        score_per_type = dict()
        for example in examples:
            pred_doc = example.predicted
            gold_doc = example.reference
            # Option to handle docs without annotation for this attribute
            if has_annotation is not None and not has_annotation(gold_doc):
                continue
            # Find all labels in gold
            labels = set([k.label_ for k in getter(gold_doc, attr)])
            # If labeled, find all labels in pred
            if has_annotation is None or (
                has_annotation is not None and has_annotation(pred_doc)
            ):
                labels |= set([k.label_ for k in getter(pred_doc, attr)])
            # Set up all labels for per type scoring and prepare gold per type
            gold_per_type: Dict[str, Set] = {label: set() for label in labels}
            for label in labels:
                if label not in score_per_type:
                    score_per_type[label] = PRFScore()
            # Find all predidate labels, for all and per type
            gold_spans = set()
            pred_spans = set()
            for span in getter(gold_doc, attr):
                gold_span: Tuple
                if labeled:
                    gold_span = (span.label_, span.start, span.end - 1)
                else:
                    gold_span = (span.start, span.end - 1)
                gold_spans.add(gold_span)
                gold_per_type[span.label_].add(gold_span)
            pred_per_type: Dict[str, Set] = {label: set() for label in labels}
            if has_annotation is None or (
                has_annotation is not None and has_annotation(pred_doc)
            ):
                for span in example.get_aligned_spans_x2y(
                    getter(pred_doc, attr), allow_overlap
                ):
                    pred_span: Tuple
                    if labeled:
                        pred_span = (span.label_, span.start, span.end - 1)
                    else:
                        pred_span = (span.start, span.end - 1)
                    pred_spans.add(pred_span)
                    pred_per_type[span.label_].add(pred_span)
            # Scores per label
            if labeled:
                for k, v in score_per_type.items():
                    if k in pred_per_type:
                        v.score_set(pred_per_type[k], gold_per_type[k])
            # Score for all labels
            score.score_set(pred_spans, gold_spans)
        # Assemble final result
        final_scores: Dict[str, Any] = {
            f"{attr}_p": None,
            f"{attr}_r": None,
            f"{attr}_f": None,
        }
        if labeled:
            final_scores[f"{attr}_per_type"] = None
        if len(score) > 0:
            final_scores[f"{attr}_p"] = score.precision
            final_scores[f"{attr}_r"] = score.recall
            final_scores[f"{attr}_f"] = score.fscore
            if labeled:
                final_scores[f"{attr}_per_type"] = {
                    k: v.to_dict() for k, v in score_per_type.items()
                }
        return final_scores

    @staticmethod
    def score_cats(
        examples: Iterable[Example],
        attr: str,
        *,
        getter: Callable[[Doc, str], Any] = getattr,
        labels: Iterable[str] = SimpleFrozenList(),
        multi_label: bool = True,
        positive_label: Optional[str] = None,
        threshold: Optional[float] = None,
        **cfg,
    ) -> Dict[str, Any]:
        """Returns PRF and ROC AUC scores for a doc-level attribute with a
        dict with scores for each label like Doc.cats. The reported overall
        score depends on the scorer settings.

        examples (Iterable[Example]): Examples to score
        attr (str): The attribute to score.
        getter (Callable[[Doc, str], Any]): Defaults to getattr. If provided,
            getter(doc, attr) should return the values for the individual doc.
        labels (Iterable[str]): The set of possible labels. Defaults to [].
        multi_label (bool): Whether the attribute allows multiple labels.
            Defaults to True.
        positive_label (str): The positive label for a binary task with
            exclusive classes. Defaults to None.
        threshold (float): Cutoff to consider a prediction "positive". Defaults
            to 0.5 for multi-label, and 0.0 (i.e. whatever's highest scoring)
            otherwise.
        RETURNS (Dict[str, Any]): A dictionary containing the scores, with
            inapplicable scores as None:
            for all:
                attr_score (one of attr_micro_f / attr_macro_f / attr_macro_auc),
                attr_score_desc (text description of the overall score),
                attr_micro_p,
                attr_micro_r,
                attr_micro_f,
                attr_macro_p,
                attr_macro_r,
                attr_macro_f,
                attr_macro_auc,
                attr_f_per_type,
                attr_auc_per_type

        DOCS: https://spacy.io/api/scorer#score_cats
        """
        if threshold is None:
            threshold = 0.5 if multi_label else 0.0
        f_per_type = {label: PRFScore() for label in labels}
        auc_per_type = {label: ROCAUCScore() for label in labels}
        labels = set(labels)
        if labels:
            for eg in examples:
                labels.update(eg.predicted.cats.keys())
                labels.update(eg.reference.cats.keys())
        for example in examples:
            # Through this loop, None in the gold_cats indicates missing label.
            pred_cats = getter(example.predicted, attr)
            gold_cats = getter(example.reference, attr)

            for label in labels:
                pred_score = pred_cats.get(label, 0.0)
                gold_score = gold_cats.get(label, 0.0)
                if gold_score is not None:
                    auc_per_type[label].score_set(pred_score, gold_score)
            if multi_label:
                for label in labels:
                    pred_score = pred_cats.get(label, 0.0)
                    gold_score = gold_cats.get(label, 0.0)
                    if gold_score is not None:
                        if pred_score >= threshold and gold_score > 0:
                            f_per_type[label].tp += 1
                        elif pred_score >= threshold and gold_score == 0:
                            f_per_type[label].fp += 1
                        elif pred_score < threshold and gold_score > 0:
                            f_per_type[label].fn += 1
            elif pred_cats and gold_cats:
                # Get the highest-scoring for each.
                pred_label, pred_score = max(pred_cats.items(), key=lambda it: it[1])
                gold_label, gold_score = max(gold_cats.items(), key=lambda it: it[1])
                if gold_score is not None:
                    if pred_label == gold_label and pred_score >= threshold:
                        f_per_type[pred_label].tp += 1
                    else:
                        f_per_type[gold_label].fn += 1
                        if pred_score >= threshold:
                            f_per_type[pred_label].fp += 1
            elif gold_cats:
                gold_label, gold_score = max(gold_cats, key=lambda it: it[1])
                if gold_score is not None and gold_score > 0:
                    f_per_type[gold_label].fn += 1
            elif pred_cats:
                pred_label, pred_score = max(pred_cats.items(), key=lambda it: it[1])
                if pred_score >= threshold:
                    f_per_type[pred_label].fp += 1
        micro_prf = PRFScore()
        for label_prf in f_per_type.values():
            micro_prf.tp += label_prf.tp
            micro_prf.fn += label_prf.fn
            micro_prf.fp += label_prf.fp
        n_cats = len(f_per_type) + 1e-100
        macro_p = sum(prf.precision for prf in f_per_type.values()) / n_cats
        macro_r = sum(prf.recall for prf in f_per_type.values()) / n_cats
        macro_f = sum(prf.fscore for prf in f_per_type.values()) / n_cats
        # Limit macro_auc to those labels with gold annotations,
        # but still divide by all cats to avoid artificial boosting of datasets with missing labels
        macro_auc = (
            sum(auc.score if auc.is_binary() else 0.0 for auc in auc_per_type.values())
            / n_cats
        )
        results: Dict[str, Any] = {
            f"{attr}_score": None,
            f"{attr}_score_desc": None,
            f"{attr}_micro_p": micro_prf.precision,
            f"{attr}_micro_r": micro_prf.recall,
            f"{attr}_micro_f": micro_prf.fscore,
            f"{attr}_macro_p": macro_p,
            f"{attr}_macro_r": macro_r,
            f"{attr}_macro_f": macro_f,
            f"{attr}_macro_auc": macro_auc,
            f"{attr}_f_per_type": {k: v.to_dict() for k, v in f_per_type.items()},
            f"{attr}_auc_per_type": {
                k: v.score if v.is_binary() else None for k, v in auc_per_type.items()
            },
        }
        if len(labels) == 2 and not multi_label and positive_label:
            positive_label_f = results[f"{attr}_f_per_type"][positive_label]["f"]
            results[f"{attr}_score"] = positive_label_f
            results[f"{attr}_score_desc"] = f"F ({positive_label})"
        elif not multi_label:
            results[f"{attr}_score"] = results[f"{attr}_macro_f"]
            results[f"{attr}_score_desc"] = "macro F"
        else:
            results[f"{attr}_score"] = results[f"{attr}_macro_auc"]
            results[f"{attr}_score_desc"] = "macro AUC"
        return results

    @staticmethod
    def score_links(
        examples: Iterable[Example], *, negative_labels: Iterable[str], **cfg
    ) -> Dict[str, Any]:
        """Returns PRF for predicted links on the entity level.
        To disentangle the performance of the NEL from the NER,
        this method only evaluates NEL links for entities that overlap
        between the gold reference and the predictions.

        examples (Iterable[Example]): Examples to score
        negative_labels (Iterable[str]): The string values that refer to no annotation (e.g. "NIL")
        RETURNS (Dict[str, Any]): A dictionary containing the scores.

        DOCS: https://spacy.io/api/scorer#score_links
        """
        f_per_type = {}
        for example in examples:
            gold_ent_by_offset = {}
            for gold_ent in example.reference.ents:
                gold_ent_by_offset[(gold_ent.start_char, gold_ent.end_char)] = gold_ent

            for pred_ent in example.predicted.ents:
                gold_span = gold_ent_by_offset.get(
                    (pred_ent.start_char, pred_ent.end_char), None
                )
                if gold_span is not None:
                    label = gold_span.label_
                    if label not in f_per_type:
                        f_per_type[label] = PRFScore()
                    gold = gold_span.kb_id_
                    # only evaluating entities that overlap between gold and pred,
                    # to disentangle the performance of the NEL from the NER
                    if gold is not None:
                        pred = pred_ent.kb_id_
                        if gold in negative_labels and pred in negative_labels:
                            # ignore true negatives
                            pass
                        elif gold == pred:
                            f_per_type[label].tp += 1
                        elif gold in negative_labels:
                            f_per_type[label].fp += 1
                        elif pred in negative_labels:
                            f_per_type[label].fn += 1
                        else:
                            # a wrong prediction (e.g. Q42 != Q3) counts as both a FP as well as a FN
                            f_per_type[label].fp += 1
                            f_per_type[label].fn += 1
        micro_prf = PRFScore()
        for label_prf in f_per_type.values():
            micro_prf.tp += label_prf.tp
            micro_prf.fn += label_prf.fn
            micro_prf.fp += label_prf.fp
        n_labels = len(f_per_type) + 1e-100
        macro_p = sum(prf.precision for prf in f_per_type.values()) / n_labels
        macro_r = sum(prf.recall for prf in f_per_type.values()) / n_labels
        macro_f = sum(prf.fscore for prf in f_per_type.values()) / n_labels
        results = {
            f"nel_score": micro_prf.fscore,
            f"nel_score_desc": "micro F",
            f"nel_micro_p": micro_prf.precision,
            f"nel_micro_r": micro_prf.recall,
            f"nel_micro_f": micro_prf.fscore,
            f"nel_macro_p": macro_p,
            f"nel_macro_r": macro_r,
            f"nel_macro_f": macro_f,
            f"nel_f_per_type": {k: v.to_dict() for k, v in f_per_type.items()},
        }
        return results

    @staticmethod
    def score_deps(
        examples: Iterable[Example],
        attr: str,
        *,
        getter: Callable[[Token, str], Any] = getattr,
        head_attr: str = "head",
        head_getter: Callable[[Token, str], Token] = getattr,
        ignore_labels: Iterable[str] = SimpleFrozenList(),
        missing_values: Set[Any] = MISSING_VALUES,  # type: ignore[assignment]
        **cfg,
    ) -> Dict[str, Any]:
        """Returns the UAS, LAS, and LAS per type scores for dependency
        parses.

        examples (Iterable[Example]): Examples to score
        attr (str): The attribute containing the dependency label.
        getter (Callable[[Token, str], Any]): Defaults to getattr. If provided,
            getter(token, attr) should return the value of the attribute for an
            individual token.
        head_attr (str): The attribute containing the head token. Defaults to
            'head'.
        head_getter (Callable[[Token, str], Token]): Defaults to getattr. If provided,
            head_getter(token, attr) should return the value of the head for an
            individual token.
        ignore_labels (Tuple): Labels to ignore while scoring (e.g., punct).
        missing_values (Set[Any]): Attribute values to treat as missing annotation
            in the reference annotation.
        RETURNS (Dict[str, Any]): A dictionary containing the scores:
            attr_uas, attr_las, and attr_las_per_type.

        DOCS: https://spacy.io/api/scorer#score_deps
        """
        unlabelled = PRFScore()
        labelled = PRFScore()
        labelled_per_dep = dict()
        missing_indices = set()
        for example in examples:
            gold_doc = example.reference
            pred_doc = example.predicted
            align = example.alignment
            gold_deps = set()
            gold_deps_per_dep: Dict[str, Set] = {}
            for gold_i, token in enumerate(gold_doc):
                dep = getter(token, attr)
                head = head_getter(token, head_attr)
                if dep not in missing_values:
                    if dep not in ignore_labels:
                        gold_deps.add((gold_i, head.i, dep))
                        if dep not in labelled_per_dep:
                            labelled_per_dep[dep] = PRFScore()
                        if dep not in gold_deps_per_dep:
                            gold_deps_per_dep[dep] = set()
                        gold_deps_per_dep[dep].add((gold_i, head.i, dep))
                else:
                    missing_indices.add(gold_i)
            pred_deps = set()
            pred_deps_per_dep: Dict[str, Set] = {}
            for token in pred_doc:
                if token.orth_.isspace():
                    continue
                if align.x2y.lengths[token.i] != 1:
                    gold_i = None  # type: ignore
                else:
                    gold_i = align.x2y[token.i].dataXd[0, 0]
                if gold_i not in missing_indices:
                    dep = getter(token, attr)
                    head = head_getter(token, head_attr)
                    if dep not in ignore_labels and token.orth_.strip():
                        if align.x2y.lengths[head.i] == 1:
                            gold_head = align.x2y[head.i].dataXd[0, 0]
                        else:
                            gold_head = None
                        # None is indistinct, so we can't just add it to the set
                        # Multiple (None, None) deps are possible
                        if gold_i is None or gold_head is None:
                            unlabelled.fp += 1
                            labelled.fp += 1
                        else:
                            pred_deps.add((gold_i, gold_head, dep))
                            if dep not in labelled_per_dep:
                                labelled_per_dep[dep] = PRFScore()
                            if dep not in pred_deps_per_dep:
                                pred_deps_per_dep[dep] = set()
                            pred_deps_per_dep[dep].add((gold_i, gold_head, dep))
            labelled.score_set(pred_deps, gold_deps)
            for dep in labelled_per_dep:
                labelled_per_dep[dep].score_set(
                    pred_deps_per_dep.get(dep, set()), gold_deps_per_dep.get(dep, set())
                )
            unlabelled.score_set(
                set(item[:2] for item in pred_deps), set(item[:2] for item in gold_deps)
            )
        if len(unlabelled) > 0:
            return {
                f"{attr}_uas": unlabelled.fscore,
                f"{attr}_las": labelled.fscore,
                f"{attr}_las_per_type": {
                    k: v.to_dict() for k, v in labelled_per_dep.items()
                },
            }
        else:
            return {
                f"{attr}_uas": None,
                f"{attr}_las": None,
                f"{attr}_las_per_type": None,
            }


def get_ner_prf(examples: Iterable[Example], **kwargs) -> Dict[str, Any]:
    """Compute micro-PRF and per-entity PRF scores for a sequence of examples."""
    score_per_type = defaultdict(PRFScore)
    for eg in examples:
        if not eg.y.has_annotation("ENT_IOB"):
            continue
        golds = {(e.label_, e.start, e.end) for e in eg.y.ents}
        align_x2y = eg.alignment.x2y
        for pred_ent in eg.x.ents:
            if pred_ent.label_ not in score_per_type:
                score_per_type[pred_ent.label_] = PRFScore()
            indices = align_x2y[pred_ent.start : pred_ent.end].dataXd.ravel()
            if len(indices):
                g_span = eg.y[indices[0] : indices[-1] + 1]
                # Check we aren't missing annotation on this span. If so,
                # our prediction is neither right nor wrong, we just
                # ignore it.
                if all(token.ent_iob != 0 for token in g_span):
                    key = (pred_ent.label_, indices[0], indices[-1] + 1)
                    if key in golds:
                        score_per_type[pred_ent.label_].tp += 1
                        golds.remove(key)
                    else:
                        score_per_type[pred_ent.label_].fp += 1
        for label, start, end in golds:
            score_per_type[label].fn += 1
    totals = PRFScore()
    for prf in score_per_type.values():
        totals += prf
    if len(totals) > 0:
        return {
            "ents_p": totals.precision,
            "ents_r": totals.recall,
            "ents_f": totals.fscore,
            "ents_per_type": {k: v.to_dict() for k, v in score_per_type.items()},
        }
    else:
        return {
            "ents_p": None,
            "ents_r": None,
            "ents_f": None,
            "ents_per_type": None,
        }


# The following implementation of roc_auc_score() is adapted from
# scikit-learn, which is distributed under the New BSD License.
# Copyright (c) 2007–2019 The scikit-learn developers.
# See licenses/3rd_party_licenses.txt
def _roc_auc_score(y_true, y_score):
    """Compute Area Under the Receiver Operating Characteristic Curve (ROC AUC)
    from prediction scores.

    Note: this implementation is restricted to the binary classification task

    Parameters
    ----------
    y_true : array, shape = [n_samples] or [n_samples, n_classes]
        True binary labels or binary label indicators.
        The multiclass case expects shape = [n_samples] and labels
        with values in ``range(n_classes)``.

    y_score : array, shape = [n_samples] or [n_samples, n_classes]
        Target scores, can either be probability estimates of the positive
        class, confidence values, or non-thresholded measure of decisions
        (as returned by "decision_function" on some classifiers). For binary
        y_true, y_score is supposed to be the score of the class with greater
        label. The multiclass case expects shape = [n_samples, n_classes]
        where the scores correspond to probability estimates.

    Returns
    -------
    auc : float

    References
    ----------
    .. [1] `Wikipedia entry for the Receiver operating characteristic
            <https://en.wikipedia.org/wiki/Receiver_operating_characteristic>`_

    .. [2] Fawcett T. An introduction to ROC analysis[J]. Pattern Recognition
           Letters, 2006, 27(8):861-874.

    .. [3] `Analyzing a portion of the ROC curve. McClish, 1989
            <https://www.ncbi.nlm.nih.gov/pubmed/2668680>`_
    """
    if len(np.unique(y_true)) != 2:
        raise ValueError(Errors.E165.format(label=np.unique(y_true)))
    fpr, tpr, _ = _roc_curve(y_true, y_score)
    return _auc(fpr, tpr)


def _roc_curve(y_true, y_score):
    """Compute Receiver operating characteristic (ROC)

    Note: this implementation is restricted to the binary classification task.

    Parameters
    ----------

    y_true : array, shape = [n_samples]
        True binary labels. If labels are not either {-1, 1} or {0, 1}, then
        pos_label should be explicitly given.

    y_score : array, shape = [n_samples]
        Target scores, can either be probability estimates of the positive
        class, confidence values, or non-thresholded measure of decisions
        (as returned by "decision_function" on some classifiers).

    Returns
    -------
    fpr : array, shape = [>2]
        Increasing false positive rates such that element i is the false
        positive rate of predictions with score >= thresholds[i].

    tpr : array, shape = [>2]
        Increasing true positive rates such that element i is the true
        positive rate of predictions with score >= thresholds[i].

    thresholds : array, shape = [n_thresholds]
        Decreasing thresholds on the decision function used to compute
        fpr and tpr. `thresholds[0]` represents no instances being predicted
        and is arbitrarily set to `max(y_score) + 1`.

    Notes
    -----
    Since the thresholds are sorted from low to high values, they
    are reversed upon returning them to ensure they correspond to both ``fpr``
    and ``tpr``, which are sorted in reversed order during their calculation.

    References
    ----------
    .. [1] `Wikipedia entry for the Receiver operating characteristic
            <https://en.wikipedia.org/wiki/Receiver_operating_characteristic>`_

    .. [2] Fawcett T. An introduction to ROC analysis[J]. Pattern Recognition
           Letters, 2006, 27(8):861-874.
    """
    fps, tps, thresholds = _binary_clf_curve(y_true, y_score)

    # Add an extra threshold position
    # to make sure that the curve starts at (0, 0)
    tps = np.r_[0, tps]
    fps = np.r_[0, fps]
    thresholds = np.r_[thresholds[0] + 1, thresholds]

    if fps[-1] <= 0:
        fpr = np.repeat(np.nan, fps.shape)
    else:
        fpr = fps / fps[-1]

    if tps[-1] <= 0:
        tpr = np.repeat(np.nan, tps.shape)
    else:
        tpr = tps / tps[-1]

    return fpr, tpr, thresholds


def _binary_clf_curve(y_true, y_score):
    """Calculate true and false positives per binary classification threshold.

    Parameters
    ----------
    y_true : array, shape = [n_samples]
        True targets of binary classification

    y_score : array, shape = [n_samples]
        Estimated probabilities or decision function

    Returns
    -------
    fps : array, shape = [n_thresholds]
        A count of false positives, at index i being the number of negative
        samples assigned a score >= thresholds[i]. The total number of
        negative samples is equal to fps[-1] (thus true negatives are given by
        fps[-1] - fps).

    tps : array, shape = [n_thresholds <= len(np.unique(y_score))]
        An increasing count of true positives, at index i being the number
        of positive samples assigned a score >= thresholds[i]. The total
        number of positive samples is equal to tps[-1] (thus false negatives
        are given by tps[-1] - tps).

    thresholds : array, shape = [n_thresholds]
        Decreasing score values.
    """
    pos_label = 1.0

    y_true = np.ravel(y_true)
    y_score = np.ravel(y_score)

    # make y_true a boolean vector
    y_true = y_true == pos_label

    # sort scores and corresponding truth values
    desc_score_indices = np.argsort(y_score, kind="mergesort")[::-1]
    y_score = y_score[desc_score_indices]
    y_true = y_true[desc_score_indices]
    weight = 1.0

    # y_score typically has many tied values. Here we extract
    # the indices associated with the distinct values. We also
    # concatenate a value for the end of the curve.
    distinct_value_indices = np.where(np.diff(y_score))[0]
    threshold_idxs = np.r_[distinct_value_indices, y_true.size - 1]

    # accumulate the true positives with decreasing threshold
    tps = _stable_cumsum(y_true * weight)[threshold_idxs]
    fps = 1 + threshold_idxs - tps
    return fps, tps, y_score[threshold_idxs]


def _stable_cumsum(arr, axis=None, rtol=1e-05, atol=1e-08):
    """Use high precision for cumsum and check that final value matches sum

    Parameters
    ----------
    arr : array-like
        To be cumulatively summed as flat
    axis : int, optional
        Axis along which the cumulative sum is computed.
        The default (None) is to compute the cumsum over the flattened array.
    rtol : float
        Relative tolerance, see ``np.allclose``
    atol : float
        Absolute tolerance, see ``np.allclose``
    """
    out = np.cumsum(arr, axis=axis, dtype=np.float64)
    expected = np.sum(arr, axis=axis, dtype=np.float64)
    if not np.all(
        np.isclose(
            out.take(-1, axis=axis), expected, rtol=rtol, atol=atol, equal_nan=True
        )
    ):
        raise ValueError(Errors.E163)
    return out


def _auc(x, y):
    """Compute Area Under the Curve (AUC) using the trapezoidal rule

    This is a general function, given points on a curve.  For computing the
    area under the ROC-curve, see :func:`roc_auc_score`.

    Parameters
    ----------
    x : array, shape = [n]
        x coordinates. These must be either monotonic increasing or monotonic
        decreasing.
    y : array, shape = [n]
        y coordinates.

    Returns
    -------
    auc : float
    """
    x = np.ravel(x)
    y = np.ravel(y)

    direction = 1
    dx = np.diff(x)
    if np.any(dx < 0):
        if np.all(dx <= 0):
            direction = -1
        else:
            raise ValueError(Errors.E164.format(x=x))

    area = direction * np.trapz(y, x)
    if isinstance(area, np.memmap):
        # Reductions such as .sum used internally in np.trapz do not return a
        # scalar by default for numpy.memmap instances contrary to
        # regular numpy.ndarray instances.
        area = area.dtype.type(area)
    return area
