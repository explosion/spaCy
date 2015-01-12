from libc.stdio cimport fopen, fclose, fread, fwrite, FILE
from libc.string cimport memset

from os import path
import codecs

from .lexeme cimport EMPTY_LEXEME
from .lexeme cimport init as lexeme_init
from .lexeme cimport Lexeme_cinit
from .strings cimport slice_unicode
from .strings cimport hash_string
from .orth cimport word_shape


DEF MAX_VEC_SIZE = 100000


cdef float[MAX_VEC_SIZE] EMPTY_VEC
memset(EMPTY_VEC, 0, sizeof(EMPTY_VEC))
memset(&EMPTY_LEXEME, 0, sizeof(LexemeC))
EMPTY_LEXEME.vec = EMPTY_VEC


cdef LexemeC init_lexeme(id_t i, unicode string, hash_t hashed,
                  StringStore string_store, dict props) except *:
    cdef LexemeC lex
    lex.id = i
    lex.length = len(string)
    lex.sic = string_store[string]
    
    lex.cluster = props.get('cluster', 0)
    lex.prob = props.get('prob', 0)

    lex.prefix = string_store[string[:1]]
    lex.suffix = string_store[string[-3:]]
    lex.shape = string_store[word_shape(string)]
   
    lex.flags = props.get('flags', 0)
    return lex


cdef class Vocab:
    '''A map container for a language's LexemeC structs.
    '''
    def __init__(self, data_dir=None, get_lex_props=None):
        self.mem = Pool()
        self._map = PreshMap(2 ** 20)
        self.strings = StringStore()
        self.lexemes.push_back(&EMPTY_LEXEME)
        self.get_lex_props = get_lex_props

        if data_dir is not None:
            if not path.exists(data_dir):
                raise IOError("Directory %s not found -- cannot load Vocab." % data_dir)
        if data_dir is not None:
            if not path.isdir(data_dir):
                raise IOError("Path %s is a file, not a dir -- cannot load Vocab." % data_dir)
            self.strings.load(path.join(data_dir, 'strings.txt'))
            self.load_lexemes(path.join(data_dir, 'lexemes.bin'))
            #self.load_vectors(path.join(data_dir, 'deps.words'))

    def __len__(self):
        """The current number of lexemes stored."""
        return self.lexemes.size()

    cdef const LexemeC* get(self, Pool mem, UniStr* string) except NULL:
        '''Get a pointer to a LexemeC from the lexicon, creating a new Lexeme
        if necessary, using memory acquired from the given pool.  If the pool
        is the lexicon's own memory, the lexeme is saved in the lexicon.'''
        cdef LexemeC* lex
        lex = <LexemeC*>self._map.get(string.key)
        if lex != NULL:
            return lex
        if string.n < 3:
            mem = self.mem
        cdef unicode py_string = string.chars[:string.n]
        lex = <LexemeC*>mem.alloc(sizeof(LexemeC), 1)
        lex[0] = init_lexeme(self.lexemes.size(), py_string, string.key, self.strings,
                             self.get_lex_props(py_string))
        if mem is self.mem:
            self._map.set(string.key, lex)
            while self.lexemes.size() < (lex.id + 1):
                self.lexemes.push_back(&EMPTY_LEXEME)
            self.lexemes[lex.id] = lex
        else:
            lex[0].id = 1
        return lex

    def __getitem__(self,  id_or_string):
        '''Retrieve a lexeme, given an int ID or a unicode string.  If a previously
        unseen unicode string is given, a new LexemeC is created and stored.

        Args:
            id_or_string (int or unicode): The integer ID of a word, or its unicode
                string.  If an int >= Lexicon.size, IndexError is raised.
                If id_or_string is neither an int nor a unicode string, ValueError
                is raised.

        Returns:
            lexeme (Lexeme): An instance of the Lexeme Python class, with data
                copied on instantiation.
        '''
        cdef UniStr string
        cdef const LexemeC* lexeme
        if type(id_or_string) == int:
            if id_or_string >= self.lexemes.size():
                raise IndexError
            lexeme = self.lexemes.at(id_or_string)
        else:
            slice_unicode(&string, id_or_string, 0, len(id_or_string))
            lexeme = self.get(self.mem, &string)
        return Lexeme_cinit(lexeme, self.strings)

    def __setitem__(self, unicode uni_string, dict props):
        cdef UniStr s
        slice_unicode(&s, uni_string, 0, len(uni_string))
        # Cast through the const here, since we're allowed to change our own
        # LexemeCs.
        lex = <LexemeC*><void*>self.get(self.mem, &s)
        lex[0] = lexeme_init(lex.id, s.chars[:s.n], s.key, self.strings, props)

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
            st = fwrite(&key, sizeof(key), 1, fp)
            assert st == 1
            st = fwrite(lexeme, sizeof(LexemeC), 1, fp)
            assert st == 1
        st = fclose(fp)
        assert st == 0

    def load_lexemes(self, loc):
        if not path.exists(loc):
            raise IOError('LexemeCs file not found at %s' % loc)
        cdef bytes bytes_loc = loc.encode('utf8') if type(loc) == unicode else loc
        cdef FILE* fp = fopen(<char*>bytes_loc, 'rb')
        assert fp != NULL
        cdef size_t st
        cdef LexemeC* lexeme
        cdef hash_t key
        i = 0
        while True:
            st = fread(&key, sizeof(key), 1, fp)
            if st != 1:
                break
            lexeme = <LexemeC*>self.mem.alloc(sizeof(LexemeC), 1)
            st = fread(lexeme, sizeof(LexemeC), 1, fp)
            if st != 1:
                break
            self._map.set(key, lexeme)
            while self.lexemes.size() < (lexeme.id + 1):
                self.lexemes.push_back(&EMPTY_LEXEME)
            self.lexemes[lexeme.id] = lexeme
            i += 1
        fclose(fp)

    def load_vectors(self, loc):
        cdef int i
        cdef unicode line
        cdef unicode word
        cdef unicode val_str
        cdef hash_t key
        cdef LexemeC* lex
        cdef float* vec
 
        with codecs.open(loc, 'r', 'utf8') as file_:
            for line in file_:
                pieces = line.split()
                word = pieces.pop(0)
                if len(pieces) >= MAX_VEC_SIZE:
                    sizes = (len(pieces), MAX_VEC_SIZE)
                    msg = ("Your vector is %d elements."
                           "The compile-time limit is %d elements." % sizes)
                    raise ValueError(msg)
                key = hash_string(word)
                lex = <LexemeC*>self._map.get(key)
                if lex is not NULL:
                    vec = <float*>self.mem.alloc(len(pieces), sizeof(float))
                    for i, val_str in enumerate(pieces):
                        vec[i] = float(val_str)
                    lex.vec = vec
