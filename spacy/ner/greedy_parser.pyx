from __future__ import division
from __future__ import unicode_literals

cimport cython
import random
import os
from os import path
import shutil
import json

from thinc.features cimport ConjFeat

from .context cimport fill_context
from .context cimport N_FIELDS
from .moves cimport Move
from .moves cimport fill_moves, transition, best_accepted
from .moves cimport set_accept_if_valid, set_accept_if_oracle
from ._state cimport entity_is_open
from .moves import get_n_moves
from ._state cimport State
from ._state cimport init_state


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



def train(train_sents, model_dir, nr_iter=10):
    cdef Tokens tokens
    parser = NERParser(model_dir)
    for _ in range(nr_iter):
        n_corr = 0
        total = 0
        for i, (tokens, golds) in enumerate(train_sents):
            if any([g == 0 for g in golds]):
                continue
            n_corr += parser.train(tokens, golds)
            total += len([g for g in golds if g != 0])
        print('%.4f' % ((n_corr / total) * 100))
        random.shuffle(train_sents)
    parser.model.end_training()
    parser.model.dump(path.join(model_dir, 'model'))


cdef class NERParser:
    def __init__(self, model_dir):
        self.mem = Pool()
        cfg = json.load(open(path.join(model_dir, 'config.json')))
        templates = cfg['templates']
        self.tag_names = cfg['tag_names']
        self.extractor = Extractor(templates, [ConjFeat] * len(templates))
        self.n_classes = len(self.tag_names)
        self._moves = <Move*>self.mem.alloc(len(self.tag_names), sizeof(Move))
        fill_moves(self._moves, self.tag_names)
        self.model = LinearModel(self.n_classes)
        if path.exists(path.join(model_dir, 'model')):
            self.model.load(path.join(model_dir, 'model'))

        self._context = <atom_t*>self.mem.alloc(N_FIELDS, sizeof(atom_t))
        self._feats = <feat_t*>self.mem.alloc(self.extractor.n+1, sizeof(feat_t))
        self._values = <weight_t*>self.mem.alloc(self.extractor.n+1, sizeof(weight_t))
        self._scores = <weight_t*>self.mem.alloc(self.model.nr_class, sizeof(weight_t))

    cpdef int train(self, Tokens tokens, gold_classes) except -1:
        cdef Pool mem = Pool()
        cdef State* s = init_state(mem, tokens.length)
        cdef Move* golds = <Move*>mem.alloc(len(gold_classes), sizeof(Move))
        for tok_i, clas in enumerate(gold_classes):
            golds[tok_i] = self._moves[clas]
            assert golds[tok_i].clas == clas, '%d vs %d' % (golds[tok_i].clas, clas)
        cdef Move* guess
        n_correct = 0
        cdef int f = 0
        while s.i < tokens.length:
            fill_context(self._context, s.i, tokens)
            self.extractor.extract(self._feats, self._values, self._context, NULL)
            self.model.score(self._scores, self._feats, self._values)
            
            set_accept_if_valid(self._moves, self.n_classes, s)
            guess = best_accepted(self._moves, self._scores, self.n_classes)
            assert guess.clas != 0
            assert gold_classes[s.i] != 0
            set_accept_if_oracle(self._moves, golds, self.n_classes, s)
            gold = best_accepted(self._moves, self._scores, self.n_classes)
            if guess.clas == gold.clas:
                counts = {}
                n_correct += 1
            else:
                counts = {guess.clas: {}, gold.clas: {}}
                self.extractor.count(counts[gold.clas], self._feats, 1)
                self.extractor.count(counts[guess.clas], self._feats, -1)
            self.model.update(counts)
            gold_str = self.tag_names[gold.clas]
            transition(s, gold)
            tokens.ner[s.i-1] = s.tags[s.i-1]
        return n_correct

    cpdef int set_tags(self, Tokens tokens) except -1:
        cdef Pool mem = Pool()
        cdef State* s = init_state(mem, tokens.length)
        cdef Move* move
        while s.i < tokens.length:
            fill_context(self._context, s.i, tokens)
            self.extractor.extract(self._feats, self._values, self._context, NULL)
            self.model.score(self._scores, self._feats, self._values)
            set_accept_if_valid(self._moves, self.n_classes, s)
            move = best_accepted(self._moves, self._scores, self.n_classes)
            transition(s, move)
            tokens.ner[s.i-1] = s.tags[s.i-1]
