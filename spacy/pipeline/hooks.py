# coding: utf8
from __future__ import unicode_literals

from thinc.t2v import Pooling, max_pool, mean_pool
from thinc.neural._classes.difference import Siamese, CauchySimilarity

from .pipes import Pipe
from .._ml import link_vectors_to_models


class SentenceSegmenter(object):
    """A simple spaCy hook, to allow custom sentence boundary detection logic
    (that doesn't require the dependency parse). To change the sentence
    boundary detection strategy, pass a generator function `strategy` on
    initialization, or assign a new strategy to the .strategy attribute.
    Sentence detection strategies should be generators that take `Doc` objects
    and yield `Span` objects for each sentence.

    DOCS: https://spacy.io/api/sentencesegmenter
    """

    name = "sentencizer"

    def __init__(self, vocab, strategy=None):
        self.vocab = vocab
        if strategy is None or strategy == "on_punct":
            strategy = self.split_on_punct
        self.strategy = strategy

    def __call__(self, doc):
        doc.user_hooks["sents"] = self.strategy
        return doc

    @staticmethod
    def split_on_punct(doc):
        start = 0
        seen_period = False
        for i, word in enumerate(doc):
            if seen_period and not word.is_punct:
                yield doc[start : word.i]
                start = word.i
                seen_period = False
            elif word.text in [".", "!", "?"]:
                seen_period = True
        if start < len(doc):
            yield doc[start : len(doc)]


class SimilarityHook(Pipe):
    """
    Experimental: A pipeline component to install a hook for supervised
    similarity into `Doc` objects. Requires a `Tensorizer` to pre-process
    documents. The similarity model can be any object obeying the Thinc `Model`
    interface. By default, the model concatenates the elementwise mean and
    elementwise max of the two tensors, and compares them using the
    Cauchy-like similarity function from Chen (2013):

        >>> similarity = 1. / (1. + (W * (vec1-vec2)**2).sum())

    Where W is a vector of dimension weights, initialized to 1.
    """

    name = "similarity"

    def __init__(self, vocab, model=True, **cfg):
        self.vocab = vocab
        self.model = model
        self.cfg = dict(cfg)

    @classmethod
    def Model(cls, length):
        return Siamese(Pooling(max_pool, mean_pool), CauchySimilarity(length))

    def __call__(self, doc):
        """Install similarity hook"""
        doc.user_hooks["similarity"] = self.predict
        return doc

    def pipe(self, docs, **kwargs):
        for doc in docs:
            yield self(doc)

    def predict(self, doc1, doc2):
        self.require_model()
        return self.model.predict([(doc1, doc2)])

    def update(self, doc1_doc2, golds, sgd=None, drop=0.0):
        self.require_model()
        sims, bp_sims = self.model.begin_update(doc1_doc2, drop=drop)

    def begin_training(self, _=tuple(), pipeline=None, sgd=None, **kwargs):
        """Allocate model, using width from tensorizer in pipeline.

        gold_tuples (iterable): Gold-standard training data.
        pipeline (list): The pipeline the model is part of.
        """
        if self.model is True:
            self.model = self.Model(pipeline[0].model.nO)
            link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd
