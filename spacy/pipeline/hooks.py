from thinc.api import concatenate, reduce_max, reduce_mean, siamese, CauchySimilarity

from .pipes import Pipe
from ..language import component
from ..util import link_vectors_to_models


@component("sentencizer_hook", assigns=["doc.user_hooks"])
class SentenceSegmenter(object):
    """A simple spaCy hook, to allow custom sentence boundary detection logic
    (that doesn't require the dependency parse). To change the sentence
    boundary detection strategy, pass a generator function `strategy` on
    initialization, or assign a new strategy to the .strategy attribute.
    Sentence detection strategies should be generators that take `Doc` objects
    and yield `Span` objects for each sentence.
    """

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
        for i, token in enumerate(doc):
            if seen_period and not token.is_punct:
                yield doc[start : token.i]
                start = token.i
                seen_period = False
            elif token.text in [".", "!", "?"]:
                seen_period = True
        if start < len(doc):
            yield doc[start : len(doc)]


@component("similarity", assigns=["doc.user_hooks"])
class SimilarityHook(Pipe):
    """
    Experimental: A pipeline component to install a hook for supervised
    similarity into `Doc` objects.
    The similarity model can be any object obeying the Thinc `Model`
    interface. By default, the model concatenates the elementwise mean and
    elementwise max of the two tensors, and compares them using the
    Cauchy-like similarity function from Chen (2013):

        >>> similarity = 1. / (1. + (W * (vec1-vec2)**2).sum())

    Where W is a vector of dimension weights, initialized to 1.
    """

    def __init__(self, vocab, model=True, **cfg):
        self.vocab = vocab
        self.model = model
        self.cfg = dict(cfg)

    @classmethod
    def Model(cls, length):
        return siamese(
            concatenate(reduce_max(), reduce_mean()), CauchySimilarity(length * 2)
        )

    def __call__(self, doc):
        """Install similarity hook"""
        doc.user_hooks["similarity"] = self.predict
        return doc

    def pipe(self, docs, **kwargs):
        for doc in docs:
            yield self(doc)

    def predict(self, doc1, doc2):
        return self.model.predict([(doc1, doc2)])

    def update(self, doc1_doc2, golds, sgd=None, drop=0.0):
        sims, bp_sims = self.model.begin_update(doc1_doc2)

    def begin_training(self, _=tuple(), pipeline=None, sgd=None, **kwargs):
        """Allocate model, using nO from the first model in the pipeline.

        gold_tuples (iterable): Gold-standard training data.
        pipeline (list): The pipeline the model is part of.
        """
        if self.model is True:
            self.model = self.Model(pipeline[0].model.get_dim("nO"))
            link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd
