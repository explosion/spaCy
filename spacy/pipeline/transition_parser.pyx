# cython: infer_types=True, cdivision=True, boundscheck=False, binding=True
from __future__ import print_function
from cymem.cymem cimport Pool
cimport numpy as np
from itertools import islice
from libcpp.vector cimport vector
from libc.string cimport memset, memcpy
from libc.stdlib cimport calloc, free
import random
from typing import Optional

import srsly
from thinc.api import set_dropout_rate, CupyOps, get_array_module
from thinc.extra.search cimport Beam
import numpy.random
import numpy
import warnings

from ._parser_internals.stateclass cimport StateClass
from ..tokens.doc cimport Doc
from .trainable_pipe import TrainablePipe
from ._parser_internals cimport _beam_utils
from ._parser_internals import _beam_utils
from ..vocab cimport Vocab
from ._parser_internals.transition_system cimport TransitionSystem

from ..training import validate_examples, validate_get_examples
from ..errors import Errors, Warnings
from .. import util


class Parser(TrainablePipe):
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
            "learn_tokens": learn_tokens,
            "beam_width": beam_width,
            "beam_density": beam_density,
            "beam_update_prob": beam_update_prob
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
        cdef TransitionSystem moves = self.moves
        for i in range(self.moves.n_moves):
            name = self.moves.move_name(moves.c[i].move, moves.c[i].label)
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
        set_dropout_rate(self.model, drop)
        # This is pretty dirty, but the NER can resize itself in init_batch,
        # if labels are missing. We therefore have to check whether we need to
        # expand our model output.
        self._resize()
        states, scores = self.model.predict((docs, self.moves))
        return states

    def beam_parse(self, docs, int beam_width, float drop=0., beam_density=0.):
        raise NotImplementedError

    def set_annotations(self, docs, states_or_beams):
        cdef StateClass state
        cdef Beam beam
        cdef Doc doc
        states = _beam_utils.collect_states(states_or_beams, docs)
        for i, (state, doc) in enumerate(zip(states, docs)):
            self.moves.set_annotations(state, doc)
            for hook in self.postprocesses:
                hook(doc)

    def update(self, examples, *, drop=0., sgd=None, losses=None):
        cdef StateClass state
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.)
        validate_examples(examples, "Parser.update")
        for multitask in self._multitasks:
            multitask.update(examples, drop=drop, sgd=sgd)
        # We need to take care to act on the whole batch, because we might be
        # getting vectors via a listener.
        n_examples = len([eg for eg in examples if self.moves.has_gold(eg)])
        if n_examples == 0:
            return losses
        set_dropout_rate(self.model, drop)
        docs = [eg.x for eg in examples]
        (states, scores), backprop_scores = self.model.begin_update((docs, self.moves))
        if sum(s.shape[0] for s in scores) == 0:
            return losses
        d_scores = self.get_loss((states, scores), examples)
        backprop_scores((states, d_scores))
        if sgd not in (None, False):
            self.finish_update(sgd)
        losses[self.name] += (d_scores**2).sum()
        # Ugh, this is annoying. If we're working on GPU, we want to free the
        # memory ASAP. It seems that Python doesn't necessarily get around to
        # removing these in time if we don't explicitly delete? It's confusing.
        del backprop_scores
        return losses

    def get_loss(self, states_scores, examples):
        states, scores = states_scores
        scores = self.model.ops.xp.vstack(scores)
        costs = self._get_costs_from_histories(
            examples,
            [list(state.history) for state in states]
        )
        xp = get_array_module(scores)
        best_costs = costs.min(axis=1, keepdims=True)
        gscores = scores.copy()
        min_score = scores.min()
        gscores[costs > best_costs] = min_score
        max_ = scores.max(axis=1, keepdims=True)
        gmax = gscores.max(axis=1, keepdims=True)
        exp_scores = xp.exp(scores - max_)
        exp_gscores = xp.exp(gscores - gmax)
        Z = exp_scores.sum(axis=1, keepdims=True)
        gZ = exp_gscores.sum(axis=1, keepdims=True)
        d_scores = exp_scores / Z
        d_scores -= (costs <= best_costs) * (exp_gscores / gZ)
        return d_scores

    def _get_costs_from_histories(self, examples, histories):
        cdef TransitionSystem moves = self.moves
        cdef StateClass state
        cdef int clas
        cdef int nF = self.model.get_dim("nF")
        cdef int nO = moves.n_moves
        cdef int nS = sum([len(history) for history in histories])
        cdef np.ndarray costs = numpy.zeros((nS, nO), dtype="f")
        cdef Pool mem = Pool()
        is_valid = <int*>mem.alloc(nO, sizeof(int))
        c_costs = <float*>costs.data
        states = moves.init_batch([eg.x for eg in examples])
        cdef int i = 0
        for eg, state, history in zip(examples, states, histories):
            gold = moves.init_gold(state, eg)
            for clas in history:
                moves.set_costs(is_valid, &c_costs[i*nO], state.c, gold)
                action = moves.c[clas]
                action.do(state.c, action.label)
                state.c.history.push_back(clas)
                i += 1
        # If the model is on GPU, copy the costs to device.
        costs = self.model.ops.asarray(costs)
        return costs

    def rehearse(self, examples, sgd=None, losses=None, **cfg):
        """Perform a "rehearsal" update, to prevent catastrophic forgetting."""
        raise NotImplementedError

    def update_beam(self, examples, *, beam_width,
            drop=0., sgd=None, losses=None, beam_density=0.0):
        raise NotImplementedError

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
        self.model.initialize((doc_sample, self.moves))
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
