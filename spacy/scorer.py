import numpy as np

from .errors import Errors


class PRFScore(object):
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


class ROCAUCScore(object):
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


class Scorer(object):
    """Compute evaluation scores."""

    def __init__(self, eval_punct=False, pipeline=None):
        """Initialize the Scorer.

        eval_punct (bool): Evaluate the dependency attachments to and from
            punctuation.
        RETURNS (Scorer): The newly created object.

        DOCS: https://spacy.io/api/scorer#init
        """
        self.tokens = PRFScore()
        self.sbd = PRFScore()
        self.unlabelled = PRFScore()
        self.labelled = PRFScore()
        self.labelled_per_dep = dict()
        self.tags = PRFScore()
        self.pos = PRFScore()
        self.morphs = PRFScore()
        self.morphs_per_feat = dict()
        self.sent_starts = PRFScore()
        self.ner = PRFScore()
        self.ner_per_ents = dict()
        self.eval_punct = eval_punct
        self.textcat = PRFScore()
        self.textcat_f_per_cat = dict()
        self.textcat_auc_per_cat = dict()
        self.textcat_positive_label = None
        self.textcat_multilabel = False

        if pipeline:
            for name, component in pipeline:
                if name == "textcat":
                    self.textcat_multilabel = component.model.attrs["multi_label"]
                    self.textcat_positive_label = component.cfg.get(
                        "positive_label", None
                    )
                    for label in component.cfg.get("labels", []):
                        self.textcat_auc_per_cat[label] = ROCAUCScore()
                        self.textcat_f_per_cat[label] = PRFScore()

    @property
    def tags_acc(self):
        """RETURNS (float): Part-of-speech tag accuracy (fine grained tags,
            i.e. `Token.tag`).
        """
        return self.tags.fscore * 100

    @property
    def pos_acc(self):
        """RETURNS (float): Part-of-speech tag accuracy (coarse grained pos,
            i.e. `Token.pos`).
        """
        return self.pos.fscore * 100

    @property
    def morphs_acc(self):
        """RETURNS (float): Morph tag accuracy (morphological features,
           i.e. `Token.morph`).
       """
        return self.morphs.fscore * 100

    @property
    def morphs_per_type(self):
        """RETURNS (dict): Scores per dependency label.
       """
        return {
            k: {"p": v.precision * 100, "r": v.recall * 100, "f": v.fscore * 100}
            for k, v in self.morphs_per_feat.items()
        }

    @property
    def sent_p(self):
        """RETURNS (float): F-score for identification of sentence starts.
            i.e. `Token.is_sent_start`).
        """
        return self.sent_starts.precision * 100

    @property
    def sent_r(self):
        """RETURNS (float): F-score for identification of sentence starts.
            i.e. `Token.is_sent_start`).
        """
        return self.sent_starts.recall * 100

    @property
    def sent_f(self):
        """RETURNS (float): F-score for identification of sentence starts.
            i.e. `Token.is_sent_start`).
        """
        return self.sent_starts.fscore * 100

    @property
    def token_acc(self):
        """RETURNS (float): Tokenization accuracy."""
        return self.tokens.precision * 100

    @property
    def uas(self):
        """RETURNS (float): Unlabelled dependency score."""
        return self.unlabelled.fscore * 100

    @property
    def las(self):
        """RETURNS (float): Labelled dependency score."""
        return self.labelled.fscore * 100

    @property
    def las_per_type(self):
        """RETURNS (dict): Scores per dependency label.
        """
        return {
            k: {"p": v.precision * 100, "r": v.recall * 100, "f": v.fscore * 100}
            for k, v in self.labelled_per_dep.items()
        }

    @property
    def ents_p(self):
        """RETURNS (float): Named entity accuracy (precision)."""
        return self.ner.precision * 100

    @property
    def ents_r(self):
        """RETURNS (float): Named entity accuracy (recall)."""
        return self.ner.recall * 100

    @property
    def ents_f(self):
        """RETURNS (float): Named entity accuracy (F-score)."""
        return self.ner.fscore * 100

    @property
    def ents_per_type(self):
        """RETURNS (dict): Scores per entity label.
        """
        return {
            k: {"p": v.precision * 100, "r": v.recall * 100, "f": v.fscore * 100}
            for k, v in self.ner_per_ents.items()
        }

    @property
    def textcat_f(self):
        """RETURNS (float): f-score on positive label for binary classification,
        macro-averaged f-score for multilabel classification
        """
        if not self.textcat_multilabel:
            if self.textcat_positive_label:
                # binary classification
                return self.textcat.fscore * 100
        # multi-class and/or multi-label
        return (
            sum([score.fscore for label, score in self.textcat_f_per_cat.items()])
            / (len(self.textcat_f_per_cat) + 1e-100)
            * 100
        )

    @property
    def textcat_auc(self):
        """RETURNS (float): macro-averaged AUC ROC score for multilabel classification (-1 if undefined)
        """
        return max(
            sum([score.score for label, score in self.textcat_auc_per_cat.items()])
            / (len(self.textcat_auc_per_cat) + 1e-100),
            -1,
        )

    @property
    def textcats_auc_per_cat(self):
        """RETURNS (dict): AUC ROC Scores per textcat label.
        """
        return {
            k: {"roc_auc_score": max(v.score, -1)}
            for k, v in self.textcat_auc_per_cat.items()
        }

    @property
    def textcats_f_per_cat(self):
        """RETURNS (dict): F-scores per textcat label.
        """
        return {
            k: {"p": v.precision * 100, "r": v.recall * 100, "f": v.fscore * 100}
            for k, v in self.textcat_f_per_cat.items()
        }

    @property
    def scores(self):
        """RETURNS (dict): All scores mapped by key.
        """
        return {
            "uas": self.uas,
            "las": self.las,
            "las_per_type": self.las_per_type,
            "ents_p": self.ents_p,
            "ents_r": self.ents_r,
            "ents_f": self.ents_f,
            "ents_per_type": self.ents_per_type,
            "tags_acc": self.tags_acc,
            "pos_acc": self.pos_acc,
            "morphs_acc": self.morphs_acc,
            "morphs_per_type": self.morphs_per_type,
            "sent_p": self.sent_p,
            "sent_r": self.sent_r,
            "sent_f": self.sent_f,
            "token_acc": self.token_acc,
            "textcat_f": self.textcat_f,
            "textcat_auc": self.textcat_auc,
            "textcats_f_per_cat": self.textcats_f_per_cat,
            "textcats_auc_per_cat": self.textcats_auc_per_cat,
        }

    def score(self, example, verbose=False, punct_labels=("p", "punct")):
        """Update the evaluation scores from a single Example.

        example (Example): The predicted annotations + correct annotations.
        verbose (bool): Print debugging information.
        punct_labels (tuple): Dependency labels for punctuation. Used to
            evaluate dependency attachments to punctuation if `eval_punct` is
            `True`.

        DOCS: https://spacy.io/api/scorer#score
        """
        doc = example.predicted
        gold_doc = example.reference
        align = example.alignment
        gold_deps = set()
        gold_deps_per_dep = {}
        gold_tags = set()
        gold_pos = set()
        gold_morphs = set()
        gold_morphs_per_feat = {}
        gold_sent_starts = set()
        for gold_i, token in enumerate(gold_doc):
            gold_tags.add((gold_i, token.tag_))
            gold_pos.add((gold_i, token.pos_))
            gold_morphs.add((gold_i, token.morph_))
            if token.morph_:
                for feat in token.morph_.split("|"):
                    field, values = feat.split("=")
                    if field not in self.morphs_per_feat:
                        self.morphs_per_feat[field] = PRFScore()
                    if field not in gold_morphs_per_feat:
                        gold_morphs_per_feat[field] = set()
                    gold_morphs_per_feat[field].add((gold_i, feat))
            if token.sent_start:
                gold_sent_starts.add(gold_i)
            dep = token.dep_.lower()
            if dep not in punct_labels:
                gold_deps.add((gold_i, token.head.i, dep))
                if dep not in self.labelled_per_dep:
                    self.labelled_per_dep[dep] = PRFScore()
                if dep not in gold_deps_per_dep:
                    gold_deps_per_dep[dep] = set()
                gold_deps_per_dep[dep].add((gold_i, token.head.i, dep))
        cand_deps = set()
        cand_deps_per_dep = {}
        cand_tags = set()
        cand_pos = set()
        cand_morphs = set()
        cand_morphs_per_feat = {}
        cand_sent_starts = set()
        for token in doc:
            if token.orth_.isspace():
                continue
            if align.x2y.lengths[token.i] != 1:
                self.tokens.fp += 1
                gold_i = None
            else:
                gold_i = align.x2y[token.i].dataXd[0, 0]
                self.tokens.tp += 1
                cand_tags.add((gold_i, token.tag_))
                cand_pos.add((gold_i, token.pos_))
                cand_morphs.add((gold_i, token.morph_))
                if token.morph_:
                    for feat in token.morph_.split("|"):
                        field, values = feat.split("=")
                        if field not in self.morphs_per_feat:
                            self.morphs_per_feat[field] = PRFScore()
                        if field not in cand_morphs_per_feat:
                            cand_morphs_per_feat[field] = set()
                        cand_morphs_per_feat[field].add((gold_i, feat))
                if token.is_sent_start:
                    cand_sent_starts.add(gold_i)
            if token.dep_.lower() not in punct_labels and token.orth_.strip():
                if align.x2y.lengths[token.head.i] == 1:
                    gold_head = align.x2y[token.head.i].dataXd[0, 0]
                else:
                    gold_head = None
                # None is indistinct, so we can't just add it to the set
                # Multiple (None, None) deps are possible
                if gold_i is None or gold_head is None:
                    self.unlabelled.fp += 1
                    self.labelled.fp += 1
                else:
                    cand_deps.add((gold_i, gold_head, token.dep_.lower()))
                    if token.dep_.lower() not in self.labelled_per_dep:
                        self.labelled_per_dep[token.dep_.lower()] = PRFScore()
                    if token.dep_.lower() not in cand_deps_per_dep:
                        cand_deps_per_dep[token.dep_.lower()] = set()
                    cand_deps_per_dep[token.dep_.lower()].add(
                        (gold_i, gold_head, token.dep_.lower())
                    )
        # Find all NER labels in gold and doc
        ent_labels = set(
            [k.label_ for k in gold_doc.ents] + [k.label_ for k in doc.ents]
        )
        # Set up all labels for per type scoring and prepare gold per type
        gold_per_ents = {ent_label: set() for ent_label in ent_labels}
        for ent_label in ent_labels:
            if ent_label not in self.ner_per_ents:
                self.ner_per_ents[ent_label] = PRFScore()
        # Find all candidate labels, for all and per type
        gold_ents = set()
        cand_ents = set()
        # If we have missing values in the gold, we can't easily tell whether
        # our NER predictions are true.
        # It seems bad but it's what we've always done.
        if all(token.ent_iob != 0 for token in gold_doc):
            for ent in gold_doc.ents:
                gold_ent = (ent.label_, ent.start, ent.end - 1)
                gold_ents.add(gold_ent)
                gold_per_ents[ent.label_].add((ent.label_, ent.start, ent.end - 1))
            cand_per_ents = {ent_label: set() for ent_label in ent_labels}
            for ent in example.get_aligned_spans_x2y(doc.ents):
                cand_ents.add((ent.label_, ent.start, ent.end - 1))
                cand_per_ents[ent.label_].add((ent.label_, ent.start, ent.end - 1))
            # Scores per ent
            for k, v in self.ner_per_ents.items():
                if k in cand_per_ents:
                    v.score_set(cand_per_ents[k], gold_per_ents[k])
            # Score for all ents
            self.ner.score_set(cand_ents, gold_ents)
        self.tags.score_set(cand_tags, gold_tags)
        self.pos.score_set(cand_pos, gold_pos)
        self.morphs.score_set(cand_morphs, gold_morphs)
        for field in self.morphs_per_feat:
            self.morphs_per_feat[field].score_set(
                cand_morphs_per_feat.get(field, set()),
                gold_morphs_per_feat.get(field, set()),
            )
        self.sent_starts.score_set(cand_sent_starts, gold_sent_starts)
        self.labelled.score_set(cand_deps, gold_deps)
        for dep in self.labelled_per_dep:
            self.labelled_per_dep[dep].score_set(
                cand_deps_per_dep.get(dep, set()), gold_deps_per_dep.get(dep, set())
            )
        self.unlabelled.score_set(
            set(item[:2] for item in cand_deps), set(item[:2] for item in gold_deps)
        )
        if (
            len(gold_doc.cats) > 0
            and set(self.textcat_f_per_cat)
            == set(self.textcat_auc_per_cat)
            == set(gold_doc.cats)
            and set(gold_doc.cats) == set(doc.cats)
        ):
            goldcat = max(gold_doc.cats, key=gold_doc.cats.get)
            candcat = max(doc.cats, key=doc.cats.get)
            if self.textcat_positive_label:
                self.textcat.score_set(
                    set([self.textcat_positive_label]) & set([candcat]),
                    set([self.textcat_positive_label]) & set([goldcat]),
                )
            for label in set(gold_doc.cats):
                self.textcat_auc_per_cat[label].score_set(
                    doc.cats[label], gold_doc.cats[label]
                )
                self.textcat_f_per_cat[label].score_set(
                    set([label]) & set([candcat]), set([label]) & set([goldcat])
                )
        elif len(self.textcat_f_per_cat) > 0:
            model_labels = set(self.textcat_f_per_cat)
            eval_labels = set(gold_doc.cats)
            raise ValueError(
                Errors.E162.format(model_labels=model_labels, eval_labels=eval_labels)
            )
        elif len(self.textcat_auc_per_cat) > 0:
            model_labels = set(self.textcat_auc_per_cat)
            eval_labels = set(gold_doc.cats)
            raise ValueError(
                Errors.E162.format(model_labels=model_labels, eval_labels=eval_labels)
            )
        if verbose:
            gold_words = gold_doc.words
            for w_id, h_id, dep in cand_deps - gold_deps:
                print("F", gold_words[w_id], dep, gold_words[h_id])
            for w_id, h_id, dep in gold_deps - cand_deps:
                print("M", gold_words[w_id], dep, gold_words[h_id])


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
