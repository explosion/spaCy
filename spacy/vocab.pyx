from __future__ import unicode_literals


from libc.stdio cimport fopen, fclose, fread, fwrite, FILE
from libc.string cimport memset
from libc.stdint cimport int32_t

import bz2
from os import path
import codecs
import math
import json

from .lexeme cimport EMPTY_LEXEME
from .lexeme cimport set_lex_struct_props
from .lexeme cimport Lexeme
from .strings cimport hash_string
from .orth cimport word_shape
from .typedefs cimport attr_t
from .cfile cimport CFile

from cymem.cymem cimport Address
from . import util
from .serialize.packer cimport Packer


DEF MAX_VEC_SIZE = 100000


cdef float[MAX_VEC_SIZE] EMPTY_VEC
memset(EMPTY_VEC, 0, sizeof(EMPTY_VEC))
memset(&EMPTY_LEXEME, 0, sizeof(LexemeC))
EMPTY_LEXEME.repvec = EMPTY_VEC


cdef class Vocab:
    '''A map container for a language's LexemeC structs.
    '''
    def __init__(self, data_dir=None, get_lex_props=None, load_vectors=True,
                 pos_tags=None, oov_prob=-30):
        if oov_prob is None:
            oov_prob = -30
        self.mem = Pool()
        self._by_hash = PreshMap()
        self._by_orth = PreshMap()
        self.strings = StringStore()
        self.pos_tags = pos_tags if pos_tags is not None else {}

        self.lexeme_props_getter = get_lex_props
        self.repvec_length = 0
        self.length = 0
        self._add_lex_to_vocab(0, &EMPTY_LEXEME)
        if data_dir is not None:
            if not path.exists(data_dir):
                raise IOError("Directory %s not found -- cannot load Vocab." % data_dir)
        if data_dir is not None:
            if not path.isdir(data_dir):
                raise IOError("Path %s is a file, not a dir -- cannot load Vocab." % data_dir)
            self.load_lexemes(path.join(data_dir, 'strings.txt'),
                              path.join(data_dir, 'lexemes.bin'))
            if load_vectors and path.exists(path.join(data_dir, 'vec.bin')):
                self.repvec_length = self.load_rep_vectors(path.join(data_dir, 'vec.bin'))

        self._serializer = None
        self.data_dir = data_dir
        self.oov_prob = oov_prob

    property serializer:
        def __get__(self):
            if self._serializer is None:
                freqs = []
                if self.data_dir is not None:
                    freqs_loc = path.join(self.data_dir, 'serializer.json')
                    if path.exists(freqs_loc):
                        freqs = json.load(open(freqs_loc))
                self._serializer = Packer(self, freqs)
            return self._serializer

    def __len__(self):
        """The current number of lexemes stored."""
        return self.length

    cdef const LexemeC* get(self, Pool mem, unicode string) except NULL:
        '''Get a pointer to a LexemeC from the lexicon, creating a new Lexeme
        if necessary, using memory acquired from the given pool.  If the pool
        is the lexicon's own memory, the lexeme is saved in the lexicon.'''
        if string == u'':
            return &EMPTY_LEXEME
        cdef LexemeC* lex
        cdef hash_t key = hash_string(string)
        lex = <LexemeC*>self._by_hash.get(key)
        if lex != NULL:
            return lex
        cdef bint is_oov = mem is not self.mem
        if len(string) < 3:
            mem = self.mem
        lex = <LexemeC*>mem.alloc(sizeof(LexemeC), 1)
        props = self.lexeme_props_getter(string, self.oov_prob)
        set_lex_struct_props(lex, props, self.strings, EMPTY_VEC)
        if is_oov:
            lex.id = 0
        else:
            self._add_lex_to_vocab(key, lex)
        return lex

    cdef const LexemeC* get_by_orth(self, Pool mem, attr_t orth) except NULL:
        '''Get a pointer to a LexemeC from the lexicon, creating a new Lexeme
        if necessary, using memory acquired from the given pool.  If the pool
        is the lexicon's own memory, the lexeme is saved in the lexicon.'''
        if orth == 0:
            return &EMPTY_LEXEME
        cdef LexemeC* lex
        lex = <LexemeC*>self._by_orth.get(orth)
        if lex != NULL:
            return lex
        cdef unicode string = self.strings[orth]
        cdef bint is_oov = mem is not self.mem
        if len(string) < 3:
            mem = self.mem
        lex = <LexemeC*>mem.alloc(sizeof(LexemeC), 1)
        props = self.lexeme_props_getter(string)
        set_lex_struct_props(lex, props, self.strings, EMPTY_VEC)
        if is_oov:
            lex.id = 0
        else:
            self._add_lex_to_vocab(hash_string(string), lex)
        return lex

    cdef int _add_lex_to_vocab(self, hash_t key, const LexemeC* lex) except -1:
        self._by_hash.set(key, <void*>lex)
        self._by_orth.set(lex.orth, <void*>lex)
        self.length += 1

    def __iter__(self):
        cdef attr_t orth
        cdef size_t addr
        for orth, addr in self._by_orth.items():
            yield Lexeme.from_ptr(<LexemeC*>addr, self.strings, self.repvec_length)

    def __getitem__(self,  id_or_string):
        '''Retrieve a lexeme, given an int ID or a unicode string.  If a previously
        unseen unicode string is given, a new lexeme is created and stored.

        Args:
            id_or_string (int or unicode):
              The integer ID of a word, or its unicode string.  If an int >= Lexicon.size,
              IndexError is raised. If id_or_string is neither an int nor a unicode string,
              ValueError is raised.

        Returns:
            lexeme (Lexeme):
              An instance of the Lexeme Python class, with data copied on
              instantiation.
        '''
        cdef const LexemeC* lexeme
        cdef attr_t orth
        if type(id_or_string) == int:
            orth = id_or_string
            lexeme = <LexemeC*>self._by_orth.get(orth)
            if lexeme == NULL:
                raise KeyError(id_or_string)
            assert lexeme.orth == orth, ('%d vs %d' % (lexeme.orth, orth))
        elif type(id_or_string) == unicode:
            lexeme = self.get(self.mem, id_or_string)
            assert lexeme.orth == self.strings[id_or_string]
        else:
            raise ValueError("Vocab unable to map type: "
                "%s. Maps unicode --> Lexeme or "
                "int --> Lexeme" % str(type(id_or_string)))
        return Lexeme.from_ptr(lexeme, self.strings, self.repvec_length)

    def __setitem__(self, unicode string, dict props):
        cdef hash_t key = hash_string(string)
        cdef LexemeC* lex
        lex = <LexemeC*>self._by_hash.get(key)
        if lex == NULL:
            lex = <LexemeC*>self.mem.alloc(sizeof(LexemeC), 1)
        set_lex_struct_props(lex, props, self.strings, EMPTY_VEC)
        self._add_lex_to_vocab(key, lex)

    def dump(self, loc):
        if path.exists(loc):
            assert not path.isdir(loc)
        cdef bytes bytes_loc = loc.encode('utf8') if type(loc) == unicode else loc

        cdef CFile fp = CFile(bytes_loc, 'wb')
        cdef size_t st
        cdef size_t addr
        cdef hash_t key
        for key, addr in self._by_hash.items():
            lexeme = <LexemeC*>addr
            fp.write_from(&lexeme.orth, sizeof(lexeme.orth), 1)
            fp.write_from(lexeme, sizeof(LexemeC), 1)
        fp.close()

    def load_lexemes(self, strings_loc, loc):
        self.strings.load(strings_loc)
        if not path.exists(loc):
            raise IOError('LexemeCs file not found at %s' % loc)
        cdef bytes bytes_loc = loc.encode('utf8') if type(loc) == unicode else loc
        cdef FILE* fp = fopen(<char*>bytes_loc, b'rb')
        if fp == NULL:
            raise IOError('lexemes data file present, but cannot open from ' % loc)
        cdef size_t st
        cdef LexemeC* lexeme
        cdef attr_t orth
        cdef hash_t key
        cdef unicode py_str
        i = 0
        while True:
            st = fread(&orth, sizeof(orth), 1, fp)
            if st != 1:
                break
            lexeme = <LexemeC*>self.mem.alloc(sizeof(LexemeC), 1)
            # Copies data from the file into the lexeme
            st = fread(lexeme, sizeof(LexemeC), 1, fp)
            lexeme.repvec = EMPTY_VEC
            if st != 1:
                break
            if orth != lexeme.orth:
                # TODO: Improve this error message, pending resolution to Issue #64
                raise IOError('Error reading from lexemes.bin. Integrity check fails.')
            py_str = self.strings[orth]
            key = hash_string(py_str)
            self._by_hash.set(key, lexeme)
            self._by_orth.set(lexeme.orth, lexeme)
            self.length += 1
            i += 1
        fclose(fp)

    def load_rep_vectors(self, loc):
        cdef CFile file_ = CFile(loc, b'rb')
        cdef int32_t word_len
        cdef int32_t vec_len
        cdef int32_t prev_vec_len = 0
        cdef float* vec
        cdef Address mem
        cdef attr_t string_id
        cdef bytes py_word
        cdef vector[float*] vectors
        cdef int i
        cdef Pool tmp_mem = Pool()
        while True:
            try:
                file_.read_into(&word_len, sizeof(word_len), 1)
            except IOError:
                break
            file_.read_into(&vec_len, sizeof(vec_len), 1)
            if prev_vec_len != 0 and vec_len != prev_vec_len:
                raise VectorReadError.mismatched_sizes(loc, vec_len, prev_vec_len)
            if 0 >= vec_len >= MAX_VEC_SIZE:
                raise VectorReadError.bad_size(loc, vec_len)

            chars = <char*>file_.alloc_read(tmp_mem, word_len, sizeof(char))
            vec = <float*>file_.alloc_read(self.mem, vec_len, sizeof(float))

            string_id = self.strings[chars[:word_len]]
            while string_id >= vectors.size():
                vectors.push_back(EMPTY_VEC)
            assert vec != NULL
            vectors[string_id] = vec
        cdef LexemeC* lex
        cdef size_t lex_addr
        for orth, lex_addr in self._by_orth.items():
            lex = <LexemeC*>lex_addr
            if lex.lower < vectors.size():
                lex.repvec = vectors[lex.lower]
                for i in range(vec_len):
                    lex.l2_norm += (lex.repvec[i] * lex.repvec[i])
                lex.l2_norm = math.sqrt(lex.l2_norm)
            else:
                lex.repvec = EMPTY_VEC
        return vec_len


