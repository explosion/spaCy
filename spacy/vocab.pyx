from __future__ import unicode_literals

from libc.stdio cimport fopen, fclose, fread, fwrite, FILE
from libc.string cimport memset
from libc.stdint cimport int32_t
from libc.stdint cimport uint64_t
from libc.math cimport sqrt

from pathlib import Path
import bz2
import io
import math
import ujson as json
import tempfile

from .lexeme cimport EMPTY_LEXEME
from .lexeme cimport Lexeme
from .strings cimport hash_string
from .orth cimport word_shape
from .typedefs cimport attr_t
from .cfile cimport CFile
from .lemmatizer import Lemmatizer
from .attrs import intify_attrs
from .tokens.token cimport Token

from . import attrs
from . import symbols

from cymem.cymem cimport Address
from .serialize.packer cimport Packer
from .attrs cimport PROB, LANG
from . import deprecated
from . import util


try:
    import copy_reg
except ImportError:
    import copyreg as copy_reg


DEF MAX_VEC_SIZE = 100000


cdef float[MAX_VEC_SIZE] EMPTY_VEC
memset(EMPTY_VEC, 0, sizeof(EMPTY_VEC))
memset(&EMPTY_LEXEME, 0, sizeof(LexemeC))
EMPTY_LEXEME.vector = EMPTY_VEC


