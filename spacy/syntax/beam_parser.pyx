# cython: profile=True
# cython: experimental_cpp_class_def=True
"""
MALT-style dependency parser
"""
from __future__ import unicode_literals
cimport cython

from cpython.ref cimport PyObject, Py_INCREF, Py_XDECREF

from libc.stdint cimport uint32_t, uint64_t
from libc.string cimport memset, memcpy
from libc.stdlib cimport rand
from libc.math cimport log, exp
import random
import os.path
from os import path
import shutil
import json

from cymem.cymem cimport Pool, Address
from murmurhash.mrmr cimport hash64
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
from .parser cimport ParserPerceptron
from .parser cimport ParserNeuralNet

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

    def train(self, Doc tokens, GoldParse gold_parse):
        self.moves.preprocess_gold(gold_parse)
        cdef Beam pred = Beam(self.moves.n_moves, self.beam_width)
        pred.initialize(_init_state, tokens.length, tokens.c)
        pred.check_done(_check_final_state, NULL)
        
        cdef Beam gold = Beam(self.moves.n_moves, self.beam_width)
        gold.initialize(_init_state, tokens.length, tokens.c)
        gold.check_done(_check_final_state, NULL)
        while not pred.is_done and not gold.is_done:
            # We search separately here, to allow for ambiguity in the gold
            # parse.
            self._advance_beam(pred, gold_parse, False)
            self._advance_beam(gold, gold_parse, True)
            # Early update
            if pred.min_score > gold.score:
                break
        # Gather the partition function --- Z --- by which we can normalize the
        # scores into a probability distribution. The simple idea here is that
        # we clip the probability of all parses outside the beam to 0.
        cdef long double Z = 0.0
        for i in range(pred.size):
            # Make sure we've only got negative examples here.
            # Otherwise, we might double-count the gold.
            if pred._states[i].loss > 0: 
                Z += exp(pred._states[i].score)
        if Z > 0: # If no negative examples, don't update.
            Z += exp(gold.score)
            for i, hist in enumerate(pred.histories):
                if pred._states[i].loss > 0:
                    # Update with the negative example.
                    # Gradient of loss is P(parse) - 0
                    self._update_dense(tokens, hist, exp(pred._states[i].score) / Z)
            # Update with the positive example.
            # Gradient of loss is P(parse) - 1
            self._update_dense(tokens, gold.histories[0], (exp(gold.score) / Z) - 1)
        _cleanup(pred)
        _cleanup(gold)
        return pred.loss

    def _advance_beam(self, Beam beam, GoldParse gold, bint follow_gold):
        cdef Example py_eg = Example(nr_class=self.moves.n_moves, nr_atom=CONTEXT_SIZE,
                                     nr_feat=self.model.nr_feat, widths=self.model.widths)
        cdef ExampleC* eg = py_eg.c
 
        cdef ParserNeuralNet model = self.model
        for i in range(beam.size):
            py_eg.reset()
            stcls = <StateClass>beam.at(i)
            if not stcls.c.is_final():
                model.set_featuresC(eg, stcls.c)
                model.set_scoresC(beam.scores[i], eg.features, eg.nr_feat, 1)
                self.moves.set_valid(beam.is_valid[i], stcls.c)
        if gold is not None:
            for i in range(beam.size):
                py_eg.reset()
                stcls = <StateClass>beam.at(i)
                if not stcls.c.is_final():
                    self.moves.set_costs(beam.is_valid[i], beam.costs[i], stcls, gold)
                    if follow_gold:
                        for j in range(self.moves.n_moves):
                            beam.is_valid[i][j] *= beam.costs[i][j] == 0
        beam.advance(_transition_state, _hash_state, <void*>self.moves.c)
        beam.check_done(_check_final_state, NULL)

    def _update_dense(self, Doc doc, history, weight_t loss):
        cdef Example py_eg = Example(nr_class=self.moves.n_moves,
                                     nr_atom=CONTEXT_SIZE,
                                     nr_feat=self.model.nr_feat,
                                     widths=self.model.widths)
        cdef ExampleC* eg = py_eg.c
        cdef ParserNeuralNet model = self.model
        stcls = StateClass.init(doc.c, doc.length)
        self.moves.initialize_state(stcls.c)
        for clas in history:
            model.set_featuresC(eg, stcls.c)
            self.moves.set_valid(eg.is_valid, stcls.c)
            for i in range(self.moves.n_moves):
                eg.costs[i] = loss if i == clas else 0
            model.updateC(
                eg.features, eg.nr_feat, True, eg.costs, eg.is_valid, False)
            self.moves.c[clas].do(stcls.c, self.moves.c[clas].label)
            py_eg.reset()

    def _update(self, Doc tokens, list hist, weight_t inc):
        cdef Pool mem = Pool()
        cdef atom_t[CONTEXT_SIZE] context
        features = <FeatureC*>mem.alloc(self.model.nr_feat, sizeof(FeatureC))
        
        cdef StateClass stcls = StateClass.init(tokens.c, tokens.length)
        self.moves.initialize_state(stcls.c)

        cdef class_t clas
        cdef ParserPerceptron model = self.model
        for clas in hist:
            fill_context(context, stcls.c)
            nr_feat = model.extracter.set_features(features, context)
            for feat in features[:nr_feat]:
                model.update_weight(feat.key, clas, feat.value * inc)
            self.moves.c[clas].do(stcls.c, self.moves.c[clas].label)
    

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

