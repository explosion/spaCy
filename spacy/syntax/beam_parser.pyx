# cython: profile=True
# cython: experimental_cpp_class_def=True
# cython: cdivision=True
# cython: infer_types=True
"""
MALT-style dependency parser
"""
from __future__ import unicode_literals
cimport cython

from cpython.ref cimport PyObject, Py_INCREF, Py_XDECREF

from libc.stdint cimport uint32_t, uint64_t
from libc.string cimport memset, memcpy
from libc.stdlib cimport rand
from libc.math cimport log, exp, isnan, isinf
import random
import os.path
from os import path
import shutil
import json
import math

from cymem.cymem cimport Pool, Address
from murmurhash.mrmr cimport real_hash64 as hash64
from thinc.typedefs cimport weight_t, class_t, feat_t, atom_t, hash_t


from util import Config

from thinc.linear.features cimport ConjunctionExtracter
from thinc.structs cimport FeatureC, ExampleC

from thinc.extra.search cimport Beam
from thinc.extra.search cimport MaxViolation
from thinc.extra.eg cimport Example

from ..structs cimport TokenC

from ..tokens.doc cimport Doc
from ..strings cimport StringStore

from .transition_system cimport TransitionSystem, Transition

from ..gold cimport GoldParse

from . import _parse_features
from ._parse_features cimport CONTEXT_SIZE
from ._parse_features cimport fill_context
from .stateclass cimport StateClass
from .parser cimport Parser
from ._neural cimport ParserPerceptron
from ._neural cimport ParserNeuralNet


DEBUG = False
def set_debug(val):
    global DEBUG
    DEBUG = val


def get_templates(name):
    pf = _parse_features
    if name == 'ner':
        return pf.ner
    elif name == 'debug':
        return pf.unigrams
    else:
        return (pf.unigrams + pf.s0_n0 + pf.s1_n0 + pf.s1_s0 + pf.s0_n1 + pf.n0_n1 + \
                pf.tree_shape + pf.trigrams)


cdef int BEAM_WIDTH = 8

cdef class BeamParser(Parser):
    cdef public int beam_width

    def __init__(self, *args, **kwargs):
        self.beam_width = kwargs.get('beam_width', BEAM_WIDTH)
        Parser.__init__(self, *args, **kwargs)

    cdef int parseC(self, TokenC* tokens, int length, int nr_feat, int nr_class) with gil:
        self._parseC(tokens, length, nr_feat, nr_class)

    cdef int _parseC(self, TokenC* tokens, int length, int nr_feat, int nr_class) except -1:
        cdef Beam beam = Beam(self.moves.n_moves, self.beam_width)
        beam.initialize(_init_state, length, tokens)
        beam.check_done(_check_final_state, NULL)
        while not beam.is_done:
            self._advance_beam(beam, None, False)
        state = <StateClass>beam.at(0)
        self.moves.finalize_state(state.c)
        for i in range(length):
            tokens[i] = state.c._sent[i]
        _cleanup(beam)

    def train(self, Doc tokens, GoldParse gold_parse, itn=0):
        self.moves.preprocess_gold(gold_parse)
        cdef Beam pred = Beam(self.moves.n_moves, self.beam_width)
        pred.initialize(_init_state, tokens.length, tokens.c)
        pred.check_done(_check_final_state, NULL)
        
        cdef Beam gold = Beam(self.moves.n_moves, self.beam_width)
        gold.initialize(_init_state, tokens.length, tokens.c)
        gold.check_done(_check_final_state, NULL)
        violn = MaxViolation()
        while not pred.is_done and not gold.is_done:
            # We search separately here, to allow for ambiguity in the gold parse.
            self._advance_beam(pred, gold_parse, False)
            self._advance_beam(gold, gold_parse, True)
            violn.check_crf(pred, gold)
            if pred.loss > 0 and pred.min_score > (gold.score + self.model.time):
                break
        else:
            violn.check_crf(pred, gold)
        min_grad = 0.1 ** (itn+1)
        histories = zip(violn.p_probs, violn.p_hist) + zip(violn.g_probs, violn.g_hist)
        for grad, hist in histories:
            assert not math.isnan(grad) and not math.isinf(grad)
            if abs(grad) >= min_grad:
                self._update_from_history(self.moves, tokens, hist, grad)
        _cleanup(pred)
        _cleanup(gold)
        return pred.loss
    
    def _advance_beam(self, Beam beam, GoldParse gold, bint follow_gold):
        cdef Example py_eg = Example(nr_class=self.moves.n_moves, nr_atom=CONTEXT_SIZE,
                                     nr_feat=self.model.nr_feat, widths=self.model.widths)
        cdef ExampleC* eg = py_eg.c
 
        for i in range(beam.size):
            py_eg.reset()
            stcls = <StateClass>beam.at(i)
            if not stcls.c.is_final():
                self.model.set_featuresC(eg, stcls.c)
                self.model.set_scoresC(beam.scores[i], eg.features, eg.nr_feat)
                self.moves.set_valid(beam.is_valid[i], stcls.c)
        if gold is not None:
            for i in range(beam.size):
                py_eg.reset()
                stcls = <StateClass>beam.at(i)
                if not stcls.c.is_final():
                    self.moves.set_costs(beam.is_valid[i], beam.costs[i], stcls, gold)
                    if follow_gold:
                        for j in range(self.moves.n_moves):
                            beam.is_valid[i][j] *= beam.costs[i][j] < 1
        beam.advance(_transition_state, _hash_state, <void*>self.moves.c)
        beam.check_done(_check_final_state, NULL)


# These are passed as callbacks to thinc.search.Beam
cdef int _transition_state(void* _dest, void* _src, class_t clas, void* _moves) except -1:
    dest = <StateClass>_dest
    src = <StateClass>_src
    moves = <const Transition*>_moves
    dest.clone(src)
    moves[clas].do(dest.c, moves[clas].label)


cdef void* _init_state(Pool mem, int length, void* tokens) except NULL:
    cdef StateClass st = StateClass.init(<const TokenC*>tokens, length)
    # Ensure sent_start is set to 0 throughout
    for i in range(st.c.length):
        st.c._sent[i].sent_start = False
        st.c._sent[i].l_edge = i
        st.c._sent[i].r_edge = i
    st.fast_forward()
    Py_INCREF(st)
    return <void*>st


cdef int _check_final_state(void* _state, void* extra_args) except -1:
    return (<StateClass>_state).is_final()


def _cleanup(Beam beam):
    for i in range(beam.width):
        Py_XDECREF(<PyObject*>beam._states[i].content)
        Py_XDECREF(<PyObject*>beam._parents[i].content)


cdef hash_t _hash_state(void* _state, void* _) except 0:
    state = <StateClass>_state
    return state.c.hash()
