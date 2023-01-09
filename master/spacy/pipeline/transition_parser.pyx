# cython: infer_types=True, cdivision=True, boundscheck=False, binding=True
from __future__ import print_function
from cymem.cymem cimport Pool
cimport numpy as np
from itertools import islice
from libcpp.vector cimport vector
from libc.string cimport memset, memcpy
from libc.stdlib cimport calloc, free
import random

import srsly
from thinc.api import get_ops, set_dropout_rate, CupyOps, NumpyOps
from thinc.extra.search cimport Beam
import numpy.random
import numpy
import warnings

from ._parser_internals.stateclass cimport StateClass
from ..ml.parser_model cimport alloc_activations, free_activations
from ..ml.parser_model cimport predict_states, arg_max_if_valid
from ..ml.parser_model cimport WeightsC, ActivationsC, SizesC, cpu_log_loss
from ..ml.parser_model cimport get_c_weights, get_c_sizes
from ..tokens.doc cimport Doc
from .trainable_pipe import TrainablePipe
from ._parser_internals cimport _beam_utils
from ._parser_internals import _beam_utils

from ..training import validate_examples, validate_get_examples
from ..errors import Errors, Warnings
from .. import util


NUMPY_OPS = NumpyOps()


cdef class Parser(TrainablePipe):
    """
    Base class of the DependencyParser and EntityRecognizer.
    """

    def __init__(
        self,
        Vocab vocab,
        model,
        name="base_parser",
        moves=None,
        *,
        update_with_oracle_cut_size,
        min_action_freq,
        learn_tokens,
        beam_width=1,
        beam_density=0.0,
        beam_update_prob=0.0,
        multitasks=tuple(),
        incorrect_spans_key=None,
        scorer=None,
    ):
        """Create a Parser.

        vocab (Vocab): The vocabulary object. Must be shared with documents
            to be processed. The value is set to the `.vocab` attribute.
        model (Model): The model for the transition-based parser. The model needs
            to have a specific substructure of named components --- see the
            spacy.ml.tb_framework.TransitionModel for details.
        name (str): The name of the pipeline component
        moves (Optional[TransitionSystem]): This defines how the parse-state is created,
            updated and evaluated. If 'moves' is None, a new instance is
            created with `self.TransitionSystem()`. Defaults to `None`.
        update_with_oracle_cut_size (int): During training, cut long sequences into
            shorter segments by creating intermediate states based on the gold-standard
            history. The model is not very sensitive to this parameter, so you usually
            won't need to change it. 100 is a good default.
        min_action_freq (int): The minimum frequency of labelled actions to retain.
            Rarer labelled actions have their label backed-off to "dep". While this
            primarily affects the label accuracy, it can also affect the attachment
            structure, as the labels are used to represent the pseudo-projectivity
            transformation.
        learn_tokens (bool): Whether to learn to merge subtokens that are split
            relative to the gold standard. Experimental.
        beam_width (int): The number of candidate analyses to maintain.
        beam_density (float): The minimum ratio between the scores of the first and
            last candidates in the beam. This allows the parser to avoid exploring
            candidates that are too far behind. This is mostly intended to improve
            efficiency, but it can also improve accuracy as deeper search is not
            always better.
        beam_update_prob (float): The chance of making a beam update, instead of a
            greedy update. Greedy updates are an approximation for the beam updates,
            and are faster to compute.
        multitasks: additional multi-tasking components. Experimental.
        incorrect_spans_key (Optional[str]): Identifies spans that are known
            to be incorrect entity annotations. The incorrect entity annotations
            can be stored in the span group, under this key.
        scorer (Optional[Callable]): The scoring method. Defaults to None.
        """
        self.vocab = vocab
        self.name = name
        cfg = {
            "moves": moves,
            "update_with_oracle_cut_size": update_with_oracle_cut_size,
            "multitasks": list(multitasks),
            "min_action_freq": min_action_freq,
            "learn_tokens": learn_tokens,
            "beam_width": beam_width,
            "beam_density": beam_density,
            "beam_update_prob": beam_update_prob,
            "incorrect_spans_key": incorrect_spans_key
        }
        if moves is None:
            # EntityRecognizer -> BiluoPushDown
            # DependencyParser -> ArcEager
            moves = self.TransitionSystem(
                self.vocab.strings,
                incorrect_spans_key=incorrect_spans_key
            )
        self.moves = moves
        self.model = model
        if self.moves.n_moves != 0:
            self.set_output(self.moves.n_moves)
        self.cfg = cfg
        self._multitasks = []
        for multitask in cfg["multitasks"]:
            self.add_multitask_objective(multitask)

        self._rehearsal_model = None
        self.scorer = scorer

    def __getnewargs_ex__(self):
        """This allows pickling the Parser and its keyword-only init arguments"""
        args = (self.vocab, self.model, self.name, self.moves)
        return args, self.cfg

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
    def label_data(self):
        return self.moves.labels

    @property
    def tok2vec(self):
        """Return the embedding and convolutional layer of the model."""
        return self.model.get_ref("tok2vec")

    @property
    def postprocesses(self):
        # Available for subclasses, e.g. to deprojectivize
        return []

    @property
    def incorrect_spans_key(self):
        return self.cfg["incorrect_spans_key"]

    def add_label(self, label):
        resized = False
        for action in self.moves.action_types:
            added = self.moves.add_action(action, label)
            if added:
                resized = True
        if resized:
            self._resize()
            self.vocab.strings.add(label)
            return 1
        return 0

    def _ensure_labels_are_added(self, docs):
        """Ensure that all labels for a batch of docs are added."""
        resized = False
        labels = set()
        for doc in docs:
            labels.update(self.moves.get_doc_labels(doc))
        for label in labels:
            for action in self.moves.action_types:
                added = self.moves.add_action(action, label)
                if added:
                    self.vocab.strings.add(label)
                    resized = True
        if resized:
            self._resize()
            return 1
        return 0

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
        """Setup models for secondary objectives, to benefit from multi-task
        learning. This method is intended to be overridden by subclasses.

        For instance, the dependency parser can benefit from sharing
        an input representation with a label prediction model. These auxiliary
        models are discarded after training.
        """
        pass

    def use_params(self, params):
        # Can't decorate cdef class :(. Workaround.
        with self.model.use_params(params):
            yield

    def pipe(self, docs, *, int batch_size=256):
        """Process a stream of documents.

        stream: The sequence of documents to process.
        batch_size (int): Number of documents to accumulate into a working set.
        error_handler (Callable[[str, List[Doc], Exception], Any]): Function that
            deals with a failing batch of documents. The default function just reraises
            the exception.

        YIELDS (Doc): Documents, in order.
        """
        cdef Doc doc
        error_handler = self.get_error_handler()
        for batch in util.minibatch(docs, size=batch_size):
            batch_in_order = list(batch)
            try:
                by_length = sorted(batch, key=lambda doc: len(doc))
                for subbatch in util.minibatch(by_length, size=max(batch_size//4, 2)):
                    subbatch = list(subbatch)
                    parse_states = self.predict(subbatch)
                    self.set_annotations(subbatch, parse_states)
                yield from batch_in_order
            except Exception as e:
                error_handler(self.name, self, batch_in_order, e)


    def predict(self, docs):
        if isinstance(docs, Doc):
            docs = [docs]
        if not any(len(doc) for doc in docs):
            result = self.moves.init_batch(docs)
            return result
        if self.cfg["beam_width"] == 1:
            return self.greedy_parse(docs, drop=0.0)
        else:
            return self.beam_parse(
                docs,
                drop=0.0,
                beam_width=self.cfg["beam_width"],
                beam_density=self.cfg["beam_density"]
            )

    def greedy_parse(self, docs, drop=0.):
        cdef vector[StateC*] states
        cdef StateClass state
        ops = self.model.ops
        cdef CBlas cblas
        if isinstance(ops, CupyOps):
            cblas = NUMPY_OPS.cblas()
        else:
            cblas = ops.cblas()
        self._ensure_labels_are_added(docs)
        set_dropout_rate(self.model, drop)
        batch = self.moves.init_batch(docs)
        model = self.model.predict(docs)
        weights = get_c_weights(model)
        for state in batch:
            if not state.is_final():
                states.push_back(state.c)
        sizes = get_c_sizes(model, states.size())
        with nogil:
            self._parseC(cblas, &states[0], weights, sizes)
        model.clear_memory()
        del model
        return batch

    def beam_parse(self, docs, int beam_width, float drop=0., beam_density=0.):
        cdef Beam beam
        cdef Doc doc
        self._ensure_labels_are_added(docs)
        batch = _beam_utils.BeamBatch(
            self.moves,
            self.moves.init_batch(docs),
            None,
            beam_width,
            density=beam_density
        )
        model = self.model.predict(docs)
        while not batch.is_done:
            states = batch.get_unfinished_states()
            if not states:
                break
            scores = model.predict(states)
            batch.advance(scores)
        model.clear_memory()
        del model
        return list(batch)

    cdef void _parseC(self, CBlas cblas, StateC** states,
            WeightsC weights, SizesC sizes) nogil:
        cdef int i, j
        cdef vector[StateC*] unfinished
        cdef ActivationsC activations = alloc_activations(sizes)
        while sizes.states >= 1:
            predict_states(cblas, &activations, states, &weights, sizes)
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

    def set_annotations(self, docs, states_or_beams):
        cdef StateClass state
        cdef Beam beam
        cdef Doc doc
        states = _beam_utils.collect_states(states_or_beams, docs)
        for i, (state, doc) in enumerate(zip(states, docs)):
            self.moves.set_annotations(state, doc)
            for hook in self.postprocesses:
                hook(doc)

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
            assert self.moves.n_moves > 0, Errors.E924.format(name=self.name)
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
        free(is_valid)

    def update(self, examples, *, drop=0., sgd=None, losses=None):
        cdef StateClass state
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.)
        validate_examples(examples, "Parser.update")
        self._ensure_labels_are_added(
            [eg.x for eg in examples] + [eg.y for eg in examples]
        )
        for multitask in self._multitasks:
            multitask.update(examples, drop=drop, sgd=sgd)
        n_examples = len([eg for eg in examples if self.moves.has_gold(eg)])
        if n_examples == 0:
            return losses
        set_dropout_rate(self.model, drop)
        # The probability we use beam update, instead of falling back to
        # a greedy update
        beam_update_prob = self.cfg["beam_update_prob"]
        if self.cfg['beam_width'] >= 2 and numpy.random.random() < beam_update_prob:
            return self.update_beam(
                examples,
                beam_width=self.cfg["beam_width"],
                sgd=sgd,
                losses=losses,
                beam_density=self.cfg["beam_density"]
            )
        max_moves = self.cfg["update_with_oracle_cut_size"]
        if max_moves >= 1:
            # Chop sequences into lengths of this many words, to make the
            # batch uniform length.
            max_moves = int(random.uniform(max_moves // 2, max_moves * 2))
            states, golds, _ = self._init_gold_batch(
                examples,
                max_length=max_moves
            )
        else:
            states, golds, _ = self.moves.init_gold_batch(examples)
        if not states:
            return losses
        model, backprop_tok2vec = self.model.begin_update([eg.x for eg in examples])
 
        all_states = list(states)
        states_golds = list(zip(states, golds))
        n_moves = 0
        while states_golds:
            states, golds = zip(*states_golds)
            scores, backprop = model.begin_update(states)
            d_scores = self.get_batch_loss(states, golds, scores, losses)
            # Note that the gradient isn't normalized by the batch size
            # here, because our "samples" are really the states...But we
            # can't normalize by the number of states either, as then we'd
            # be getting smaller gradients for states in long sequences.
            backprop(d_scores)
            # Follow the predicted action
            self.transition_states(states, scores)
            states_golds = [(s, g) for (s, g) in zip(states, golds) if not s.is_final()]
            if max_moves >= 1 and n_moves >= max_moves:
                break
            n_moves += 1

        backprop_tok2vec(golds)
        if sgd not in (None, False):
            self.finish_update(sgd)
        # Ugh, this is annoying. If we're working on GPU, we want to free the
        # memory ASAP. It seems that Python doesn't necessarily get around to
        # removing these in time if we don't explicitly delete? It's confusing.
        del backprop
        del backprop_tok2vec
        model.clear_memory()
        del model
        return losses

    def rehearse(self, examples, sgd=None, losses=None, **cfg):
        """Perform a "rehearsal" update, to prevent catastrophic forgetting."""
        if losses is None:
            losses = {}
        for multitask in self._multitasks:
            if hasattr(multitask, 'rehearse'):
                multitask.rehearse(examples, losses=losses, sgd=sgd)
        if self._rehearsal_model is None:
            return None
        losses.setdefault(self.name, 0.)
        validate_examples(examples, "Parser.rehearse")
        docs = [eg.predicted for eg in examples]
        states = self.moves.init_batch(docs)
        # This is pretty dirty, but the NER can resize itself in init_batch,
        # if labels are missing. We therefore have to check whether we need to
        # expand our model output.
        self._resize()
        # Prepare the stepwise model, and get the callback for finishing the batch
        set_dropout_rate(self._rehearsal_model, 0.0)
        set_dropout_rate(self.model, 0.0)
        tutor, _ = self._rehearsal_model.begin_update(docs)
        model, backprop_tok2vec = self.model.begin_update(docs)
        n_scores = 0.
        loss = 0.
        while states:
            targets, _ = tutor.begin_update(states)
            guesses, backprop = model.begin_update(states)
            d_scores = (guesses - targets) / targets.shape[0]
            # If all weights for an output are 0 in the original model, don't
            # supervise that output. This allows us to add classes.
            loss += (d_scores**2).sum()
            backprop(d_scores)
            # Follow the predicted action
            self.transition_states(states, guesses)
            states = [state for state in states if not state.is_final()]
            n_scores += d_scores.size
        # Do the backprop
        backprop_tok2vec(docs)
        if sgd is not None:
            self.finish_update(sgd)
        losses[self.name] += loss / n_scores
        del backprop
        del backprop_tok2vec
        model.clear_memory()
        tutor.clear_memory()
        del model
        del tutor
        return losses

    def update_beam(self, examples, *, beam_width,
            drop=0., sgd=None, losses=None, beam_density=0.0):
        states, golds, _ = self.moves.init_gold_batch(examples)
        if not states:
            return losses
        # Prepare the stepwise model, and get the callback for finishing the batch
        model, backprop_tok2vec = self.model.begin_update(
            [eg.predicted for eg in examples])
        loss = _beam_utils.update_beam(
            self.moves,
            states,
            golds,
            model,
            beam_width,
            beam_density=beam_density,
        )
        losses[self.name] += loss
        backprop_tok2vec(golds)
        if sgd is not None:
            self.finish_update(sgd)

    def get_batch_loss(self, states, golds, float[:, ::1] scores, losses):
        cdef StateClass state
        cdef Pool mem = Pool()
        cdef int i

        # n_moves should not be zero at this point, but make sure to avoid zero-length mem alloc
        assert self.moves.n_moves > 0, Errors.E924.format(name=self.name)

        is_valid = <int*>mem.alloc(self.moves.n_moves, sizeof(int))
        costs = <float*>mem.alloc(self.moves.n_moves, sizeof(float))
        cdef np.ndarray d_scores = numpy.zeros((len(states), self.moves.n_moves),
                                        dtype='f', order='C')
        c_d_scores = <float*>d_scores.data
        unseen_classes = self.model.attrs["unseen_classes"]
        for i, (state, gold) in enumerate(zip(states, golds)):
            memset(is_valid, 0, self.moves.n_moves * sizeof(int))
            memset(costs, 0, self.moves.n_moves * sizeof(float))
            self.moves.set_costs(is_valid, costs, state.c, gold)
            for j in range(self.moves.n_moves):
                if costs[j] <= 0.0 and j in unseen_classes:
                    unseen_classes.remove(j)
            cpu_log_loss(c_d_scores,
                costs, is_valid, &scores[i, 0], d_scores.shape[1])
            c_d_scores += d_scores.shape[1]
        # Note that we don't normalize this. See comment in update() for why.
        if losses is not None:
            losses.setdefault(self.name, 0.)
            losses[self.name] += (d_scores**2).sum()
        return d_scores

    def set_output(self, nO):
        self.model.attrs["resize_output"](self.model, nO)

    def initialize(self, get_examples, nlp=None, labels=None):
        validate_get_examples(get_examples, "Parser.initialize")
        util.check_lexeme_norms(self.vocab, "parser or NER")
        if labels is not None:
            actions = dict(labels)
        else:
            actions = self.moves.get_actions(
                examples=get_examples(),
                min_freq=self.cfg['min_action_freq'],
                learn_tokens=self.cfg["learn_tokens"]
            )
        for action, labels in self.moves.labels.items():
            actions.setdefault(action, {})
            for label, freq in labels.items():
                if label not in actions[action]:
                    actions[action][label] = freq
        self.moves.initialize_actions(actions)
        # make sure we resize so we have an appropriate upper layer
        self._resize()
        doc_sample = []
        if nlp is not None:
            for name, component in nlp.pipeline:
                if component is self:
                    break
                # non-trainable components may have a pipe() implementation that refers to dummy
                # predict and set_annotations methods
                if hasattr(component, "pipe"):
                    doc_sample = list(component.pipe(doc_sample, batch_size=8))
                else:
                    doc_sample = [component(doc) for doc in doc_sample]
        if not doc_sample:
            for example in islice(get_examples(), 10):
                doc_sample.append(example.predicted)
        assert len(doc_sample) > 0, Errors.E923.format(name=self.name)
        self.model.initialize(doc_sample)
        if nlp is not None:
            self.init_multitask_objectives(get_examples, nlp.pipeline)

    def to_disk(self, path, exclude=tuple()):
        serializers = {
            "model": lambda p: (self.model.to_disk(p) if self.model is not True else True),
            "vocab": lambda p: self.vocab.to_disk(p, exclude=exclude),
            "moves": lambda p: self.moves.to_disk(p, exclude=["strings"]),
            "cfg": lambda p: srsly.write_json(p, self.cfg)
        }
        util.to_disk(path, serializers, exclude)

    def from_disk(self, path, exclude=tuple()):
        deserializers = {
            "vocab": lambda p: self.vocab.from_disk(p, exclude=exclude),
            "moves": lambda p: self.moves.from_disk(p, exclude=["strings"]),
            "cfg": lambda p: self.cfg.update(srsly.read_json(p)),
            "model": lambda p: None,
        }
        util.from_disk(path, deserializers, exclude)
        if "model" not in exclude:
            path = util.ensure_path(path)
            with (path / "model").open("rb") as file_:
                bytes_data = file_.read()
            try:
                self._resize()
                self.model.from_bytes(bytes_data)
            except AttributeError:
                raise ValueError(Errors.E149)
        return self

    def to_bytes(self, exclude=tuple()):
        serializers = {
            "model": lambda: (self.model.to_bytes()),
            "vocab": lambda: self.vocab.to_bytes(exclude=exclude),
            "moves": lambda: self.moves.to_bytes(exclude=["strings"]),
            "cfg": lambda: srsly.json_dumps(self.cfg, indent=2, sort_keys=True)
        }
        return util.to_bytes(serializers, exclude)

    def from_bytes(self, bytes_data, exclude=tuple()):
        deserializers = {
            "vocab": lambda b: self.vocab.from_bytes(b, exclude=exclude),
            "moves": lambda b: self.moves.from_bytes(b, exclude=["strings"]),
            "cfg": lambda b: self.cfg.update(srsly.json_loads(b)),
            "model": lambda b: None,
        }
        msg = util.from_bytes(bytes_data, deserializers, exclude)
        if 'model' not in exclude:
            if 'model' in msg:
                try:
                    self.model.from_bytes(msg['model'])
                except AttributeError:
                    raise ValueError(Errors.E149) from None
        return self

    def _init_gold_batch(self, examples, max_length):
        """Make a square batch, of length equal to the shortest transition
        sequence or a cap. A long
        doc will get multiple states. Let's say we have a doc of length 2*N,
        where N is the shortest doc. We'll make two states, one representing
        long_doc[:N], and another representing long_doc[N:]."""
        cdef:
            StateClass start_state
            StateClass state
            Transition action
        all_states = self.moves.init_batch([eg.predicted for eg in examples])
        states = []
        golds = []
        to_cut = []
        for state, eg in zip(all_states, examples):
            if self.moves.has_gold(eg) and not state.is_final():
                gold = self.moves.init_gold(state, eg)
                if len(eg.x) < max_length:
                    states.append(state)
                    golds.append(gold)
                else:
                    oracle_actions = self.moves.get_oracle_sequence_from_state(
                        state.copy(), gold)
                    to_cut.append((eg, state, gold, oracle_actions))
        if not to_cut:
            return states, golds, 0
        cdef int clas
        for eg, state, gold, oracle_actions in to_cut:
            for i in range(0, len(oracle_actions), max_length):
                start_state = state.copy()
                for clas in oracle_actions[i:i+max_length]:
                    action = self.moves.c[clas]
                    action.do(state.c, action.label)
                    if state.is_final():
                        break
                if self.moves.has_gold(eg, start_state.B(0), state.B(0)):
                    states.append(start_state)
                    golds.append(gold)
                if state.is_final():
                    break
        return states, golds, max_length
