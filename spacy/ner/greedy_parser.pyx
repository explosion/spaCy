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
from .structs cimport Move, State
from .io_moves cimport fill_moves, transition, best_accepted
from .io_moves cimport set_accept_if_valid, set_accept_if_oracle
from .io_moves import get_n_moves
from ._state cimport init_state
from ._state cimport entity_is_open
from ._state cimport end_entity
from .annot cimport NERAnnotation


def setup_model_dir(entity_types, templates, model_dir):
    if path.exists(model_dir):
        shutil.rmtree(model_dir)
    os.mkdir(model_dir)
    config = {
        'templates': templates,
        'entity_types': entity_types,
    }
    with open(path.join(model_dir, 'config.json'), 'w') as file_:
        json.dump(config, file_)


def train(train_sents, model_dir, nr_iter=10):
    cdef Tokens tokens
    cdef NERAnnotation gold_ner
    parser = NERParser(model_dir)
    for _ in range(nr_iter):
        tp = 0
        fp = 0
        fn = 0
        for i, (tokens, gold_ner) in enumerate(train_sents):
            #print [tokens[i].string for i in range(tokens.length)]
            test_ents = set(parser.train(tokens, gold_ner))
            #print 'Test', test_ents
            gold_ents = set(gold_ner.entities)
            #print 'Gold', set(gold_ner.entities)
            tp += len(gold_ents.intersection(test_ents))
            fp += len(test_ents - gold_ents)
            fn += len(gold_ents - test_ents)
        p = tp / (tp + fp)
        r = tp / (tp + fn)
        f = 2 * ((p * r) / (p + r))
        print 'P: %.3f' % p,
        print 'R: %.3f' % r,
        print 'F: %.3f' % f
        random.shuffle(train_sents)
    parser.model.end_training()
    parser.model.dump(path.join(model_dir, 'model'))


cdef class NERParser:
    def __init__(self, model_dir):
        self.mem = Pool()
        cfg = json.load(open(path.join(model_dir, 'config.json')))
        templates = cfg['templates']
        self.extractor = Extractor(templates, [ConjFeat] * len(templates))
        self.entity_types = cfg['entity_types']
        self.n_classes = get_n_moves(len(self.entity_types))
        self._moves = <Move*>self.mem.alloc(self.n_classes, sizeof(Move))
        fill_moves(self._moves, self.n_classes, self.entity_types)
        self.model = LinearModel(self.n_classes)
        if path.exists(path.join(model_dir, 'model')):
            self.model.load(path.join(model_dir, 'model'))

        self._context = <atom_t*>self.mem.alloc(N_FIELDS, sizeof(atom_t))
        self._feats = <feat_t*>self.mem.alloc(self.extractor.n+1, sizeof(feat_t))
        self._values = <weight_t*>self.mem.alloc(self.extractor.n+1, sizeof(weight_t))
        self._scores = <weight_t*>self.mem.alloc(self.model.nr_class, sizeof(weight_t))

    cpdef list train(self, Tokens tokens, NERAnnotation annot):
        cdef Pool mem = Pool()
        cdef State* s = init_state(mem, tokens.length)
        cdef Move* guess
        cdef Move* oracle_move
        n_correct = 0
        cdef int f = 0
        while s.i < tokens.length:
            fill_context(self._context, s, tokens)
            self.extractor.extract(self._feats, self._values, self._context, NULL)
            self.model.score(self._scores, self._feats, self._values)

            set_accept_if_valid(self._moves, self.n_classes, s)
            guess = best_accepted(self._moves, self._scores, self.n_classes)
            assert guess.clas != 0
            set_accept_if_oracle(self._moves, self.n_classes, s,
                                 annot.starts, annot.ends, annot.labels)
            oracle_move = best_accepted(self._moves, self._scores, self.n_classes)
            assert oracle_move.clas != 0
            if guess.clas == oracle_move.clas:
                counts = {}
                n_correct += 1
            else:
                counts = {guess.clas: {}, oracle_move.clas: {}}
                self.extractor.count(counts[oracle_move.clas], self._feats, 1)
                self.extractor.count(counts[guess.clas], self._feats, -1)
            self.model.update(counts)
            transition(s, guess)
            tokens.ner[s.i-1] = s.tags[s.i-1]
        if entity_is_open(s):
            s.curr.label = annot.labels[s.curr.start]
            end_entity(s)
        entities = []
        for i in range(s.j):
            entities.append((s.ents[i].start, s.ents[i].end, s.ents[i].label))
        return entities

    cpdef list set_tags(self, Tokens tokens):
        cdef Pool mem = Pool()
        cdef State* s = init_state(mem, tokens.length)
        cdef Move* move
        while s.i < tokens.length:
            fill_context(self._context, s, tokens)
            self.extractor.extract(self._feats, self._values, self._context, NULL)
            self.model.score(self._scores, self._feats, self._values)
            set_accept_if_valid(self._moves, self.n_classes, s)
            move = best_accepted(self._moves, self._scores, self.n_classes)
            transition(s, move)
            tokens.ner[s.i-1] = s.tags[s.i-1]
        if entity_is_open(s):
            s.curr.label = move.label
            end_entity(s)
        entities = []
        for i in range(s.j):
            entities.append((s.ents[i].start, s.ents[i].end, s.ents[i].label))
        return entities
