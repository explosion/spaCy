import plac
import collections
import random

import cytoolz
import numpy
from keras.models import Sequential, model_from_json
from keras.layers import LSTM, Dense, Embedding, Dropout, Bidirectional
import cPickle as pickle

import spacy


class SentimentAnalyser(object):
    @classmethod
    def load(cls, path, nlp):
        with (path / 'config.json').open() as file_:

            model = model_from_json(file_.read())
        with (path / 'model').open('rb') as file_:
            lstm_weights = pickle.load(file_)
        embeddings = get_embeddings(nlp.vocab)
        model.set_weights([embeddings] + lstm_weights)
        return cls(model)

    def __init__(self, model):
        self._model = model

    def __call__(self, doc):
        X = get_features([doc], self.max_length)
        y = self._model.predict(X)
        self.set_sentiment(doc, y)

    def pipe(self, docs, batch_size=1000, n_threads=2):
        for minibatch in cytoolz.partition_all(batch_size, docs):
            Xs = get_features(minibatch, self.max_length)
            ys = self._model.predict(Xs)
            for i, doc in enumerate(minibatch):
                doc.user_data['sentiment'] = ys[i]

    def set_sentiment(self, doc, y):
        doc.sentiment = float(y[0])
        # Sentiment has a native slot for a single float.
        # For arbitrary data storage, there's:
        # doc.user_data['my_data'] = y


def get_features(docs, max_length):
    Xs = numpy.zeros(len(docs), max_length, dtype='int32')
    for i, doc in enumerate(docs):
        for j, token in enumerate(doc[:max_length]):
            Xs[i, j] = token.rank if token.has_vector else 0
    return Xs


def train(train_texts, train_labels, dev_texts, dev_labels,
        lstm_shape, lstm_settings, lstm_optimizer, batch_size=100, nb_epoch=5):
    nlp = spacy.load('en', parser=False, tagger=False, entity=False)
    embeddings = get_embeddings(nlp.vocab)
    model = compile_lstm(embeddings, lstm_shape, lstm_settings)
    train_X = get_features(nlp.pipe(train_texts), lstm_shape['max_length'])
    dev_X = get_features(nlp.pipe(dev_texts), lstm_shape['max_length'])
    model.fit(train_X, train_labels, dev_X, dev_labels,
              nb_epoch=nb_epoch, batch_size=batch_size)
    return model


def compile_lstm(embeddings, shape, settings):
    model = Sequential()
    model.add(
        Embedding(
            embeddings.shape[1],
            embeddings.shape[0],
            input_length=shape['max_length'],
            trainable=False,
            weights=[embeddings]
        )
    )
    model.add(Bidirectional(LSTM(shape['nr_hidden'])))
    model.add(Dropout(settings['dropout']))
    model.add(Dense(shape['nr_class'], activation='sigmoid'))
    return model


def get_embeddings(vocab):
    max_rank = max(lex.rank for lex in vocab if lex.has_vector)
    vectors = numpy.ndarray((max_rank+1, vocab.vectors_length), dtype='float32')
    for lex in vocab:
        if lex.has_vector:
            vectors[lex.rank] = lex.vector
    return vectors


def demonstrate_runtime(model_dir, texts):
    '''Demonstrate runtime usage of the custom sentiment model with spaCy.
    
    Here we return a dictionary mapping entities to the average sentiment of the
    documents they occurred in.
    '''
    def create_pipeline(nlp):
        '''
        This could be a lambda, but named functions are easier to read in Python.
        '''
        return [nlp.tagger, nlp.entity, SentimentAnalyser.load(model_dir, nlp)]
    
    nlp = spacy.load('en', create_pipeline=create_pipeline)

    entity_sentiments = collections.Counter(float)
    for doc in nlp.pipe(texts, batch_size=1000, n_threads=4):
        for ent in doc.ents:
            entity_sentiments[ent.text] += doc.sentiment
    return entity_sentiments


def read_data(data_dir, limit=0):
    examples = []
    for subdir, label in (('pos', 1), ('neg', 0)):
        for filename in (data_dir / subdir).iterdir():
            with filename.open() as file_:
                text = file_.read()
            examples.append((text, label))
    random.shuffle(examples)
    if limit >= 1:
        examples = examples[:limit]
    return zip(*examples) # Unzips into two lists


@plac.annotations(
    train_dir=("Location of training file or directory"),
    dev_dir=("Location of development file or directory"),
    model_dir=("Location of output model directory",),
    is_runtime=("Demonstrate run-time usage", "flag", "r", bool),
    nr_hidden=("Number of hidden units", "option", "H", int),
    max_length=("Maximum sentence length", "option", "L", int),
    dropout=("Dropout", "option", "d", float),
    nb_epoch=("Number of training epochs", "option", "i", int),
    batch_size=("Size of minibatches for training LSTM", "option", "b", int),
    nr_examples=("Limit to N examples", "option", "n", int)
)
def main(model_dir, train_dir, dev_dir,
         is_runtime=False,
         nr_hidden=64, max_length=100, # Shape
         dropout=0.5,                  # General NN config
         nb_epoch=5, batch_size=100, nr_examples=-1):  # Training params
    if is_runtime:
        dev_texts, dev_labels = read_data(dev_dir)
        demonstrate_runtime(model_dir, dev_texts)
    else:
        train_texts, train_labels = read_data(train_dir, limit=nr_examples)
        dev_texts, dev_labels = read_data(dev_dir)
        lstm = train(train_texts, train_labels, dev_texts, dev_labels,
                     {'nr_hidden': nr_hidden, 'max_length': max_length},
                     {'dropout': 0.5},
                     {},
                     nb_epoch=nb_epoch, batch_size=batch_size)
        weights = lstm.get_weights()
        with (model_dir / 'model').open('wb') as file_:
            pickle.dump(file_, weights[1:])


if __name__ == '__main__':
    plac.call(main)
