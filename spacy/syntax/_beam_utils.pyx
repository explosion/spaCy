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
            for i in range(beam.width):
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
            if beam.is_done or not scores[i].size:
                continue
            self._set_scores(beam, scores[i])
            if self.golds is not None:
                self._set_costs(beam, self.golds[i], follow_gold=follow_gold)
            beam.advance(_transition_state, NULL, <void*>self.moves.c)
            beam.check_done(_check_final_state, NULL)
            if beam.is_done:
                for j in range(beam.size):
                    if is_gold(<StateClass>beam.at(j), self.golds[i], self.moves.strings):
                        beam._states[j].loss = 0.0
                    elif beam._states[j].loss == 0.0:
                        beam._states[j].loss = 1.0

    def _set_scores(self, Beam beam, float[:, ::1] scores):
        cdef float* c_scores = &scores[0, 0]
        cdef int nr_state = min(scores.shape[0], beam.size)
        cdef int nr_class = scores.shape[1]
        for i in range(nr_state):
            state = <StateClass>beam.at(i)
            if not state.is_final():
                for j in range(nr_class):
                    beam.scores[i][j] = c_scores[i * nr_class + j]
                self.moves.set_valid(beam.is_valid[i], state.c)
            else:
                for j in range(beam.nr_class):
                    beam.scores[i][j] = 0
                    beam.costs[i][j] = 0


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
    cdef StateClass state
    beam_maps = []
    backprops = []
    violns = [MaxViolation() for _ in range(len(states))]
    for t in range(max_steps):
        # The beam maps let us find the right row in the flattened scores
        # arrays for each state. States are identified by (example id, history).
        # We keep a different beam map for each step (since we'll have a flat
        # scores array for each step). The beam map will let us take the per-state
        # losses, and compute the gradient for each (step, state, class).
        beam_maps.append({})
        # Gather all states from the two beams in a list. Some stats may occur
        # in both beams. To figure out which beam each state belonged to,
        # we keep two lists of indices, p_indices and g_indices
        states, p_indices, g_indices = get_states(pbeam, gbeam, beam_maps[-1], nr_update)
        if not states:
            break
        # Now that we have our flat list of states, feed them through the model
        token_ids = get_token_ids(states, nr_feature)
        vectors, bp_vectors = state2vec.begin_update(token_ids, drop=drop)
        scores, bp_scores = vec2scores.begin_update(vectors, drop=drop)

        # Store the callbacks for the backward pass
        backprops.append((token_ids, bp_vectors, bp_scores))

        # Unpack the flat scores into lists for the two beams. The indices arrays
        # tell us which example and state the scores-row refers to.
        p_scores = [numpy.ascontiguousarray(scores[indices], dtype='f') for indices in p_indices]
        g_scores = [numpy.ascontiguousarray(scores[indices], dtype='f')  for indices in g_indices]
        # Now advance the states in the beams. The gold beam is contrained to
        # to follow only gold analyses.
        pbeam.advance(p_scores)
        gbeam.advance(g_scores, follow_gold=True)
        # Track the "maximum violation", to use in the update.
        for i, violn in enumerate(violns):
            violn.check_crf(pbeam[i], gbeam[i])

    # Only make updates if we have non-gold states
    histories = [((v.p_hist + v.g_hist) if v.p_hist else []) for v in violns]
    losses = [((v.p_probs + v.g_probs) if v.p_probs else []) for v in violns]
    states_d_scores = get_gradient(moves.n_moves, beam_maps,
                                   histories, losses)
    return states_d_scores, backprops[:len(states_d_scores)]


def get_states(pbeams, gbeams, beam_map, nr_update):
    seen = {}
    states = []
    p_indices = []
    g_indices = []
    cdef Beam pbeam, gbeam
    assert len(pbeams) == len(gbeams)
    for eg_id, (pbeam, gbeam) in enumerate(zip(pbeams, gbeams)):
        p_indices.append([])
        g_indices.append([])
        if pbeam.loss > 0 and pbeam.min_score > (gbeam.score + nr_update):
            continue
        for i in range(pbeam.size):
            state = <StateClass>pbeam.at(i)
            if not state.is_final():
                key = tuple([eg_id] + pbeam.histories[i])
                assert key not in seen, (key, seen)
                seen[key] = len(states)
                p_indices[-1].append(len(states))
                states.append(state)
        beam_map.update(seen)
        for i in range(gbeam.size):
            state = <StateClass>gbeam.at(i)
            if not state.is_final():
                key = tuple([eg_id] + gbeam.histories[i])
                if key in seen:
                    g_indices[-1].append(seen[key])
                else:
                    g_indices[-1].append(len(states))
                    beam_map[key] = len(states)
                    states.append(state)
    p_idx = [numpy.asarray(idx, dtype='i') for idx in p_indices]
    g_idx = [numpy.asarray(idx, dtype='i') for idx in g_indices]
    return states, p_idx, g_idx


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
    nr_step = 0
    for eg_id, hists in enumerate(histories):
        for loss, hist in zip(losses[eg_id], hists):
            if abs(loss) >= 0.0001 and not numpy.isnan(loss):
                nr_step = max(nr_step, len(hist))
    for i in range(nr_step):
        grads.append(numpy.zeros((max(beam_maps[i].values())+1, nr_class), dtype='f'))
    assert len(histories) == len(losses)
    for eg_id, hists in enumerate(histories):
        for loss, hist in zip(losses[eg_id], hists):
            if abs(loss) < 0.0001 or numpy.isnan(loss):
                continue
            key = tuple([eg_id])
            for j, clas in enumerate(hist):
                i = beam_maps[j][key]
                # In step j, at state i action clas
                # resulted in loss
                grads[j][i, clas] += loss / len(histories)
                key = key + tuple([clas])
    return grads


