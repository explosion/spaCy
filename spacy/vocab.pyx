from libc.stdio cimport fopen, fclose, fread, fwrite, FILE

from os import path

from .lexeme cimport EMPTY_LEXEME
from .lexeme cimport init as lexeme_init
from .strings cimport slice_unicode


cdef class Vocab:
    '''A map container for a language's Lexeme structs.
    
    Also interns UTF-8 strings, and maps them to consecutive integer IDs.
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
            self.strings.load(path.join(data_dir, 'strings'))
            self.load(path.join(data_dir, 'lexemes'))

    def __len__(self):
        return self.lexemes.size()

    cdef const Lexeme* get(self, Pool mem, UniStr* string) except NULL:
        '''Get a pointer to a Lexeme from the lexicon, creating a new Lexeme
        if necessary, using memory acquired from the given pool.  If the pool
        is the lexicon's own memory, the lexeme is saved in the lexicon.'''
        cdef Lexeme* lex
        lex = <Lexeme*>self._map.get(string.key)
        if lex != NULL:
            return lex
        if string.n < 3:
            mem = self.mem
        cdef unicode py_string = string.chars[:string.n]
        lex = <Lexeme*>mem.alloc(sizeof(Lexeme), 1)
        lex[0] = lexeme_init(self.lexemes.size(), py_string, string.key, self.strings,
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
        unseen unicode string is given, a new Lexeme is created and stored.

        This function relies on Cython's struct-to-dict conversion.  Python clients
        receive a dict keyed by strings (byte or unicode, depending on Python 2/3),
        with int values.  Cython clients can instead receive a Lexeme struct value.
        More efficient Cython access is provided by Lexicon.get, which returns
        a Lexeme*.

        Args:
            id_or_string (int or unicode): The integer ID of a word, or its unicode
                string.  If an int >= Lexicon.size, IndexError is raised.
                If id_or_string is neither an int nor a unicode string, ValueError
                is raised.

        Returns:
            lexeme (dict): A Lexeme struct instance, which Cython translates into
                a dict if the operator is called from Python.
        '''
        if type(id_or_string) == int:
            if id_or_string >= self.lexemes.size():
                raise IndexError
            return self.lexemes.at(id_or_string)[0]
        cdef UniStr string
        slice_unicode(&string, id_or_string, 0, len(id_or_string))
        cdef const Lexeme* lexeme = self.get(self.mem, &string)
        return lexeme[0]

    def __setitem__(self, unicode uni_string, dict props):
        cdef UniStr s
        slice_unicode(&s, uni_string, 0, len(uni_string))
        # Cast through the const here, since we're allowed to change our own
        # Lexemes.
        lex = <Lexeme*><void*>self.get(self.mem, &s)
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
            lexeme = <Lexeme*>self._map.c_map.cells[i].value
            st = fwrite(&key, sizeof(key), 1, fp)
            assert st == 1
            st = fwrite(lexeme, sizeof(Lexeme), 1, fp)
            assert st == 1
        st = fclose(fp)
        assert st == 0

    def load(self, loc):
        if not path.exists(loc):
            raise IOError('Lexemes file not found at %s' % loc)
        cdef bytes bytes_loc = loc.encode('utf8') if type(loc) == unicode else loc
        cdef FILE* fp = fopen(<char*>bytes_loc, 'rb')
        assert fp != NULL
        cdef size_t st
        cdef Lexeme* lexeme
        cdef hash_t key
        i = 0
        while True:
            st = fread(&key, sizeof(key), 1, fp)
            if st != 1:
                break
            lexeme = <Lexeme*>self.mem.alloc(sizeof(Lexeme), 1)
            st = fread(lexeme, sizeof(Lexeme), 1, fp)
            if st != 1:
                break
            self._map.set(key, lexeme)
            while self.lexemes.size() < (lexeme.id + 1):
                self.lexemes.push_back(&EMPTY_LEXEME)
            self.lexemes[lexeme.id] = lexeme
            i += 1
        fclose(fp)