def write_binary_vectors(in_loc, out_loc):
    cdef CFile out_file = CFile(out_loc, 'wb')
    cdef Address mem
    cdef int32_t word_len
    cdef int32_t vec_len
    cdef char* chars
    with bz2.BZ2File(in_loc, 'r') as file_:
        for line in file_:
            pieces = line.split()
            word = pieces.pop(0)
            mem = Address(len(pieces), sizeof(float))
            vec = <float*>mem.ptr
            for i, val_str in enumerate(pieces):
                vec[i] = float(val_str)

            word_len = len(word)
            vec_len = len(pieces)

            out_file.write_from(&word_len, 1, sizeof(word_len))
            out_file.write_from(&vec_len, 1, sizeof(vec_len))

            chars = <char*>word
            out_file.write_from(chars, len(word), sizeof(char))
            out_file.write_from(vec, vec_len, sizeof(float))


class VectorReadError(Exception):
    @classmethod
    def mismatched_sizes(cls, loc, prev_size, curr_size):
        return cls(
            "Error reading word vectors from %s.\n"
            "All vectors must be the same size.\n"
            "Prev size: %d\n"
            "Curr size: %d" % (loc, prev_size, curr_size))

    @classmethod
    def bad_size(cls, loc, size):
        return cls(
            "Error reading word vectors from %s.\n"
            "Vector size: %d\n"
            "Max size: %d\n"
            "Min size: 1\n" % (loc, size, MAX_VEC_SIZE))
