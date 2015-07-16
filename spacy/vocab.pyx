from libc.stdio cimport fopen, fclose, fread, fwrite, FILE
from libc.string cimport memset
from libc.stdint cimport int32_t
from libc.math cimport exp as c_exp

import bz2
from os import path
import codecs
import math

from .lexeme cimport EMPTY_LEXEME
from .lexeme cimport set_lex_struct_props
from .lexeme cimport Lexeme
from .strings cimport slice_unicode
from .strings cimport hash_string
from .orth cimport word_shape
from .typedefs cimport attr_t
from .serialize cimport HuffmanCodec

from cymem.cymem cimport Address


DEF MAX_VEC_SIZE = 100000


cdef float[MAX_VEC_SIZE] EMPTY_VEC
memset(EMPTY_VEC, 0, sizeof(EMPTY_VEC))
memset(&EMPTY_LEXEME, 0, sizeof(LexemeC))
EMPTY_LEXEME.repvec = EMPTY_VEC


cdef class Vocab:
    '''A map container for a language's LexemeC structs.
    '''
    def __init__(self, data_dir=None, get_lex_props=None, load_vectors=True,
                 pos_tags=None):
        self.mem = Pool()
        self._map = PreshMap(2 ** 20)
        self.strings = StringStore()
        self.pos_tags = pos_tags if pos_tags is not None else {}
        self.lexemes.push_back(&EMPTY_LEXEME)
        self.lexeme_props_getter = get_lex_props
        self.repvec_length = 0
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
        self._codec = None

    def __len__(self):
        """The current number of lexemes stored."""
        return self.lexemes.size()

    cdef const LexemeC* get(self, Pool mem, UniStr* c_str) except NULL:
        '''Get a pointer to a LexemeC from the lexicon, creating a new Lexeme
        if necessary, using memory acquired from the given pool.  If the pool
        is the lexicon's own memory, the lexeme is saved in the lexicon.'''
        cdef LexemeC* lex
        lex = <LexemeC*>self._map.get(c_str.key)
        if lex != NULL:
            return lex
        if c_str.n < 3:
            mem = self.mem
        cdef unicode py_str = c_str.chars[:c_str.n]
        lex = <LexemeC*>mem.alloc(sizeof(LexemeC), 1)
        props = self.lexeme_props_getter(py_str)
        set_lex_struct_props(lex, props, self.strings, EMPTY_VEC)
        if mem is self.mem:
            lex.id = self.lexemes.size()
            self._add_lex_to_vocab(c_str.key, lex)
        else:
            lex.id = 1
        return lex

    cdef int _add_lex_to_vocab(self, hash_t key, const LexemeC* lex) except -1:
        self._map.set(key, <void*>lex)
        while self.lexemes.size() < (lex.id + 1):
            self.lexemes.push_back(&EMPTY_LEXEME)
        self.lexemes[lex.id] = lex

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
        cdef UniStr c_str
        cdef const LexemeC* lexeme
        if type(id_or_string) == int:
            if id_or_string >= self.lexemes.size():
                raise IndexError
            lexeme = self.lexemes.at(id_or_string)
        elif type(id_or_string) == unicode:
            slice_unicode(&c_str, id_or_string, 0, len(id_or_string))
            lexeme = self.get(self.mem, &c_str)
        else:
            raise ValueError("Vocab unable to map type: "
                "%s. Maps unicode --> Lexeme or "
                "int --> Lexeme" % str(type(id_or_string)))
        return Lexeme.from_ptr(lexeme, self.strings, self.repvec_length)

    def __setitem__(self, unicode py_str, dict props):
        cdef UniStr c_str
        slice_unicode(&c_str, py_str, 0, len(py_str))
        cdef LexemeC* lex
        lex = <LexemeC*>self._map.get(c_str.key)
        if lex == NULL:
            lex = <LexemeC*>self.mem.alloc(sizeof(LexemeC), 1)
            lex.id = self.lexemes.size()
            self._add_lex_to_vocab(c_str.key, lex)
        set_lex_struct_props(lex, props, self.strings, EMPTY_VEC)

    def dump(self, loc):
        if path.exists(loc):
            assert not path.isdir(loc)
        cdef bytes bytes_loc = loc.encode('utf8') if type(loc) == unicode else loc
        cdef FILE* fp = fopen(<char*>bytes_loc, 'wb')
        assert fp != NULL
        cdef size_t st
        cdef hash_t key
        for i in range(self._map.length):
            key = self._map.c_map.cells[i].key
            if key == 0:
                continue
            lexeme = <LexemeC*>self._map.c_map.cells[i].value
            st = fwrite(&lexeme.orth, sizeof(lexeme.orth), 1, fp)
            assert st == 1
            st = fwrite(lexeme, sizeof(LexemeC), 1, fp)
            assert st == 1
        st = fclose(fp)
        assert st == 0

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
            self._map.set(key, lexeme)
            while self.lexemes.size() < (lexeme.id + 1):
                self.lexemes.push_back(&EMPTY_LEXEME)
            self.lexemes[lexeme.id] = lexeme
            i += 1
        fclose(fp)

    def load_rep_vectors(self, loc):
        file_ = _CFile(loc, b'rb')
        cdef int32_t word_len
        cdef int32_t vec_len
        cdef int32_t prev_vec_len = 0
        cdef float* vec
        cdef Address mem
        cdef id_t string_id
        cdef bytes py_word
        cdef vector[float*] vectors
        cdef int i
        while True:
            try:
                file_.read(&word_len, sizeof(word_len), 1)
            except IOError:
                break
            file_.read(&vec_len, sizeof(vec_len), 1)
            if prev_vec_len != 0 and vec_len != prev_vec_len:
                raise VectorReadError.mismatched_sizes(loc, vec_len, prev_vec_len)
            if 0 >= vec_len >= MAX_VEC_SIZE:
                raise VectorReadError.bad_size(loc, vec_len)
            mem = Address(word_len, sizeof(char))
            chars = <char*>mem.ptr
            vec = <float*>self.mem.alloc(vec_len, sizeof(float))

            file_.read(chars, sizeof(char), word_len)
            file_.read(vec, sizeof(float), vec_len)

            string_id = self.strings[chars[:word_len]]
            while string_id >= vectors.size():
                vectors.push_back(EMPTY_VEC)
            assert vec != NULL
            vectors[string_id] = vec
        cdef LexemeC* lex
        for i in range(self.lexemes.size()):
            # Cast away the const, cos we can modify our lexemes
            lex = <LexemeC*>self.lexemes[i]
            if lex.lower < vectors.size():
                lex.repvec = vectors[lex.lower]
                for i in range(vec_len):
                    lex.l2_norm += (lex.repvec[i] * lex.repvec[i])
                lex.l2_norm = math.sqrt(lex.l2_norm)
            else:
                lex.repvec = EMPTY_VEC
        return vec_len

    property codec:
        def __get__(self):
            cdef Address mem
            cdef int i
            cdef float[:] cv_probs
            if self._codec is not None:
                return self._codec
            else:
                mem = Address(len(self), sizeof(float))
                probs = <float*>mem.ptr
                for i in range(len(self)):
                    probs[i] = <float>c_exp(self.lexemes[i].prob)
                cv_probs = <float[:len(self)]>probs
                self._codec = HuffmanCodec(cv_probs, 0)
                return self._codec


