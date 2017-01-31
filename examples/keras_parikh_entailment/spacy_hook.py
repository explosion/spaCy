from keras.models import model_from_json
import numpy
import numpy.random
import json
from spacy.tokens.span import Span

try:
    import cPickle as pickle
except ImportError:
    import pickle


class KerasSimilarityShim(object):
    @classmethod
    def load(cls, path, nlp, get_features=None, max_length=100):
        if get_features is None:
            get_features = get_word_ids
        with (path / 'config.json').open() as file_:
            model = model_from_json(file_.read())
        with (path / 'model').open('rb') as file_:
            weights = pickle.load(file_)
        embeddings = get_embeddings(nlp.vocab)
        model.set_weights([embeddings] + weights)
        return cls(model, get_features=get_features, max_length=max_length)

    def __init__(self, model, get_features=None, max_length=100):
        self.model = model
        self.get_features = get_features
        self.max_length = max_length

    def __call__(self, doc):
        doc.user_hooks['similarity'] = self.predict
        doc.user_span_hooks['similarity'] = self.predict

    def predict(self, doc1, doc2):
        x1 = self.get_features([doc1], max_length=self.max_length, tree_truncate=True)
        x2 = self.get_features([doc2], max_length=self.max_length, tree_truncate=True)
        scores = self.model.predict([x1, x2])
        return scores[0]


def get_embeddings(vocab, nr_unk=100):
    nr_vector = max(lex.rank for lex in vocab) + 1
    vectors = numpy.zeros((nr_vector+nr_unk+2, vocab.vectors_length), dtype='float32')
    for lex in vocab:
        if lex.has_vector:
            vectors[lex.rank+1] = lex.vector / lex.vector_norm
    return vectors


def get_word_ids(docs, rnn_encode=False, tree_truncate=False, max_length=100, nr_unk=100):
    Xs = numpy.zeros((len(docs), max_length), dtype='int32')
    for i, doc in enumerate(docs):
        if tree_truncate:
            if isinstance(doc, Span):
                queue = [doc.root]
            else:
                queue = [sent.root for sent in doc.sents]
        else:
            queue = list(doc)
        words = []
        while len(words) <= max_length and queue:
            word = queue.pop(0)
            if rnn_encode or (not word.is_punct and not word.is_space):
                words.append(word)
            if tree_truncate:
                queue.extend(list(word.lefts))
                queue.extend(list(word.rights))
        words.sort()
        for j, token in enumerate(words):
            if token.has_vector:
                Xs[i, j] = token.rank+1
            else:
                Xs[i, j] = (token.shape % (nr_unk-1))+2
            j += 1
            if j >= max_length:
                break
        else:
            Xs[i, len(words)] = 1
    return Xs


def create_similarity_pipeline(nlp):
    return [
        nlp.tagger,
        nlp.entity,
        nlp.parser,
        KerasSimilarityShim.load(nlp.path / 'similarity', nlp, max_length=10)
    ]