#
#    def _maxent_update(self, Doc doc, pred_scores, pred_hist, gold_scores, gold_hist):
#        Z = 0
#        for i, (score, history) in enumerate(zip(pred_scores, pred_hist)):
#            prob = exp(score)
#            if prob < 1e-6:
#                continue
#            stcls = StateClass.init(doc.c, doc.length)
#            self.moves.initialize_state(stcls.c)
#            for clas in history:
#                delta_loss[clas] = prob * 1/Z
#                gradient = [(input_ * prob) / Z for input_ in hidden]
#                fill_context(context, stcls.c)
#                nr_feat = model.extracter.set_features(features, context)
#                for feat in features[:nr_feat]:
#                    key = (clas, feat.key)
#                    counts[key] = counts.get(key, 0.0) + feat.value
#                    self.moves.c[clas].do(stcls.c, self.moves.c[clas].label)
#                for key in counts:
#                    counts[key] *= prob
#            Z += prob
#        gZ, g_counts = self._maxent_counts(doc, gold_scores, gold_hist)
#        for (clas, feat), value in g_counts.items():
#            self.model.update_weight(feat, clas, value / gZ)
#
#        Z, counts = self._maxent_counts(doc, pred_scores, pred_hist)
#        for (clas, feat), value in counts.items():
#            self.model.update_weight(feat, clas, -value / (Z + gZ))
#
#


#    def _maxent_update(self, doc, pred_scores, pred_hist, gold_scores, gold_hist,
#            step_size=0.001):
#        cdef weight_t Z, gZ, value
#        cdef feat_t feat
#        cdef class_t clas
#        gZ, g_counts = self._maxent_counts(doc, gold_scores, gold_hist)
#        Z, counts = self._maxent_counts(doc, pred_scores, pred_hist)
#        update = {}
#        if gZ > 0:
#            for (clas, feat), value in g_counts.items():
#                update[(clas, feat)] = value / gZ
#        Z += gZ
#        for (clas, feat), value in counts.items():
#            update.setdefault((clas, feat), 0.0)
#            update[(clas, feat)] -= value / Z
#        for (clas, feat), value in update.items():
#            if value < 1000:
#                self.model.update_weight(feat, clas, step_size * value)
# 
#    def _maxent_counts(self, Doc doc, scores, history):
#        cdef Pool mem = Pool()
#        cdef atom_t[CONTEXT_SIZE] context
#        features = <FeatureC*>mem.alloc(self.model.nr_feat, sizeof(FeatureC))
#        
#        cdef StateClass stcls
#
#        cdef class_t clas
#        cdef ParserPerceptron model = self.model
# 
#        cdef weight_t Z = 0.0
#        cdef weight_t score
#        counts = {}
#        for i, (score, history) in enumerate(zip(scores, history)):
#            prob = exp(score)
#            if prob < 1e-6:
#                continue
#            stcls = StateClass.init(doc.c, doc.length)
#            self.moves.initialize_state(stcls.c)
#            for clas in history:
#                fill_context(context, stcls.c)
#                nr_feat = model.extracter.set_features(features, context)
#                for feat in features[:nr_feat]:
#                    key = (clas, feat.key)
#                    counts[key] = counts.get(key, 0.0) + feat.value
#                self.moves.c[clas].do(stcls.c, self.moves.c[clas].label)
#            for key in counts:
#                counts[key] *= prob
#            Z += prob
#        return Z, counts
#
#
#    def _advance_beam(self, Beam beam, GoldParse gold, bint follow_gold, words):
#        cdef atom_t[CONTEXT_SIZE] context
#        cdef int i, j, cost
#        cdef bint is_valid
#        cdef const Transition* move
#
#        for i in range(beam.size):
#            state = <StateClass>beam.at(i)
#            if not state.is_final():
#                # What the model is predicting here:
#                # We know, separately, the probability of the current state
#                # We can think of a state as a sequence of (action, score) pairs
#                # We obtain a state by doing reduce(state, [act for act, score in scores])
#                # We obtain its probability by doing sum(score for act, score in scores)
#                #
#                # So after running the forward pass, we have this output layer...
#                # The output layer has N nodes in its output, for our N moves
#                # The model asserts that:
#                #
#                # P(actions[i](state)) == score + output[i]
#                #
#                # i.e. each node holds a score that means "This is the difference
#                # in goodness that will occur if you apply this action to this state.
#                # If you apply this action, this is how I would judge the state."
#                self.model.set_scoresC(beam.scores[i], eg)
#                self.moves.set_validC(beam.is_valid[i], state)
#        if gold is not None:
#            for i in range(beam.size):
#                state = <StateClass>beam.at(i)
#                if not stcls.is_final():
#                    self.moves.set_costsC(beam.costs[i], beam.is_valid[i],
#                        state, gold)
#                    if follow_gold:
#                        for j in range(self.moves.n_moves):
#                            beam.is_valid[i][j] *= beam.costs[i][j] == 0
#        beam.advance(_transition_state, _hash_state, <void*>self.moves.c)
#        beam.check_done(_check_final_state, NULL)
#
#    def _update(self, Doc doc, g_hist, p_hist, loss):
#        pred = StateClass(doc)
#        gold = StateClass(doc)
#        for g_move, p_move in zip(g_hist, p_hist):
#            self.model(pred_eg)
#            self.model(gold_eg)
# 
#            margin = pred_eg.scores[p_move] - gold_eg.scores[g_move] + 1
#            if margin > 0:
#                gold_eg.losses[g_move] = margin
#                self.model.update(gold_eg)
#                pred_eg.losses[p_move] = -margin
#                self.model.update(pred_eg.guess)
#            self.c.moves[g_move].do(gold)
#            self.c.moves[p_move].do(pred)
#
#
#
