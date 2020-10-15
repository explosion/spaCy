# cython: infer_types=True, cdivision=True, boundscheck=False, binding=True
from __future__ import print_function
from cymem.cymem cimport Pool
cimport numpy as np
from itertools import islice
from libcpp.vector cimport vector
from libc.string cimport memset
from libc.stdlib cimport calloc, free
import random
from typing import Optional

import srsly
from thinc.api import set_dropout_rate
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

from ..training import validate_examples, validate_get_examples
from ..errors import Errors, Warnings
from .. import util


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
        multitasks=tuple(),
        min_action_freq,
        learn_tokens,
    ):
        """Create a Parser.

        vocab (Vocab): The vocabulary object. Must be shared with documents
            to be processed. The value is set to the `.vocab` attribute.
        **cfg: Configuration parameters. Set to the `.cfg` attribute.
             If it doesn't include a value for 'moves',  a new instance is
             created with `self.TransitionSystem()`. This defines how the
             parse-state is created, updated and evaluated.
        """
        self.vocab = vocab
        self.name = name
        cfg = {
            "moves": moves,
            "update_with_oracle_cut_size": update_with_oracle_cut_size,
            "multitasks": list(multitasks),
            "min_action_freq": min_action_freq,
            "learn_tokens": learn_tokens
        }
        if moves is None:
            # defined by EntityRecognizer as a BiluoPushDown
            moves = self.TransitionSystem(self.vocab.strings)
        self.moves = moves
        self.model = model
        if self.moves.n_moves != 0:
            self.set_output(self.moves.n_moves)
        self.cfg = cfg
        self._multitasks = []
        for multitask in cfg["multitasks"]:
            self.add_multitask_objective(multitask)

        self._rehearsal_model = None

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

    def __call__(self, Doc doc):
        """Apply the parser or entity recognizer, setting the annotations onto
        the `Doc` object.

        doc (Doc): The document to be processed.
        """
        states = self.predict([doc])
        self.set_annotations([doc], states)
        return doc

    def pipe(self, docs, *, int batch_size=256):
        """Process a stream of documents.

        stream: The sequence of documents to process.
        batch_size (int): Number of documents to accumulate into a working set.
        YIELDS (Doc): Documents, in order.
        """
        cdef Doc doc
        for batch in util.minibatch(docs, size=batch_size):
            batch_in_order = list(batch)
            by_length = sorted(batch, key=lambda doc: len(doc))
            for subbatch in util.minibatch(by_length, size=max(batch_size//4, 2)):
                subbatch = list(subbatch)
                parse_states = self.predict(subbatch)
                self.set_annotations(subbatch, parse_states)
            yield from batch_in_order

    def predict(self, docs):
        if isinstance(docs, Doc):
            docs = [docs]
        if not any(len(doc) for doc in docs):
            result = self.moves.init_batch(docs)
            self._resize()
            return result
        return self.greedy_parse(docs, drop=0.0)

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
        model.clear_memory()
        del model
        return batch

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

    def set_annotations(self, docs, states):
        cdef StateClass state
        cdef Doc doc
        for i, (state, doc) in enumerate(zip(states, docs)):
            self.moves.finalize_state(state.c)
            for j in range(doc.length):
                doc.c[j] = state.c._sent[j]
            self.moves.finalize_doc(doc)
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
                states[i].push_hist(guess)
        free(is_valid)

    def update(self, examples, *, drop=0., set_annotations=False, sgd=None, losses=None):
        cdef StateClass state
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.)
        validate_examples(examples, "Parser.update")
        for multitask in self._multitasks:
            multitask.update(examples, drop=drop, sgd=sgd)
        n_examples = len([eg for eg in examples if self.moves.has_gold(eg)])
        if n_examples == 0:
            return losses
        set_dropout_rate(self.model, drop)
        # Prepare the stepwise model, and get the callback for finishing the batch
        model, backprop_tok2vec = self.model.begin_update(
            [eg.predicted for eg in examples])
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
        if set_annotations:
            docs = [eg.predicted for eg in examples]
            self.set_annotations(docs, all_states)
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
            self.moves.set_costs(is_valid, costs, state, gold)
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
        lexeme_norms = self.vocab.lookups.get_table("lexeme_norm", {})
        if len(lexeme_norms) == 0 and self.vocab.lang in util.LEXEME_NORM_LANGS:
            langs = ", ".join(util.LEXEME_NORM_LANGS)
            util.logger.debug(Warnings.W033.format(model="parser or NER", langs=langs))
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
            "vocab": lambda p: self.vocab.to_disk(p),
            "moves": lambda p: self.moves.to_disk(p, exclude=["strings"]),
            "cfg": lambda p: srsly.write_json(p, self.cfg)
        }
        util.to_disk(path, serializers, exclude)

    def from_disk(self, path, exclude=tuple()):
        deserializers = {
            "vocab": lambda p: self.vocab.from_disk(p),
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
                raise ValueError(Errors.E149) from None
        return self

    def to_bytes(self, exclude=tuple()):
        serializers = {
            "model": lambda: (self.model.to_bytes()),
            "vocab": lambda: self.vocab.to_bytes(),
            "moves": lambda: self.moves.to_bytes(exclude=["strings"]),
            "cfg": lambda: srsly.json_dumps(self.cfg, indent=2, sort_keys=True)
        }
        return util.to_bytes(serializers, exclude)

    def from_bytes(self, bytes_data, exclude=tuple()):
        deserializers = {
            "vocab": lambda b: self.vocab.from_bytes(b),
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
                    state.c.push_hist(action.clas)
                    if state.is_final():
                        break
                if self.moves.has_gold(eg, start_state.B(0), state.B(0)):
                    states.append(start_state)
                    golds.append(gold)
                if state.is_final():
                    break
        return states, golds, max_length
