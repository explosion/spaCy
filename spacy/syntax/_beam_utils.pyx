# cython: infer_types=True
# cython: profile=True
cimport numpy as np
import numpy
from cpython.ref cimport PyObject, Py_INCREF, Py_XDECREF
from thinc.extra.search cimport Beam
from thinc.extra.search import MaxViolation
from thinc.typedefs cimport hash_t, class_t

from .transition_system cimport TransitionSystem, Transition
from .stateclass cimport StateClass
from ..gold cimport GoldParse
from ..tokens.doc cimport Doc


# These are passed as callbacks to thinc.search.Beam
cdef int _transition_state(void* _dest, void* _src, class_t clas, void* _moves) except -1:
    dest = <StateClass>_dest
    src = <StateClass>_src
    moves = <const Transition*>_moves
    dest.clone(src)
    moves[clas].do(dest.c, moves[clas].label)


cdef int _check_final_state(void* _state, void* extra_args) except -1:
    return (<StateClass>_state).is_final()


def _cleanup(Beam beam):
    for i in range(beam.width):
        Py_XDECREF(<PyObject*>beam._states[i].content)
        Py_XDECREF(<PyObject*>beam._parents[i].content)


cdef hash_t _hash_state(void* _state, void* _) except 0:
    state = <StateClass>_state
    if state.c.is_final():
        return 1
    else:
        return state.c.hash()


cdef class ParserBeam(object):
    cdef public TransitionSystem moves
    cdef public object states
    cdef public object golds
    cdef public object beams

    def __init__(self, TransitionSystem moves, states, golds,
            int width=4, float density=0.001):
        self.moves = moves
        self.states = states
        self.golds = golds
        self.beams = []
        cdef Beam beam
        cdef StateClass state, st
        for state in states:
            beam = Beam(self.moves.n_moves, width, density)
            beam.initialize(self.moves.init_beam_state, state.c.length, state.c._sent)
            for i in range(beam.size):
                st = <StateClass>beam.at(i)
                st.c.offset = state.c.offset
            self.beams.append(beam)

    def __dealloc__(self):
        if self.beams is not None:
            for beam in self.beams:
                if beam is not None:
                    _cleanup(beam)

    @property
    def is_done(self):
        return all(b.is_done for b in self.beams)

    def __getitem__(self, i):
        return self.beams[i]

    def __len__(self):
        return len(self.beams)

    def advance(self, scores, follow_gold=False):
        cdef Beam beam
        for i, beam in enumerate(self.beams):
            if beam.is_done:
                continue
            self._set_scores(beam, scores[i])
            if self.golds is not None:
                self._set_costs(beam, self.golds[i], follow_gold=follow_gold)
            if follow_gold:
                assert self.golds is not None
                beam.advance(_transition_state, NULL, <void*>self.moves.c)
            else:
                beam.advance(_transition_state, _hash_state, <void*>self.moves.c)
            beam.check_done(_check_final_state, NULL)

    def _set_scores(self, Beam beam, float[:, ::1] scores):
        cdef float* c_scores = &scores[0, 0]
        for i in range(beam.size):
            state = <StateClass>beam.at(i)
            if not state.is_final():
                for j in range(beam.nr_class):
                    beam.scores[i][j] = c_scores[i * beam.nr_class + j]
                self.moves.set_valid(beam.is_valid[i], state.c)

    def _set_costs(self, Beam beam, GoldParse gold, int follow_gold=False):
        for i in range(beam.size):
            state = <StateClass>beam.at(i)
            if not state.c.is_final():
                self.moves.set_costs(beam.is_valid[i], beam.costs[i], state, gold)
                if follow_gold:
                    for j in range(beam.nr_class):
                        if beam.costs[i][j] >= 1:
                            beam.is_valid[i][j] = 0


def is_gold(StateClass state, GoldParse gold, strings):
    predicted = set()
    truth = set()
    for i in range(gold.length):
        if gold.cand_to_gold[i] is None:
            continue
        if state.safe_get(i).dep:
            predicted.add((i, state.H(i), strings[state.safe_get(i).dep]))
        else:
            predicted.add((i, state.H(i), 'ROOT'))
        id_, word, tag, head, dep, ner = gold.orig_annot[gold.cand_to_gold[i]]
        truth.add((id_, head, dep))
    return truth == predicted