def write_binary_vectors(in_loc, out_loc):
    cdef _CFile out_file = _CFile(out_loc, 'wb')
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

            out_file.write(sizeof(word_len), 1, &word_len)
            out_file.write(sizeof(vec_len), 1, &vec_len)

            chars = <char*>word
            out_file.write(sizeof(char), len(word), chars)
            out_file.write(sizeof(float), vec_len, vec)


cdef class _CFile:
    cdef FILE* fp
    def __init__(self, loc, bytes mode):
        cdef bytes bytes_loc = loc.encode('utf8') if type(loc) == unicode else loc
        self.fp = fopen(<char*>bytes_loc, mode)
        if self.fp == NULL:
            raise IOError

    def __dealloc__(self):
        fclose(self.fp)

    def close(self):
        fclose(self.fp)

    cdef int read(self, void* dest, size_t elem_size, size_t n) except -1:
        st = fread(dest, elem_size, n, self.fp)
        if st != n:
            raise IOError

    cdef int write(self, size_t elem_size, size_t n, void* data) except -1:
        st = fwrite(data, elem_size, n, self.fp)
        if st != n:
            raise IOError

    cdef int write_unicode(self, unicode value):
        cdef bytes py_bytes = value.encode('utf8')
        cdef char* chars = <char*>py_bytes
        self.write(sizeof(char), len(py_bytes), chars)


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
