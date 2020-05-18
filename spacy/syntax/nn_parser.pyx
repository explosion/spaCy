# cython: infer_types=True, cdivision=True, boundscheck=False
cimport cython.parallel
cimport numpy as np
from cpython.ref cimport PyObject, Py_XDECREF
from cpython.exc cimport PyErr_CheckSignals, PyErr_SetFromErrno
from libc.math cimport exp
from libcpp.vector cimport vector
from libc.string cimport memset, memcpy
from libc.stdlib cimport calloc, free
from cymem.cymem cimport Pool
from thinc.extra.search cimport Beam
from thinc.backends.linalg cimport Vec, VecVec

from thinc.api import chain, clone, Linear, list2array, NumpyOps, CupyOps, use_ops
from thinc.api import get_array_module, zero_init, set_dropout_rate
from itertools import islice
import srsly
import numpy.random
import numpy
import warnings

from ..tokens.doc cimport Doc
from ..gold cimport GoldParse
from ..typedefs cimport weight_t, class_t, hash_t
from ._parser_model cimport alloc_activations, free_activations
from ._parser_model cimport predict_states, arg_max_if_valid
from ._parser_model cimport WeightsC, ActivationsC, SizesC, cpu_log_loss
from ._parser_model cimport get_c_weights, get_c_sizes
from .stateclass cimport StateClass
from ._state cimport StateC
from .transition_system cimport Transition
from . cimport _beam_utils

from ..gold import Example
from ..util import link_vectors_to_models, create_default_optimizer, registry
from ..compat import copy_array
from ..errors import Errors, Warnings
from .. import util
from . import _beam_utils
from . import nonproj


