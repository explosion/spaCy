import numpy as np

from .language import Language


__all__ = [
    'SpacyTransformer',
    'DOC', 'VECTOR', 'SENTENCES', 'ENTITIES', 'NOUN_CHUNKS',
    'SENTIMENT', 'TOKENS'
    ]


DOC = 'self'
VECTOR = 'vector'
SENTENCES = 'sents'
ENTITIES = 'ents'
NOUN_CHUNKS = 'noun_chunks'
SENTIMENT = 'sentiment'
TOKENS = 'tokens'


try:
    from sklearn.base import BaseEstimator, TransformerMixin

    class BaseTransformer(BaseEstimator, TransformerMixin):
        pass

except ImportError:
    BaseTransformer = object


class SpacyTransformer(BaseTransformer):

    def __init__(self,
                 model=None,
                 output_feature=DOC,
                 token_property='orth_',
                 n_threads=-1):
        self.model = model
        self.output_feature = output_feature
        self.token_property = token_property
        self.n_threads = n_threads

    def fit(self, X=None, y=None):
        return self

    def transform(self, X):
        """
        Transform a sequence of strings into the desired spaCy output
        :param X: an iterable sequence of strings to be processed by spaCy
        :return: a list/array of spaCy output for each of the string.
            The exact shape and type depends on the value of
            self.output_feature and self.token_property
        """
        # make sure a valid SpaCy model has been provided
        assert isinstance(self.model, Language), \
            "Please provide a valid SpaCy model!"

        docs = self.model.pipe(X, n_threads=self.n_threads)
        if self.output_feature == DOC:
            return list(docs)
        elif self.output_feature == VECTOR:
            return np.vstack(doc.vector for doc in docs)
        elif self.output_feature == TOKENS:
            return [
                [getattr(token, self.token_property) for token in doc]
                for doc in docs
            ]
        else:
            return [
                list(getattr(doc, self.output_feature))
                for doc in docs
            ]
