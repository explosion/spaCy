# cython: infer_types=True
# cython: cdivision=True
# cython: boundscheck=False
# cython: profile=True
# coding: utf-8
from __future__ import unicode_literals, print_function

from collections import OrderedDict
import ujson
import json
import numpy
cimport cython.parallel
import cytoolz
import numpy.random
cimport numpy as np
from cpython.ref cimport PyObject, Py_XDECREF
from cpython.exc cimport PyErr_CheckSignals, PyErr_SetFromErrno
from libc.math cimport exp
from libcpp.vector cimport vector
from libc.string cimport memset, memcpy
from libc.stdlib cimport calloc, free
from cymem.cymem cimport Pool
from thinc.typedefs cimport weight_t, class_t, hash_t
from thinc.extra.search cimport Beam
from thinc.api import chain, clone
from thinc.v2v import Model, Maxout, Affine
from thinc.misc import LayerNorm
from thinc.neural.ops import CupyOps
from thinc.neural.util import get_array_module
from thinc.linalg cimport Vec, VecVec

from .._ml import zero_init, PrecomputableAffine, Tok2Vec, flatten
from .._ml import link_vectors_to_models, create_default_optimizer
from ..compat import json_dumps, copy_array
from ..tokens.doc cimport Doc
from ..gold cimport GoldParse
from ..errors import Errors, TempErrors
from .. import util
from .stateclass cimport StateClass
from ._state cimport StateC
from .transition_system cimport Transition
from . import _beam_utils, nonproj


def get_templates(*args, **kwargs):
    return []


DEBUG = False


def set_debug(val):
    global DEBUG
    DEBUG = val


cdef class precompute_hiddens:
    """Allow a model to be "primed" by pre-computing input features in bulk.

    This is used for the parser, where we want to take a batch of documents,
    and compute vectors for each (token, position) pair. These vectors can then
    be reused, especially for beam-search.

    Let's say we're using 12 features for each state, e.g. word at start of
    buffer, three words on stack, their children, etc. In the normal arc-eager
    system, a document of length N is processed in 2*N states. This means we'll
    create 2*N*12 feature vectors --- but if we pre-compute, we only need
    N*12 vector computations. The saving for beam-search is much better:
    if we have a beam of k, we'll normally make 2*N*12*K computations --
    so we can save the factor k. This also gives a nice CPU/GPU division:
    we can do all our hard maths up front, packed into large multiplications,
    and do the hard-to-program parsing on the CPU.
    """
    cdef int nF, nO, nP
    cdef bint _is_synchronized
    cdef public object ops
    cdef np.ndarray _features
    cdef np.ndarray _cached
    cdef np.ndarray bias
    cdef object _cuda_stream
    cdef object _bp_hiddens

    def __init__(self, batch_size, tokvecs, lower_model, cuda_stream=None,
                 drop=0.):
        gpu_cached, bp_features = lower_model.begin_update(tokvecs, drop=drop)
        cdef np.ndarray cached
        if not isinstance(gpu_cached, numpy.ndarray):
            # Note the passing of cuda_stream here: it lets
            # cupy make the copy asynchronously.
            # We then have to block before first use.
            cached = gpu_cached.get(stream=cuda_stream)
        else:
            cached = gpu_cached
        if not isinstance(lower_model.b, numpy.ndarray):
            self.bias = lower_model.b.get()
        else:
            self.bias = lower_model.b
        self.nF = cached.shape[1]
        self.nP = getattr(lower_model, 'nP', 1)
        self.nO = cached.shape[2]
        self.ops = lower_model.ops
        self._is_synchronized = False
        self._cuda_stream = cuda_stream
        self._cached = cached
        self._bp_hiddens = bp_features

    cdef const float* get_feat_weights(self) except NULL:
        if not self._is_synchronized and self._cuda_stream is not None:
            self._cuda_stream.synchronize()
            self._is_synchronized = True
        return <float*>self._cached.data

    def __call__(self, X):
        return self.begin_update(X)[0]

    def begin_update(self, token_ids, drop=0.):
        cdef np.ndarray state_vector = numpy.zeros(
            (token_ids.shape[0], self.nO, self.nP), dtype='f')
        # This is tricky, but (assuming GPU available);
        # - Input to forward on CPU
        # - Output from forward on CPU
        # - Input to backward on GPU!
        # - Output from backward on GPU
        bp_hiddens = self._bp_hiddens

        feat_weights = self.get_feat_weights()
        cdef int[:, ::1] ids = token_ids
        sum_state_features(<float*>state_vector.data,
            feat_weights, &ids[0,0],
            token_ids.shape[0], self.nF, self.nO*self.nP)
        state_vector += self.bias
        state_vector, bp_nonlinearity = self._nonlinearity(state_vector)

        def backward(d_state_vector_ids, sgd=None):
            d_state_vector, token_ids = d_state_vector_ids
            d_state_vector = bp_nonlinearity(d_state_vector, sgd)
            # This will usually be on GPU
            if not isinstance(d_state_vector, self.ops.xp.ndarray):
                d_state_vector = self.ops.xp.array(d_state_vector)
            d_tokens = bp_hiddens((d_state_vector, token_ids), sgd)
            return d_tokens
        return state_vector, backward

    def _nonlinearity(self, state_vector):
        if self.nP == 1:
            state_vector = state_vector.reshape(state_vector.shape[:-1])
            mask = state_vector >= 0.
            state_vector *= mask
        else:
            state_vector, mask = self.ops.maxout(state_vector)

        def backprop_nonlinearity(d_best, sgd=None):
            if self.nP == 1:
                d_best *= mask
                d_best = d_best.reshape((d_best.shape + (1,)))
                return d_best
            else:
                return self.ops.backprop_maxout(d_best, mask, self.nP)
        return state_vector, backprop_nonlinearity


