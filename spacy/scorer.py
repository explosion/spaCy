from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .gold import tags_to_entities


class PRFScore(object):
    """A precision / recall / F score"""
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
    def __init__(self, eval_punct=False):
        self.tokens = PRFScore()
        self.sbd = PRFScore()
        self.unlabelled = PRFScore()
        self.labelled = PRFScore()
        self.tags = PRFScore()
        self.ner = PRFScore()
        self.eval_punct = eval_punct

    @property
    def tags_acc(self):
        return self.tags.fscore * 100

    @property
    def token_acc(self):
        return self.tokens.precision * 100

    @property
    def uas(self):
        return self.unlabelled.fscore * 100

    @property
    def las(self):
        return self.labelled.fscore * 100

    @property
    def ents_p(self):
        return self.ner.precision * 100

    @property
    def ents_r(self):
        return self.ner.recall * 100

    @property
    def ents_f(self):
        return self.ner.fscore * 100

    @property
    def scores(self):
        return {
            'uas': self.uas, 'las': self.las,
            'ents_p': self.ents_p, 'ents_r': self.ents_r, 'ents_f': self.ents_f,
            'tags_acc': self.tags_acc,
            'token_acc': self.token_acc
        }

    def score(self, tokens, gold, verbose=False, punct_labels=('p', 'punct')):
        assert len(tokens) == len(gold)

        gold_deps = set()
        gold_tags = set()
        gold_ents = set(tags_to_entities([annot[-1] for annot in gold.orig_annot]))
        for id_, word, tag, head, dep, ner in gold.orig_annot:
            gold_tags.add((id_, tag))
            if dep is not None and dep.lower() not in punct_labels:
                gold_deps.add((id_, head, dep.lower()))
        cand_deps = set()
        cand_tags = set()
        for token in tokens:
            if token.orth_.isspace():
                continue
            gold_i = gold.cand_to_gold[token.i]
            if gold_i is None:
                if token.dep_.lower() not in punct_labels:
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
        if '-' not in [token[-1] for token in gold.orig_annot]:
            cand_ents = set()
            for ent in tokens.ents:
                first = gold.cand_to_gold[ent.start]
                last = gold.cand_to_gold[ent.end-1]
                if first is None or last is None:
                    self.ner.fp += 1
                else:
                    cand_ents.add((ent.label_, first, last))
            self.ner.score_set(cand_ents, gold_ents)
        self.tags.score_set(cand_tags, gold_tags)
        self.labelled.score_set(cand_deps, gold_deps)
        self.unlabelled.score_set(
            set(item[:2] for item in cand_deps),
            set(item[:2] for item in gold_deps),
        )
        if verbose:
            gold_words = [item[1] for item in gold.orig_annot]
            for w_id, h_id, dep in (cand_deps - gold_deps):
                print('F', gold_words[w_id], dep, gold_words[h_id])
            for w_id, h_id, dep in (gold_deps - cand_deps):
                print('M', gold_words[w_id], dep, gold_words[h_id])
