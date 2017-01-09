# cython: infer_types=True
"""
MALT-style dependency parser
"""
from __future__ import unicode_literals
cimport cython
cimport cython.parallel

from cpython.ref cimport PyObject, Py_INCREF, Py_XDECREF
from cpython.exc cimport PyErr_CheckSignals

from libc.stdint cimport uint32_t, uint64_t
from libc.string cimport memset, memcpy
from libc.stdlib cimport malloc, calloc, free
import os.path
from os import path
import shutil
import json
import sys
from .nonproj import PseudoProjectivity

from cymem.cymem cimport Pool, Address
from murmurhash.mrmr cimport hash64
from thinc.typedefs cimport weight_t, class_t, feat_t, atom_t, hash_t
from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.linalg cimport VecVec
from thinc.structs cimport SparseArrayC
from preshed.maps cimport MapStruct
from preshed.maps cimport map_get
from thinc.structs cimport FeatureC

from util import Config

from ..structs cimport TokenC

from ..tokens.doc cimport Doc
from ..strings cimport StringStore

from .transition_system import OracleError
from .transition_system cimport TransitionSystem, Transition

from ..gold cimport GoldParse

from . import _parse_features
from ._parse_features cimport CONTEXT_SIZE
from ._parse_features cimport fill_context
from .stateclass cimport StateClass
from ._state cimport StateC


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
    elif name.startswith('embed'):
        return (pf.words, pf.tags, pf.labels)
    else:
        return (pf.unigrams + pf.s0_n0 + pf.s1_n0 + pf.s1_s0 + pf.s0_n1 + pf.n0_n1 + \
                pf.tree_shape + pf.trigrams)


cdef class ParserModel(AveragedPerceptron):
    cdef void set_featuresC(self, ExampleC* eg, const StateC* state) nogil: 
        fill_context(eg.atoms, state)
        eg.nr_feat = self.extracter.set_features(eg.features, eg.atoms)


