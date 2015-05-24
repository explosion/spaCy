from __future__ import division


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
        return self.tokens.fscore * 100

    @property
    def uas(self):
        return self.unlabelled.fscore * 100

    @property
    def las(self):
        return self.labelled.fscore * 100

    @property
    def ents_p(self):
        return self.ner.precision

    @property
    def ents_r(self):
        return self.ner.recall

    @property
    def ents_f(self):
        return self.ner.fscore

    def score(self, tokens, gold, verbose=False):
        assert len(tokens) == len(gold)

        gold_deps = set()
        gold_tags = set()
        gold_tags = set()
        for id_, word, tag, head, dep, ner in gold.orig_annot:
            if dep.lower() not in ('p', 'punct'):
                gold_deps.add((id_, head, dep))
                gold_tags.add((id_, tag))
        cand_deps = set()
        cand_tags = set()
        for token in tokens:
            if token.dep_ not in ('p', 'punct') and token.orth_.strip():
                gold_i = gold.cand_to_gold[token.i]
                gold_head = gold.cand_to_gold[token.head.i]
                # None is indistinct, so we can't just add it to the set
                # Multiple (None, None) deps are possible
                if gold_i is None or gold_head is None:
                    self.unlabelled.fp += 1
                    self.labelled.fp += 1
                else:
                    cand_deps.add((gold_i, gold_head, token.dep_))
                if gold_i is None:
                    self.tags.fp += 1
                else:
                    cand_tags.add((gold_i, token.tag_))

        self.tags.score_set(cand_tags, cand_deps)
        self.labelled.score_set(cand_deps, gold_deps)
        self.unlabelled.score_set(
            set(item[:2] for item in cand_deps),
            set(item[:2] for item in gold_deps),
        )
