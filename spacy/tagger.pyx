# cython: profile=True
from __future__ import unicode_literals
from __future__ import division

from os import path
import os
import shutil
import random
import json
import cython

from thinc.features cimport Feature, count_feats


def setup_model_dir(tag_names, templates, model_dir):
    if path.exists(model_dir):
        shutil.rmtree(model_dir)
    os.mkdir(model_dir)
    config = {
        'templates': templates,
        'tag_names': tag_names,
    }
    with open(path.join(model_dir, 'config.json'), 'w') as file_:
        json.dump(config, file_)


cdef class Tagger:
    """Predict some type of tag, using greedy decoding.  The tagger reads its
    model and configuration from disk.
    """
    def __init__(self, model_dir):
        self.mem = Pool()
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

    cdef class_t predict(self, atom_t* context, object golds=None) except *:
        """Predict the tag of tokens[i].

        >>> tokens = EN.tokenize(u'An example sentence.')
        >>> tag = EN.pos_tagger.predict(0, tokens)
        >>> assert tag == EN.pos_tagger.tag_id('DT') == 5
        """
        cdef int n_feats
        cdef const Feature* feats = self.extractor.get_feats(context, &n_feats)
        cdef const weight_t* scores = self.model.get_scores(feats, n_feats)
        guess = _arg_max(scores, self.model.nr_class)
        if golds is not None and guess not in golds:
            best = _arg_max_among(scores, golds)
            counts = {guess: {}, best: {}}
            count_feats(counts[guess], feats, n_feats, -1)
            count_feats(counts[best], feats, n_feats, 1)
            self.model.update(counts)
        return guess


cdef int _arg_max(const weight_t* scores, int n_classes) except -1:
    cdef int best = 0
    cdef weight_t score = scores[best]
    cdef int i
    for i in range(1, n_classes):
        if scores[i] >= score:
            score = scores[i]
            best = i
    return best


cdef int _arg_max_among(const weight_t* scores, list classes) except -1:
    cdef int best = classes[0]
    cdef weight_t score = scores[best]
    cdef class_t clas
    for clas in classes:
        if scores[clas] > score:
            score = scores[clas]
            best = clas
    return best