cdef void sum_state_features(float* output,
        const float* cached, const int* token_ids, int B, int F, int O) nogil:
    cdef int idx, b, f, i
    cdef const float* feature
    padding = cached
    cached += F * O
    for b in range(B):
        for f in range(F):
            if token_ids[f] < 0:
                feature = &padding[f*O]
            else:
                idx = token_ids[f] * F * O + f*O
                feature = &cached[idx]
            for i in range(O):
                output[i] += feature[i]
        output += O
        token_ids += F


cdef void cpu_log_loss(float* d_scores,
        const float* costs, const int* is_valid, const float* scores,
        int O) nogil:
    """Do multi-label log loss"""
    cdef double max_, gmax, Z, gZ
    best = arg_max_if_gold(scores, costs, is_valid, O)
    guess = arg_max_if_valid(scores, is_valid, O)
    Z = 1e-10
    gZ = 1e-10
    max_ = scores[guess]
    gmax = scores[best]
    for i in range(O):
        if is_valid[i]:
            Z += exp(scores[i] - max_)
            if costs[i] <= costs[best]:
                gZ += exp(scores[i] - gmax)
    for i in range(O):
        if not is_valid[i]:
            d_scores[i] = 0.
        elif costs[i] <= costs[best]:
            d_scores[i] = (exp(scores[i]-max_) / Z) - (exp(scores[i]-gmax)/gZ)
        else:
            d_scores[i] = exp(scores[i]-max_) / Z


cdef void cpu_regression_loss(float* d_scores,
        const float* costs, const int* is_valid, const float* scores,
        int O) nogil:
    cdef float eps = 2.
    best = arg_max_if_gold(scores, costs, is_valid, O)
    for i in range(O):
        if not is_valid[i]:
            d_scores[i] = 0.
        elif scores[i] < scores[best]:
            d_scores[i] = 0.
        else:
            # I doubt this is correct?
            # Looking for something like Huber loss
            diff = scores[i] - -costs[i]
            if diff > eps:
                d_scores[i] = eps
            elif diff < -eps:
                d_scores[i] = -eps
            else:
                d_scores[i] = diff


def _collect_states(beams):
    cdef StateClass state
    cdef Beam beam
    states = []
    for beam in beams:
        state = StateClass.borrow(<StateC*>beam.at(0))
        states.append(state)
    return states


