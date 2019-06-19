# cython: infer_types=True
# cython: cdivision=True
# cython: boundscheck=False
# coding: utf-8
from __future__ import unicode_literals, print_function

from collections import OrderedDict
import numpy
cimport cython.parallel
import numpy.random
cimport numpy as np
from itertools import islice
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
import srsly

from ._parser_model cimport resize_activations, predict_states, arg_max_if_valid
from ._parser_model cimport WeightsC, ActivationsC, SizesC, cpu_log_loss
from ._parser_model cimport get_c_weights, get_c_sizes
from ._parser_model import ParserModel
from .._ml import zero_init, PrecomputableAffine, Tok2Vec, flatten
from .._ml import link_vectors_to_models, create_default_optimizer
from ..compat import copy_array
from ..tokens.doc cimport Doc
from ..gold cimport GoldParse
from ..errors import Errors, TempErrors
from .. import util
from .stateclass cimport StateClass
from ._state cimport StateC
from .transition_system cimport Transition
from . cimport _beam_utils
from . import _beam_utils
from . import nonproj


cdef class Parser:
    """
    Base class of the DependencyParser and EntityRecognizer.
    """
    @classmethod
    def Model(cls, nr_class, **cfg):
        depth = util.env_opt('parser_hidden_depth', cfg.get('hidden_depth', 1))
        subword_features = util.env_opt('subword_features',
                            cfg.get('subword_features', True))
        conv_depth = util.env_opt('conv_depth', cfg.get('conv_depth', 4))
        bilstm_depth = util.env_opt('bilstm_depth', cfg.get('bilstm_depth', 0))
        if depth != 1:
            raise ValueError(TempErrors.T004.format(value=depth))
        parser_maxout_pieces = util.env_opt('parser_maxout_pieces',
                                            cfg.get('maxout_pieces', 2))
        token_vector_width = util.env_opt('token_vector_width',
                                           cfg.get('token_vector_width', 96))
        hidden_width = util.env_opt('hidden_width', cfg.get('hidden_width', 64))
        embed_size = util.env_opt('embed_size', cfg.get('embed_size', 2000))
        pretrained_vectors = cfg.get('pretrained_vectors', None)
        tok2vec = Tok2Vec(token_vector_width, embed_size,
                          conv_depth=conv_depth,
                          subword_features=subword_features,
                          pretrained_vectors=pretrained_vectors,
                          bilstm_depth=bilstm_depth)
        tok2vec = chain(tok2vec, flatten)
        tok2vec.nO = token_vector_width
        lower = PrecomputableAffine(hidden_width,
                    nF=cls.nr_feature, nI=token_vector_width,
                    nP=parser_maxout_pieces)
        lower.nP = parser_maxout_pieces

        with Model.use_device('cpu'):
            upper = Affine(nr_class, hidden_width, drop_factor=0.0)
        upper.W *= 0

        cfg = {
            'nr_class': nr_class,
            'hidden_depth': depth,
            'token_vector_width': token_vector_width,
            'hidden_width': hidden_width,
            'maxout_pieces': parser_maxout_pieces,
            'pretrained_vectors': pretrained_vectors,
            'bilstm_depth': bilstm_depth
        }
        return ParserModel(tok2vec, lower, upper), cfg

    name = 'base_parser'

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
            self.moves = self.TransitionSystem(self.vocab.strings)
        else:
            self.moves = moves
        if 'beam_width' not in cfg:
            cfg['beam_width'] = util.env_opt('beam_width', 1)
        if 'beam_density' not in cfg:
            cfg['beam_density'] = util.env_opt('beam_density', 0.0)
        if 'beam_update_prob' not in cfg:
            cfg['beam_update_prob'] = util.env_opt('beam_update_prob', 1.0)
        cfg.setdefault('cnn_maxout_pieces', 3)
        self.cfg = cfg
        self.model = model
        self._multitasks = []
        self._rehearsal_model = None

    def __reduce__(self):
        return (Parser, (self.vocab, self.moves, self.model), None, None)

    @property
    def tok2vec(self):
        return self.model.tok2vec

    @property
    def move_names(self):
        names = []
        for i in range(self.moves.n_moves):
            name = self.moves.move_name(self.moves.c[i].move, self.moves.c[i].label)
            names.append(name)
        return names

    nr_feature = 8

    @property
    def labels(self):
        class_names = [self.moves.get_class_name(i) for i in range(self.moves.n_moves)]
        return class_names

    @property
    def tok2vec(self):
        '''Return the embedding and convolutional layer of the model.'''
        return None if self.model in (None, True, False) else self.model.tok2vec

    @property
    def postprocesses(self):
        # Available for subclasses, e.g. to deprojectivize
        return []

    def add_label(self, label):
        resized = False
        for action in self.moves.action_types:
            added = self.moves.add_action(action, label)
            if added:
                resized = True
        if resized and "nr_class" in self.cfg:
            self.cfg["nr_class"] = self.moves.n_moves
        if self.model not in (True, False, None) and resized:
            self.model.resize_output(self.moves.n_moves)

    def add_multitask_objective(self, target):
        # Defined in subclasses, to avoid circular import
        raise NotImplementedError

    def init_multitask_objectives(self, get_gold_tuples, pipeline, **cfg):
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
        with self.model.use_params(params):
            yield

    def __call__(self, Doc doc, beam_width=None):
        """Apply the parser or entity recognizer, setting the annotations onto
        the `Doc` object.

        doc (Doc): The document to be processed.
        """
        if beam_width is None:
            beam_width = self.cfg.get('beam_width', 1)
        beam_density = self.cfg.get('beam_density', 0.)
        states = self.predict([doc], beam_width=beam_width,
                              beam_density=beam_density)
        self.set_annotations([doc], states, tensors=None)
        return doc

    def pipe(self, docs, int batch_size=256, int n_threads=-1, beam_width=None):
        """Process a stream of documents.

        stream: The sequence of documents to process.
        batch_size (int): Number of documents to accumulate into a working set.
        YIELDS (Doc): Documents, in order.
        """
        if beam_width is None:
            beam_width = self.cfg.get('beam_width', 1)
        beam_density = self.cfg.get('beam_density', 0.)
        cdef Doc doc
        for batch in util.minibatch(docs, size=batch_size):
            batch_in_order = list(batch)
            by_length = sorted(batch_in_order, key=lambda doc: len(doc))
            for subbatch in util.minibatch(by_length, size=max(batch_size//4, 2)):
                subbatch = list(subbatch)
                parse_states = self.predict(subbatch, beam_width=beam_width,
                                            beam_density=beam_density)
                self.set_annotations(subbatch, parse_states, tensors=None)
            for doc in batch_in_order:
                yield doc

    def require_model(self):
        """Raise an error if the component's model is not initialized."""
        if getattr(self, 'model', None) in (None, True, False):
            raise ValueError(Errors.E109.format(name=self.name))

    def predict(self, docs, beam_width=1, beam_density=0.0, drop=0.):
        self.require_model()
        if isinstance(docs, Doc):
            docs = [docs]
        if not any(len(doc) for doc in docs):
            return self.moves.init_batch(docs)
        if beam_width < 2:
            return self.greedy_parse(docs, drop=drop)
        else:
            return self.beam_parse(docs, beam_width=beam_width,
                                   beam_density=beam_density, drop=drop)

    def greedy_parse(self, docs, drop=0.):
        cdef vector[StateC*] states
        cdef StateClass state
        batch = self.moves.init_batch(docs)
        # This is pretty dirty, but the NER can resize itself in init_batch,
        # if labels are missing. We therefore have to check whether we need to
        # expand our model output.
        self.model.resize_output(self.moves.n_moves)
        model = self.model(docs)
        weights = get_c_weights(model)
        for state in batch:
            if not state.is_final():
                states.push_back(state.c)
        sizes = get_c_sizes(model, states.size())
        with nogil:
            self._parseC(&states[0],
                weights, sizes)
        return batch

    def beam_parse(self, docs, int beam_width, float drop=0., beam_density=0.):
        cdef Beam beam
        cdef Doc doc
        cdef np.ndarray token_ids
        beams = self.moves.init_beams(docs, beam_width, beam_density=beam_density)
        # This is pretty dirty, but the NER can resize itself in init_batch,
        # if labels are missing. We therefore have to check whether we need to
        # expand our model output.
        self.model.resize_output(self.moves.n_moves)
        model = self.model(docs)
        token_ids = numpy.zeros((len(docs) * beam_width, self.nr_feature),
                                 dtype='i', order='C')
        cdef int* c_ids
        cdef int nr_feature = self.nr_feature
        cdef int n_states
        model = self.model(docs)
        todo = [beam for beam in beams if not beam.is_done]
        while todo:
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
            vectors = model.state2vec(token_ids[:n_states])
            scores = model.vec2scores(vectors)
            todo = self.transition_beams(todo, scores)
        return beams

    cdef void _parseC(self, StateC** states,
            WeightsC weights, SizesC sizes) nogil:
        cdef int i, j
        cdef vector[StateC*] unfinished
        cdef ActivationsC activations
        memset(&activations, 0, sizeof(activations))
        while sizes.states >= 1:
            predict_states(&activations,
                states, &weights, sizes)
            # Validate actions, argmax, take action.
            self.c_transition_batch(states,
                activations.scores, sizes.classes, sizes.states)
            for i in range(sizes.states):
                if not states[i].is_final():
                    unfinished.push_back(states[i])
            for i in range(unfinished.size()):
                states[i] = unfinished[i]
            sizes.states = unfinished.size()
            unfinished.clear()

    def set_annotations(self, docs, states_or_beams, tensors=None):
        cdef StateClass state
        cdef Beam beam
        cdef Doc doc
        states = []
        beams = []
        for state_or_beam in states_or_beams:
            if isinstance(state_or_beam, StateClass):
                states.append(state_or_beam)
            else:
                beam = state_or_beam
                state = StateClass.borrow(<StateC*>beam.at(0))
                states.append(state)
                beams.append(beam)
        for i, (state, doc) in enumerate(zip(states, docs)):
            self.moves.finalize_state(state.c)
            for j in range(doc.length):
                doc.c[j] = state.c._sent[j]
            self.moves.finalize_doc(doc)
            for hook in self.postprocesses:
                hook(doc)
        for beam in beams:
            _beam_utils.cleanup_beam(beam)

    def transition_states(self, states, float[:, ::1] scores):
        cdef StateClass state
        cdef float* c_scores = &scores[0, 0]
        cdef vector[StateC*] c_states
        for state in states:
            c_states.push_back(state.c)
        self.c_transition_batch(&c_states[0], c_scores, scores.shape[1], scores.shape[0])
        return [state for state in states if not state.c.is_final()]

    cdef void c_transition_batch(self, StateC** states, const float* scores,
            int nr_class, int batch_size) nogil:
        is_valid = <int*>calloc(self.moves.n_moves, sizeof(int))
        cdef int i, guess
        cdef Transition action
        for i in range(batch_size):
            self.moves.set_valid(is_valid, states[i])
            guess = arg_max_if_valid(&scores[i*nr_class], is_valid, nr_class)
            if guess == -1:
                # This shouldn't happen, but it's hard to raise an error here,
                # and we don't want to infinite loop. So, force to end state.
                states[i].force_final()
            else:
                action = self.moves.c[guess]
                action.do(states[i], action.label)
                states[i].push_hist(guess)
        free(is_valid)

    def transition_beams(self, beams, float[:, ::1] scores):
        cdef Beam beam
        cdef float* c_scores = &scores[0, 0]
        for beam in beams:
            for i in range(beam.size):
                state = <StateC*>beam.at(i)
                if not state.is_final():
                    self.moves.set_valid(beam.is_valid[i], state)
                    memcpy(beam.scores[i], c_scores, scores.shape[1] * sizeof(float))
                    c_scores += scores.shape[1]
            beam.advance(_beam_utils.transition_state, _beam_utils.hash_state, <void*>self.moves.c)
            beam.check_done(_beam_utils.check_final_state, NULL)
        return [b for b in beams if not b.is_done]

    def update(self, docs, golds, drop=0., sgd=None, losses=None):
        self.require_model()
        if isinstance(docs, Doc) and isinstance(golds, GoldParse):
            docs = [docs]
            golds = [golds]
        if len(docs) != len(golds):
            raise ValueError(Errors.E077.format(value='update', n_docs=len(docs),
                                                n_golds=len(golds)))
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.)
        for multitask in self._multitasks:
            multitask.update(docs, golds, drop=drop, sgd=sgd)
        # The probability we use beam update, instead of falling back to
        # a greedy update
        beam_update_prob = self.cfg.get('beam_update_prob', 0.5)
        if self.cfg.get('beam_width', 1) >= 2 and numpy.random.random() < beam_update_prob:
            return self.update_beam(docs, golds, self.cfg.get('beam_width', 1),
                    drop=drop, sgd=sgd, losses=losses,
                    beam_density=self.cfg.get('beam_density', 0.001))
        # Chop sequences into lengths of this many transitions, to make the
        # batch uniform length.
        cut_gold = numpy.random.choice(range(20, 100))
        states, golds, max_steps = self._init_gold_batch(docs, golds, max_length=cut_gold)
        states_golds = [(s, g) for (s, g) in zip(states, golds)
                        if not s.is_final() and g is not None]

        # Prepare the stepwise model, and get the callback for finishing the batch
        model, finish_update = self.model.begin_update(docs, drop=drop)
        for _ in range(max_steps):
            if not states_golds:
                break
            states, golds = zip(*states_golds)
            scores, backprop = model.begin_update(states, drop=drop)
            d_scores = self.get_batch_loss(states, golds, scores, losses)
            backprop(d_scores, sgd=sgd)
            # Follow the predicted action
            self.transition_states(states, scores)
            states_golds = [eg for eg in states_golds if not eg[0].is_final()]
        # Do the backprop
        finish_update(golds, sgd=sgd)
        return losses

    def rehearse(self, docs, sgd=None, losses=None, **cfg):
        """Perform a "rehearsal" update, to prevent catastrophic forgetting."""
        if isinstance(docs, Doc):
            docs = [docs]
        if losses is None:
            losses = {}
        for multitask in self._multitasks:
            if hasattr(multitask, 'rehearse'):
                multitask.rehearse(docs, losses=losses, sgd=sgd)
        if self._rehearsal_model is None:
            return None
        losses.setdefault(self.name, 0.)

        states = self.moves.init_batch(docs)
        # This is pretty dirty, but the NER can resize itself in init_batch,
        # if labels are missing. We therefore have to check whether we need to
        # expand our model output.
        self.model.resize_output(self.moves.n_moves)
        self._rehearsal_model.resize_output(self.moves.n_moves)
        # Prepare the stepwise model, and get the callback for finishing the batch
        tutor, _ = self._rehearsal_model.begin_update(docs, drop=0.0)
        model, finish_update = self.model.begin_update(docs, drop=0.0)
        n_scores = 0.
        loss = 0.
        while states:
            targets, _ = tutor.begin_update(states, drop=0.)
            guesses, backprop = model.begin_update(states, drop=0.)
            d_scores = (guesses - targets) / targets.shape[0]
            # If all weights for an output are 0 in the original model, don't
            # supervise that output. This allows us to add classes.
            loss += (d_scores**2).sum()
            backprop(d_scores, sgd=sgd)
            # Follow the predicted action
            self.transition_states(states, guesses)
            states = [state for state in states if not state.is_final()]
            n_scores += d_scores.size
        # Do the backprop
        finish_update(docs, sgd=sgd)
        losses[self.name] += loss / n_scores
        return losses

    def update_beam(self, docs, golds, width, drop=0., sgd=None, losses=None,
                    beam_density=0.0):
        lengths = [len(d) for d in docs]
        states = self.moves.init_batch(docs)
        for gold in golds:
            self.moves.preprocess_gold(gold)
        model, finish_update = self.model.begin_update(docs, drop=drop)
        states_d_scores, backprops, beams = _beam_utils.update_beam(
            self.moves, self.nr_feature, 10000, states, golds, model.state2vec,
            model.vec2scores, width, drop=drop, losses=losses,
            beam_density=beam_density)
        for i, d_scores in enumerate(states_d_scores):
            losses[self.name] += (d_scores**2).mean()
            ids, bp_vectors, bp_scores = backprops[i]
            d_vector = bp_scores(d_scores, sgd=sgd)
            if isinstance(model.ops, CupyOps) \
            and not isinstance(ids, model.state2vec.ops.xp.ndarray):
                model.backprops.append((
                    util.get_async(model.cuda_stream, ids),
                    util.get_async(model.cuda_stream, d_vector),
                    bp_vectors))
            else:
                model.backprops.append((ids, d_vector, bp_vectors))
        model.make_updates(sgd)
        cdef Beam beam
        for beam in beams:
            _beam_utils.cleanup_beam(beam)

    def _init_gold_batch(self, whole_docs, whole_golds, min_length=5, max_length=500):
        """Make a square batch, of length equal to the shortest doc. A long
        doc will get multiple states. Let's say we have a doc of length 2*N,
        where N is the shortest doc. We'll make two states, one representing
        long_doc[:N], and another representing long_doc[N:]."""
        cdef:
            StateClass state
            Transition action
        whole_states = self.moves.init_batch(whole_docs)
        max_length = max(min_length, min(max_length, min([len(doc) for doc in whole_docs])))
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

    def get_batch_loss(self, states, golds, float[:, ::1] scores, losses):
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
            for j in range(self.moves.n_moves):
                if costs[j] <= 0.0 and j in self.model.unseen_classes:
                    self.model.unseen_classes.remove(j)
            cpu_log_loss(c_d_scores,
                costs, is_valid, &scores[i, 0], d_scores.shape[1])
            c_d_scores += d_scores.shape[1]
        if losses is not None:
            losses.setdefault(self.name, 0.)
            losses[self.name] += (d_scores**2).sum()
        return d_scores

    def create_optimizer(self):
        return create_default_optimizer(self.model.ops,
                                        **self.cfg.get('optimizer', {}))

    def begin_training(self, get_gold_tuples, pipeline=None, sgd=None, **cfg):
        if 'model' in cfg:
            self.model = cfg['model']
        if not hasattr(get_gold_tuples, '__call__'):
            gold_tuples = get_gold_tuples
            get_gold_tuples = lambda: gold_tuples
        cfg.setdefault('min_action_freq', 30)
        actions = self.moves.get_actions(gold_parses=get_gold_tuples(),
                                         min_freq=cfg.get('min_action_freq', 30))
        for action, labels in self.moves.labels.items():
            actions.setdefault(action, {})
            for label, freq in labels.items():
                if label not in actions[action]:
                    actions[action][label] = freq
        self.moves.initialize_actions(actions)
        cfg.setdefault('token_vector_width', 96)
        if self.model is True:
            self.model, cfg = self.Model(self.moves.n_moves, **cfg)
            if sgd is None:
                sgd = self.create_optimizer()
            doc_sample = []
            gold_sample = []
            for raw_text, annots_brackets in islice(get_gold_tuples(), 1000):
                for annots, brackets in annots_brackets:
                    ids, words, tags, heads, deps, ents = annots
                    doc_sample.append(Doc(self.vocab, words=words))
                    gold_sample.append(GoldParse(doc_sample[-1], words=words, tags=tags,
                                                 heads=heads, deps=deps, ents=ents))
            self.model.begin_training(doc_sample, gold_sample)
            if pipeline is not None:
                self.init_multitask_objectives(get_gold_tuples, pipeline, sgd=sgd, **cfg)
            link_vectors_to_models(self.vocab)
        else:
            if sgd is None:
                sgd = self.create_optimizer()
            self.model.begin_training([])
        self.cfg.update(cfg)
        return sgd

    def to_disk(self, path, exclude=tuple(), **kwargs):
        serializers = {
            'model': lambda p: (self.model.to_disk(p) if self.model is not True else True),
            'vocab': lambda p: self.vocab.to_disk(p),
            'moves': lambda p: self.moves.to_disk(p, exclude=["strings"]),
            'cfg': lambda p: srsly.write_json(p, self.cfg)
        }
        exclude = util.get_serialization_exclude(serializers, exclude, kwargs)
        util.to_disk(path, serializers, exclude)

    def from_disk(self, path, exclude=tuple(), **kwargs):
        deserializers = {
            'vocab': lambda p: self.vocab.from_disk(p),
            'moves': lambda p: self.moves.from_disk(p, exclude=["strings"]),
            'cfg': lambda p: self.cfg.update(srsly.read_json(p)),
            'model': lambda p: None
        }
        exclude = util.get_serialization_exclude(deserializers, exclude, kwargs)
        util.from_disk(path, deserializers, exclude)
        if 'model' not in exclude:
            path = util.ensure_path(path)
            if self.model is True:
                self.model, cfg = self.Model(**self.cfg)
            else:
                cfg = {}
            with (path / 'model').open('rb') as file_:
                bytes_data = file_.read()
            self.model.from_bytes(bytes_data)
            self.cfg.update(cfg)
        return self

    def to_bytes(self, exclude=tuple(), **kwargs):
        serializers = OrderedDict((
            ('model', lambda: (self.model.to_bytes() if self.model is not True else True)),
            ('vocab', lambda: self.vocab.to_bytes()),
            ('moves', lambda: self.moves.to_bytes(exclude=["strings"])),
            ('cfg', lambda: srsly.json_dumps(self.cfg, indent=2, sort_keys=True))
        ))
        exclude = util.get_serialization_exclude(serializers, exclude, kwargs)
        return util.to_bytes(serializers, exclude)

    def from_bytes(self, bytes_data, exclude=tuple(), **kwargs):
        deserializers = OrderedDict((
            ('vocab', lambda b: self.vocab.from_bytes(b)),
            ('moves', lambda b: self.moves.from_bytes(b, exclude=["strings"])),
            ('cfg', lambda b: self.cfg.update(srsly.json_loads(b))),
            ('model', lambda b: None)
        ))
        exclude = util.get_serialization_exclude(deserializers, exclude, kwargs)
        msg = util.from_bytes(bytes_data, deserializers, exclude)
        if 'model' not in exclude:
            # TODO: Remove this once we don't have to handle previous models
            if self.cfg.get('pretrained_dims') and 'pretrained_vectors' not in self.cfg:
                self.cfg['pretrained_vectors'] = self.vocab.vectors.name
            if self.model is True:
                self.model, cfg = self.Model(**self.cfg)
            else:
                cfg = {}
            if 'model' in msg:
                self.model.from_bytes(msg['model'])
            self.cfg.update(cfg)
        return self
