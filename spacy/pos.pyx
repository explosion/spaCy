# cython: profile=True
from os import path
import os
import shutil
import ujson
import random
import codecs
import gzip


from thinc.weights cimport arg_max
from thinc.features import NonZeroConjFeat
from thinc.features import ConjFeat

from .en import EN
from .lexeme cimport LexStr_shape, LexStr_suff, LexStr_pre, LexStr_norm
from .lexeme cimport LexDist_upper, LexDist_title
from .lexeme cimport LexDist_upper, LexInt_cluster, LexInt_id


NULL_TAG = 0


cdef class Tagger:
    tags = {'NULL': NULL_TAG}
    def __init__(self, model_dir):
        self.mem = Pool()
        self.extractor = Extractor(TEMPLATES, [ConjFeat for _ in TEMPLATES])
        self.model = LinearModel(len(self.tags), self.extractor.n)
        self._atoms = <atom_t*>self.mem.alloc(CONTEXT_SIZE, sizeof(atom_t))
        self._feats = <feat_t*>self.mem.alloc(self.extractor.n+1, sizeof(feat_t))
        self._values = <weight_t*>self.mem.alloc(self.extractor.n+1, sizeof(weight_t))
        self._scores = <weight_t*>self.mem.alloc(len(self.tags), sizeof(weight_t))
        self._guess = NULL_TAG
        if path.exists(path.join(model_dir, 'model.gz')):
            with gzip.open(path.join(model_dir, 'model.gz'), 'r') as file_:
                self.model.load(file_)

    cpdef class_t predict(self, int i, Tokens tokens, class_t prev, class_t prev_prev) except 0:
        get_atoms(self._atoms, i, tokens, prev, prev_prev)
        self.extractor.extract(self._feats, self._values, self._atoms, NULL)
        assert self._feats[self.extractor.n] == 0
        self._guess = self.model.score(self._scores, self._feats, self._values)
        return self._guess

    cpdef bint tell_answer(self, class_t gold) except *:
        cdef class_t guess = self._guess
        if gold == guess or gold == NULL_TAG:
            self.model.update({})
            return 0
        counts = {guess: {}, gold: {}}
        self.extractor.count(counts[gold], self._feats, 1)
        self.extractor.count(counts[guess], self._feats, -1)
        self.model.update(counts)

    @classmethod
    def encode_pos(cls, tag):
        if tag not in cls.tags:
            cls.tags[tag] = len(cls.tags)
        return cls.tags[tag]


cpdef enum:
    P2i
    P1i
    N0i
    N1i
    N2i
    
    P2c
    P1c
    N0c
    N1c
    N2c
    
    P2shape
    P1shape
    N0shape
    N1shape
    N2shape

    P2suff
    P1suff
    N0suff
    N1suff
    N2suff

    P2pref
    P1pref
    N0pref
    N1pref
    N2pref

    P2w
    P1w
    N0w
    N1w
    N2w

    P2oft_title
    P1oft_title
    N0oft_title
    N1oft_title
    N2oft_title

    P2oft_upper
    P1oft_upper
    N0oft_upper
    N1oft_upper
    N2oft_upper

    P1t
    P2t
    CONTEXT_SIZE


cdef int get_atoms(atom_t* context, int i, Tokens tokens, class_t prev_tag,
                   class_t prev_prev_tag) except -1:
    cdef int j
    for j in range(CONTEXT_SIZE):
        context[j] = 0
    cdef int[5] indices
    indices[0] = i-2
    indices[1] = i-1
    indices[2] = i
    indices[3] = i+1
    indices[4] = i+2

    cdef int[2] int_feats
    int_feats[0] = <int>LexInt_id
    int_feats[1] = <int>LexInt_cluster

    cdef int[4] string_feats
    string_feats[0] = <int>LexStr_shape
    string_feats[1] = <int>LexStr_suff
    string_feats[2] = <int>LexStr_pre
    string_feats[3] = <int>LexStr_norm

    cdef int[2] bool_feats
    bool_feats[0] = <int>LexDist_title
    bool_feats[1] = <int>LexDist_upper

    cdef int c = 0
    c = tokens.int_array(context, c, indices, 5, int_feats, 2)
    c = tokens.string_array(context, c, indices, 5, string_feats, 4)
    c = tokens.bool_array(context, c, indices, 5, bool_feats, 2)
    context[P1t] = prev_tag
    context[P2t] = prev_prev_tag


TEMPLATES = (
    (N0i,),
    (N0w,),
    (N0suff,),
    (N0pref,),
    (P1t,),
    (P2t,),
    (P1t, P2t),
    (P1t, N0w),
    (P1w,),
    (P1suff,),
    (P2w,),
    (N1w,),
    (N1suff,),
    (N2w,),

    (N0shape,),
    (N0c,),
    (N1c,),
    (N2c,),
    (P1c,),
    (P2c,),
    (N0oft_upper,),
    (N0oft_title,),
)