cdef class Parser:
    """
    Base class of the DependencyParser and EntityRecognizer.
    """
    @classmethod
    def Model(cls, nr_class, **cfg):
        depth = util.env_opt('parser_hidden_depth', cfg.get('hidden_depth', 1))
        if depth != 1:
            raise ValueError(TempErrors.T004.format(value=depth))
        parser_maxout_pieces = util.env_opt('parser_maxout_pieces',
                                            cfg.get('maxout_pieces', 2))
        token_vector_width = util.env_opt('token_vector_width',
                                           cfg.get('token_vector_width', 128))
        hidden_width = util.env_opt('hidden_width', cfg.get('hidden_width', 200))
        embed_size = util.env_opt('embed_size', cfg.get('embed_size', 7000))
        hist_size = util.env_opt('history_feats', cfg.get('hist_size', 0))
        hist_width = util.env_opt('history_width', cfg.get('hist_width', 0))
        if hist_size != 0:
            raise ValueError(TempErrors.T005.format(value=hist_size))
        if hist_width != 0:
            raise ValueError(TempErrors.T006.format(value=hist_width))
        pretrained_vectors = cfg.get('pretrained_vectors', None)
        tok2vec = Tok2Vec(token_vector_width, embed_size,
                          pretrained_vectors=pretrained_vectors)
        tok2vec = chain(tok2vec, flatten)
        lower = PrecomputableAffine(hidden_width,
                    nF=cls.nr_feature, nI=token_vector_width,
                    nP=parser_maxout_pieces)
        lower.nP = parser_maxout_pieces

        with Model.use_device('cpu'):
            upper = chain(
                clone(LayerNorm(Maxout(hidden_width, hidden_width)), depth-1),
                zero_init(Affine(nr_class, hidden_width, drop_factor=0.0))
            )

        cfg = {
            'nr_class': nr_class,
            'hidden_depth': depth,
            'token_vector_width': token_vector_width,
            'hidden_width': hidden_width,
            'maxout_pieces': parser_maxout_pieces,
            'pretrained_vectors': pretrained_vectors,
            'hist_size': hist_size,
            'hist_width': hist_width
        }
        return (tok2vec, lower, upper), cfg

    def create_optimizer(self):
        return create_default_optimizer(self.model[0].ops,
                                        **self.cfg.get('optimizer', {}))

    def __init__(self, Vocab vocab, moves=True, model=True, **cfg):
        """Create a Parser.

        vocab (Vocab): The vocabulary object. Must be shared with documents
            to be processed. The value is set to the `.vocab` attribute.
        moves (TransitionSystem): Defines how the parse-state is created,
            updated and evaluated. The value is set to the .moves attribute
            unless True (default), in which case a new instance is created with
            `Parser.Moves()`.
        model (object): Defines how the parse-state is created, updated and
            evaluated. The value is set to the .model attribute. If set to True
            (default), a new instance will be created with `Parser.Model()`
            in parser.begin_training(), parser.from_disk() or parser.from_bytes().
        **cfg: Arbitrary configuration parameters. Set to the `.cfg` attribute
        """
        self.vocab = vocab
        if moves is True:
            self.moves = self.TransitionSystem(self.vocab.strings, {})
        else:
            self.moves = moves
        if 'beam_width' not in cfg:
            cfg['beam_width'] = util.env_opt('beam_width', 1)
        if 'beam_density' not in cfg:
            cfg['beam_density'] = util.env_opt('beam_density', 0.0)
        cfg.setdefault('cnn_maxout_pieces', 3)
        self.cfg = cfg
        if 'actions' in self.cfg:
            for action, labels in self.cfg.get('actions', {}).items():
                for label in labels:
                    self.moves.add_action(action, label)
        self.model = model
        self._multitasks = []

    def __reduce__(self):
        return (Parser, (self.vocab, self.moves, self.model), None, None)

    def __call__(self, Doc doc, beam_width=None, beam_density=None):
        """Apply the parser or entity recognizer, setting the annotations onto
        the `Doc` object.

        doc (Doc): The document to be processed.
        """
        if beam_width is None:
            beam_width = self.cfg.get('beam_width', 1)
        if beam_density is None:
            beam_density = self.cfg.get('beam_density', 0.0)
        cdef Beam beam
        if beam_width == 1:
            states, tokvecs = self.parse_batch([doc])
            self.set_annotations([doc], states, tensors=tokvecs)
            return doc
        else:
            beams, tokvecs = self.beam_parse([doc],
                                beam_width=beam_width,
                                beam_density=beam_density)
            beam = beams[0]
            output = self.moves.get_beam_annot(beam)
            state = StateClass.borrow(<StateC*>beam.at(0))
            self.set_annotations([doc], [state], tensors=tokvecs)
            _cleanup(beam)
            return output

    def pipe(self, docs, int batch_size=256, int n_threads=2,
             beam_width=None, beam_density=None):
        """Process a stream of documents.

        stream: The sequence of documents to process.
        batch_size (int): Number of documents to accumulate into a working set.
        n_threads (int): The number of threads with which to work on the buffer
            in parallel.
        YIELDS (Doc): Documents, in order.
        """
        if beam_width is None:
            beam_width = self.cfg.get('beam_width', 1)
        if beam_density is None:
            beam_density = self.cfg.get('beam_density', 0.0)
        cdef Doc doc
        for batch in cytoolz.partition_all(batch_size, docs):
            batch_in_order = list(batch)
            by_length = sorted(batch_in_order, key=lambda doc: len(doc))
            batch_beams = []
            for subbatch in cytoolz.partition_all(8, by_length):
                subbatch = list(subbatch)
                if beam_width == 1:
                    parse_states, tokvecs = self.parse_batch(subbatch)
                    beams = []
                else:
                    beams, tokvecs = self.beam_parse(subbatch,
                                        beam_width=beam_width,
                                        beam_density=beam_density)
                    parse_states = _collect_states(beams)
                self.set_annotations(subbatch, parse_states, tensors=None)
                for beam in beams:
                    _cleanup(beam)
            for doc in batch_in_order:
                yield doc

    def parse_batch(self, docs):
        cdef:
            precompute_hiddens state2vec
            Pool mem
            const float* feat_weights
            StateC* st
            StateClass stcls
            vector[StateC*] states
            int guess, nr_class, nr_feat, nr_piece, nr_dim, nr_state, nr_step
            int j
        if isinstance(docs, Doc):
            docs = [docs]

        cuda_stream = util.get_cuda_stream()
        (tokvecs, bp_tokvecs), state2vec, vec2scores = self.get_batch_model(
            docs, cuda_stream, 0.0)
        nr_state = len(docs)
        nr_class = self.moves.n_moves
        nr_dim = tokvecs.shape[1]
        nr_feat = self.nr_feature
        nr_piece = state2vec.nP

        state_objs = self.moves.init_batch(docs)
        for stcls in state_objs:
            if not stcls.c.is_final():
                states.push_back(stcls.c)

        feat_weights = state2vec.get_feat_weights()
        cdef int i
        cdef np.ndarray hidden_weights = numpy.ascontiguousarray(
            vec2scores._layers[-1].W.T)
        cdef np.ndarray hidden_bias = vec2scores._layers[-1].b

        hW = <float*>hidden_weights.data
        hb = <float*>hidden_bias.data
        bias = <float*>state2vec.bias.data
        cdef int nr_hidden = hidden_weights.shape[0]
        cdef int nr_task = states.size()
        with nogil:
            for i in range(nr_task):
                self._parseC(states[i],
                    feat_weights, bias, hW, hb,
                    nr_class, nr_hidden, nr_feat, nr_piece)
        PyErr_CheckSignals()
        tokvecs = self.model[0].ops.unflatten(tokvecs,
                                    [len(doc) for doc in docs])
        return state_objs, tokvecs

    cdef void _parseC(self, StateC* state,
            const float* feat_weights, const float* bias,
            const float* hW, const float* hb,
            int nr_class, int nr_hidden, int nr_feat, int nr_piece) nogil:
        token_ids = <int*>calloc(nr_feat, sizeof(int))
        is_valid = <int*>calloc(nr_class, sizeof(int))
        vectors = <float*>calloc(nr_hidden * nr_piece, sizeof(float))
        scores = <float*>calloc(nr_class, sizeof(float))
        if not (token_ids and is_valid and vectors and scores):
            with gil:
                PyErr_SetFromErrno(MemoryError)
                PyErr_CheckSignals()
        cdef float feature
        while not state.is_final():
            state.set_context_tokens(token_ids, nr_feat)
            memset(vectors, 0, nr_hidden * nr_piece * sizeof(float))
            memset(scores, 0, nr_class * sizeof(float))
            sum_state_features(vectors,
                feat_weights, token_ids, 1, nr_feat, nr_hidden * nr_piece)
            for i in range(nr_hidden * nr_piece):
                vectors[i] += bias[i]
            V = vectors
            W = hW
            for i in range(nr_hidden):
                if nr_piece == 1:
                    feature = V[0] if V[0] >= 0. else 0.
                elif nr_piece == 2:
                    feature = V[0] if V[0] >= V[1] else V[1]
                else:
                    feature = Vec.max(V, nr_piece)
                for j in range(nr_class):
                    scores[j] += feature * W[j]
                W += nr_class
                V += nr_piece
            for i in range(nr_class):
                scores[i] += hb[i]
            self.moves.set_valid(is_valid, state)
            guess = arg_max_if_valid(scores, is_valid, nr_class)
            action = self.moves.c[guess]
            action.do(state, action.label)
            state.push_hist(guess)
        free(token_ids)
        free(is_valid)
        free(vectors)
        free(scores)

    def beam_parse(self, docs, int beam_width=3, float beam_density=0.001):
        cdef Beam beam
        cdef np.ndarray scores
        cdef Doc doc
        cdef int nr_class = self.moves.n_moves
        cuda_stream = util.get_cuda_stream()
        (tokvecs, bp_tokvecs), state2vec, vec2scores = self.get_batch_model(
            docs, cuda_stream, 0.0)
        cdef int offset = 0
        cdef int j = 0
        cdef int k

        beams = []
        for doc in docs:
            beam = Beam(nr_class, beam_width, min_density=beam_density)
            beam.initialize(self.moves.init_beam_state, doc.length, doc.c)
            for i in range(beam.width):
                state = <StateC*>beam.at(i)
                state.offset = offset
            offset += len(doc)
            beam.check_done(_check_final_state, NULL)
            beams.append(beam)
        cdef np.ndarray token_ids
        token_ids = numpy.zeros((len(docs) * beam_width, self.nr_feature),
                                 dtype='i', order='C')
        todo = [beam for beam in beams if not beam.is_done]

        cdef int* c_ids
        cdef int nr_feature = self.nr_feature
        cdef int n_states
        while todo:
            todo = [beam for beam in beams if not beam.is_done]
            token_ids.fill(-1)
            c_ids = <int*>token_ids.data
            n_states = 0
            for beam in todo:
                for i in range(beam.size):
                    state = <StateC*>beam.at(i)
                    # This way we avoid having to score finalized states
                    # We do have to take care to keep indexes aligned, though
                    if not state.is_final():
                        state.set_context_tokens(c_ids, nr_feature)
                        c_ids += nr_feature
                        n_states += 1
            if n_states == 0:
                break
            vectors = state2vec(token_ids[:n_states])
            scores = vec2scores(vectors)
            c_scores = <float*>scores.data
            for beam in todo:
                for i in range(beam.size):
                    state = <StateC*>beam.at(i)
                    if not state.is_final():
                        self.moves.set_valid(beam.is_valid[i], state)
                        memcpy(beam.scores[i], c_scores, nr_class * sizeof(float))
                        c_scores += nr_class
                beam.advance(_transition_state, NULL, <void*>self.moves.c)
                beam.check_done(_check_final_state, NULL)
        tokvecs = self.model[0].ops.unflatten(tokvecs,
                                    [len(doc) for doc in docs])
        return beams, tokvecs

    def update(self, docs, golds, drop=0., sgd=None, losses=None):
        if not any(self.moves.has_gold(gold) for gold in golds):
            return None
        if len(docs) != len(golds):
            raise ValueError(Errors.E077.format(value='update', n_docs=len(docs),
                                                n_golds=len(golds)))
        # The probability we use beam update, instead of falling back to
        # a greedy update
        beam_update_prob = 1-self.cfg.get('beam_update_prob', 0.5)
        if self.cfg.get('beam_width', 1) >= 2 and numpy.random.random() >= beam_update_prob:
            return self.update_beam(docs, golds,
                    self.cfg['beam_width'], self.cfg['beam_density'],
                    drop=drop, sgd=sgd, losses=losses)
        if losses is not None and self.name not in losses:
            losses[self.name] = 0.
        if isinstance(docs, Doc) and isinstance(golds, GoldParse):
            docs = [docs]
            golds = [golds]
        for multitask in self._multitasks:
            multitask.update(docs, golds, drop=drop, sgd=sgd)
        cuda_stream = util.get_cuda_stream()
        states, golds, max_steps = self._init_gold_batch(docs, golds)
        (tokvecs, bp_tokvecs), state2vec, vec2scores = self.get_batch_model(docs, cuda_stream,
                                                                            drop)
        todo = [(s, g) for (s, g) in zip(states, golds)
                if not s.is_final() and g is not None]
        if not todo:
            return None

        backprops = []
        # Add a padding vector to the d_tokvecs gradient, so that missing
        # values don't affect the real gradient.
        d_tokvecs = state2vec.ops.allocate((tokvecs.shape[0]+1, tokvecs.shape[1]))
        cdef float loss = 0.
        n_steps = 0
        while todo:
            states, golds = zip(*todo)
            token_ids = self.get_token_ids(states)
            vector, bp_vector = state2vec.begin_update(token_ids, drop=0.0)
            if drop != 0:
                mask = vec2scores.ops.get_dropout_mask(vector.shape, drop)
                vector *= mask
            hists = numpy.asarray([st.history for st in states], dtype='i')
            if self.cfg.get('hist_size', 0):
                scores, bp_scores = vec2scores.begin_update((vector, hists), drop=drop)
            else:
                scores, bp_scores = vec2scores.begin_update(vector, drop=drop)

            d_scores = self.get_batch_loss(states, golds, scores)
            d_scores /= len(docs)
            d_vector = bp_scores(d_scores, sgd=sgd)
            if drop != 0:
                d_vector *= mask

            if isinstance(self.model[0].ops, CupyOps) \
            and not isinstance(token_ids, state2vec.ops.xp.ndarray):
                # Move token_ids and d_vector to GPU, asynchronously
                backprops.append((
                    util.get_async(cuda_stream, token_ids),
                    util.get_async(cuda_stream, d_vector),
                    bp_vector
                ))
            else:
                backprops.append((token_ids, d_vector, bp_vector))
            self.transition_batch(states, scores)
            todo = [(st, gold) for (st, gold) in todo
                    if not st.is_final()]
            if losses is not None:
                losses[self.name] += (d_scores**2).sum()
            n_steps += 1
            if n_steps >= max_steps:
                break
        self._make_updates(d_tokvecs,
            bp_tokvecs, backprops, sgd, cuda_stream)

    def update_beam(self, docs, golds, width=None, density=None,
            drop=0., sgd=None, losses=None):
        if not any(self.moves.has_gold(gold) for gold in golds):
            return None
        if not golds:
            return None
        if width is None:
            width = self.cfg.get('beam_width', 2)
        if density is None:
            density = self.cfg.get('beam_density', 0.0)
        if losses is not None and self.name not in losses:
            losses[self.name] = 0.
        lengths = [len(d) for d in docs]
        states = self.moves.init_batch(docs)
        for gold in golds:
            self.moves.preprocess_gold(gold)
        cuda_stream = util.get_cuda_stream()
        (tokvecs, bp_tokvecs), state2vec, vec2scores = self.get_batch_model(
            docs, cuda_stream, drop)
        states_d_scores, backprops, beams = _beam_utils.update_beam(
            self.moves, self.nr_feature, 500, states, golds, state2vec,
            vec2scores, width, density, self.cfg.get('hist_size', 0),
            drop=drop, losses=losses)
        backprop_lower = []
        cdef float batch_size = len(docs)
        for i, d_scores in enumerate(states_d_scores):
            d_scores /= batch_size
            if losses is not None:
                losses[self.name] += (d_scores**2).sum()
            ids, bp_vectors, bp_scores = backprops[i]
            d_vector = bp_scores(d_scores, sgd=sgd)
            if isinstance(self.model[0].ops, CupyOps) \
            and not isinstance(ids, state2vec.ops.xp.ndarray):
                backprop_lower.append((
                    util.get_async(cuda_stream, ids),
                    util.get_async(cuda_stream, d_vector),
                    bp_vectors))
            else:
                backprop_lower.append((ids, d_vector, bp_vectors))
        # Add a padding vector to the d_tokvecs gradient, so that missing
        # values don't affect the real gradient.
        d_tokvecs = state2vec.ops.allocate((tokvecs.shape[0]+1, tokvecs.shape[1]))
        self._make_updates(d_tokvecs, bp_tokvecs, backprop_lower, sgd,
                           cuda_stream)
        cdef Beam beam
        for beam in beams:
            _cleanup(beam)


    def _init_gold_batch(self, whole_docs, whole_golds):
        """Make a square batch, of length equal to the shortest doc. A long
        doc will get multiple states. Let's say we have a doc of length 2*N,
        where N is the shortest doc. We'll make two states, one representing
        long_doc[:N], and another representing long_doc[N:]."""
        cdef:
            StateClass state
            Transition action
        whole_states = self.moves.init_batch(whole_docs)
        max_length = max(5, min(50, min([len(doc) for doc in whole_docs])))
        max_moves = 0
        states = []
        golds = []
        for doc, state, gold in zip(whole_docs, whole_states, whole_golds):
            gold = self.moves.preprocess_gold(gold)
            if gold is None:
                continue
            oracle_actions = self.moves.get_oracle_sequence(doc, gold)
            start = 0
            while start < len(doc):
                state = state.copy()
                n_moves = 0
                while state.B(0) < start and not state.is_final():
                    action = self.moves.c[oracle_actions.pop(0)]
                    action.do(state.c, action.label)
                    state.c.push_hist(action.clas)
                    n_moves += 1
                has_gold = self.moves.has_gold(gold, start=start,
                                               end=start+max_length)
                if not state.is_final() and has_gold:
                    states.append(state)
                    golds.append(gold)
                    max_moves = max(max_moves, n_moves)
                start += min(max_length, len(doc)-start)
            max_moves = max(max_moves, len(oracle_actions))
        return states, golds, max_moves

    def _make_updates(self, d_tokvecs, bp_tokvecs, backprops, sgd, cuda_stream=None):
        # Tells CUDA to block, so our async copies complete.
        if cuda_stream is not None:
            cuda_stream.synchronize()
        xp = get_array_module(d_tokvecs)
        for ids, d_vector, bp_vector in backprops:
            d_state_features = bp_vector((d_vector, ids), sgd=sgd)
            ids = ids.flatten()
            d_state_features = d_state_features.reshape(
                (ids.size, d_state_features.shape[2]))
            self.model[0].ops.scatter_add(d_tokvecs, ids,
                d_state_features)
        # Padded -- see update()
        bp_tokvecs(d_tokvecs[:-1], sgd=sgd)

    @property
    def move_names(self):
        names = []
        for i in range(self.moves.n_moves):
            name = self.moves.move_name(self.moves.c[i].move, self.moves.c[i].label)
            names.append(name)
        return names

    def get_batch_model(self, docs, stream, dropout):
        tok2vec, lower, upper = self.model
        tokvecs, bp_tokvecs = tok2vec.begin_update(docs, drop=dropout)
        state2vec = precompute_hiddens(len(docs), tokvecs,
                                       lower, stream, drop=0.0)
        return (tokvecs, bp_tokvecs), state2vec, upper

    nr_feature = 13

    def get_token_ids(self, states):
        cdef StateClass state
        cdef int n_tokens = self.nr_feature
        cdef np.ndarray ids = numpy.zeros((len(states), n_tokens),
                                          dtype='i', order='C')
        c_ids = <int*>ids.data
        for i, state in enumerate(states):
            if not state.is_final():
                state.c.set_context_tokens(c_ids, n_tokens)
            c_ids += ids.shape[1]
        return ids

    def transition_batch(self, states, float[:, ::1] scores):
        cdef StateClass state
        cdef Pool mem = Pool()
        is_valid = <int*>mem.alloc(self.moves.n_moves, sizeof(int))
        cdef float* c_scores = &scores[0, 0]
        for state in states:
            self.moves.set_valid(is_valid, state.c)
            guess = arg_max_if_valid(c_scores, is_valid, scores.shape[1])
            action = self.moves.c[guess]
            action.do(state.c, action.label)
            c_scores += scores.shape[1]
            state.c.push_hist(guess)

    def get_batch_loss(self, states, golds, float[:, ::1] scores):
        cdef StateClass state
        cdef GoldParse gold
        cdef Pool mem = Pool()
        cdef int i
        is_valid = <int*>mem.alloc(self.moves.n_moves, sizeof(int))
        costs = <float*>mem.alloc(self.moves.n_moves, sizeof(float))
        cdef np.ndarray d_scores = numpy.zeros((len(states), self.moves.n_moves),
                                        dtype='f', order='C')
        c_d_scores = <float*>d_scores.data
        for i, (state, gold) in enumerate(zip(states, golds)):
            memset(is_valid, 0, self.moves.n_moves * sizeof(int))
            memset(costs, 0, self.moves.n_moves * sizeof(float))
            self.moves.set_costs(is_valid, costs, state, gold)
            cpu_log_loss(c_d_scores,
                costs, is_valid, &scores[i, 0], d_scores.shape[1])
            c_d_scores += d_scores.shape[1]
        return d_scores

    def set_annotations(self, docs, states, tensors=None):
        cdef StateClass state
        cdef Doc doc
        for i, (state, doc) in enumerate(zip(states, docs)):
            self.moves.finalize_state(state.c)
            for j in range(doc.length):
                doc.c[j] = state.c._sent[j]
            if tensors is not None:
                if isinstance(doc.tensor, numpy.ndarray) \
                and not isinstance(tensors[i], numpy.ndarray):
                    doc.extend_tensor(tensors[i].get())
                else:
                    doc.extend_tensor(tensors[i])
            self.moves.finalize_doc(doc)

            for hook in self.postprocesses:
                for doc in docs:
                    hook(doc)

    @property
    def tok2vec(self):
        '''Return the embedding and convolutional layer of the model.'''
        if self.model in (None, True, False):
            return None
        else:
            return self.model[0]

    @property
    def postprocesses(self):
        # Available for subclasses, e.g. to deprojectivize
        return []

    def add_label(self, label):
        resized = False
        for action in self.moves.action_types:
            added = self.moves.add_action(action, label)
            if added:
                # Important that the labels be stored as a list! We need the
                # order, or the model goes out of synch
                self.cfg.setdefault('extra_labels', []).append(label)
                resized = True
        if self.model not in (True, False, None) and resized:
            # Weights are stored in (nr_out, nr_in) format, so we're basically
            # just adding rows here.
            smaller = self.model[-1]._layers[-1]
            larger = Affine(self.moves.n_moves, smaller.nI)
            copy_array(larger.W[:smaller.nO], smaller.W)
            copy_array(larger.b[:smaller.nO], smaller.b)
            self.model[-1]._layers[-1] = larger

    def begin_training(self, gold_tuples, pipeline=None, sgd=None, **cfg):
        if 'model' in cfg:
            self.model = cfg['model']
        gold_tuples = nonproj.preprocess_training_data(gold_tuples,
                                                       label_freq_cutoff=100)
        actions = self.moves.get_actions(gold_parses=gold_tuples)
        for action, labels in actions.items():
            for label in labels:
                self.moves.add_action(action, label)
        cfg.setdefault('token_vector_width', 128)
        if self.model is True:
            self.model, cfg = self.Model(self.moves.n_moves, **cfg)
            if sgd is None:
                sgd = self.create_optimizer()
            self.model[1].begin_training(
                    self.model[1].ops.allocate((5, cfg['token_vector_width'])))
            if pipeline is not None:
                self.init_multitask_objectives(gold_tuples, pipeline, sgd=sgd, **cfg)
            link_vectors_to_models(self.vocab)
        else:
            if sgd is None:
                sgd = self.create_optimizer()
            self.model[1].begin_training(
                self.model[1].ops.allocate((5, cfg['token_vector_width'])))
        self.cfg.update(cfg)
        return sgd

    def add_multitask_objective(self, target):
        # Defined in subclasses, to avoid circular import
        raise NotImplementedError

    def init_multitask_objectives(self, gold_tuples, pipeline, **cfg):
        '''Setup models for secondary objectives, to benefit from multi-task
        learning. This method is intended to be overridden by subclasses.

        For instance, the dependency parser can benefit from sharing
        an input representation with a label prediction model. These auxiliary
        models are discarded after training.
        '''
        pass

    def preprocess_gold(self, docs_golds):
        for doc, gold in docs_golds:
            yield doc, gold

    def use_params(self, params):
        # Can't decorate cdef class :(. Workaround.
        with self.model[0].use_params(params):
            with self.model[1].use_params(params):
                yield

    def to_disk(self, path, **exclude):
        serializers = {
            'tok2vec_model': lambda p: p.open('wb').write(
                self.model[0].to_bytes()),
            'lower_model': lambda p: p.open('wb').write(
                self.model[1].to_bytes()),
            'upper_model': lambda p: p.open('wb').write(
                self.model[2].to_bytes()),
            'vocab': lambda p: self.vocab.to_disk(p),
            'moves': lambda p: self.moves.to_disk(p, strings=False),
            'cfg': lambda p: p.open('w').write(json_dumps(self.cfg))
        }
        util.to_disk(path, serializers, exclude)

    def from_disk(self, path, **exclude):
        deserializers = {
            'vocab': lambda p: self.vocab.from_disk(p),
            'moves': lambda p: self.moves.from_disk(p, strings=False),
            'cfg': lambda p: self.cfg.update(util.read_json(p)),
            'model': lambda p: None
        }
        util.from_disk(path, deserializers, exclude)
        if 'model' not in exclude:
            # TODO: Remove this once we don't have to handle previous models
            if self.cfg.get('pretrained_dims') and 'pretrained_vectors' not in self.cfg:
                self.cfg['pretrained_vectors'] = self.vocab.vectors.name
            path = util.ensure_path(path)
            if self.model is True:
                self.model, cfg = self.Model(**self.cfg)
            else:
                cfg = {}
            with (path / 'tok2vec_model').open('rb') as file_:
                bytes_data = file_.read()
            self.model[0].from_bytes(bytes_data)
            with (path / 'lower_model').open('rb') as file_:
                bytes_data = file_.read()
            self.model[1].from_bytes(bytes_data)
            with (path / 'upper_model').open('rb') as file_:
                bytes_data = file_.read()
            self.model[2].from_bytes(bytes_data)
            self.cfg.update(cfg)
        return self

    def to_bytes(self, **exclude):
        serializers = OrderedDict((
            ('tok2vec_model', lambda: self.model[0].to_bytes()),
            ('lower_model', lambda: self.model[1].to_bytes()),
            ('upper_model', lambda: self.model[2].to_bytes()),
            ('vocab', lambda: self.vocab.to_bytes()),
            ('moves', lambda: self.moves.to_bytes(strings=False)),
            ('cfg', lambda: json.dumps(self.cfg, indent=2, sort_keys=True))
        ))
        if 'model' in exclude:
            exclude['tok2vec_model'] = True
            exclude['lower_model'] = True
            exclude['upper_model'] = True
            exclude.pop('model')
        return util.to_bytes(serializers, exclude)

    def from_bytes(self, bytes_data, **exclude):
        deserializers = OrderedDict((
            ('vocab', lambda b: self.vocab.from_bytes(b)),
            ('moves', lambda b: self.moves.from_bytes(b, strings=False)),
            ('cfg', lambda b: self.cfg.update(json.loads(b))),
            ('tok2vec_model', lambda b: None),
            ('lower_model', lambda b: None),
            ('upper_model', lambda b: None)
        ))
        msg = util.from_bytes(bytes_data, deserializers, exclude)
        if 'model' not in exclude:
            # TODO: Remove this once we don't have to handle previous models
            if self.cfg.get('pretrained_dims') and 'pretrained_vectors' not in self.cfg:
                self.cfg['pretrained_vectors'] = self.vocab.vectors.name
            if self.model is True:
                self.model, cfg = self.Model(**self.cfg)
            else:
                cfg = {}
            if 'tok2vec_model' in msg:
                self.model[0].from_bytes(msg['tok2vec_model'])
            if 'lower_model' in msg:
                self.model[1].from_bytes(msg['lower_model'])
            if 'upper_model' in msg:
                self.model[2].from_bytes(msg['upper_model'])
            self.cfg.update(cfg)
        return self


