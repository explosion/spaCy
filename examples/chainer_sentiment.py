'''WIP --- Doesn't work well yet'''
import plac
import random
import six

import cProfile
import pstats

import pathlib
import cPickle as pickle
from itertools import izip

import spacy

import cytoolz
import cupy as xp
import cupy.cuda
import chainer.cuda

import chainer.links as L
import chainer.functions as F
from chainer import Chain, Variable, report
import chainer.training
import chainer.optimizers
from chainer.training import extensions
from chainer.iterators import SerialIterator
from chainer.datasets import TupleDataset


class SentimentAnalyser(object):
    @classmethod
    def load(cls, path, nlp, max_length=100):
        raise NotImplementedError
        #with (path / 'config.json').open() as file_:
        #    model = model_from_json(file_.read())
        #with (path / 'model').open('rb') as file_:
        #    lstm_weights = pickle.load(file_)
        #embeddings = get_embeddings(nlp.vocab)
        #model.set_weights([embeddings] + lstm_weights)
        #return cls(model, max_length=max_length)

    def __init__(self, model, max_length=100):
        self._model = model
        self.max_length = max_length

    def __call__(self, doc):
        X = get_features([doc], self.max_length)
        y = self._model.predict(X)
        self.set_sentiment(doc, y)

    def pipe(self, docs, batch_size=1000, n_threads=2):
        for minibatch in cytoolz.partition_all(batch_size, docs):
            minibatch = list(minibatch)
            sentences = []
            for doc in minibatch:
                sentences.extend(doc.sents)
            Xs = get_features(sentences, self.max_length)
            ys = self._model.predict(Xs)
            for sent, label in zip(sentences, ys):
                sent.doc.sentiment += label - 0.5
            for doc in minibatch:
                yield doc

    def set_sentiment(self, doc, y):
        doc.sentiment = float(y[0])
        # Sentiment has a native slot for a single float.
        # For arbitrary data storage, there's:
        # doc.user_data['my_data'] = y


class Classifier(Chain):
    def __init__(self, predictor):
        super(Classifier, self).__init__(predictor=predictor)

    def __call__(self, x, t):
        y = self.predictor(x)
        loss = F.softmax_cross_entropy(y, t)
        accuracy = F.accuracy(y, t)
        report({'loss': loss, 'accuracy': accuracy}, self)
        return loss


class SentimentModel(Chain):
    def __init__(self, nlp, shape, **settings):
        Chain.__init__(self,
            embed=_Embed(shape['nr_vector'], shape['nr_dim'], shape['nr_hidden'],
                set_vectors=lambda arr: set_vectors(arr, nlp.vocab)),
            encode=_Encode(shape['nr_hidden'], shape['nr_hidden']),
            attend=_Attend(shape['nr_hidden'], shape['nr_hidden']),
            predict=_Predict(shape['nr_hidden'], shape['nr_class']))
        self.to_gpu(0)

    def __call__(self, sentence):
        return self.predict(
                  self.attend(
                      self.encode(
                          self.embed(sentence))))


class _Embed(Chain):
    def __init__(self, nr_vector, nr_dim, nr_out, set_vectors=None):
        Chain.__init__(self,
            embed=L.EmbedID(nr_vector, nr_dim, initialW=set_vectors),
            project=L.Linear(None, nr_out, nobias=True))
        self.embed.W.volatile = False

    def __call__(self, sentence):
        return [self.project(self.embed(ts)) for ts in F.transpose(sentence)]


class _Encode(Chain):
    def __init__(self, nr_in, nr_out):
        Chain.__init__(self,
            fwd=L.LSTM(nr_in, nr_out),
            bwd=L.LSTM(nr_in, nr_out),
            mix=L.Bilinear(nr_out, nr_out, nr_out))

    def __call__(self, sentence):
        self.fwd.reset_state()
        fwds = map(self.fwd, sentence)
        self.bwd.reset_state()
        bwds = reversed(map(self.bwd, reversed(sentence)))
        return [F.elu(self.mix(f, b)) for f, b in zip(fwds, bwds)]


class _Attend(Chain):
    def __init__(self, nr_in, nr_out):
        Chain.__init__(self)

    def __call__(self, sentence):
        sent = sum(sentence)
        return sent


class _Predict(Chain):
    def __init__(self, nr_in, nr_out):
        Chain.__init__(self,
            l1=L.Linear(nr_in, nr_in),
            l2=L.Linear(nr_in, nr_out))

    def __call__(self, vector):
        vector = self.l1(vector)
        vector = F.elu(vector)
        vector = self.l2(vector)
        return vector


class SentenceDataset(TupleDataset):
    def __init__(self, nlp, texts, labels, max_length):
        self.max_length = max_length
        sents, labels = self._get_labelled_sentences(
            nlp.pipe(texts, batch_size=5000, n_threads=3),
            labels)
        TupleDataset.__init__(self,
            get_features(sents, max_length),
            labels)

    def __getitem__(self, index):
        batches = [dataset[index] for dataset in self._datasets]
        if isinstance(index, slice):
            length = len(batches[0])
            returns = [tuple([batch[i] for batch in batches])
                       for i in six.moves.range(length)]
            return returns
        else:
            return tuple(batches)

    def _get_labelled_sentences(self, docs, doc_labels):
        labels = []
        sentences = []
        for doc, y in izip(docs, doc_labels):
            for sent in doc.sents:
                sentences.append(sent)
                labels.append(y)
        return sentences, xp.asarray(labels, dtype='i')


