# cython: profile=True
from __future__ import unicode_literals
from __future__ import division

from os import path
import os
from collections import defaultdict
import shutil
import random
import json
import cython

from thinc.features cimport Feature, count_feats


def setup_model_dir(tag_names, tag_map, templates, model_dir):
    if path.exists(model_dir):
        shutil.rmtree(model_dir)
    os.mkdir(model_dir)
    config = {
        'templates': templates,
        'tag_names': tag_names,
        'tag_map': tag_map
    }
    with open(path.join(model_dir, 'config.json'), 'w') as file_:
        json.dump(config, file_)


cdef class Model:
    def __init__(self, n_classes, templates, model_dir=None):
        self._extractor = Extractor(templates)
        self._model = LinearModel(n_classes, self._extractor.n_templ)
        self.model_loc = path.join(model_dir, 'model') if model_dir else None
        if self.model_loc and path.exists(self.model_loc):
            self._model.load(self.model_loc, freq_thresh=0)

    cdef class_t predict(self, atom_t* context) except *:
        cdef int n_feats
        cdef const Feature* feats = self._extractor.get_feats(context, &n_feats)
        cdef const weight_t* scores = self._model.get_scores(feats, n_feats)
        guess = _arg_max(scores, self._model.nr_class)
        return guess

    cdef class_t predict_among(self, atom_t* context, const bint* valid) except *:
        cdef int n_feats
        cdef const Feature* feats = self._extractor.get_feats(context, &n_feats)
        cdef const weight_t* scores = self._model.get_scores(feats, n_feats)
        return _arg_max_among(scores, valid, self._model.nr_class)

    cdef class_t predict_and_update(self, atom_t* context, const bint* valid,
                                    const int* costs) except *:
        cdef:
            int n_feats
            const Feature* feats
            const weight_t* scores

            int guess
            int best
            int cost
            int i
            weight_t score
        
        feats = self._extractor.get_feats(context, &n_feats)
        scores = self._model.get_scores(feats, n_feats)
        guess = _arg_max_among(scores, valid, self._model.nr_class)
        cost = costs[guess]
        if cost == 0:
            self._model.update({})
            return guess

        guess_counts = defaultdict(int)
        best_counts = defaultdict(int)
        for i in range(n_feats):
            feat = (feats[i].i, feats[i].key)
            upd = feats[i].value * cost
            best_counts[feat] += upd
            guess_counts[feat] -= upd
        best = -1
        score = 0
        for i in range(self._model.nr_class):
            if valid[i] and costs[i] == 0 and (best == -1 or scores[i] > score):
                best = i
                score = scores[i]
        self._model.update({guess: guess_counts, best: best_counts})
        return guess

    def end_training(self):
        self._model.end_training()
        self._model.dump(self.model_loc, freq_thresh=0)


"""
cdef class HastyModel:
    def __init__(self, model_dir):
        cfg = json.load(open(path.join(model_dir, 'config.json')))
        templates = cfg['templates']
        univ_counts = {}
        cdef unicode tag
        cdef unicode univ_tag
        tag_names = cfg['tag_names']
        self.extractor = Extractor(templates)
        self.model = LinearModel(len(tag_names) + 1, self.extractor.n_templ+2) # TODO
        if path.exists(path.join(model_dir, 'model')):
            self.model.load(path.join(model_dir, 'model'))

    cdef class_t predict(self, atom_t* context) except *:
        pass

    cdef class_t predict_among(self, atom_t* context, bint* valid) except *:
        pass

    cdef class_t predict_and_update(self, atom_t* context, int* costs) except *:
        pass

    def dump(self, model_dir):
        pass
"""

cdef int _arg_max(const weight_t* scores, int n_classes) except -1:
    cdef int best = 0
    cdef weight_t score = scores[best]
    cdef int i
    for i in range(1, n_classes):
        if scores[i] >= score:
            score = scores[i]
            best = i
    return best


cdef int _arg_max_among(const weight_t* scores, const bint* valid, int n_classes) except -1:
    cdef int clas
    cdef weight_t score = 0
    cdef int best = -1
    for clas in range(n_classes):
        if valid[clas] and (best == -1 or scores[clas] > score):
            score = scores[clas]
            best = clas
    return best