class ParserStateError(ValueError):
    def __init__(self, doc):
        ValueError.__init__(self,
            "Error analysing doc -- no valid actions available. This should "
            "never happen, so please report the error on the issue tracker. "
            "Here's the thread to do so --- reopen it if it's closed:\n"
            "https://github.com/spacy-io/spaCy/issues/429\n"
            "Please include the text that the parser failed on, which is:\n"
            "%s" % repr(doc.text))


cdef int arg_max_if_gold(const weight_t* scores, const weight_t* costs, const int* is_valid, int n) nogil:
    # Find minimum cost
    cdef float cost = 1
    for i in range(n):
        if is_valid[i] and costs[i] < cost:
            cost = costs[i]
    # Now find best-scoring with that cost
    cdef int best = -1
    for i in range(n):
        if costs[i] <= cost and is_valid[i]:
            if best == -1 or scores[i] > scores[best]:
                best = i
    return best


cdef int arg_max_if_valid(const weight_t* scores, const int* is_valid, int n) nogil:
    cdef int best = -1
    for i in range(n):
        if is_valid[i] >= 1:
            if best == -1 or scores[i] > scores[best]:
                best = i
    return best


# These are passed as callbacks to thinc.search.Beam
cdef int _transition_state(void* _dest, void* _src, class_t clas, void* _moves) except -1:
    dest = <StateC*>_dest
    src = <StateC*>_src
    moves = <const Transition*>_moves
    dest.clone(src)
    moves[clas].do(dest, moves[clas].label)
    dest.push_hist(clas)


cdef int _check_final_state(void* _state, void* extra_args) except -1:
    state = <StateC*>_state
    return state.is_final()


def _cleanup(Beam beam):
    cdef StateC* state
    # Once parsing has finished, states in beam may not be unique. Is this
    # correct?
    seen = set()
    for i in range(beam.width):
        addr = <size_t>beam._parents[i].content
        if addr not in seen:
            state = <StateC*>addr
            del state
            seen.add(addr)
        else:
            raise ValueError(Errors.E023.format(addr=addr, i=i))
        addr = <size_t>beam._states[i].content
        if addr not in seen:
            state = <StateC*>addr
            del state
            seen.add(addr)
        else:
            raise ValueError(Errors.E023.format(addr=addr, i=i))
