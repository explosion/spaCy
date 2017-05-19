# coding: utf8
from __future__ import absolute_import, unicode_literals

import random
import tqdm
from cytoolz import partition_all

from thinc.neural.optimizers import Adam
from thinc.neural.ops import NumpyOps, CupyOps
from thinc.neural.train import Trainer as ThincTrainer

from .syntax.nonproj import PseudoProjectivity
from .gold import GoldParse, merge_sents
from .scorer import Scorer
from .tokens.doc import Doc
from . import util


class Trainer(object):
    """
    Manage training of an NLP pipeline.
    """
    def __init__(self, nlp, gold_tuples, **cfg):
        self.nlp = nlp
        self.nr_epoch = 0
        self.optimizer = Adam(NumpyOps(), 0.001)
        self.gold_tuples = gold_tuples
        self.cfg = cfg
        self.batch_size = float(util.env_opt('min_batch_size', 4))
        self.max_batch_size = util.env_opt('max_batch_size', 64)
        self.accel_batch_size = util.env_opt('batch_accel', 1.001)

    def epochs(self, nr_epoch, augment_data=None, gold_preproc=False):
        cached_golds = {}
        cached_docs = {}
        def _epoch(indices):
            all_docs = []
            all_golds = []
            for i in indices:
                raw_text, paragraph_tuples = self.gold_tuples[i]
                if gold_preproc:
                    raw_text = None
                else:
                    paragraph_tuples = merge_sents(paragraph_tuples)
                if augment_data is None:
                    docs = self.make_docs(raw_text, paragraph_tuples)
                    golds = self.make_golds(docs, paragraph_tuples)
                    #if i not in cached_docs:
                    #    cached_docs[i] = self.make_docs(raw_text, paragraph_tuples)
                    #docs = cached_docs[i]
                    #if i not in cached_golds:
                    #    cached_golds[i] = self.make_golds(docs, paragraph_tuples)
                    #golds = cached_golds[i]
                else:
                    raw_text, paragraph_tuples = augment_data(raw_text, paragraph_tuples)
                    docs = self.make_docs(raw_text, paragraph_tuples)
                    golds = self.make_golds(docs, paragraph_tuples)
                all_docs.extend(docs)
                all_golds.extend(golds)

            thinc_trainer = ThincTrainer(self.nlp.pipeline[0].model)
            thinc_trainer.batch_size = int(self.batch_size)
            thinc_trainer.nb_epoch = 1
            for X, y in thinc_trainer.iterate(all_docs, all_golds):
                yield X, y
                thinc_trainer.batch_size = min(int(self.batch_size), self.max_batch_size)
                self.batch_size *= self.accel_batch_size

        indices = list(range(len(self.gold_tuples)))
        for itn in range(nr_epoch):
            random.shuffle(indices)
            yield _epoch(indices)
            self.nr_epoch += 1

    def evaluate(self, dev_sents, gold_preproc=False):
        all_docs = []
        all_golds = []
        for raw_text, paragraph_tuples in dev_sents:
            if gold_preproc:
                raw_text = None
            else:
                paragraph_tuples = merge_sents(paragraph_tuples)
            docs = self.make_docs(raw_text, paragraph_tuples)
            golds = self.make_golds(docs, paragraph_tuples)
            all_docs.extend(docs)
            all_golds.extend(golds)
        scorer = Scorer()
        for doc, gold in zip(self.nlp.pipe(all_docs, batch_size=16), all_golds):
            scorer.score(doc, gold)
        return scorer

    def make_docs(self, raw_text, paragraph_tuples):
        if raw_text is not None:
            return [self.nlp.make_doc(raw_text)]
        else:
            return [
                Doc(self.nlp.vocab, words=sent_tuples[0][1])
                for sent_tuples in paragraph_tuples]

    def make_golds(self, docs, paragraph_tuples):
        if len(docs) == 1:
            return [GoldParse.from_annot_tuples(docs[0], sent_tuples[0])
                    for sent_tuples in paragraph_tuples]
        else:
            return [GoldParse.from_annot_tuples(doc, sent_tuples[0])
                    for doc, sent_tuples in zip(docs, paragraph_tuples)]
