# coding: utf8
from __future__ import division, print_function, unicode_literals

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


class Scorer(object):
    """Compute evaluation scores."""

    def __init__(self, eval_punct=False):
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
    def scores(self):
        """RETURNS (dict): All scores with keys `uas`, `las`, `ents_p`,
            `ents_r`, `ents_f`, `tags_acc` and `token_acc`.
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
            cand_ents = set()
            current_ent = {k.label_: set() for k in doc.ents}
            current_gold = {k.label_: set() for k in doc.ents}
            for ent in doc.ents:
                if ent.label_ not in self.ner_per_ents:
                    self.ner_per_ents[ent.label_] = PRFScore()
                first = gold.cand_to_gold[ent.start]
                last = gold.cand_to_gold[ent.end - 1]
                if first is None or last is None:
                    self.ner.fp += 1
                    self.ner_per_ents[ent.label_].fp += 1
                else:
                    cand_ents.add((ent.label_, first, last))
                    current_ent[ent.label_].add(
                        tuple(x for x in cand_ents if x[0] == ent.label_)
                    )
                    current_gold[ent.label_].add(
                        tuple(x for x in gold_ents if x[0] == ent.label_)
                    )
            # Scores per ent
            [
                v.score_set(current_ent[k], current_gold[k])
                for k, v in self.ner_per_ents.items()
                if k in current_ent
            ]
            # Score for all ents
            self.ner.score_set(cand_ents, gold_ents)
        self.tags.score_set(cand_tags, gold_tags)
        self.labelled.score_set(cand_deps, gold_deps)
        self.unlabelled.score_set(
            set(item[:2] for item in cand_deps), set(item[:2] for item in gold_deps)
        )
        if verbose:
            gold_words = [item[1] for item in gold.orig_annot]
            for w_id, h_id, dep in cand_deps - gold_deps:
                print("F", gold_words[w_id], dep, gold_words[h_id])
            for w_id, h_id, dep in gold_deps - cand_deps:
                print("M", gold_words[w_id], dep, gold_words[h_id])
