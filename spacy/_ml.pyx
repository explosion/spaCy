# cython: profile=True
from __future__ import unicode_literals
from __future__ import division

from os import path
import tempfile
import os
import shutil
import json
import cython
import numpy.random

from libc.string cimport memcpy

from thinc.features cimport Feature, count_feats
from thinc.api cimport Example

from thinc.learner cimport arg_max, arg_max_if_true, arg_max_if_zero


cdef class Model:
    def __init__(self, n_classes, templates, model_loc=None):
        if model_loc is not None and path.isdir(model_loc):
            model_loc = path.join(model_loc, 'model')
        self._templates = templates
        n_atoms = max([max(templ) for templ in templates]) + 1
        self.n_classes = n_classes
        self._extractor = Extractor(templates)
        self.n_feats = self._extractor.n_templ
        self._model = LinearModel(n_classes, self._extractor)
        self._eg = Example(n_classes, n_atoms, self._extractor.n_templ, self._extractor.n_templ)
        self.model_loc = model_loc
        if self.model_loc and path.exists(self.model_loc):
            self._model.load(self.model_loc, freq_thresh=0)

    def __reduce__(self):
        _, model_loc = tempfile.mkstemp()
        # TODO: This is a potentially buggy implementation. We're not really
        # given a good guarantee that all internal state is saved correctly here,
        # since there are learning parameters for e.g. the model averaging in
        # averaged perceptron, the gradient calculations in AdaGrad, etc
        # that aren't necessarily saved. So, if we're part way through training
        # the model, and then we pickle it, we won't recover the state correctly.
        self._model.dump(model_loc)
        return (Model, (self.n_classes, self._templates, model_loc),
                None, None)

    def predict(self, Example eg):
        self._model(eg)

    def train(self, Example eg):
        self._model.train(eg)

    cdef const weight_t* score(self, atom_t* context) except NULL:
        memcpy(self._eg.c.atoms, context, self._eg.c.nr_atom * sizeof(context[0]))
        self._model(self._eg)
        return self._eg.c.scores

    cdef int set_scores(self, weight_t* scores, atom_t* context) nogil:
        cdef int nr_feat = self._extractor.set_feats(self._eg.c.features, context)

        self._model.set_scores(scores, self._eg.c.features, nr_feat)

    def end_training(self, model_loc=None):
        if model_loc is None:
            model_loc = self.model_loc
        self._model.end_training()
        self._model.dump(model_loc, freq_thresh=0)
