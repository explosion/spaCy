# coding: utf8
from __future__ import division, print_function, unicode_literals

from sklearn.metrics import roc_auc_score
from math import inf
from .gold import tags_to_entities, GoldParse


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
            self.saved_score = roc_auc_score(self.golds, self.cands)
        # catch ValueError: Only one class present in y_true.
        # ROC AUC score is not defined in that case.
        except:
            self.saved_score = -inf
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
        self.tags = PRFScore()
        self.ner = PRFScore()
        self.ner_per_ents = dict()
        self.eval_punct = eval_punct
        self.textcat = None
        self.textcat_per_cat = dict()
        self.textcat_positive_label = None
        self.textcat_multilabel = False

        if pipeline:
            for name, model in pipeline:
                if name == "textcat":
                    self.textcat_positive_label = model.cfg.get("positive_label", None)
                    if self.textcat_positive_label:
                        self.textcat = PRFScore()
                    if not model.cfg.get("exclusive_classes", False):
                        self.textcat_multilabel = True
                        for label in model.cfg.get("labels", []):
                            self.textcat_per_cat[label] = ROCAUCScore()
                    else:
                        for label in model.cfg.get("labels", []):
                            self.textcat_per_cat[label] = PRFScore()

    @property
    def tags_acc(self):
        """RETURNS (float): Part-of-speech tag accuracy (fine grained tags,
            i.e. `Token.tag`).
        """
        return self.tags.fscore * 100

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
        """RETURNS (float): Labelled depdendency score."""
        return self.labelled.fscore * 100

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
    def textcat_score(self):
        """RETURNS (float): f-score on positive label for binary exclusive,
        macro-averaged f-score for 3+ exclusive,
        macro-averaged AUC ROC score for multilabel (-1 if undefined)
        """
        if not self.textcat_multilabel:
            # binary multiclass
            if self.textcat_positive_label:
                return self.textcat.fscore * 100
            # other multiclass
            return sum([score.fscore for label, score in self.textcat_per_cat.items()]) / (len(self.textcat_per_cat) + 1e-100) * 100
        # multilabel
        return max(sum([score.score for label, score in self.textcat_per_cat.items()]) / (len(self.textcat_per_cat) + 1e-100), -1)

    @property
    def textcats_per_cat(self):
        """RETURNS (dict): Scores per textcat label.
        """
        if not self.textcat_multilabel:
            return {
                k: {"p": v.precision * 100, "r": v.recall * 100, "f": v.fscore * 100}
                for k, v in self.textcat_per_cat.items()
            }
        return {
            k: {"roc_auc_score": max(v.score, -1)}
            for k, v in self.textcat_per_cat.items()
        }

    @property
    def scores(self):
        """RETURNS (dict): All scores with keys `uas`, `las`, `ents_p`,
            `ents_r`, `ents_f`, `tags_acc`, `token_acc`, and `textcat_score`.
        """
        return {
            "uas": self.uas,
            "las": self.las,
            "ents_p": self.ents_p,
            "ents_r": self.ents_r,
            "ents_f": self.ents_f,
            "ents_per_type": self.ents_per_type,
            "tags_acc": self.tags_acc,
            "token_acc": self.token_acc,
            "textcat_score": self.textcat_score,
            "textcats_per_cat": self.textcats_per_cat,
        }

    def score(self, doc, gold, verbose=False, punct_labels=("p", "punct")):
        """Update the evaluation scores from a single Doc / GoldParse pair.

        doc (Doc): The predicted annotations.
        gold (GoldParse): The correct annotations.
        verbose (bool): Print debugging information.
        punct_labels (tuple): Dependency labels for punctuation. Used to
            evaluate dependency attachments to punctuation if `eval_punct` is
            `True`.

        DOCS: https://spacy.io/api/scorer#score
        """
        if len(doc) != len(gold):
            gold = GoldParse.from_annot_tuples(doc, zip(*gold.orig_annot))
        gold_deps = set()
        gold_tags = set()
        gold_ents = set(tags_to_entities([annot[-1] for annot in gold.orig_annot]))
        for id_, word, tag, head, dep, ner in gold.orig_annot:
            gold_tags.add((id_, tag))
            if dep not in (None, "") and dep.lower() not in punct_labels:
                gold_deps.add((id_, head, dep.lower()))
        cand_deps = set()
        cand_tags = set()
        for token in doc:
            if token.orth_.isspace():
                continue
            gold_i = gold.cand_to_gold[token.i]
            if gold_i is None:
                self.tokens.fp += 1
            else:
                self.tokens.tp += 1
                cand_tags.add((gold_i, token.tag_))
            if token.dep_.lower() not in punct_labels and token.orth_.strip():
                gold_head = gold.cand_to_gold[token.head.i]
                # None is indistinct, so we can't just add it to the set
                # Multiple (None, None) deps are possible
                if gold_i is None or gold_head is None:
                    self.unlabelled.fp += 1
                    self.labelled.fp += 1
                else:
                    cand_deps.add((gold_i, gold_head, token.dep_.lower()))
        if "-" not in [token[-1] for token in gold.orig_annot]:
            # Find all NER labels in gold and doc
            ent_labels = set([x[0] for x in gold_ents] + [k.label_ for k in doc.ents])
            # Set up all labels for per type scoring and prepare gold per type
            gold_per_ents = {ent_label: set() for ent_label in ent_labels}
            for ent_label in ent_labels:
                if ent_label not in self.ner_per_ents:
                    self.ner_per_ents[ent_label] = PRFScore()
                gold_per_ents[ent_label].update(
                    [x for x in gold_ents if x[0] == ent_label]
                )
            # Find all candidate labels, for all and per type
            cand_ents = set()
            cand_per_ents = {ent_label: set() for ent_label in ent_labels}
            for ent in doc.ents:
                first = gold.cand_to_gold[ent.start]
                last = gold.cand_to_gold[ent.end - 1]
                if first is None or last is None:
                    self.ner.fp += 1
                    self.ner_per_ents[ent.label_].fp += 1
                else:
                    cand_ents.add((ent.label_, first, last))
                    cand_per_ents[ent.label_].add((ent.label_, first, last))
            # Scores per ent
            for k, v in self.ner_per_ents.items():
                if k in cand_per_ents:
                    v.score_set(cand_per_ents[k], gold_per_ents[k])
            # Score for all ents
            self.ner.score_set(cand_ents, gold_ents)
        self.tags.score_set(cand_tags, gold_tags)
        self.labelled.score_set(cand_deps, gold_deps)
        self.unlabelled.score_set(
            set(item[:2] for item in cand_deps), set(item[:2] for item in gold_deps)
        )
        if len(gold.cats) > 0 and set(self.textcat_per_cat) == set(gold.cats) and set(gold.cats) == set(doc.cats):
            goldcat = max(gold.cats, key=gold.cats.get)
            candcat = max(doc.cats, key=doc.cats.get)
            if self.textcat_positive_label:
                self.textcat.score_set(set([self.textcat_positive_label]) & set([candcat]), set([self.textcat_positive_label]) & set([goldcat]))
            for label in self.textcat_per_cat:
                if self.textcat_multilabel:
                    self.textcat_per_cat[label].score_set(doc.cats[label], gold.cats[label])
                else:
                    self.textcat_per_cat[label].score_set(set([label]) & set([candcat]), set([label]) & set([goldcat]))
        elif len(self.textcat_per_cat) > 0 or len(gold.cats) == 0:
            raise ValueError("Cannot evaluate textcat model on data with different labels.\nLabels in model: {}\nLabels in evaluation data: {}".format(set(self.textcat_per_cat), set(gold.cats)))
        if verbose:
            gold_words = [item[1] for item in gold.orig_annot]
            for w_id, h_id, dep in cand_deps - gold_deps:
                print("F", gold_words[w_id], dep, gold_words[h_id])
            for w_id, h_id, dep in gold_deps - cand_deps:
                print("M", gold_words[w_id], dep, gold_words[h_id])