cdef class Parser:
    """Base class of the DependencyParser and EntityRecognizer."""
    @classmethod
    def load(cls, path, Vocab vocab, TransitionSystem=None, require=False, **cfg):
        """Load the statistical model from the supplied path.

        Arguments:
            path (Path):
                The path to load from.
            vocab (Vocab):
                The vocabulary. Must be shared by the documents to be processed.
            require (bool):
                Whether to raise an error if the files are not found.
        Returns (Parser):
            The newly constructed object.
        """
        with (path / 'config.json').open() as file_:
            cfg = json.load(file_)
        # TODO: remove this shim when we don't have to support older data
        if 'labels' in cfg and 'actions' not in cfg:
            cfg['actions'] = cfg.pop('labels')
        self = cls(vocab, TransitionSystem=TransitionSystem, model=None, **cfg)
        if (path / 'model').exists():
            self.model.load(str(path / 'model'))
        elif require:
            raise IOError(
                "Required file %s/model not found when loading" % str(path))
        return self

    def __init__(self, Vocab vocab, TransitionSystem=None, ParserModel model=None, **cfg):
        """Create a Parser.

        Arguments:
            vocab (Vocab):
                The vocabulary object. Must be shared with documents to be processed.
            model (thinc.linear.AveragedPerceptron):
                The statistical model.
        Returns (Parser):
            The newly constructed object.
        """
        if TransitionSystem is None:
            TransitionSystem = self.TransitionSystem
        self.vocab = vocab
        actions = TransitionSystem.get_actions(**cfg)
        self.moves = TransitionSystem(vocab.strings, actions)
        # TODO: Remove this when we no longer need to support old-style models
        if isinstance(cfg.get('features'), basestring):
            cfg['features'] = get_templates(cfg['features'])
        elif 'features' not in cfg:
            cfg['features'] = self.feature_templates
        self.model = ParserModel(cfg['features'])
        self.cfg = cfg

    def __reduce__(self):
        return (Parser, (self.vocab, self.moves, self.model), None, None)

    def __call__(self, Doc tokens):
        """Apply the entity recognizer, setting the annotations onto the Doc object.

        Arguments:
            doc (Doc): The document to be processed.
        Returns:
            None
        """
        cdef int nr_feat = self.model.nr_feat
        with nogil:
            status = self.parseC(tokens.c, tokens.length, nr_feat)
        # Check for KeyboardInterrupt etc. Untested
        PyErr_CheckSignals()
        if status != 0:
            raise ParserStateError(tokens)
        self.moves.finalize_doc(tokens)

    def pipe(self, stream, int batch_size=1000, int n_threads=2):
        """Process a stream of documents.

        Arguments:
            stream: The sequence of documents to process.
            batch_size (int):
                The number of documents to accumulate into a working set.
            n_threads (int):
                The number of threads with which to work on the buffer in parallel.
        Yields (Doc): Documents, in order.
        """
        cdef Pool mem = Pool()
        cdef TokenC** doc_ptr = <TokenC**>mem.alloc(batch_size, sizeof(TokenC*))
        cdef int* lengths = <int*>mem.alloc(batch_size, sizeof(int))
        cdef Doc doc
        cdef int i
        cdef int nr_feat = self.model.nr_feat
        cdef int status
        queue = []
        for doc in stream:
            doc_ptr[len(queue)] = doc.c
            lengths[len(queue)] = doc.length
            queue.append(doc)
            if len(queue) == batch_size:
                with nogil:
                    for i in cython.parallel.prange(batch_size, num_threads=n_threads):
                        status = self.parseC(doc_ptr[i], lengths[i], nr_feat)
                        if status != 0:
                            with gil:
                                raise ParserStateError(queue[i])
                PyErr_CheckSignals()
                for doc in queue:
                    self.moves.finalize_doc(doc)
                    yield doc
                queue = []
        batch_size = len(queue)
        with nogil:
            for i in cython.parallel.prange(batch_size, num_threads=n_threads):
                status = self.parseC(doc_ptr[i], lengths[i], nr_feat)
                if status != 0:
                    with gil:
                        raise ParserStateError(queue[i])
        PyErr_CheckSignals()
        for doc in queue:
            self.moves.finalize_doc(doc)
            yield doc

    cdef int parseC(self, TokenC* tokens, int length, int nr_feat) nogil:
        state = new StateC(tokens, length)
        # NB: This can change self.moves.n_moves!
        self.moves.initialize_state(state)
        nr_class = self.moves.n_moves

        cdef ExampleC eg
        eg.nr_feat = nr_feat
        eg.nr_atom = CONTEXT_SIZE
        eg.nr_class = nr_class
        eg.features = <FeatureC*>calloc(sizeof(FeatureC), nr_feat)
        eg.atoms = <atom_t*>calloc(sizeof(atom_t), CONTEXT_SIZE)
        eg.scores = <weight_t*>calloc(sizeof(weight_t), nr_class)
        eg.is_valid = <int*>calloc(sizeof(int), nr_class)
        cdef int i
        while not state.is_final():
            self.model.set_featuresC(&eg, state)
            self.moves.set_valid(eg.is_valid, state)
            self.model.set_scoresC(eg.scores, eg.features, eg.nr_feat)

            guess = VecVec.arg_max_if_true(eg.scores, eg.is_valid, eg.nr_class)

            action = self.moves.c[guess]
            if not eg.is_valid[guess]:
                return 1

            action.do(state, action.label)
            memset(eg.scores, 0, sizeof(eg.scores[0]) * eg.nr_class)
            for i in range(eg.nr_class):
                eg.is_valid[i] = 1
        self.moves.finalize_state(state)
        for i in range(length):
            tokens[i] = state._sent[i]
        del state
        free(eg.features)
        free(eg.atoms)
        free(eg.scores)
        free(eg.is_valid)
        return 0
  
    def update(self, Doc tokens, GoldParse gold):
        """Update the statistical model.

        Arguments:
            doc (Doc):
                The example document for the update.
            gold (GoldParse):
                The gold-standard annotations, to calculate the loss.
        Returns (float):
            The loss on this example.
        """
        self.moves.preprocess_gold(gold)
        cdef StateClass stcls = StateClass.init(tokens.c, tokens.length)
        self.moves.initialize_state(stcls.c)
        cdef Pool mem = Pool()
        cdef Example eg = Example(
                nr_class=self.moves.n_moves,
                nr_atom=CONTEXT_SIZE,
                nr_feat=self.model.nr_feat)
        cdef weight_t loss = 0
        cdef Transition action
        while not stcls.is_final():
            self.model.set_featuresC(&eg.c, stcls.c)
            self.moves.set_costs(eg.c.is_valid, eg.c.costs, stcls, gold)
            self.model.set_scoresC(eg.c.scores, eg.c.features, eg.c.nr_feat)
            self.model.updateC(&eg.c)
            guess = VecVec.arg_max_if_true(eg.c.scores, eg.c.is_valid, eg.c.nr_class)

            action = self.moves.c[eg.guess]
            action.do(stcls.c, action.label)
            loss += eg.costs[eg.guess]
            eg.fill_scores(0, eg.nr_class)
            eg.fill_costs(0, eg.nr_class)
            eg.fill_is_valid(1, eg.nr_class)
        return loss

    def step_through(self, Doc doc):
        """Set up a stepwise state, to introspect and control the transition sequence.

        Arguments:
            doc (Doc): The document to step through.
        Returns (StepwiseState):
            A state object, to step through the annotation process.
        """
        return StepwiseState(self, doc)

    def from_transition_sequence(self, Doc doc, sequence):
        """Control the annotations on a document by specifying a transition sequence
        to follow.

        Arguments:
            doc (Doc): The document to annotate.
            sequence: A sequence of action names, as unicode strings.
        Returns: None
        """
        with self.step_through(doc) as stepwise:
            for transition in sequence:
                stepwise.transition(transition)

    def add_label(self, label):
        # Doesn't set label into serializer -- subclasses override it to do that.
        for action in self.moves.action_types:
            self.moves.add_action(action, label)
                

