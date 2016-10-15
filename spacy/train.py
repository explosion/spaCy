from __future__ import absolute_import
from __future__ import unicode_literals

import random
from .gold import GoldParse
from .scorer import Scorer
from .gold import merge_sents


class Trainer(object):
    '''Manage training of an NLP pipeline.'''
    def __init__(self, nlp, gold_tuples):
        self.nlp = nlp
        self.gold_tuples = gold_tuples

    def epochs(self, nr_epoch, augment_data=None, gold_preproc=False):
        def _epoch():
            for raw_text, paragraph_tuples in self.gold_tuples:
                if gold_preproc:
                    raw_text = None
                else:
                    paragraph_tuples = merge_sents(paragraph_tuples)
                if augment_data is not None:
                    raw_text, paragraph_tuples = augment_data(raw_text, paragraph_tuples)
                docs = self.make_docs(raw_text, paragraph_tuples)
                golds = self.make_golds(docs, paragraph_tuples)
                for doc, gold in zip(docs, golds):
                    yield doc, gold

        for itn in range(nr_epoch):
            random.shuffle(self.gold_tuples)
            yield _epoch()
 
    def update(self, doc, gold):
        for process in self.nlp.pipeline:
            if hasattr(process, 'update'):
                process.update(doc, gold)
            process(doc)
        return doc

    def evaluate(self, dev_sents, gold_preproc=False):
        scorer = Scorer()
        for raw_text, paragraph_tuples in dev_sents:
            if gold_preproc:
                raw_text = None
            else:
                paragraph_tuples = merge_sents(paragraph_tuples)
            docs = self.make_docs(raw_text, paragraph_tuples)
            golds = self.make_golds(docs, paragraph_tuples)
            for doc, gold in zip(docs, golds):
                for process in self.nlp.pipeline[1:]:
                    process(doc)
                scorer.score(doc, gold)
        return scorer

    def make_docs(self, raw_text, paragraph_tuples):
        if raw_text is not None:
            return [self.nlp.tokenizer(raw_text)]
        else:
            return [self.nlp.tokenizer.tokens_from_list(sent_tuples[0][1])
                    for sent_tuples in paragraph_tuples]

    def make_golds(self, docs, paragraph_tuples):
        if len(docs) == 1:
            return [GoldParse(docs[0], sent_tuples[0])
                    for sent_tuples in paragraph_tuples]
        else:
            return [GoldParse(doc, sent_tuples[0])
                    for doc, sent_tuples in zip(docs, paragraph_tuples)]
