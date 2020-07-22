import numpy as np

from .errors import Errors
from .util import get_lang_class
from .morphology import Morphology


class PRFScore:
    """
    A precision / recall / F score
    """

    def __init__(self):
        self.tp = 0
        self.fp = 0
        self.fn = 0

    def score_set(self, cand, gold):
        self.tp += len(cand.intersection(gold))
        self.fp += len(cand - gold)
        self.fn += len(gold - cand)

    @property
    def precision(self):
        return self.tp / (self.tp + self.fp + 1e-100)

    @property
    def recall(self):
        return self.tp / (self.tp + self.fn + 1e-100)

    @property
    def fscore(self):
        p = self.precision
        r = self.recall
        return 2 * ((p * r) / (p + r + 1e-100))

    def to_dict(self):
        return {"p": self.precision, "r": self.recall, "f": self.fscore}


class ROCAUCScore:
    """
    An AUC ROC score.
    """

    def __init__(self):
        self.golds = []
        self.cands = []
        self.saved_score = 0.0
        self.saved_score_at_len = 0

    def score_set(self, cand, gold):
        self.cands.append(cand)
        self.golds.append(gold)

    @property
    def score(self):
        if len(self.golds) == self.saved_score_at_len:
            return self.saved_score
        try:
            self.saved_score = _roc_auc_score(self.golds, self.cands)
        # catch ValueError: Only one class present in y_true.
        # ROC AUC score is not defined in that case.
        except ValueError:
            self.saved_score = -float("inf")
        self.saved_score_at_len = len(self.golds)
        return self.saved_score


