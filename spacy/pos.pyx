# cython: profile=True
from os import path
import os
import shutil
import ujson
import random
import codecs
import gzip
import cython

from libc.stdint cimport uint32_t


from thinc.weights cimport arg_max
from thinc.features import NonZeroConjFeat
from thinc.features import ConjFeat

from .lexeme cimport *
from .lang cimport Lexicon


NULL_TAG = 0


cdef class Tagger:
    tags = {'NULL': NULL_TAG}
    def __init__(self, model_dir):
        self.mem = Pool()
        tags_loc = path.join(model_dir, 'postags.json')
        if path.exists(tags_loc):
            with open(tags_loc) as file_:
                Tagger.tags.update(ujson.load(file_))
        self.model = LinearModel(len(self.tags), self.extractor.n)
        if path.exists(path.join(model_dir, 'model')):
            self.model.load(path.join(model_dir, 'model'))
        self.extractor = Extractor(TEMPLATES, [ConjFeat for _ in TEMPLATES])
        self._atoms = <atom_t*>self.mem.alloc(CONTEXT_SIZE, sizeof(atom_t))
        self._feats = <feat_t*>self.mem.alloc(self.extractor.n+1, sizeof(feat_t))
        self._values = <weight_t*>self.mem.alloc(self.extractor.n+1, sizeof(weight_t))
        self._scores = <weight_t*>self.mem.alloc(len(self.tags), sizeof(weight_t))
        self._guess = NULL_TAG
            
    cpdef class_t predict(self, int i, Tokens tokens, class_t prev, class_t prev_prev) except 0:
        get_atoms(self._atoms, tokens.lex[i-2], tokens.lex[i-1], tokens.lex[i],
                  tokens.lex[i+1], tokens.lex[i+2], prev, prev_prev)
        self.extractor.extract(self._feats, self._values, self._atoms, NULL)
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


@cython.boundscheck(False)
def count_tags(Tagger tagger, Tokens tokens, uint32_t[:, :] tag_counts):
    cdef class_t prev_prev, prev, tag
    prev = tagger.tags['EOL']; prev_prev = tagger.tags['EOL']
    cdef int i
    cdef id_t token
    for i in range(tokens.length):
        tag = tagger.predict(i, tokens, prev, prev_prev)
        prev_prev = prev
        prev = tag
        token = tokens.lex[i].id
        if token < tag_counts.shape[0]:
            tag_counts[token, tag] += 1


cpdef enum:
    P2i
    P2c
    P2w
    P2shape
    P2pref
    P2suff
    P2oft_title
    P2oft_upper
    P2pos
    P2url
    P2num

    P1i
    P1c
    P1w
    P1shape
    P1pre
    P1suff
    P1oft_title
    P1oft_upper
    P1pos
    P1url
    P1num

    N0i
    N0c
    N0w
    N0shape
    N0pref
    N0suff
    N0oft_title
    N0oft_upper
    N0pos
    N0url
    N0num

    N1i
    N1c
    N1w
    N1shape
    N1pref
    N1suff
    N1oft_title
    N1oft_upper
    N1pos
    N1url
    N1num

    N2i
    N2c
    N2w
    N2shape
    N2pref
    N2suff
    N2oft_title
    N2oft_upper
    N2pos
    N2url
    N2num

    P2t
    P1t

    CONTEXT_SIZE


cdef int get_atoms(atom_t* atoms, Lexeme* p2, Lexeme* p1, Lexeme* n0, Lexeme* n1,
                   Lexeme* n2, class_t prev_tag, class_t prev_prev_tag) except -1:
    _fill_token(&atoms[P2i], p2)
    _fill_token(&atoms[P1i], p1)
    _fill_token(&atoms[N0i], n0)
    _fill_token(&atoms[N1i], n1)
    _fill_token(&atoms[N2i], n2)
    atoms[P1t] = prev_tag
    atoms[P2t] = prev_prev_tag


cdef inline void _fill_token(atom_t* atoms, Lexeme* lex) nogil:
    atoms[0] = lex.sic
    atoms[1] = lex.cluster
    atoms[2] = lex.norm
    atoms[3] = lex.shape
    atoms[4] = lex.prefix
    atoms[5] = lex.suffix

    atoms[6] = lex.flags & (1 << OFT_TITLE)
    atoms[7] = lex.flags & (1 << OFT_UPPER)
    atoms[8] = lex.postype
    atoms[9] = lex.flags & (1 << LIKE_URL)
    atoms[10] = lex.flags & (1 << LIKE_NUMBER)


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

    (P1t, N1w),
    (P1t, P2t, N1w),
    (P1w, P2w, N1w),
    (P2w, N1w, N2w),

    (N0pos,),
    (N0w, N1pos),
    (N0w, N1pos, N2pos),
    (P1t, N0pos),
    (P2t, P1t, N0pos),

    (P2url,),
    (P1url,),
    (N0url,),
    (N1url,),
    (N2url,),

    (P2num,),
    (P1num,),
    (N0num,),
    (N1num,),
    (N2num,),
)
