from keras.models import model_from_json
import numpy
import numpy.random


class KerasSimilarityShim(object):
    @classmethod
    def load(cls, path, nlp, get_features=None):
        if get_features is None:
            get_features = doc2ids
        with (path / 'config.json').open() as file_:
            config = json.load(file_)
        model = model_from_json(config['model'])
        with (path / 'model').open('rb') as file_:
            weights = pickle.load(file_)
        embeddings = get_embeddings(nlp.vocab)
        model.set_weights([embeddings] + weights)
        return cls(model, get_features=get_features)

    def __init__(self, model, get_features=None):
        self.model = model
        self.get_features = get_features

    def __call__(self, doc):
        doc.user_hooks['similarity'] = self.predict
        doc.user_span_hooks['similarity'] = self.predict
    
    def predict(self, doc1, doc2):
        x1 = self.get_features(doc1)
        x2 = self.get_features(doc2)
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
    return [SimilarityModel.load(
                nlp.path / 'similarity',
                nlp,
                feature_extracter=get_features)]
