from __future__ import division


class Scorer(object):
    def __init__(self, eval_punct=False):
        self.heads_corr = 0
        self.labels_corr = 0
        self.tags_corr = 0
        self.ents_tp = 0
        self.ents_fp = 0
        self.ents_fn = 0
        self.total = 1e-100
        self.mistokened = 0
        self.n_tokens = 0
        self.eval_punct = eval_punct

    @property
    def tags_acc(self):
        return ((self.tags_corr - self.mistokened) / (self.n_tokens - self.mistokened)) * 100

    @property
    def uas(self):
        return (self.heads_corr / self.total) * 100

    @property
    def las(self):
        return (self.labels_corr / self.total) * 100

    @property
    def ents_p(self):
        return (self.ents_tp / (self.ents_tp + self.ents_fp + 1e-100)) * 100

    @property
    def ents_r(self):
        return (self.ents_tp / (self.ents_tp + self.ents_fn + 1e-100)) * 100
    
    @property
    def ents_f(self):
        return (2 * self.ents_p * self.ents_r) / (self.ents_p + self.ents_r + 1e-100)

    def score(self, tokens, gold, verbose=False):
        assert len(tokens) == len(gold)

        for i, token in enumerate(tokens):
            if gold.orths.get(token.idx) != token.orth_:
                self.mistokened += 1
            if not self.skip_token(i, token, gold):
                self.total += 1
                if verbose:
                    print token.orth_, token.dep_, token.head.orth_
                if token.head.i == gold.heads[i]:
                    self.heads_corr += 1
                    self.labels_corr += token.dep_ == gold.labels[i]
            self.tags_corr += token.tag_ == gold.tags[i]
            self.n_tokens += 1
        gold_ents = set((start, end, label) for (start, end, label) in gold.ents)
        guess_ents = set((e.start, e.end, e.label_) for e in tokens.ents)
        if verbose and gold_ents:
            for start, end, label in guess_ents:
                mark = 'T' if (start, end, label) in gold_ents else 'F'
                ent_str = ' '.join(tokens[i].orth_ for i in range(start, end))
                print mark, label, ent_str
            for start, end, label in gold_ents:
                if (start, end, label) not in guess_ents:
                    ent_str = ' '.join(tokens[i].orth_ for i in range(start, end))
                    print 'M', label, ent_str
            print
        if gold_ents:
            self.ents_tp += len(gold_ents.intersection(guess_ents))
            self.ents_fn += len(gold_ents - guess_ents)
            self.ents_fp += len(guess_ents - gold_ents)

    def skip_token(self, i, token, gold):
        return gold.labels[i] in ('P', 'punct')
