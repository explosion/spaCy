import json
from os import path
from collections import defaultdict

from thinc.typedefs cimport atom_t, weight_t
from thinc.learner cimport arg_max, arg_max_if_true, arg_max_if_zero
from thinc.api cimport Example

from .typedefs cimport attr_t
from .tokens.doc cimport Doc
from .attrs cimport TAG
from .parts_of_speech cimport NO_TAG, ADJ, ADV, ADP, CONJ, DET, NOUN, NUM, PRON
from .parts_of_speech cimport VERB, X, PUNCT, EOL, SPACE

from .attrs cimport *

 
cpdef enum:
    P2_orth
    P2_cluster
    P2_shape
    P2_prefix
    P2_suffix
    P2_pos
    P2_lemma
    P2_flags

    P1_orth
    P1_cluster
    P1_shape
    P1_prefix
    P1_suffix
    P1_pos
    P1_lemma
    P1_flags

    W_orth
    W_cluster
    W_shape
    W_prefix
    W_suffix
    W_pos
    W_lemma
    W_flags

    N1_orth
    N1_cluster
    N1_shape
    N1_prefix
    N1_suffix
    N1_pos
    N1_lemma
    N1_flags

    N2_orth
    N2_cluster
    N2_shape
    N2_prefix
    N2_suffix
    N2_pos
    N2_lemma
    N2_flags

    N_CONTEXT_FIELDS


cdef class Tagger:
    """A part-of-speech tagger for English"""
    @classmethod
    def read_config(cls, data_dir):
        return json.load(open(path.join(data_dir, 'pos', 'config.json')))

    @classmethod
    def default_templates(cls):
        return (
            (W_orth,),
            (P1_lemma, P1_pos),
            (P2_lemma, P2_pos),
            (N1_orth,),
            (N2_orth,),

            (W_suffix,),
            (W_prefix,),

            (P1_pos,),
            (P2_pos,),
            (P1_pos, P2_pos),
            (P1_pos, W_orth),
            (P1_suffix,),
            (N1_suffix,),

            (W_shape,),
            (W_cluster,),
            (N1_cluster,),
            (N2_cluster,),
            (P1_cluster,),
            (P2_cluster,),

            (W_flags,),
            (N1_flags,),
            (N2_flags,),
            (P1_flags,),
            (P2_flags,),
        )

    @classmethod
    def blank(cls, vocab, templates):
        model = Model(vocab.morphology.n_tags, templates, model_loc=None)
        return cls(vocab, model)

    @classmethod
    def from_dir(cls, data_dir, vocab):
        if path.exists(path.join(data_dir, 'templates.json')):
            templates = json.loads(open(path.join(data_dir, 'templates.json')))
        else:
            templates = cls.default_templates()
        model = Model(vocab.morphology.n_tags, templates, data_dir)
        return cls(vocab, model)

    def __init__(self, Vocab vocab, model):
        self.vocab = vocab
        self.model = model
        
        # TODO: Move this to tag map
        self.freqs = {TAG: defaultdict(int)}
        for tag in self.tag_names:
            self.freqs[TAG][self.vocab.strings[tag]] = 1
        self.freqs[TAG][0] = 1

    @property
    def tag_names(self):
        return self.vocab.morphology.tag_names

    def __call__(self, Doc tokens):
        """Apply the tagger, setting the POS tags onto the Doc object.

        Args:
            tokens (Doc): The tokens to be tagged.
        """
        if tokens.length == 0:
            return 0

        cdef Example eg = self.model._eg
        cdef int i
        for i in range(tokens.length):
            if tokens.c[i].pos == 0:
                eg.wipe()
                fill_atoms(eg.c.atoms, tokens.c, i)
                self.model(eg)
                self.vocab.morphology.assign_tag(&tokens.c[i], eg.c.guess)

        tokens.is_tagged = True
        tokens._py_tokens = [None] * tokens.length

    def __reduce__(self):
        return (self.__class__, (self.vocab, self.model), None, None)

    def tag_from_strings(self, Doc tokens, object tag_strs):
        cdef int i
        for i in range(tokens.length):
            self.vocab.morphology.assign_tag(&tokens.c[i], tag_strs[i])
        tokens.is_tagged = True
        tokens._py_tokens = [None] * tokens.length

    def train(self, Doc tokens, object gold_tag_strs):
        assert len(tokens) == len(gold_tag_strs)
        cdef int i
        cdef int loss
        cdef const weight_t* scores
        try:
            golds = [self.tag_names.index(g) if g is not None else -1 for g in gold_tag_strs]
        except ValueError:
            raise ValueError(
                [g for g in gold_tag_strs if g is not None and g not in self.tag_names])
        correct = 0
        cdef Example eg = self.model._eg
        for i in range(tokens.length):
            eg.wipe()
            fill_atoms(eg.c.atoms, tokens.c, i)
            self.train(eg)

            self.vocab.morphology.assign_tag(&tokens.c[i], eg.c.guess)
            
            correct += eg.c.cost == 0
            self.freqs[TAG][tokens.c[i].tag] += 1
        return correct


cdef inline void fill_atoms(atom_t* atoms, const TokenC* tokens, int i) nogil:
    _fill_from_token(&atoms[P2_orth], &tokens[i-2])
    _fill_from_token(&atoms[P1_orth], &tokens[i-1])
    _fill_from_token(&atoms[W_orth], &tokens[i])
    _fill_from_token(&atoms[N1_orth], &tokens[i+1])
    _fill_from_token(&atoms[N2_orth], &tokens[i+2])
    

cdef inline void _fill_from_token(atom_t* context, const TokenC* t) nogil:
    context[0] = t.lex.lower
    context[1] = t.lex.cluster
    context[2] = t.lex.shape
    context[3] = t.lex.prefix
    context[4] = t.lex.suffix
    context[5] = t.tag
    context[6] = t.lemma
    if t.lex.flags & (1 << IS_ALPHA):
        context[7] = 1
    elif t.lex.flags & (1 << IS_PUNCT):
        context[7] = 2
    elif t.lex.flags & (1 << LIKE_URL):
        context[7] = 3
    elif t.lex.flags & (1 << LIKE_NUM):
        context[7] = 4
    else:
        context[7] = 0
