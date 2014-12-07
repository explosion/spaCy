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


def setup_model_dir(tag_names, tag_counts, templates, model_dir):
    if path.exists(model_dir):
        shutil.rmtree(model_dir)
    os.mkdir(model_dir)
    config = {
        'templates': templates,
        'tag_names': tag_names,
        'tag_counts': tag_counts,
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
        self.tag_names = cfg['tag_names']
        self.tagdict = _make_tag_dict(cfg['tag_counts'])
        self.extractor = Extractor(templates)
        self.model = LinearModel(len(self.tag_names), self.extractor.n_templ+2)
        if path.exists(path.join(model_dir, 'model')):
            self.model.load(path.join(model_dir, 'model'))

    cdef class_t predict(self, const atom_t* context, object golds=None) except *:
        """Predict the tag of tokens[i].  The tagger remembers the features and
        prediction, in case you later call tell_answer.

        >>> tokens = EN.tokenize(u'An example sentence.')
        >>> tag = EN.pos_tagger.predict(0, tokens)
        >>> assert tag == EN.pos_tagger.tag_id('DT') == 5
        """
        cdef int n_feats
        cdef Feature* feats = self.extractor.get_feats(context, &n_feats)
        cdef weight_t* scores = self.model.get_scores(feats, n_feats)
        guess = _arg_max(scores, self.model.nr_class)
        if golds is not None and guess not in golds:
            best = _arg_max_among(scores, golds)
            counts = {guess: {}, best: {}}
            count_feats(counts[guess], feats, n_feats, -1)
            count_feats(counts[best], feats, n_feats, 1)
            self.model.update(counts)
        return guess

    def tag_id(self, object tag_name):
        """Encode tag_name into a tag ID integer."""
        tag_id = self.tag_names.index(tag_name)
        if tag_id == -1:
            tag_id = len(self.tag_names)
            self.tag_names.append(tag_name)
        return tag_id


def _make_tag_dict(counts):
    freq_thresh = 50
    ambiguity_thresh = 0.98
    tagdict = {}
    cdef atom_t word
    cdef atom_t tag
    for word_str, tag_freqs in counts.items():
        tag_str, mode = max(tag_freqs.items(), key=lambda item: item[1])
        n = sum(tag_freqs.values())
        word = int(word_str)
        tag = int(tag_str)
        if n >= freq_thresh and (float(mode) / n) >= ambiguity_thresh:
            tagdict[word] = tag
    return tagdict


cdef class_t _arg_max(weight_t* scores, int n_classes) except 9000:
    cdef int best = 0
    cdef weight_t score = scores[best]
    cdef int i
    for i in range(1, n_classes):
        if scores[i] >= score:
            score = scores[i]
            best = i
    return best


cdef class_t _arg_max_among(weight_t* scores, list classes):
    cdef int best = classes[0]
    cdef weight_t score = scores[best]
    cdef class_t clas
    for clas in classes:
        if scores[clas] > score:
            score = scores[clas]
            best = clas
    return best