class DocDataset(TupleDataset):
    def __init__(self, nlp, texts, labels):
        self.max_length = max_length
        DatasetMixin.__init__(self,
            get_features(
                nlp.pipe(texts, batch_size=5000, n_threads=3), self.max_length),
            labels)

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


def get_features(docs, max_length):
    docs = list(docs)
    Xs = xp.zeros((len(docs), max_length), dtype='i')
    for i, doc in enumerate(docs):
        j = 0
        for token in doc:
            if token.has_vector and not token.is_punct and not token.is_space:
                Xs[i, j] = token.norm
                j += 1
                if j >= max_length:
                    break
    return Xs


def set_vectors(vectors, vocab):
    for lex in vocab:
        if lex.has_vector and (lex.rank+1) < vectors.shape[0]:
            lex.norm = lex.rank+1
            vectors[lex.rank + 1] = lex.vector
        else:
            lex.norm = 0
    return vectors


def train(train_texts, train_labels, dev_texts, dev_labels,
        lstm_shape, lstm_settings, lstm_optimizer, batch_size=100, nb_epoch=5,
        by_sentence=True):
    nlp = spacy.load('en', entity=False)
    if 'nr_vector' not in lstm_shape:
        lstm_shape['nr_vector'] = max(lex.rank+1 for lex in nlp.vocab if lex.has_vector)
    if 'nr_dim' not in lstm_shape:
        lstm_shape['nr_dim'] = nlp.vocab.vectors_length
    print("Make model")
    model = Classifier(SentimentModel(nlp, lstm_shape, **lstm_settings))
    print("Parsing texts...")
    if by_sentence:
        train_data = SentenceDataset(nlp, train_texts, train_labels, lstm_shape['max_length'])
        dev_data = SentenceDataset(nlp, dev_texts, dev_labels, lstm_shape['max_length'])
    else:
        train_data = DocDataset(nlp, train_texts, train_labels)
        dev_data = DocDataset(nlp, dev_texts, dev_labels)
    train_iter = SerialIterator(train_data, batch_size=batch_size,
                                shuffle=True, repeat=True)
    dev_iter = SerialIterator(dev_data, batch_size=batch_size,
                              shuffle=False, repeat=False)
    optimizer = chainer.optimizers.Adam()
    optimizer.setup(model)
    updater = chainer.training.StandardUpdater(train_iter, optimizer, device=0)
    trainer = chainer.training.Trainer(updater, (1, 'epoch'), out='result')

    trainer.extend(extensions.Evaluator(dev_iter, model, device=0))
    trainer.extend(extensions.LogReport())
    trainer.extend(extensions.PrintReport([
        'epoch', 'main/accuracy', 'validation/main/accuracy']))
    trainer.extend(extensions.ProgressBar())
    
    trainer.run()


def evaluate(model_dir, texts, labels, max_length=100):
    def create_pipeline(nlp):
        '''
        This could be a lambda, but named functions are easier to read in Python.
        '''
        return [nlp.tagger, nlp.parser, SentimentAnalyser.load(model_dir, nlp,
                                                               max_length=max_length)]
    
    nlp = spacy.load('en')
    nlp.pipeline = create_pipeline(nlp)

    correct = 0
    i = 0 
    for doc in nlp.pipe(texts, batch_size=1000, n_threads=4):
        correct += bool(doc.sentiment >= 0.5) == bool(labels[i])
        i += 1
    return float(correct) / i


@plac.annotations(
    train_dir=("Location of training file or directory"),
    dev_dir=("Location of development file or directory"),
    model_dir=("Location of output model directory",),
    is_runtime=("Demonstrate run-time usage", "flag", "r", bool),
    nr_hidden=("Number of hidden units", "option", "H", int),
    max_length=("Maximum sentence length", "option", "L", int),
    dropout=("Dropout", "option", "d", float),
    learn_rate=("Learn rate", "option", "e", float),
    nb_epoch=("Number of training epochs", "option", "i", int),
    batch_size=("Size of minibatches for training LSTM", "option", "b", int),
    nr_examples=("Limit to N examples", "option", "n", int)
)
def main(model_dir, train_dir, dev_dir,
         is_runtime=False,
         nr_hidden=64, max_length=100, # Shape
         dropout=0.5, learn_rate=0.001, # General NN config
         nb_epoch=5, batch_size=32, nr_examples=-1):  # Training params
    model_dir = pathlib.Path(model_dir)
    train_dir = pathlib.Path(train_dir)
    dev_dir = pathlib.Path(dev_dir)
    if is_runtime:
        dev_texts, dev_labels = read_data(dev_dir)
        acc = evaluate(model_dir, dev_texts, dev_labels, max_length=max_length)
        print(acc)
    else:
        print("Read data")
        train_texts, train_labels = read_data(train_dir, limit=nr_examples)
        dev_texts, dev_labels = read_data(dev_dir, limit=nr_examples)
        print("Using GPU 0")
        #chainer.cuda.get_device(0).use()
        train_labels = xp.asarray(train_labels, dtype='i')
        dev_labels = xp.asarray(dev_labels, dtype='i')
        lstm = train(train_texts, train_labels, dev_texts, dev_labels,
                     {'nr_hidden': nr_hidden, 'max_length': max_length, 'nr_class': 2,
                      'nr_vector': 5000},
                      {'dropout': 0.5, 'lr': learn_rate},
                      {},
                      nb_epoch=nb_epoch, batch_size=batch_size)


if __name__ == '__main__':
    #cProfile.runctx("plac.call(main)", globals(), locals(), "Profile.prof")
    #s = pstats.Stats("Profile.prof")
    #s.strip_dirs().sort_stats("time").print_stats()
    plac.call(main)