cdef class Vocab:
    '''A map container for a language's LexemeC structs.
    '''
    @classmethod
    def load(cls, path, lex_attr_getters=None, lemmatizer=True,
             tag_map=True, serializer_freqs=True, oov_prob=True, **deprecated_kwargs):
        """
        Load the vocabulary from a path.

        Arguments:
            path (Path):
                The path to load from.
            lex_attr_getters (dict):
                A dictionary mapping attribute IDs to functions to compute them.
                Defaults to None.
            lemmatizer (object):
                A lemmatizer. Defaults to None.
            tag_map (dict):
                A dictionary mapping fine-grained tags to coarse-grained parts-of-speech,
                and optionally morphological attributes.
            oov_prob (float):
                The default probability for out-of-vocabulary words.
        Returns:
            Vocab: The newly constructed vocab object.
        """
        if isinstance(path, basestring):
            path = Path(path)
        util.check_renamed_kwargs({'get_lex_attr': 'lex_attr_getters'}, deprecated_kwargs)
        if 'vectors' in deprecated_kwargs:
            raise AttributeError(
                "vectors argument to Vocab.load() deprecated. "
                "Install vectors after loading.")
        if tag_map is True and (path / 'vocab' / 'tag_map.json').exists():
            with (path / 'vocab' / 'tag_map.json').open('r', encoding='utf8') as file_:
                tag_map = json.load(file_)
        elif tag_map is True:
            tag_map = None
        if lex_attr_getters is not None \
        and oov_prob is True \
        and (path / 'vocab' / 'oov_prob').exists():
            with (path / 'vocab' / 'oov_prob').open('r', encoding='utf8') as file_:
                oov_prob = float(file_.read())
            lex_attr_getters[PROB] = lambda text: oov_prob
        if lemmatizer is True:
            lemmatizer = Lemmatizer.load(path)
        if serializer_freqs is True and (path / 'vocab' / 'serializer.json').exists():
            with (path / 'vocab' / 'serializer.json').open('r', encoding='utf8') as file_:
                serializer_freqs = json.load(file_)
        else:
            serializer_freqs = None

        cdef Vocab self = cls(lex_attr_getters=lex_attr_getters, tag_map=tag_map,
                              lemmatizer=lemmatizer, serializer_freqs=serializer_freqs)

        with (path / 'vocab' / 'strings.json').open('r', encoding='utf8') as file_:
            self.strings.load(file_)
        self.load_lexemes(path / 'vocab' / 'lexemes.bin')
        return self

    def __init__(self, lex_attr_getters=None, tag_map=None, lemmatizer=None,
            serializer_freqs=None, **deprecated_kwargs):
        '''Create the vocabulary.

        lex_attr_getters (dict):
            A dictionary mapping attribute IDs to functions to compute them.
            Defaults to None.
        lemmatizer (object):
            A lemmatizer. Defaults to None.
        tag_map (dict):
            A dictionary mapping fine-grained tags to coarse-grained parts-of-speech,
            and optionally morphological attributes.
        oov_prob (float):
            The default probability for out-of-vocabulary words.

        Returns:
            Vocab: The newly constructed vocab object.
        '''
        util.check_renamed_kwargs({'get_lex_attr': 'lex_attr_getters'}, deprecated_kwargs)

        lex_attr_getters = lex_attr_getters if lex_attr_getters is not None else {}
        tag_map = tag_map if tag_map is not None else {}
        if lemmatizer in (None, True, False):
            lemmatizer = Lemmatizer({}, {}, {})
        serializer_freqs = serializer_freqs if serializer_freqs is not None else {}

        self.mem = Pool()
        self._by_hash = PreshMap()
        self._by_orth = PreshMap()
        self.strings = StringStore()
        # Load strings in a special order, so that we have an onset number for
        # the vocabulary. This way, when words are added in order, the orth ID
        # is the frequency rank of the word, plus a certain offset. The structural
        # strings are loaded first, because the vocab is open-class, and these
        # symbols are closed class.
        # TODO: Actually this has turned out to be a pain in the ass...
        # It means the data is invalidated when we add a symbol :(
        # Need to rethink this.
        for name in symbols.NAMES + list(sorted(tag_map.keys())):
            if name:
                _ = self.strings[name]
        self.lex_attr_getters = lex_attr_getters
        self.morphology = Morphology(self.strings, tag_map, lemmatizer)
        self.serializer_freqs = serializer_freqs

        self.length = 1
        self._serializer = None

    property serializer:
        # Having the serializer live here is super messy :(
        def __get__(self):
            if self._serializer is None:
                self._serializer = Packer(self, self.serializer_freqs)
            return self._serializer

    property lang:
        def __get__(self):
            langfunc = None
            if self.lex_attr_getters:
                langfunc = self.lex_attr_getters.get(LANG, None)
            return langfunc('_') if langfunc else ''

    def __len__(self):
        """The current number of lexemes stored."""
        return self.length

    def resize_vectors(self, int new_size):
        '''
        Set vectors_length to a new size, and allocate more memory for the Lexeme
        vectors if necessary. The memory will be zeroed.

        Arguments:
            new_size (int): The new size of the vectors.
        '''
        cdef hash_t key
        cdef size_t addr
        if new_size > self.vectors_length:
            for key, addr in self._by_hash.items():
                lex = <LexemeC*>addr
                lex.vector = <float*>self.mem.realloc(lex.vector,
                                        new_size * sizeof(lex.vector[0]))
        self.vectors_length = new_size

    def add_flag(self, flag_getter, int flag_id=-1):
        '''Set a new boolean flag to words in the vocabulary.

        The flag_setter function will be called over the words currently in the
        vocab, and then applied to new words as they occur. You'll then be able
        to access the flag value on each token, using token.check_flag(flag_id).

        See also:
            Lexeme.set_flag, Lexeme.check_flag, Token.set_flag, Token.check_flag.

        Arguments:
            flag_getter:
                A function f(unicode) -> bool, to get the flag value.

            flag_id (int):
                An integer between 1 and 63 (inclusive), specifying the bit at which the
                flag will be stored. If -1, the lowest available bit will be
                chosen.

        Returns:
            flag_id (int): The integer ID by which the flag value can be checked.
        '''
        if flag_id == -1:
            for bit in range(1, 64):
                if bit not in self.lex_attr_getters:
                    flag_id = bit
                    break
            else:
                raise ValueError(
                    "Cannot find empty bit for new lexical flag. All bits between "
                    "0 and 63 are occupied. You can replace one by specifying the "
                    "flag_id explicitly, e.g. nlp.vocab.add_flag(your_func, flag_id=IS_ALPHA")
        elif flag_id >= 64 or flag_id < 1:
            raise ValueError(
                "Invalid value for flag_id: %d. Flag IDs must be between "
                "1 and 63 (inclusive)" % flag_id)
        for lex in self:
            lex.set_flag(flag_id, flag_getter(lex.orth_))
        self.lex_attr_getters[flag_id] = flag_getter
        return flag_id

    cdef const LexemeC* get(self, Pool mem, unicode string) except NULL:
        '''Get a pointer to a LexemeC from the lexicon, creating a new Lexeme
        if necessary, using memory acquired from the given pool.  If the pool
        is the lexicon's own memory, the lexeme is saved in the lexicon.'''
        if string == u'':
            return &EMPTY_LEXEME
        cdef LexemeC* lex
        cdef hash_t key = hash_string(string)
        lex = <LexemeC*>self._by_hash.get(key)
        cdef size_t addr
        if lex != NULL:
            if lex.orth != self.strings[string]:
                raise LookupError.mismatched_strings(
                    lex.orth, self.strings[string], self.strings[lex.orth], string)
            return lex
        else:
            return self._new_lexeme(mem, string)

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
        else:
            return self._new_lexeme(mem, self.strings[orth])

    cdef const LexemeC* _new_lexeme(self, Pool mem, unicode string) except NULL:
        cdef hash_t key
        if len(string) < 3 or self.length < 10000:
            mem = self.mem
        cdef bint is_oov = mem is not self.mem
        lex = <LexemeC*>mem.alloc(sizeof(LexemeC), 1)
        lex.orth = self.strings[string]
        lex.length = len(string)
        lex.id = self.length
        lex.vector = <float*>mem.alloc(self.vectors_length, sizeof(float))
        if self.lex_attr_getters is not None:
            for attr, func in self.lex_attr_getters.items():
                value = func(string)
                if isinstance(value, unicode):
                    value = self.strings[value]
                if attr == PROB:
                    lex.prob = value
                elif value is not None:
                    Lexeme.set_struct_attr(lex, attr, value)
        if is_oov:
            lex.id = 0
        else:
            key = hash_string(string)
            self._add_lex_to_vocab(key, lex)
        assert lex != NULL, string
        return lex

    cdef int _add_lex_to_vocab(self, hash_t key, const LexemeC* lex) except -1:
        self._by_hash.set(key, <void*>lex)
        self._by_orth.set(lex.orth, <void*>lex)
        self.length += 1

    def __contains__(self, unicode string):
        '''Check whether the string has an entry in the vocabulary.

        Arguments:
            string (unicode): The ID string.

        Returns:
            bool Whether the string has an entry in the vocabulary.
        '''
        key = hash_string(string)
        lex = self._by_hash.get(key)
        return True if lex is not NULL else False

    def __iter__(self):
        '''Iterate over the lexemes in the vocabulary.

        Yields: Lexeme An entry in the vocabulary.
        '''
        cdef attr_t orth
        cdef size_t addr
        for orth, addr in self._by_orth.items():
            yield Lexeme(self, orth)

    def __getitem__(self,  id_or_string):
        '''Retrieve a lexeme, given an int ID or a unicode string.  If a previously
        unseen unicode string is given, a new lexeme is created and stored.

        Arguments:
            id_or_string (int or unicode):
              The integer ID of a word, or its unicode string.

              If an int >= Lexicon.size, IndexError is raised. If id_or_string
              is neither an int nor a unicode string, ValueError is raised.

        Returns:
            lexeme (Lexeme): The lexeme indicated by the given ID.
        '''
        cdef attr_t orth
        if type(id_or_string) == unicode:
            orth = self.strings[id_or_string]
        else:
            orth = id_or_string
        return Lexeme(self, orth)

    cdef const TokenC* make_fused_token(self, substrings) except NULL:
        cdef int i
        tokens = <TokenC*>self.mem.alloc(len(substrings) + 1, sizeof(TokenC))
        for i, props in enumerate(substrings):
            props = intify_attrs(props, strings_map=self.strings, _do_deprecated=True)
            token = &tokens[i]
            # Set the special tokens up to have arbitrary attributes
            token.lex = <LexemeC*>self.get_by_orth(self.mem, props[attrs.ORTH])
            if attrs.TAG in props:
                self.morphology.assign_tag(token, props[attrs.TAG])
            for attr_id, value in props.items():
                Token.set_struct_attr(token, attr_id, value)
        return tokens

    def dump(self, loc):
        """Save the lexemes binary data to the given location.

        Arguments:
            loc (Path): The path to save to.
        """
        if hasattr(loc, 'as_posix'):
            loc = loc.as_posix()
        cdef bytes bytes_loc = loc.encode('utf8') if type(loc) == unicode else loc

        cdef CFile fp = CFile(bytes_loc, 'wb')
        cdef size_t st
        cdef size_t addr
        cdef hash_t key
        for key, addr in self._by_hash.items():
            lexeme = <LexemeC*>addr
            fp.write_from(&lexeme.orth, sizeof(lexeme.orth), 1)
            fp.write_from(&lexeme.flags, sizeof(lexeme.flags), 1)
            fp.write_from(&lexeme.id, sizeof(lexeme.id), 1)
            fp.write_from(&lexeme.length, sizeof(lexeme.length), 1)
            fp.write_from(&lexeme.orth, sizeof(lexeme.orth), 1)
            fp.write_from(&lexeme.lower, sizeof(lexeme.lower), 1)
            fp.write_from(&lexeme.norm, sizeof(lexeme.norm), 1)
            fp.write_from(&lexeme.shape, sizeof(lexeme.shape), 1)
            fp.write_from(&lexeme.prefix, sizeof(lexeme.prefix), 1)
            fp.write_from(&lexeme.suffix, sizeof(lexeme.suffix), 1)
            fp.write_from(&lexeme.cluster, sizeof(lexeme.cluster), 1)
            fp.write_from(&lexeme.prob, sizeof(lexeme.prob), 1)
            fp.write_from(&lexeme.sentiment, sizeof(lexeme.sentiment), 1)
            fp.write_from(&lexeme.l2_norm, sizeof(lexeme.l2_norm), 1)
            fp.write_from(&lexeme.lang, sizeof(lexeme.lang), 1)
        fp.close()

    def load_lexemes(self, loc):
        '''Load the binary vocabulary data from the given location.

        Arguments:
            loc (Path): The path to load from.

        Returns:
            None
        '''
        fp = CFile(loc, 'rb',
                on_open_error=lambda: IOError('LexemeCs file not found at %s' % loc))
        cdef LexemeC* lexeme
        cdef hash_t key
        cdef unicode py_str
        cdef attr_t orth
        assert sizeof(orth) == sizeof(lexeme.orth)
        i = 0
        while True:
            try:
                fp.read_into(&orth, 1, sizeof(orth))
            except IOError:
                break
            lexeme = <LexemeC*>self.mem.alloc(sizeof(LexemeC), 1)
            # Copy data from the file into the lexeme
            fp.read_into(&lexeme.flags, 1, sizeof(lexeme.flags))
            fp.read_into(&lexeme.id, 1, sizeof(lexeme.id))
            fp.read_into(&lexeme.length, 1, sizeof(lexeme.length))
            fp.read_into(&lexeme.orth, 1, sizeof(lexeme.orth))
            fp.read_into(&lexeme.lower, 1, sizeof(lexeme.lower))
            fp.read_into(&lexeme.norm, 1, sizeof(lexeme.norm))
            fp.read_into(&lexeme.shape, 1, sizeof(lexeme.shape))
            fp.read_into(&lexeme.prefix, 1, sizeof(lexeme.prefix))
            fp.read_into(&lexeme.suffix, 1, sizeof(lexeme.suffix))
            fp.read_into(&lexeme.cluster, 1, sizeof(lexeme.cluster))
            fp.read_into(&lexeme.prob, 1, sizeof(lexeme.prob))
            fp.read_into(&lexeme.sentiment, 1, sizeof(lexeme.sentiment))
            fp.read_into(&lexeme.l2_norm, 1, sizeof(lexeme.l2_norm))
            fp.read_into(&lexeme.lang, 1, sizeof(lexeme.lang))

            lexeme.vector = EMPTY_VEC
            py_str = self.strings[lexeme.orth]
            key = hash_string(py_str)
            self._by_hash.set(key, lexeme)
            self._by_orth.set(lexeme.orth, lexeme)
            self.length += 1
            i += 1
        fp.close()

    def dump_vectors(self, out_loc):
        '''Save the word vectors to a binary file.

        Arguments:
            loc (Path): The path to save to.
        Returns:
            None
        '''
        cdef int32_t vec_len = self.vectors_length
        cdef int32_t word_len
        cdef bytes word_str
        cdef char* chars

        cdef Lexeme lexeme
        cdef CFile out_file = CFile(out_loc, 'wb')
        for lexeme in self:
            word_str = lexeme.orth_.encode('utf8')
            vec = lexeme.c.vector
            word_len = len(word_str)

            out_file.write_from(&word_len, 1, sizeof(word_len))
            out_file.write_from(&vec_len, 1, sizeof(vec_len))

            chars = <char*>word_str
            out_file.write_from(chars, word_len, sizeof(char))
            out_file.write_from(vec, vec_len, sizeof(float))
        out_file.close()

    def load_vectors(self, file_):
        """Load vectors from a text-based file.

        Arguments:
            file_ (buffer): The file to read from. Entries should be separated by newlines,
        and each entry should be whitespace delimited. The first value of the entry
        should be the word string, and subsequent entries should be the values of the
        vector.

        Returns:
            vec_len (int): The length of the vectors loaded.
        """
        cdef LexemeC* lexeme
        cdef attr_t orth
        cdef int32_t vec_len = -1
        cdef double norm = 0.0
        for line_num, line in enumerate(file_):
            pieces = line.split()
            word_str = pieces.pop(0)
            if vec_len == -1:
                vec_len = len(pieces)
            elif vec_len != len(pieces):
                raise VectorReadError.mismatched_sizes(file_, line_num,
                                                        vec_len, len(pieces))
            orth = self.strings[word_str]
            lexeme = <LexemeC*><void*>self.get_by_orth(self.mem, orth)
            lexeme.vector = <float*>self.mem.alloc(vec_len, sizeof(float))
            for i, val_str in enumerate(pieces):
                lexeme.vector[i] = float(val_str)
            norm = 0.0
            for i in range(vec_len):
                norm += lexeme.vector[i] * lexeme.vector[i]
            lexeme.l2_norm = sqrt(norm)
        self.vectors_length = vec_len
        return vec_len

    def load_vectors_from_bin_loc(self, loc):
        """Load vectors from the location of a binary file.

        Arguments:
            loc (unicode): The path of the binary file to load from.

        Returns:
            vec_len (int): The length of the vectors loaded.
        """
        cdef CFile file_ = CFile(loc, b'rb')
        cdef int32_t word_len
        cdef int32_t vec_len = 0
        cdef int32_t prev_vec_len = 0
        cdef float* vec
        cdef Address mem
        cdef attr_t string_id
        cdef bytes py_word
        cdef vector[float*] vectors
        cdef int line_num = 0
        cdef Pool tmp_mem = Pool()
        while True:
            try:
                file_.read_into(&word_len, sizeof(word_len), 1)
            except IOError:
                break
            file_.read_into(&vec_len, sizeof(vec_len), 1)
            if prev_vec_len != 0 and vec_len != prev_vec_len:
                raise VectorReadError.mismatched_sizes(loc, line_num,
                                                       vec_len, prev_vec_len)
            if 0 >= vec_len >= MAX_VEC_SIZE:
                raise VectorReadError.bad_size(loc, vec_len)

            chars = <char*>file_.alloc_read(tmp_mem, word_len, sizeof(char))
            vec = <float*>file_.alloc_read(self.mem, vec_len, sizeof(float))

            string_id = self.strings[chars[:word_len]]
            while string_id >= vectors.size():
                vectors.push_back(EMPTY_VEC)
            assert vec != NULL
            vectors[string_id] = vec
            line_num += 1
        cdef LexemeC* lex
        cdef size_t lex_addr
        cdef double norm = 0.0
        cdef int i
        for orth, lex_addr in self._by_orth.items():
            lex = <LexemeC*>lex_addr
            if lex.lower < vectors.size():
                lex.vector = vectors[lex.lower]
                norm = 0.0
                for i in range(vec_len):
                    norm += lex.vector[i] * lex.vector[i]
                lex.l2_norm = sqrt(norm)
            else:
                lex.vector = EMPTY_VEC
        self.vectors_length = vec_len
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


class LookupError(Exception):
    @classmethod
    def mismatched_strings(cls, id_, id_string, original_string):
        return cls(
            "Error fetching a Lexeme from the Vocab. When looking up a string, "
            "the lexeme returned had an orth ID that did not match the query string. "
            "This means that the cached lexeme structs are mismatched to the "
            "string encoding table. The mismatched:\n"
            "Query string: {query}\n"
            "Orth cached: {orth_str}\n"
            "ID of orth: {orth_id}".format(
                query=repr(original_string), orth_str=repr(id_string), orth_id=id_)
        )


class VectorReadError(Exception):
    @classmethod
    def mismatched_sizes(cls, loc, line_num, prev_size, curr_size):
        return cls(
            "Error reading word vectors from %s on line %d.\n"
            "All vectors must be the same size.\n"
            "Prev size: %d\n"
            "Curr size: %d" % (loc, line_num, prev_size, curr_size))

    @classmethod
    def bad_size(cls, loc, size):
        return cls(
            "Error reading word vectors from %s.\n"
            "Vector size: %d\n"
            "Max size: %d\n"
            "Min size: 1\n" % (loc, size, MAX_VEC_SIZE))
