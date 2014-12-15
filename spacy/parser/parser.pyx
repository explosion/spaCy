# cython: profile=True
"""
MALT-style dependency parser
"""
cimport cython
import random
import os.path
from os.path import join as pjoin
import shutil
import json

from cymem.cymem cimport Pool, Address
from thinc.typedefs cimport weight_t, class_t, feat_t, atom_t


from util import Config

from thinc.features cimport Extractor
from thinc.features cimport Feature
from thinc.features cimport count_feats

from thinc.learner cimport LinearModel

from ..tokens cimport Tokens, TokenC

from .arc_eager cimport TransitionSystem

from ._state cimport init_state, State, is_final, get_s1

VOCAB_SIZE = 1e6
TAG_SET_SIZE = 50

DEF CONTEXT_SIZE = 50


DEBUG = False 
def set_debug(val):
    global DEBUG
    DEBUG = val


cdef str print_state(State* s, list words):
    top = words[s.top]
    second = words[get_s1(s)]
    n0 = words[s.i]
    n1 = words[s.i + 1]
    return ' '.join((second, top, '|', n0, n1))


def train(sents, golds, model_dir, n_iter=15, feat_set=u'basic', seed=0):
    if os.path.exists(model_dir):
        shutil.rmtree(model_dir)
    os.mkdir(model_dir)
    left_labels, right_labels, dfl_labels = get_labels(golds)
    Config.write(model_dir, 'config', features=feat_set, seed=seed,
                 left_labels=left_labels, right_labels=right_labels)
    parser = Parser(model_dir)
    indices = list(range(len(sents)))
    for n in range(n_iter):
        for i in indices:
            parser.train_sent(sents[i], *golds[i])
            #parser.tagger.train_sent(py_sent) # TODO
        acc = float(parser.guide.n_corr) / parser.guide.total
        print(parser.guide.end_train_iter(n) + '\t' +
              parser.tagger.guide.end_train_iter(n))
        random.shuffle(indices)
    parser.guide.end_training()
    parser.tagger.guide.end_training()
    parser.guide.dump(pjoin(model_dir, 'model'), freq_thresh=0)
    parser.tagger.guide.dump(pjoin(model_dir, 'tagger'))
    return acc


def get_labels(sents):
    '''Get alphabetically-sorted lists of left, right and disfluency labels that
    occur in a sample of sentences. Used to determine the set of legal transitions
    from the training set.

    Args:
        sentences (list[Input]): A list of Input objects, usually the training set.

    Returns:
        labels (tuple[list, list, list]): Sorted lists of left, right and disfluency
            labels.
    '''
    left_labels = set()
    right_labels = set()
    # TODO
    return list(sorted(left_labels)), list(sorted(right_labels))


def get_templates(feats_str):
    '''Interpret feats_str, returning a list of template tuples. Each template
    is a tuple of numeric indices, referring to positions in the context
    array. See _parse_features.pyx for examples. The templates are applied by
    thinc.features.Extractor, which picks out the appointed values and hashes
    the resulting array, to produce a single feature code.
    '''
    return tuple()


cdef class Parser:
    def __init__(self, model_dir):
        assert os.path.exists(model_dir) and os.path.isdir(model_dir)
        self.cfg = Config.read(model_dir, 'config')
        self.extractor = Extractor(get_templates(self.cfg.features))
        self.moves = TransitionSystem(self.cfg.left_labels, self.cfg.right_labels)
        
        self.model = LinearModel(self.moves.n_moves, self.extractor.n_templ)
        if os.path.exists(pjoin(model_dir, 'model')):
            self.model.load(pjoin(model_dir, 'model'))

    cpdef int parse(self, Tokens tokens) except -1:
        cdef:
            Feature* feats
            weight_t* scores

        cdef atom_t[CONTEXT_SIZE] context
        cdef int n_feats
        cdef Pool mem = Pool()
        cdef State* state = init_state(mem, tokens.length)
        while not is_final(state):
            fill_context(context, state, tokens.data) # TODO
            feats = self.extractor.get_feats(context, &n_feats)
            scores = self.model.get_scores(feats, n_feats)

            guess = self.moves.best_valid(scores, state)
            
            self.moves.transition(state, guess)
        # TODO output

    def train_sent(self, Tokens tokens, list gold_heads, list gold_labels):
        cdef:
            Feature* feats
            weight_t* scores

        cdef int n_feats
        cdef atom_t[CONTEXT_SIZE] context
        cdef Pool mem = Pool()
        cdef State* state = init_state(mem, tokens.length)

        while not is_final(state):
            fill_context(context, state, tokens.data) # TODO
            feats = self.extractor.get_feats(context, &n_feats)
            scores = self.model.get_scores(feats, n_feats)

            guess = self.moves.best_valid(scores, state)
            best = self.moves.best_gold(scores, state, gold_heads, gold_labels)
            
            counts = {guess: {}, best: {}}
            if guess != best:
                count_feats(counts[guess], feats, n_feats, -1)
                count_feats(counts[best], feats, n_feats, 1)
            self.model.update(counts)

            self.moves.transition(state, guess)


cdef int fill_context(atom_t* context, State* s, TokenC* sent) except -1:
    pass