class Scorer:
    """Compute evaluation scores."""

    def __init__(self, nlp=None, **cfg):
        """Initialize the Scorer.
        RETURNS (Scorer): The newly created object.

        DOCS: https://spacy.io/api/scorer#init
        """
        self.nlp = nlp
        self.cfg = cfg

        if not nlp:
            # create a default pipeline
            nlp = get_lang_class("xx")()
            nlp.add_pipe("senter")
            nlp.add_pipe("tagger")
            nlp.add_pipe("morphologizer")
            nlp.add_pipe("parser")
            nlp.add_pipe("ner")
            nlp.add_pipe("textcat")
            self.nlp = nlp

    def score(self, examples):
        """Evaluate a list of Examples.

        examples (Iterable[Example]): The predicted annotations + correct annotations.
        RETURNS (Dict): A dictionary of scores.
        DOCS: https://spacy.io/api/scorer#score
        """
        scores = {}

        if hasattr(self.nlp.tokenizer, "score"):
            scores.update(self.nlp.tokenizer.score(examples, **self.cfg))
        for name, component in self.nlp.pipeline:
            if hasattr(component, "score"):
                scores.update(component.score(examples, **self.cfg))

        return scores

    @staticmethod
    def score_tokenization(examples, **cfg):
        """Returns accuracy and PRF scores for tokenization.

        * token_acc: # correct tokens / # gold tokens
        * token_p/r/f: PRF for token character spans

        examples (Iterable[Example]): Examples to score
        RETURNS (dict): A dictionary containing the scores token_acc/p/r/f.
        """
        acc_score = PRFScore()
        prf_score = PRFScore()
        for example in examples:
            gold_doc = example.reference
            pred_doc = example.predicted
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
        return {
            "token_acc": acc_score.fscore,
            "token_p": prf_score.precision,
            "token_r": prf_score.recall,
            "token_f": prf_score.fscore,
        }

    @staticmethod
    def score_token_attr(examples, attr, getter=getattr, **cfg):
        """Returns an accuracy score for a token-level attribute.

        examples (Iterable[Example]): Examples to score
        attr (str): The attribute to score.
        getter (callable): Defaults to getattr. If provided,
            getter(token, attr) should return the value of the attribute for an
            individual token.
        RETURNS (dict): A dictionary containing the accuracy score under the
            key attr_acc.
        """
        tag_score = PRFScore()
        for example in examples:
            gold_doc = example.reference
            pred_doc = example.predicted
            align = example.alignment
            gold_tags = set()
            for gold_i, token in enumerate(gold_doc):
                gold_tags.add((gold_i, getter(token, attr)))
            pred_tags = set()
            for token in pred_doc:
                if token.orth_.isspace():
                    continue
                if align.x2y.lengths[token.i] == 1:
                    gold_i = align.x2y[token.i].dataXd[0, 0]
                    pred_tags.add((gold_i, getter(token, attr)))
            tag_score.score_set(pred_tags, gold_tags)
        return {
            attr + "_acc": tag_score.fscore,
        }

    @staticmethod
    def score_token_attr_per_feat(examples, attr, getter=getattr, **cfg):
        """Return PRF scores per feat for a token attribute in UFEATS format.

        examples (Iterable[Example]): Examples to score
        attr (str): The attribute to score.
        getter (callable): Defaults to getattr. If provided,
            getter(token, attr) should return the value of the attribute for an
            individual token.
        RETURNS (dict): A dictionary containing the per-feat PRF scores unders
            the key attr_per_feat.
        """
        per_feat = {}
        for example in examples:
            pred_doc = example.predicted
            gold_doc = example.reference
            align = example.alignment
            gold_per_feat = {}
            for gold_i, token in enumerate(gold_doc):
                morph = str(getter(token, attr))
                if morph:
                    for feat in morph.split(Morphology.FEATURE_SEP):
                        field, values = feat.split(Morphology.FIELD_SEP)
                        if field not in per_feat:
                            per_feat[field] = PRFScore()
                        if field not in gold_per_feat:
                            gold_per_feat[field] = set()
                        gold_per_feat[field].add((gold_i, feat))
            pred_per_feat = {}
            for token in pred_doc:
                if token.orth_.isspace():
                    continue
                if align.x2y.lengths[token.i] == 1:
                    gold_i = align.x2y[token.i].dataXd[0, 0]
                    morph = str(getter(token, attr))
                    if morph:
                        for feat in morph.split("|"):
                            field, values = feat.split("=")
                            if field not in per_feat:
                                per_feat[field] = PRFScore()
                            if field not in pred_per_feat:
                                pred_per_feat[field] = set()
                            pred_per_feat[field].add((gold_i, feat))
            for field in per_feat:
                per_feat[field].score_set(
                    pred_per_feat.get(field, set()), gold_per_feat.get(field, set()),
                )
        return {
            attr + "_per_feat": per_feat,
        }

    @staticmethod
    def score_spans(examples, attr, getter=getattr, **cfg):
        """Returns PRF scores for labeled spans.

        examples (Iterable[Example]): Examples to score
        attr (str): The attribute to score.
        getter (callable): Defaults to getattr. If provided,
            getter(doc, attr) should return the spans for the individual doc.
        RETURNS (dict): A dictionary containing the PRF scores under the
            keys attr_p/r/f and the per-type PRF scores under attr_per_type.
        """
        score = PRFScore()
        score_per_type = dict()
        for example in examples:
            pred_doc = example.predicted
            gold_doc = example.reference
            # Find all labels in gold and doc
            labels = set(
                [k.label_ for k in getter(gold_doc, attr)]
                + [k.label_ for k in getter(pred_doc, attr)]
            )
            # Set up all labels for per type scoring and prepare gold per type
            gold_per_type = {label: set() for label in labels}
            for label in labels:
                if label not in score_per_type:
                    score_per_type[label] = PRFScore()
            # Find all predidate labels, for all and per type
            gold_spans = set()
            pred_spans = set()

            # Special case for ents:
            # If we have missing values in the gold, we can't easily tell
            # whether our NER predictions are true.
            # It seems bad but it's what we've always done.
            if attr == "ents" and not all(token.ent_iob != 0 for token in gold_doc):
                continue

            for span in getter(gold_doc, attr):
                gold_span = (span.label_, span.start, span.end - 1)
                gold_spans.add(gold_span)
                gold_per_type[span.label_].add((span.label_, span.start, span.end - 1))
            pred_per_type = {label: set() for label in labels}
            for span in example.get_aligned_spans_x2y(getter(pred_doc, attr)):
                pred_spans.add((span.label_, span.start, span.end - 1))
                pred_per_type[span.label_].add((span.label_, span.start, span.end - 1))
            # Scores per label
            for k, v in score_per_type.items():
                if k in pred_per_type:
                    v.score_set(pred_per_type[k], gold_per_type[k])
            # Score for all labels
            score.score_set(pred_spans, gold_spans)
        results = {
            attr + "_p": score.precision,
            attr + "_r": score.recall,
            attr + "_f": score.fscore,
            attr + "_per_type": {k: v.to_dict() for k, v in score_per_type.items()},
        }
        return results

    @staticmethod
    def score_cats(
        examples,
        attr,
        getter=getattr,
        labels=[],
        multi_label=True,
        positive_label=None,
        **cfg
    ):
        """Returns PRF and ROC AUC scores for a doc-level attribute with a
        dict with scores for each label like Doc.cats.

        examples (Iterable[Example]): Examples to score
        attr (str): The attribute to score.
        getter (callable): Defaults to getattr. If provided,
            getter(doc, attr) should return the values for the individual doc.
        labels (Iterable[str]): The set of possible labels. Defaults to [].
        multi_label (bool): Whether the attribute allows multiple labels.
            Defaults to True.
        positive_label (str): The positive label for a binary task with
            exclusive classes. Defaults to None.
        RETURNS (dict): A dictionary containing the scores:
            for binary exclusive with positive label: attr_p/r/f,
            for 3+ exclusive classes, macro-averaged fscore: attr_macro_f,
            for multilabel, macro-averaged AUC: attr_macro_auc,
            for all: attr_f_per_type, attr_auc_per_type
        """
        score = PRFScore()
        f_per_type = dict()
        auc_per_type = dict()
        for label in labels:
            f_per_type[label] = PRFScore()
            auc_per_type[label] = ROCAUCScore()
        for example in examples:
            gold_doc = example.reference
            pred_doc = example.predicted
            gold_values = getter(gold_doc, attr)
            pred_values = getter(pred_doc, attr)
            if (
                len(gold_values) > 0
                and set(f_per_type) == set(auc_per_type) == set(gold_values)
                and set(gold_values) == set(pred_values)
            ):
                gold_val = max(gold_values, key=gold_values.get)
                pred_val = max(pred_values, key=pred_values.get)
                if positive_label:
                    score.score_set(
                        set([positive_label]) & set([pred_val]),
                        set([positive_label]) & set([gold_val]),
                    )
                for label in set(gold_values):
                    auc_per_type[label].score_set(
                        pred_values[label], gold_values[label]
                    )
                    f_per_type[label].score_set(
                        set([label]) & set([pred_val]), set([label]) & set([gold_val])
                    )
            elif len(f_per_type) > 0:
                model_labels = set(f_per_type)
                eval_labels = set(gold_values)
                raise ValueError(
                    Errors.E162.format(
                        model_labels=model_labels, eval_labels=eval_labels
                    )
                )
            elif len(auc_per_type) > 0:
                model_labels = set(auc_per_type)
                eval_labels = set(gold_values)
                raise ValueError(
                    Errors.E162.format(
                        model_labels=model_labels, eval_labels=eval_labels
                    )
                )
        results = {
            attr + "_f_per_type": {k: v.to_dict() for k, v in f_per_type.items()},
            attr + "_auc_per_type": {k: v.score for k, v in auc_per_type.items()},
        }
        if len(labels) == 2 and not multi_label and positive_label:
            results[attr + "_p"] = score.precision
            results[attr + "_r"] = score.recall
            results[attr + "_f"] = score.fscore
        elif not multi_label:
            results[attr + "_macro_f"] = sum(
                [score.fscore for label, score in f_per_type.items()]
            ) / (len(f_per_type) + 1e-100)
        else:
            results[attr + "_macro_auc"] = max(
                sum([score.score for label, score in auc_per_type.items()])
                / (len(auc_per_type) + 1e-100),
                -1,
            )
        return results

    @staticmethod
    def score_deps(
        examples,
        attr,
        getter=getattr,
        head_attr="head",
        head_getter=getattr,
        ignore_labels=tuple(),
        **cfg
    ):
        """Returns the UAS, LAS, and LAS per type scores for dependency
        parses.

        examples (Iterable[Example]): Examples to score
        attr (str): The attribute containing the dependency label.
        getter (callable): Defaults to getattr. If provided,
            getter(token, attr) should return the value of the attribute for an
            individual token.
        head_attr (str): The attribute containing the head token. Defaults to
            'head'.
        head_getter (callable): Defaults to getattr. If provided,
            head_getter(token, attr) should return the value of the head for an
            individual token.
        ignore_labels (Tuple): Labels to ignore while scoring (e.g., punct).
        RETURNS (dict): A dictionary containing the scores:
            attr_uas, attr_las, and attr_las_per_type.
        """
        unlabelled = PRFScore()
        labelled = PRFScore()
        labelled_per_dep = dict()
        for example in examples:
            gold_doc = example.reference
            pred_doc = example.predicted
            align = example.alignment
            gold_deps = set()
            gold_deps_per_dep = {}
            for gold_i, token in enumerate(gold_doc):
                dep = getter(token, attr)
                head = head_getter(token, head_attr)
                if dep not in ignore_labels:
                    gold_deps.add((gold_i, head.i, dep))
                    if dep not in labelled_per_dep:
                        labelled_per_dep[dep] = PRFScore()
                    if dep not in gold_deps_per_dep:
                        gold_deps_per_dep[dep] = set()
                    gold_deps_per_dep[dep].add((gold_i, head.i, dep))
            pred_deps = set()
            pred_deps_per_dep = {}
            for token in pred_doc:
                if token.orth_.isspace():
                    continue
                if align.x2y.lengths[token.i] != 1:
                    gold_i = None
                else:
                    gold_i = align.x2y[token.i].dataXd[0, 0]
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
        return {
            attr + "_uas": unlabelled.fscore,
            attr + "_las": labelled.fscore,
            attr
            + "_las_per_type": {k: v.to_dict() for k, v in labelled_per_dep.items()},
        }


#############################################################################
#
# The following implementation of roc_auc_score() is adapted from
# scikit-learn, which is distributed under the following license:
#
# New BSD License
#
# Copyright (c) 2007–2019 The scikit-learn developers.
# All rights reserved.
#
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   a. Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   b. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#   c. Neither the name of the Scikit-learn Developers  nor the names of
#      its contributors may be used to endorse or promote products
#      derived from this software without specific prior written
#      permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.


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
        raise ValueError(Errors.E165)
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
            raise ValueError(Errors.E164.format(x))

    area = direction * np.trapz(y, x)
    if isinstance(area, np.memmap):
        # Reductions such as .sum used internally in np.trapz do not return a
        # scalar by default for numpy.memmap instances contrary to
        # regular numpy.ndarray instances.
        area = area.dtype.type(area)
    return area
