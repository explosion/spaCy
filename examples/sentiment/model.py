from __future__ import division
from numpy import average, zeros, outer, random, exp, sqrt, concatenate, argmax
import numpy

from .util import Scorer


class Adagrad(object): 
    def __init__(self, dim, lr):
        self.dim = dim
        self.eps = 1e-3
        # initial learning rate
        self.learning_rate = lr
        # stores sum of squared gradients 
        self.h = zeros(self.dim)
        self._curr_rate = zeros(self.h.shape)

    def rescale(self, gradient):
        self._curr_rate.fill(0)
        self.h += gradient ** 2
        self._curr_rate = self.learning_rate / (sqrt(self.h) + self.eps)
        return self._curr_rate * gradient

    def reset_weights(self):
        self.h = zeros(self.dim)


class Params(object):
    @classmethod
    def zero(cls, depth, n_embed, n_hidden, n_labels, n_vocab):
        return cls(depth, n_embed, n_hidden, n_labels, n_vocab, lambda x: zeros((x,)))

    @classmethod
    def random(cls, depth, nE, nH, nL, nV):
        return cls(depth, nE, nH, nL, nV, lambda x: (random.rand(x) * 2 - 1) * 0.08)

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


def softmax(actvn, W, b):
    w = W.dot(actvn) + b
    ew = exp(w - max(w))
    return (ew / sum(ew)).ravel()


def relu(actvn, W, b):
    x = W.dot(actvn) + b
    return x * (x > 0)


def d_relu(x):
    return x > 0


class Network(object):
    def __init__(self, depth, n_embed, n_hidden, n_labels, n_vocab, rho=1e-4, lr=0.005):
        self.depth = depth
        self.n_embed = n_embed
        self.n_hidden = n_hidden
        self.n_labels = n_labels
        self.n_vocab = n_vocab

        self.params = Params.random(depth, n_embed, n_hidden, n_labels, n_vocab)
        self.gradient = Params.zero(depth, n_embed, n_hidden, n_labels, n_vocab)
        self.adagrad = Adagrad(self.params.data.shape, lr)
        self.seen_words = {}
 
        self.pred = zeros(self.n_labels)
        self.actvn = zeros((self.depth, self.n_hidden))
        self.input_vector = zeros((self.n_embed, ))
    
    def forward(self, word_ids, embeddings):
        self.input_vector.fill(0)
        self.input_vector += sum(embeddings)
        # Apply the fine-tuning we've learned
        for id_ in word_ids:
            if id_ < self.n_vocab:
                self.input_vector += self.params.E[id_]
        # Average
        self.input_vector /= len(embeddings)
        prev = self.input_vector
        for i in range(self.depth):
            self.actvn[i] = relu(prev, self.params.W[i], self.params.b[i])
            return x * (x > 0)


            prev = self.actvn[i]
        self.pred = softmax(self.actvn[-1], self.params.W[-1], self.params.b[-1])
        return argmax(self.pred)

    def backward(self, word_ids, label):
        target = zeros(self.n_labels)
        target[label] = 1.0
        D = self.pred - target

        for i in range(self.depth, 0, -1):
            self.gradient.b[i] += D
            self.gradient.W[i] += outer(D, self.actvn[i-1])
            D = d_relu(self.actvn[i-1]) * self.params.W[i].T.dot(D)

        self.gradient.b[0] += D
        self.gradient.W[0] += outer(D, self.input_vector)

        grad = self.params.W[0].T.dot(D).reshape((self.n_embed,)) / len(word_ids)
        for word_id in word_ids:
            if word_id < self.n_vocab:
                self.gradient.E[word_id] += grad
                self.seen_words[word_id] = self.seen_words.get(word_id, 0) + 1

    def update(self, rho, n):
        # L2 Regularization
        for i in range(self.depth):
            self.gradient.W[i] += self.params.W[i] * rho
            self.gradient.b[i] += self.params.b[i] * rho
        # Do word embedding tuning
        for word_id, freq in self.seen_words.items():
            self.gradient.E[word_id] += (self.params.E[word_id] * freq) * rho
 
        update = self.gradient.data / n
        update = self.adagrad.rescale(update)
        self.params.data -= update
        self.gradient.data.fill(0)
        self.seen_words = {}


def get_words(doc, dropout_rate, n_vocab):
    mask = random.rand(len(doc)) > dropout_rate
    word_ids = []
    embeddings = []
    for word in doc:
        if mask[word.i] and not word.is_punct:
            embeddings.append(word.vector)
            word_ids.append(word.orth)
    # all examples must have at least one word
    if not embeddings:
        return [w.orth for w in doc], [w.vector for w in doc]
    else:
        return word_ids, embeddings


def train(dataset, n_embed, n_hidden, n_labels, n_vocab, depth, dropout_rate, rho,
          n_iter, save_model):
    model = Network(depth, n_embed, n_hidden, n_labels, n_vocab)
    best_acc = 0
    for epoch in range(n_iter):
        train_score = Scorer()
        # create mini-batches
        for batch in dataset.batches(dataset.train):
            for doc, label in batch:
                if len(doc) == 0:
                    continue
                word_ids, embeddings = get_words(doc, dropout_rate, n_vocab)
                guess = model.forward(word_ids, embeddings)
                model.backward(word_ids, label)
                train_score += guess == label
            model.update(rho, len(batch))
        test_score = Scorer()
        for doc, label in dataset.dev:
            word_ids, embeddings = get_words(doc, 0.0, n_vocab)
            guess = model.forward(word_ids, embeddings)
            test_score += guess == label
        if test_score.true >= best_acc:
            best_acc = test_score.true
            save_model(epoch, model.params.data)
        print "%d\t%s\t%s" % (epoch, train_score, test_score)
    return model