def get_token_ids(states, int n_tokens):
    cdef StateClass state
    cdef np.ndarray ids = numpy.zeros((len(states), n_tokens),
                                      dtype='int32', order='C')
    c_ids = <int*>ids.data
    for i, state in enumerate(states):
        if not state.is_final():
            state.c.set_context_tokens(c_ids, n_tokens)
        else:
            ids[i] = -1
        c_ids += ids.shape[1]
    return ids

nr_update = 0
def update_beam(TransitionSystem moves, int nr_feature, int max_steps,
                states, tokvecs, golds,
                state2vec, vec2scores, drop=0., sgd=None,
                losses=None, int width=4, float density=0.001):
    global nr_update
    nr_update += 1
    pbeam = ParserBeam(moves, states, golds,
                       width=width, density=density)
    gbeam = ParserBeam(moves, states, golds,
                       width=width, density=0.0)
    beam_maps = []
    backprops = []
    violns = [MaxViolation() for _ in range(len(states))]
    for t in range(max_steps):
        beam_maps.append({})
        states, p_indices, g_indices = get_states(pbeam, gbeam, beam_maps[-1], nr_update)
        if not states:
            break
        token_ids = get_token_ids(states, nr_feature)
        vectors, bp_vectors = state2vec.begin_update(token_ids, drop=drop)
        scores, bp_scores = vec2scores.begin_update(vectors, drop=drop)

        backprops.append((token_ids, bp_vectors, bp_scores))

        p_scores = [numpy.ascontiguousarray(scores[indices], dtype='f') for indices in p_indices]
        g_scores = [numpy.ascontiguousarray(scores[indices], dtype='f')  for indices in g_indices]
        pbeam.advance(p_scores)
        gbeam.advance(g_scores, follow_gold=True)

        for i, violn in enumerate(violns):
            violn.check_crf(pbeam[i], gbeam[i])

    histories = [(v.p_hist + v.g_hist) for v in violns]
    losses = [(v.p_probs + v.g_probs) for v in violns]
    states_d_scores = get_gradient(moves.n_moves, beam_maps,
                                   histories, losses)
    return states_d_scores, backprops


def get_states(pbeams, gbeams, beam_map, nr_update):
    seen = {}
    states = []
    p_indices = []
    g_indices = []
    cdef Beam pbeam, gbeam
    for eg_id, (pbeam, gbeam) in enumerate(zip(pbeams, gbeams)):
        p_indices.append([])
        for i in range(pbeam.size):
            state = <StateClass>pbeam.at(i)
            if not state.is_final():
                key = tuple([eg_id] + pbeam.histories[i])
                seen[key] = len(states)
                p_indices[-1].append(len(states))
                states.append(<StateClass>pbeam.at(i))
        beam_map.update(seen)
        g_indices.append([])
        for i in range(gbeam.size):
            state = <StateClass>gbeam.at(i)
            if not state.is_final():
                key = tuple([eg_id] + gbeam.histories[i])
                if key in seen:
                    g_indices[-1].append(seen[key])
                else:
                    g_indices[-1].append(len(states))
                    beam_map[key] = len(states)
                    states.append(<StateClass>gbeam.at(i))
    p_indices = [numpy.asarray(idx, dtype='i') for idx in p_indices]
    g_indices = [numpy.asarray(idx, dtype='i') for idx in g_indices]
    return states, p_indices, g_indices


def get_gradient(nr_class, beam_maps, histories, losses):
    """
    The global model assigns a loss to each parse. The beam scores
    are additive, so the same gradient is applied to each action
    in the history. This gives the gradient of a single *action*
    for a beam state -- so we have "the gradient of loss for taking
    action i given history H."

    Histories: Each hitory is a list of actions
    Each candidate has a history
    Each beam has multiple candidates
    Each batch has multiple beams
    So history is list of lists of lists of ints
    """
    nr_step = len(beam_maps)
    grads = []
    for beam_map in beam_maps:
        grads.append(numpy.zeros((max(beam_map.values())+1, nr_class), dtype='f'))
    assert len(histories) == len(losses)
    for eg_id, hists in enumerate(histories):
        for loss, hist in zip(losses[eg_id], hists):
            key = tuple([eg_id])
            for j, clas in enumerate(hist):
                try:
                    i = beam_maps[j][key]
                except:
                    print(sorted(beam_maps[j].items()))
                    raise
                # In step j, at state i action clas
                # resulted in loss
                grads[j][i, clas] += loss
                key = key + tuple([clas])
    return grads


