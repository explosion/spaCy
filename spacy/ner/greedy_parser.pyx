cimport cython
import random
import os
from os import path
import shutil
import json

from thinc.features cimport ConjFeat

from ..context cimport fill_context
from ..context cimport N_FIELDS
from .moves cimport Move
from .moves cimport fill_moves, transition, best_accepted
from .moves cimport set_accept_if_valid, set_accept_if_oracle
from .moves import get_n_moves
from ._state cimport State
from ._state cimport init_state


cdef class NERParser:
    def __init__(self, model_dir):
        self.mem = Pool()
        cfg = json.load(open(path.join(model_dir, 'config.json')))
        templates = cfg['templates']
        self.entity_types = cfg['entity_types']
        self.extractor = Extractor(templates, [ConjFeat] * len(templates))
        self.n_classes = get_n_moves(len(self.entity_types))
        self._moves = <Move*>self.mem.alloc(self.n_classes, sizeof(Move))
        fill_moves(self._moves, len(self.entity_types))
        self.model = LinearModel(len(self.tag_names))
        if path.exists(path.join(model_dir, 'model')):
            self.model.load(path.join(model_dir, 'model'))

        self._context = <atom_t*>self.mem.alloc(N_FIELDS, sizeof(atom_t))
        self._feats = <feat_t*>self.mem.alloc(self.extractor.n+1, sizeof(feat_t))
        self._values = <weight_t*>self.mem.alloc(self.extractor.n+1, sizeof(weight_t))
        self._scores = <weight_t*>self.mem.alloc(self.model.nr_class, sizeof(weight_t))

    cpdef int train(self, Tokens tokens, gold_classes):
        cdef Pool mem = Pool()
        cdef State* s = init_state(mem, tokens.length)
        cdef Move* golds = <Move*>mem.alloc(len(gold_classes), sizeof(Move))
        for i, clas in enumerate(gold_classes):
            golds[i] = self.moves[clas - 1]
            assert golds[i].id == clas
        cdef Move* guess
        while s.i < tokens.length:
            fill_context(self._context, s.i, tokens)
            self.extractor.extract(self._feats, self._values, self._context, NULL)
            self.model.score(self._scores, self._feats, self._values)
            
            set_accept_if_valid(self._moves, self.n_classes, s)
            guess = best_accepted(self._moves, self._scores, self.n_classes)

            set_accept_if_oracle(self._moves, golds, self.n_classes, s) # TODO
            gold = best_accepted(self._moves, self._scores, self.n_classes)

            if guess.clas == gold.clas:
                self.model.update({})
                return 0

            counts = {guess.clas: {}, gold.clas: {}}
            self.extractor.count(counts[gold.clas], self._feats, 1)
            self.extractor.count(counts[guess.clas], self._feats, -1)
            self.model.update(counts)

            transition(s, guess)
            tokens.ner[s.i-1] = s.tags[s.i-1]

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
