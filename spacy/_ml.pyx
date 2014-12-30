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
    def __init__(self, n_classes, templates, model_loc=None):
        self._extractor = Extractor(templates)
        self._model = LinearModel(n_classes, self._extractor.n_templ)
        self.model_loc = model_loc
        if self.model_loc and path.exists(self.model_loc):
            self._model.load(self.model_loc, freq_thresh=0)

    cdef const weight_t* score(self, atom_t* context) except NULL:
        cdef int n_feats
        cdef const Feature* feats = self._extractor.get_feats(context, &n_feats)
        return self._model.get_scores(feats, n_feats)

    cdef class_t predict(self, atom_t* context) except *:
        cdef weight_t _
        scores = self.score(context)
        guess = _arg_max(scores, self._model.nr_class, &_)
        return guess

    cdef class_t predict_among(self, atom_t* context, const bint* valid) except *:
        cdef weight_t _
        scores = self.score(context)
        return _arg_max_among(scores, valid, self._model.nr_class, &_)

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
            weight_t _
        
        feats = self._extractor.get_feats(context, &n_feats)
        scores = self._model.get_scores(feats, n_feats)
        guess = _arg_max_among(scores, valid, self._model.nr_class, &_)
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


cdef class HastyModel:
    def __init__(self, n_classes, hasty_templates, full_templates, model_dir,
                 weight_t confidence=0.1):
        self.n_classes = n_classes
        self.confidence = confidence
        self._hasty = Model(n_classes, hasty_templates, path.join(model_dir, 'hasty_model'))
        self._full = Model(n_classes, full_templates, path.join(model_dir, 'full_model'))

    cdef class_t predict(self, atom_t* context) except *:
        cdef weight_t ratio
        scores = self._hasty.score(context)
        guess = _arg_max(scores, self.n_classes, &ratio)
        if ratio < self.confidence:
            return guess
        else:
            return self._full.predict(context)

    cdef class_t predict_among(self, atom_t* context, bint* valid) except *:
        cdef weight_t ratio
        scores = self._hasty.score(context)
        guess = _arg_max_among(scores, valid, self.n_classes, &ratio)
        if ratio < self.confidence:
            return guess
        else:
            return self._full.predict(context)

    cdef class_t predict_and_update(self, atom_t* context, bint* valid, int* costs) except *:
        cdef weight_t ratio
        scores = self._hasty.score(context)
        _arg_max_among(scores, valid, self.n_classes, &ratio)
        hasty_guess = self._hasty.predict_and_update(context, valid, costs)
        full_guess = self._full.predict_and_update(context, valid, costs)
        if ratio < self.confidence:
            return hasty_guess
        else:
            return full_guess

    def end_training(self):
        self._hasty.end_training()
        self._full.end_training()


@cython.cdivision(True)
cdef int _arg_max(const weight_t* scores, int n_classes, weight_t* ratio) except -1:
    cdef int best = 0
    cdef weight_t score = scores[best]
    cdef int i
    ratio[0] = 0.0
    for i in range(1, n_classes):
        if scores[i] >= score:
            if score > 0:
                ratio[0] = score / scores[i]
            score = scores[i]
            best = i
    return best


@cython.cdivision(True)
cdef int _arg_max_among(const weight_t* scores, const bint* valid, int n_classes,
                        weight_t* ratio) except -1:
    cdef int clas
    cdef weight_t score = 0
    cdef int best = -1
    ratio[0] = 0
    for clas in range(n_classes):
        if valid[clas] and (best == -1 or scores[clas] > score):
            if score > 0:
                ratio[0] = score / scores[clas]
            score = scores[clas]
            best = clas
    return best
