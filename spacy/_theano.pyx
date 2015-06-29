from thinc.api cimport Example, ExampleC
from thinc.typedefs cimport weight_t

from ._ml cimport arg_max_if_true
from ._ml cimport arg_max_if_zero

import numpy
from os import path


cdef class TheanoModel(Model):
    def __init__(self, n_classes, input_spec, train_func, predict_func, model_loc=None,
                 eta=0.001, mu=0.9,
                 debug=None):
        if model_loc is not None and path.isdir(model_loc):
            model_loc = path.join(model_loc, 'model')

        self.eta = eta
        self.mu = mu
        self.t = 1
        initializer = lambda: 0.2 * numpy.random.uniform(-1.0, 1.0)
        self.input_layer = InputLayer(input_spec, initializer)
        self.train_func = train_func
        self.predict_func = predict_func
        self.debug = debug

        self.n_classes = n_classes
        self.n_feats = len(self.input_layer)
        self.model_loc = model_loc
        
    def predict(self, Example eg):
        self.input_layer.fill(eg.embeddings, eg.atoms, use_avg=True)
        theano_scores = self.predict_func(eg.embeddings)[0]
        cdef int i
        for i in range(self.n_classes):
            eg.c.scores[i] = theano_scores[i]
        eg.c.guess = arg_max_if_true(eg.c.scores, eg.c.is_valid, self.n_classes)

    def train(self, Example eg):
        self.input_layer.fill(eg.embeddings, eg.atoms, use_avg=False)
        theano_scores, update, y, loss = self.train_func(eg.embeddings, eg.costs,
                                                         self.eta, self.mu)
        self.input_layer.update(update, eg.atoms, self.t, self.eta, self.mu)
        for i in range(self.n_classes):
            eg.c.scores[i] = theano_scores[i]
        eg.c.guess = arg_max_if_true(eg.c.scores, eg.c.is_valid, self.n_classes)
        eg.c.best = arg_max_if_zero(eg.c.scores, eg.c.costs, self.n_classes)
        eg.c.cost = eg.c.costs[eg.c.guess]
        eg.c.loss = loss
        self.t += 1

    def end_training(self):
        pass
