"""This script expects something like a binary sentiment data set, such as
 that available here: `http://www.cs.cornell.edu/people/pabo/movie-review-data/`

It expects a directory structure like: `data_dir/train/{pos|neg}`
 and `data_dir/test/{pos|neg}`. Put (say) 90% of the files in the former
 and the remainder in the latter.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

from collections import defaultdict
from pathlib import Path
import numpy
import plac

import spacy.en


def read_data(nlp, data_dir):
    for subdir, label in (('pos', 1), ('neg', 0)):
        for filename in (data_dir / subdir).iterdir():
            text = filename.open().read()
            doc = nlp(text)
            if len(doc) >= 1:
                yield doc, label


def partition(examples, split_size):
    examples = list(examples)
    numpy.random.shuffle(examples)
    n_docs = len(examples)
    split = int(n_docs * split_size)
    return examples[:split], examples[split:]


def minibatch(data, bs=24):
    for i in range(0, len(data), bs):
        yield data[i:i+bs]


class Extractor(object):
    def __init__(self, nlp, vector_length, dropout=0.3):
        self.nlp = nlp
        self.dropout = dropout
        self.vector = numpy.zeros((vector_length, ))

    def doc2bow(self, doc, dropout=None):
        if dropout is None:
            dropout = self.dropout
        bow = defaultdict(int)
        all_words = defaultdict(int)
        for word in doc:
            if numpy.random.random() >= dropout and not word.is_punct:
                bow[word.lower] += 1
            all_words[word.lower] += 1
        if sum(bow.values()) >= 1:
            return bow
        else:
            return all_words

    def bow2vec(self, bow, E):
        self.vector.fill(0)
        n = 0
        for orth_id, freq in bow.items():
            self.vector += self.nlp.vocab[self.nlp.vocab.strings[orth_id]].vector * freq
            # Apply the fine-tuning we've learned
            if orth_id < E.shape[0]:
                self.vector += E[orth_id] * freq
            n += freq
        return self.vector / n


class NeuralNetwork(object):
    def __init__(self, depth, width, n_classes, n_vocab, extracter, optimizer):
        self.depth = depth
        self.width = width
        self.n_classes = n_classes
        self.weights = Params.random(depth, width, width, n_classes, n_vocab)
        self.doc2bow = extracter.doc2bow
        self.bow2vec = extracter.bow2vec
        self.optimizer = optimizer
        self._gradient = Params.zero(depth, width, width, n_classes, n_vocab)
        self._activity = numpy.zeros((depth, width))

    def train(self, batch):
        activity = self._activity
        gradient = self._gradient
        activity.fill(0)
        gradient.data.fill(0)
        loss = 0
        word_freqs = defaultdict(int)
        for doc, label in batch:
            word_ids = self.doc2bow(doc)
            vector = self.bow2vec(word_ids, self.weights.E)
            self.forward(activity, vector)
            loss += self.backprop(vector, gradient, activity, word_ids, label)
            for w, freq in word_ids.items():
                word_freqs[w] += freq
        self.optimizer(self.weights, gradient, len(batch), word_freqs)
        return loss

    def predict(self, doc):
        actv = self._activity
        actv.fill(0)
        W = self.weights.W
        b = self.weights.b
        E = self.weights.E
        
        vector = self.bow2vec(self.doc2bow(doc, dropout=0.0), E)
        self.forward(actv, vector)
        return numpy.argmax(softmax(actv[-1], W[-1], b[-1]))

    def forward(self, actv, in_):
        actv.fill(0)
        W = self.weights.W; b = self.weights.b
        actv[0] = relu(in_, W[0], b[0])
        for i in range(1, self.depth):
            actv[i] = relu(actv[i-1], W[i], b[i])

    def backprop(self, input_vector, gradient, activity, ids, label):
        W = self.weights.W
        b = self.weights.b

        target = numpy.zeros(self.n_classes)
        target[label] = 1.0
        pred = softmax(activity[-1], W[-1], b[-1])
        delta = pred - target

        for i in range(self.depth, 0, -1):
            gradient.b[i] += delta
            gradient.W[i] += numpy.outer(delta, activity[i-1])
            delta = d_relu(activity[i-1]) * W[i].T.dot(delta)

        gradient.b[0] += delta
        gradient.W[0] += numpy.outer(delta, input_vector)
        tuning = W[0].T.dot(delta).reshape((self.width,)) / len(ids)
        for w, freq in ids.items():
            if w < gradient.E.shape[0]:
                gradient.E[w] += tuning * freq
        return -sum(target * numpy.log(pred))


def softmax(actvn, W, b):
    w = W.dot(actvn) + b
    ew = numpy.exp(w - max(w))
    return (ew / sum(ew)).ravel()


def relu(actvn, W, b):
    x = W.dot(actvn) + b
    return x * (x > 0)


def d_relu(x):
    return x > 0


class Adagrad(object):
    def __init__(self, lr, rho):
        self.eps = 1e-3
        # initial learning rate
        self.learning_rate = lr
        self.rho = rho
        # stores sum of squared gradients 
        #self.h = numpy.zeros(self.dim)
        #self._curr_rate = numpy.zeros(self.h.shape)
        self.h = None
        self._curr_rate = None
    
    def __call__(self, weights, gradient, batch_size, word_freqs):
        if self.h is None:
            self.h = numpy.zeros(gradient.data.shape)
            self._curr_rate = numpy.zeros(gradient.data.shape)
        self.L2_penalty(gradient, weights, word_freqs)
        update = self.rescale(gradient.data / batch_size)
        weights.data -= update

    def rescale(self, gradient):
        if self.h is None:
            self.h = numpy.zeros(gradient.data.shape)
            self._curr_rate = numpy.zeros(gradient.data.shape)
        self._curr_rate.fill(0)
        self.h += gradient ** 2
        self._curr_rate = self.learning_rate / (numpy.sqrt(self.h) + self.eps)
        return self._curr_rate * gradient

    def L2_penalty(self, gradient, weights, word_freqs):
        # L2 Regularization
        for i in range(len(weights.W)):
            gradient.W[i] += weights.W[i] * self.rho
            gradient.b[i] += weights.b[i] * self.rho
        for w, freq in word_freqs.items():
            if w < gradient.E.shape[0]:
                gradient.E[w] += weights.E[w] * self.rho


class Params(object):
    @classmethod
    def zero(cls, depth, n_embed, n_hidden, n_labels, n_vocab):
        return cls(depth, n_embed, n_hidden, n_labels, n_vocab, lambda x: numpy.zeros((x,)))

    @classmethod
    def random(cls, depth, nE, nH, nL, nV):
        return cls(depth, nE, nH, nL, nV, lambda x: (numpy.random.rand(x) * 2 - 1) * 0.08)

    def __init__(self, depth, n_embed, n_hidden, n_labels, n_vocab, initializer):
        nE = n_embed; nH = n_hidden; nL = n_labels; nV = n_vocab
        n_weights = sum([
            (nE * nH) + nH, 
            (nH * nH  + nH) * depth,
            (nH * nL) + nL,
            (nV * nE)
        ])
        self.data = initializer(n_weights)
        self.W = []
        self.b = []
        i = self._add_layer(0, nE, nH)
        for _ in range(1, depth):
            i = self._add_layer(i, nH, nH)
        i = self._add_layer(i, nL, nH)
        self.E = self.data[i : i + (nV * nE)].reshape((nV, nE))
        self.E.fill(0)

    def _add_layer(self, start, x, y):
        end = start + (x * y)
        self.W.append(self.data[start : end].reshape((x, y)))
        self.b.append(self.data[end : end + x].reshape((x, )))
        return end + x


@plac.annotations(
    data_dir=("Data directory", "positional", None, Path),
    n_iter=("Number of iterations (epochs)", "option", "i", int),
    width=("Size of hidden layers", "option", "H", int),
    depth=("Depth", "option", "d", int),
    dropout=("Drop-out rate", "option", "r", float),
    rho=("Regularization penalty", "option", "p", float),
    eta=("Learning rate", "option", "e", float),
    batch_size=("Batch size", "option", "b", int),
    vocab_size=("Number of words to fine-tune", "option", "w", int),
)
def main(data_dir, depth=3, width=300, n_iter=5, vocab_size=40000,
         batch_size=24, dropout=0.3, rho=1e-5, eta=0.005):
    n_classes = 2
    print("Loading")
    nlp = spacy.en.English(parser=False)
    train_data, dev_data = partition(read_data(nlp, data_dir / 'train'), 0.8)
    print("Begin training")
    extracter = Extractor(nlp, width, dropout=0.3)
    optimizer = Adagrad(eta, rho)
    model = NeuralNetwork(depth, width, n_classes, vocab_size, extracter, optimizer)
    prev_best = 0
    best_weights = None
    for epoch in range(n_iter):
        numpy.random.shuffle(train_data)
        train_loss = 0.0
        for batch in minibatch(train_data, bs=batch_size):
            train_loss += model.train(batch)
        n_correct = sum(model.predict(x) == y for x, y in dev_data)
        print(epoch, train_loss, n_correct / len(dev_data))
        if n_correct >= prev_best:
            best_weights = model.weights.data.copy()
            prev_best = n_correct

    model.weights.data = best_weights
    print("Evaluating")
    eval_data = list(read_data(nlp, data_dir / 'test'))
    n_correct = sum(model.predict(x) == y for x, y in eval_data)
    print(n_correct / len(eval_data))
 


if __name__ == '__main__':
    #import cProfile
    #import pstats
    #cProfile.runctx("main(Path('data/aclImdb'))", globals(), locals(), "Profile.prof")
    #s = pstats.Stats("Profile.prof")
    #s.strip_dirs().sort_stats("time").print_stats(100)
    plac.call(main)