cdef class StepwiseState:
    cdef readonly StateClass stcls
    cdef readonly Example eg
    cdef readonly Doc doc
    cdef readonly Parser parser

    def __init__(self, Parser parser, Doc doc):
        self.parser = parser
        self.doc = doc
        self.stcls = StateClass.init(doc.c, doc.length)
        self.parser.moves.initialize_state(self.stcls.c)
        self.eg = Example(
            nr_class=self.parser.moves.n_moves,
            nr_atom=CONTEXT_SIZE,
            nr_feat=self.parser.model.nr_feat)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.finish()

    @property
    def is_final(self):
        return self.stcls.is_final()

    @property
    def stack(self):
        return self.stcls.stack

    @property
    def queue(self):
        return self.stcls.queue

    @property
    def heads(self):
        return [self.stcls.H(i) for i in range(self.stcls.c.length)]

    @property
    def deps(self):
        return [self.doc.vocab.strings[self.stcls.c._sent[i].dep]
                for i in range(self.stcls.c.length)]

    def predict(self):
        self.eg.reset()
        self.parser.model.set_featuresC(&self.eg.c, self.stcls.c)
        self.parser.moves.set_valid(self.eg.c.is_valid, self.stcls.c)
        self.parser.model.set_scoresC(self.eg.c.scores,
            self.eg.c.features, self.eg.c.nr_feat)

        cdef Transition action = self.parser.moves.c[self.eg.guess]
        return self.parser.moves.move_name(action.move, action.label)

    def transition(self, action_name=None):
        if action_name is None:
            action_name = self.predict()
        moves = {'S': 0, 'D': 1, 'L': 2, 'R': 3}
        if action_name == '_':
            action_name = self.predict()
            action = self.parser.moves.lookup_transition(action_name)
        elif action_name == 'L' or action_name == 'R':
            self.predict()
            move = moves[action_name]
            clas = _arg_max_clas(self.eg.c.scores, move, self.parser.moves.c,
                                 self.eg.c.nr_class)
            action = self.parser.moves.c[clas]
        else:
            action = self.parser.moves.lookup_transition(action_name)
        action.do(self.stcls.c, action.label)

    def finish(self):
        if self.stcls.is_final():
            self.parser.moves.finalize_state(self.stcls.c)
        self.doc.set_parse(self.stcls.c._sent)
        self.parser.moves.finalize_doc(self.doc)


class ParserStateError(ValueError):
    def __init__(self, doc):
        ValueError.__init__(self,
            "Error analysing doc -- no valid actions available. This should "
            "never happen, so please report the error on the issue tracker. "
            "Here's the thread to do so --- reopen it if it's closed:\n"
            "https://github.com/spacy-io/spaCy/issues/429\n"
            "Please include the text that the parser failed on, which is:\n"
            "%s" % repr(doc.text))


cdef int _arg_max_clas(const weight_t* scores, int move, const Transition* actions,
                       int nr_class) except -1:
    cdef weight_t score = 0
    cdef int mode = -1
    cdef int i
    for i in range(nr_class):
        if actions[i].move == move and (mode == -1 or scores[i] >= score):
            mode = i
            score = scores[i]
    return mode