cdef class Parser:
    """
    Base class of the DependencyParser and EntityRecognizer.
    """
    name = 'base_parser'


    def __init__(self, Vocab vocab, model, **cfg):
        """Create a Parser.

        vocab (Vocab): The vocabulary object. Must be shared with documents
            to be processed. The value is set to the `.vocab` attribute.
        **cfg: Configuration parameters. Set to the `.cfg` attribute.
             If it doesn't include a value for 'moves',  a new instance is
             created with `self.TransitionSystem()`. This defines how the
             parse-state is created, updated and evaluated.
        """
        self.vocab = vocab
        moves = cfg.get("moves", None)
        if moves is None:
            # defined by EntityRecognizer as a BiluoPushDown
            moves = self.TransitionSystem(self.vocab.strings)
        self.moves = moves
        cfg.setdefault('min_action_freq', 30)
        cfg.setdefault('learn_tokens', False)
        cfg.setdefault('beam_width', 1)
        cfg.setdefault('beam_update_prob', 1.0)  # or 0.5 (both defaults were previously used)
        self.model = model
        if self.moves.n_moves != 0:
            self.set_output(self.moves.n_moves)
        self.cfg = cfg
        self._multitasks = []
        self._rehearsal_model = None

    @classmethod
    def from_nlp(cls, nlp, model, **cfg):
        return cls(nlp.vocab, model, **cfg)

    def __reduce__(self):
        return (Parser, (self.vocab, self.model), self.moves)

    def __getstate__(self):
        return self.moves

    def __setstate__(self, moves):
        self.moves = moves

    @property
    def move_names(self):
        names = []
        for i in range(self.moves.n_moves):
            name = self.moves.move_name(self.moves.c[i].move, self.moves.c[i].label)
            # Explicitly removing the internal "U-" token used for blocking entities
            if name != "U-":
                names.append(name)
        return names

    @property
    def labels(self):
        class_names = [self.moves.get_class_name(i) for i in range(self.moves.n_moves)]
        return class_names

    @property
    def tok2vec(self):
        '''Return the embedding and convolutional layer of the model.'''
        return self.model.get_ref("tok2vec")

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
        if resized:
            self._resize()

    def _resize(self):
        self.model.attrs["resize_output"](self.model, self.moves.n_moves)
        if self._rehearsal_model not in (True, False, None):
            self._rehearsal_model.attrs["resize_output"](
                self._rehearsal_model, self.moves.n_moves
            )

    def add_multitask_objective(self, target):
        # Defined in subclasses, to avoid circular import
        raise NotImplementedError

    def init_multitask_objectives(self, get_examples, pipeline, **cfg):
        '''Setup models for secondary objectives, to benefit from multi-task
        learning. This method is intended to be overridden by subclasses.

        For instance, the dependency parser can benefit from sharing
        an input representation with a label prediction model. These auxiliary
        models are discarded after training.
        '''
        pass

    def preprocess_gold(self, examples):
        for ex in examples:
            yield ex

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
            beam_width = self.cfg['beam_width']
        beam_density = self.cfg.get('beam_density', 0.)
        states = self.predict([doc], beam_width=beam_width,
                              beam_density=beam_density)
        self.set_annotations([doc], states, tensors=None)
        return doc

    def pipe(self, docs, int batch_size=256, int n_threads=-1, beam_width=None,
             as_example=False):
        """Process a stream of documents.

        stream: The sequence of documents to process.
        batch_size (int): Number of documents to accumulate into a working set.
        YIELDS (Doc): Documents, in order.
        """
        if beam_width is None:
            beam_width = self.cfg['beam_width']
        beam_density = self.cfg.get('beam_density', 0.)
        cdef Doc doc
        for batch in util.minibatch(docs, size=batch_size):
            batch_in_order = list(batch)
            docs = [self._get_doc(ex) for ex in batch_in_order]
            by_length = sorted(docs, key=lambda doc: len(doc))
            for subbatch in util.minibatch(by_length, size=max(batch_size//4, 2)):
                subbatch = list(subbatch)
                parse_states = self.predict(subbatch, beam_width=beam_width,
                                            beam_density=beam_density)
                self.set_annotations(subbatch, parse_states, tensors=None)
            if as_example:
                annotated_examples = []
                for ex, doc in zip(batch_in_order, docs):
                    ex.doc = doc
                    annotated_examples.append(ex)
                yield from annotated_examples
            else:
                yield from batch_in_order

    def predict(self, docs, beam_width=1, beam_density=0.0, drop=0.):
        if isinstance(docs, Doc):
            docs = [docs]
        if not any(len(doc) for doc in docs):
            result = self.moves.init_batch(docs)
            self._resize()
            return result
        if beam_width < 2:
            return self.greedy_parse(docs, drop=drop)
        else:
            return self.beam_parse(docs, beam_width=beam_width,
                                   beam_density=beam_density, drop=drop)

    def greedy_parse(self, docs, drop=0.):
        cdef vector[StateC*] states
        cdef StateClass state
        set_dropout_rate(self.model, drop)
        batch = self.moves.init_batch(docs)
        # This is pretty dirty, but the NER can resize itself in init_batch,
        # if labels are missing. We therefore have to check whether we need to
        # expand our model output.
        self._resize()
        model = self.model.predict(docs)
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
        set_dropout_rate(self.model, drop)
        beams = self.moves.init_beams(docs, beam_width, beam_density=beam_density)
        # This is pretty dirty, but the NER can resize itself in init_batch,
        # if labels are missing. We therefore have to check whether we need to
        # expand our model output.
        self._resize()
        cdef int nr_feature = self.model.get_ref("lower").get_dim("nF")
        model = self.model.predict(docs)
        token_ids = numpy.zeros((len(docs) * beam_width, nr_feature),
                                 dtype='i', order='C')
        cdef int* c_ids
        cdef int n_states
        model = self.model.predict(docs)
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
            vectors = model.state2vec.predict(token_ids[:n_states])
            scores = model.vec2scores.predict(vectors)
            todo = self.transition_beams(todo, scores)
        return beams

    cdef void _parseC(self, StateC** states,
            WeightsC weights, SizesC sizes) nogil:
        cdef int i, j
        cdef vector[StateC*] unfinished
        cdef ActivationsC activations = alloc_activations(sizes)
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
        free_activations(&activations)

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
        # n_moves should not be zero at this point, but make sure to avoid zero-length mem alloc
        with gil:
            assert self.moves.n_moves > 0
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

    def update(self, examples, drop=0., set_annotations=False, sgd=None, losses=None):
        examples = Example.to_example_objects(examples)

        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.)
        for multitask in self._multitasks:
            multitask.update(examples, drop=drop, sgd=sgd)
        # The probability we use beam update, instead of falling back to
        # a greedy update
        beam_update_prob = self.cfg['beam_update_prob']
        if self.cfg['beam_width'] >= 2 and numpy.random.random() < beam_update_prob:
            return self.update_beam(examples, self.cfg['beam_width'],
                    drop=drop, sgd=sgd, losses=losses, set_annotations=set_annotations,
                    beam_density=self.cfg.get('beam_density', 0.001))

        set_dropout_rate(self.model, drop)
        cut_gold = True
        if cut_gold:
            # Chop sequences into lengths of this many transitions, to make the
            # batch uniform length.
            cut_gold = numpy.random.choice(range(20, 100))
            states, golds, max_steps = self._init_gold_batch(examples, max_length=cut_gold)
        else:
            states, golds, max_steps = self._init_gold_batch_no_cut(examples)
        states_golds = [(s, g) for (s, g) in zip(states, golds)
                        if not s.is_final() and g is not None]
        # Prepare the stepwise model, and get the callback for finishing the batch
        model, backprop_tok2vec = self.model.begin_update([ex.doc for ex in examples])
        all_states = list(states)
        for _ in range(max_steps):
            if not states_golds:
                break
            states, golds = zip(*states_golds)
            scores, backprop = model.begin_update(states)
            d_scores = self.get_batch_loss(states, golds, scores, losses)
            backprop(d_scores)
            # Follow the predicted action
            self.transition_states(states, scores)
            states_golds = [eg for eg in states_golds if not eg[0].is_final()]
        backprop_tok2vec(golds)
        if sgd is not None:
            self.model.finish_update(sgd)
        if set_annotations:
            docs = [ex.doc for ex in examples]
            self.set_annotations(docs, all_states)
        return losses

    def rehearse(self, examples, sgd=None, losses=None, **cfg):
        """Perform a "rehearsal" update, to prevent catastrophic forgetting."""
        examples = Example.to_example_objects(examples)
        if losses is None:
            losses = {}
        for multitask in self._multitasks:
            if hasattr(multitask, 'rehearse'):
                multitask.rehearse(examples, losses=losses, sgd=sgd)
        if self._rehearsal_model is None:
            return None
        losses.setdefault(self.name, 0.)

        docs = [ex.doc for ex in examples]
        states = self.moves.init_batch(docs)
        # This is pretty dirty, but the NER can resize itself in init_batch,
        # if labels are missing. We therefore have to check whether we need to
        # expand our model output.
        self._resize()
        # Prepare the stepwise model, and get the callback for finishing the batch
        set_dropout_rate(self._rehearsal_model, 0.0)
        set_dropout_rate(self.model, 0.0)
        tutor, _ = self._rehearsal_model.begin_update(docs)
        model, finish_update = self.model.begin_update(docs)
        n_scores = 0.
        loss = 0.
        while states:
            targets, _ = tutor.begin_update(states)
            guesses, backprop = model.begin_update(states)
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
        finish_update(docs)
        if sgd is not None:
            self.model.finish_update(sgd)
        losses[self.name] += loss / n_scores
        return losses

    def update_beam(self, examples, width, drop=0., sgd=None, losses=None,
                    set_annotations=False, beam_density=0.0):
        examples = Example.to_example_objects(examples)
        docs = [ex.doc for ex in examples]
        golds = [ex.gold for ex in examples]
        new_golds = []
        lengths = [len(d) for d in docs]
        states = self.moves.init_batch(docs)
        for gold in golds:
            self.moves.preprocess_gold(gold)
            new_golds.append(gold)
        set_dropout_rate(self.model, drop)
        model, backprop_tok2vec = self.model.begin_update(docs)
        states_d_scores, backprops, beams = _beam_utils.update_beam(
            self.moves,
            self.model.get_ref("lower").get_dim("nF"),
            10000,
            states,
            golds,
            model.state2vec,
            model.vec2scores,
            width,
            losses=losses,
            beam_density=beam_density
        )
        for i, d_scores in enumerate(states_d_scores):
            losses[self.name] += (d_scores**2).mean()
            ids, bp_vectors, bp_scores = backprops[i]
            d_vector = bp_scores(d_scores)
            if isinstance(model.ops, CupyOps) \
            and not isinstance(ids, model.state2vec.ops.xp.ndarray):
                model.backprops.append((
                    util.get_async(model.cuda_stream, ids),
                    util.get_async(model.cuda_stream, d_vector),
                    bp_vectors))
            else:
                model.backprops.append((ids, d_vector, bp_vectors))
        backprop_tok2vec(golds)
        if sgd is not None:
            self.model.finish_update(sgd)
        if set_annotations:
            self.set_annotations(docs, beams)
        cdef Beam beam
        for beam in beams:
            _beam_utils.cleanup_beam(beam)

    def get_gradients(self):
        """Get non-zero gradients of the model's parameters, as a dictionary
        keyed by the parameter ID. The values are (weights, gradients) tuples.
        """
        gradients = {}
        queue = [self.model]
        seen = set()
        for node in queue:
            if node.id in seen:
                continue
            seen.add(node.id)
            if hasattr(node, "_mem") and node._mem.gradient.any():
                gradients[node.id] = [node._mem.weights, node._mem.gradient]
            if hasattr(node, "_layers"):
                queue.extend(node._layers)
        return gradients

    def _init_gold_batch_no_cut(self, whole_examples):
        states = self.moves.init_batch([eg.doc for eg in whole_examples])
        good_docs = []
        good_golds = []
        good_states = []
        for i, eg in enumerate(whole_examples):
            doc = eg.doc
            gold = self.moves.preprocess_gold(eg.gold)
            if gold is not None and self.moves.has_gold(gold):
                good_docs.append(doc)
                good_golds.append(gold)
                good_states.append(states[i])
        n_moves = []
        for doc, gold in zip(good_docs, good_golds):
            oracle_actions = self.moves.get_oracle_sequence(doc, gold)
            n_moves.append(len(oracle_actions))
        return good_states, good_golds, max(n_moves, default=0) * 2
 
    def _init_gold_batch(self, whole_examples, min_length=5, max_length=500):
        """Make a square batch, of length equal to the shortest doc. A long
        doc will get multiple states. Let's say we have a doc of length 2*N,
        where N is the shortest doc. We'll make two states, one representing
        long_doc[:N], and another representing long_doc[N:]."""
        cdef:
            StateClass state
            Transition action
        whole_docs = [ex.doc for ex in whole_examples]
        whole_golds = [ex.gold for ex in whole_examples]
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

        # n_moves should not be zero at this point, but make sure to avoid zero-length mem alloc
        assert self.moves.n_moves > 0

        is_valid = <int*>mem.alloc(self.moves.n_moves, sizeof(int))
        costs = <float*>mem.alloc(self.moves.n_moves, sizeof(float))
        cdef np.ndarray d_scores = numpy.zeros((len(states), self.moves.n_moves),
                                        dtype='f', order='C')
        c_d_scores = <float*>d_scores.data
        unseen_classes = self.model.attrs["unseen_classes"]
        for i, (state, gold) in enumerate(zip(states, golds)):
            memset(is_valid, 0, self.moves.n_moves * sizeof(int))
            memset(costs, 0, self.moves.n_moves * sizeof(float))
            self.moves.set_costs(is_valid, costs, state, gold)
            for j in range(self.moves.n_moves):
                if costs[j] <= 0.0 and j in unseen_classes:
                    unseen_classes.remove(j)
            cpu_log_loss(c_d_scores,
                costs, is_valid, &scores[i, 0], d_scores.shape[1])
            c_d_scores += d_scores.shape[1]
        if len(states):
            d_scores /= len(states)
        if losses is not None:
            losses.setdefault(self.name, 0.)
            losses[self.name] += (d_scores**2).sum()
        return d_scores

    def create_optimizer(self):
        return create_default_optimizer()

    def set_output(self, nO):
        self.model.attrs["resize_output"](self.model, nO)

    def begin_training(self, get_examples, pipeline=None, sgd=None, **kwargs):
        self.cfg.update(kwargs)
        if not hasattr(get_examples, '__call__'):
            gold_tuples = get_examples
            get_examples = lambda: gold_tuples
        actions = self.moves.get_actions(gold_parses=get_examples(),
                                         min_freq=self.cfg['min_action_freq'],
                                         learn_tokens=self.cfg["learn_tokens"])
        for action, labels in self.moves.labels.items():
            actions.setdefault(action, {})
            for label, freq in labels.items():
                if label not in actions[action]:
                    actions[action][label] = freq
        self.moves.initialize_actions(actions)
        # make sure we resize so we have an appropriate upper layer
        self._resize()
        if sgd is None:
            sgd = self.create_optimizer()
        doc_sample = []
        gold_sample = []
        for example in islice(get_examples(), 1000):
            parses = example.get_gold_parses(merge=False, vocab=self.vocab)
            for doc, gold in parses:
                doc_sample.append(doc)
                gold_sample.append(gold)
        self.model.initialize(doc_sample, gold_sample)
        if pipeline is not None:
            self.init_multitask_objectives(get_examples, pipeline, sgd=sgd, **self.cfg)
        link_vectors_to_models(self.vocab)
        return sgd

    def _get_doc(self, example):
        """ Use this method if the `example` can be both a Doc or an Example """
        if isinstance(example, Doc):
            return example
        return example.doc

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
            'model': lambda p: None,
        }
        exclude = util.get_serialization_exclude(deserializers, exclude, kwargs)
        util.from_disk(path, deserializers, exclude)
        if 'model' not in exclude:
            path = util.ensure_path(path)
            with (path / 'model').open('rb') as file_:
                bytes_data = file_.read()
            try:
                self._resize()
                self.model.from_bytes(bytes_data)
            except AttributeError:
                raise ValueError(Errors.E149)
        return self

    def to_bytes(self, exclude=tuple(), **kwargs):
        serializers = {
            "model": lambda: (self.model.to_bytes()),
            "vocab": lambda: self.vocab.to_bytes(),
            "moves": lambda: self.moves.to_bytes(exclude=["strings"]),
            "cfg": lambda: srsly.json_dumps(self.cfg, indent=2, sort_keys=True)
        }
        exclude = util.get_serialization_exclude(serializers, exclude, kwargs)
        return util.to_bytes(serializers, exclude)

    def from_bytes(self, bytes_data, exclude=tuple(), **kwargs):
        deserializers = {
            "vocab": lambda b: self.vocab.from_bytes(b),
            "moves": lambda b: self.moves.from_bytes(b, exclude=["strings"]),
            "cfg": lambda b: self.cfg.update(srsly.json_loads(b)),
            "model": lambda b: None,
        }
        exclude = util.get_serialization_exclude(deserializers, exclude, kwargs)
        msg = util.from_bytes(bytes_data, deserializers, exclude)
        if 'model' not in exclude:
            if 'model' in msg:
                try:
                    self.model.from_bytes(msg['model'])
                except AttributeError:
                    raise ValueError(Errors.E149)
        return self
