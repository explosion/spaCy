# coding: utf8
from __future__ import unicode_literals

import bz2
import ujson
import re
import numpy

from libc.string cimport memset, memcpy
from libc.stdint cimport int32_t
from libc.math cimport sqrt
from cymem.cymem cimport Address
from collections import OrderedDict
from .lexeme cimport EMPTY_LEXEME
from .lexeme cimport Lexeme
from .strings cimport hash_string
from .typedefs cimport attr_t
from .cfile cimport CFile
from .tokens.token cimport Token
from .attrs cimport PROB, LANG
from .structs cimport SerializedLexemeC

from .compat import copy_reg, pickle, basestring_
from .lemmatizer import Lemmatizer
from .attrs import intify_attrs
from .vectors import Vectors
from . import util
from . import attrs
from . import symbols


cdef class Vocab:
    """A look-up table that allows you to access `Lexeme` objects. The `Vocab`
    instance also provides access to the `StringStore`, and owns underlying
    C-data that is shared between `Doc` objects.
    """
    def __init__(self, lex_attr_getters=None, tag_map=None, lemmatizer=None,
            strings=tuple(), **deprecated_kwargs):
        """Create the vocabulary.

        lex_attr_getters (dict): A dictionary mapping attribute IDs to functions
            to compute them. Defaults to `None`.
        tag_map (dict): A dictionary mapping fine-grained tags to coarse-grained
            parts-of-speech, and optionally morphological attributes.
        lemmatizer (object): A lemmatizer. Defaults to `None`.
        strings (StringStore): StringStore that maps strings to integers, and
            vice versa.
        RETURNS (Vocab): The newly constructed vocab object.
        """
        lex_attr_getters = lex_attr_getters if lex_attr_getters is not None else {}
        tag_map = tag_map if tag_map is not None else {}
        if lemmatizer in (None, True, False):
            lemmatizer = Lemmatizer({}, {}, {})

        self.mem = Pool()
        self._by_hash = PreshMap()
        self._by_orth = PreshMap()
        self.strings = StringStore()
        self.length = 0
        if strings:
            for string in strings:
                _ = self[string]
        for name in tag_map.keys():
            if name:
                self.strings.add(name)
        self.lex_attr_getters = lex_attr_getters
        self.morphology = Morphology(self.strings, tag_map, lemmatizer)
        self.vectors = Vectors(self.strings)

    property lang:
        def __get__(self):
            langfunc = None
            if self.lex_attr_getters:
                langfunc = self.lex_attr_getters.get(LANG, None)
            return langfunc('_') if langfunc else ''

    def __len__(self):
        """The current number of lexemes stored.

        RETURNS (int): The current number of lexemes stored.
        """
        return self.length

    def add_flag(self, flag_getter, int flag_id=-1):
        """Set a new boolean flag to words in the vocabulary.

        The flag_getter function will be called over the words currently in the
        vocab, and then applied to new words as they occur. You'll then be able
        to access the flag value on each token, using token.check_flag(flag_id).
        See also: `Lexeme.set_flag`, `Lexeme.check_flag`, `Token.set_flag`,
        `Token.check_flag`.

        flag_getter (callable): A function `f(unicode) -> bool`, to get the flag
            value.
        flag_id (int): An integer between 1 and 63 (inclusive), specifying
            the bit at which the flag will be stored. If -1, the lowest
            available bit will be chosen.
        RETURNS (int): The integer ID by which the flag value can be checked.

        EXAMPLE:
            >>> MY_PRODUCT = nlp.vocab.add_flag(lambda text: text in ['spaCy', 'dislaCy'])
            >>> doc = nlp(u'I like spaCy')
            >>> assert doc[2].check_flag(MY_PRODUCT) == True
        """
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
        """Get a pointer to a `LexemeC` from the lexicon, creating a new `Lexeme`
        if necessary, using memory acquired from the given pool. If the pool
        is the lexicon's own memory, the lexeme is saved in the lexicon.
        """
        if string == u'':
            return &EMPTY_LEXEME
        cdef LexemeC* lex
        cdef hash_t key = hash_string(string)
        lex = <LexemeC*>self._by_hash.get(key)
        cdef size_t addr
        if lex != NULL:
            if lex.orth != self.strings[string]:
                raise LookupError.mismatched_strings(
                    lex.orth, self.strings[string], string)
            return lex
        else:
            return self._new_lexeme(mem, string)

    cdef const LexemeC* get_by_orth(self, Pool mem, attr_t orth) except NULL:
        """Get a pointer to a `LexemeC` from the lexicon, creating a new `Lexeme`
        if necessary, using memory acquired from the given pool. If the pool
        is the lexicon's own memory, the lexeme is saved in the lexicon.
        """
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
        lex.orth = self.strings.add(string)
        lex.length = len(string)
        lex.id = self.length
        if self.lex_attr_getters is not None:
            for attr, func in self.lex_attr_getters.items():
                value = func(string)
                if isinstance(value, unicode):
                    value = self.strings.add(value)
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
        """Check whether the string has an entry in the vocabulary.

        string (unicode): The ID string.
        RETURNS (bool) Whether the string has an entry in the vocabulary.
        """
        key = hash_string(string)
        lex = self._by_hash.get(key)
        return lex is not NULL

    def __iter__(self):
        """Iterate over the lexemes in the vocabulary.

        YIELDS (Lexeme): An entry in the vocabulary.
        """
        cdef attr_t orth
        cdef size_t addr
        for orth, addr in self._by_orth.items():
            yield Lexeme(self, orth)

    def __getitem__(self,  id_or_string):
        """Retrieve a lexeme, given an int ID or a unicode string.  If a
        previously unseen unicode string is given, a new lexeme is created and
        stored.

        id_or_string (int or unicode): The integer ID of a word, or its unicode
            string. If `int >= Lexicon.size`, `IndexError` is raised. If
            `id_or_string` is neither an int nor a unicode string, `ValueError`
            is raised.
        RETURNS (Lexeme): The lexeme indicated by the given ID.

        EXAMPLE:
            >>> apple = nlp.vocab.strings['apple']
            >>> assert nlp.vocab[apple] == nlp.vocab[u'apple']
        """
        cdef attr_t orth
        if type(id_or_string) == unicode:
            orth = self.strings.add(id_or_string)
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
            lex = <LexemeC*>self.get_by_orth(self.mem, props[attrs.ORTH])
            token.lex = lex
            if attrs.TAG in props:
                self.morphology.assign_tag(token, props[attrs.TAG])
            for attr_id, value in props.items():
                Token.set_struct_attr(token, attr_id, value)
                Lexeme.set_struct_attr(lex, attr_id, value)
        return tokens

    @property
    def vectors_length(self):
        return self.vectors.data.shape[1]

    def clear_vectors(self, new_dim=None):
        """Drop the current vector table. Because all vectors must be the same
        width, you have to call this to change the size of the vectors.
        """
        if new_dim is None:
            new_dim = self.vectors.data.shape[1]
        self.vectors = Vectors(self.strings, new_dim)

    def get_vector(self, orth):
        """Retrieve a vector for a word in the vocabulary.

        Words can be looked up by string or int ID.

        RETURNS:
            A word vector. Size and shape determed by the
            vocab.vectors instance. Usually, a numpy ndarray
            of shape (300,) and dtype float32.

        RAISES: If no vectors data is loaded, ValueError is raised.
        """
        if isinstance(orth, basestring_):
            orth = self.strings.add(orth)
        if orth in self.vectors.key2row:
            return self.vectors[orth]
        else:
            return numpy.zeros((self.vectors_length,), dtype='f')

    def set_vector(self, orth, vector):
        """Set a vector for a word in the vocabulary.

        Words can be referenced by string or int ID.

        RETURNS:
            None
        """
        if not isinstance(orth, basestring_):
            orth = self.strings[orth]
        self.vectors.add(orth, vector=vector)

    def has_vector(self, orth):
        """Check whether a word has a vector. Returns False if no
        vectors have been loaded. Words can be looked up by string
        or int ID."""
        if isinstance(orth, basestring_):
            orth = self.strings.add(orth)
        return orth in self.vectors

    def to_disk(self, path, **exclude):
        """Save the current state to a directory.

        path (unicode or Path): A path to a directory, which will be created if
            it doesn't exist. Paths may be either strings or `Path`-like objects.
        """
        path = util.ensure_path(path)
        if not path.exists():
            path.mkdir()
        self.strings.to_disk(path / 'strings.json')
        with (path / 'lexemes.bin').open('wb') as file_:
            file_.write(self.lexemes_to_bytes())
        if self.vectors is not None:
            self.vectors.to_disk(path)

    def from_disk(self, path, **exclude):
        """Loads state from a directory. Modifies the object in place and
        returns it.

        path (unicode or Path): A path to a directory. Paths may be either
            strings or `Path`-like objects.
        RETURNS (Vocab): The modified `Vocab` object.
        """
        path = util.ensure_path(path)
        self.strings.from_disk(path / 'strings.json')
        with (path / 'lexemes.bin').open('rb') as file_:
            self.lexemes_from_bytes(file_.read())
        if self.vectors is not None:
            self.vectors.from_disk(path, exclude='strings.json')
        return self

    def to_bytes(self, **exclude):
        """Serialize the current state to a binary string.

        **exclude: Named attributes to prevent from being serialized.
        RETURNS (bytes): The serialized form of the `Vocab` object.
        """
        def deserialize_vectors():
            if self.vectors is None:
                return None
            else:
                return self.vectors.to_bytes(exclude='strings.json')

        getters = OrderedDict((
            ('strings', lambda: self.strings.to_bytes()),
            ('lexemes', lambda: self.lexemes_to_bytes()),
            ('vectors', deserialize_vectors)
        ))
        return util.to_bytes(getters, exclude)

    def from_bytes(self, bytes_data, **exclude):
        """Load state from a binary string.

        bytes_data (bytes): The data to load from.
        **exclude: Named attributes to prevent from being loaded.
        RETURNS (Vocab): The `Vocab` object.
        """
        def serialize_vectors(b):
            if self.vectors is None:
                return None
            else:
                return self.vectors.from_bytes(b, exclude='strings')
        setters = OrderedDict((
            ('strings', lambda b: self.strings.from_bytes(b)),
            ('lexemes', lambda b: self.lexemes_from_bytes(b)),
            ('vectors', lambda b: serialize_vectors(b))
        ))
        util.from_bytes(bytes_data, setters, exclude)
        return self

    def lexemes_to_bytes(self):
        cdef hash_t key
        cdef size_t addr
        cdef LexemeC* lexeme = NULL
        cdef SerializedLexemeC lex_data
        cdef int size = 0
        for key, addr in self._by_hash.items():
            if addr == 0:
                continue
            size += sizeof(lex_data.data)
        byte_string = b'\0' * size
        byte_ptr = <unsigned char*>byte_string
        cdef int j
        cdef int i = 0
        for key, addr in self._by_hash.items():
            if addr == 0:
                continue
            lexeme = <LexemeC*>addr
            lex_data = Lexeme.c_to_bytes(lexeme)
            for j in range(sizeof(lex_data.data)):
                byte_ptr[i] = lex_data.data[j]
                i += 1
        return byte_string

    def lexemes_from_bytes(self, bytes bytes_data):
        """Load the binary vocabulary data from the given string."""
        cdef LexemeC* lexeme
        cdef hash_t key
        cdef unicode py_str
        cdef int i = 0
        cdef int j = 0
        cdef SerializedLexemeC lex_data
        chunk_size = sizeof(lex_data.data)
        cdef unsigned char* bytes_ptr = bytes_data
        for i in range(0, len(bytes_data), chunk_size):
            lexeme = <LexemeC*>self.mem.alloc(1, sizeof(LexemeC))
            for j in range(sizeof(lex_data.data)):
                lex_data.data[j] = bytes_ptr[i+j]
            Lexeme.c_from_bytes(lexeme, lex_data)

            py_str = self.strings[lexeme.orth]
            assert self.strings[py_str] == lexeme.orth, (py_str, lexeme.orth)
            key = hash_string(py_str)
            self._by_hash.set(key, lexeme)
            self._by_orth.set(lexeme.orth, lexeme)
            self.length += 1


def pickle_vocab(vocab):
    sstore = vocab.strings
    morph = vocab.morphology
    length = vocab.length
    data_dir = vocab.data_dir
    lex_attr_getters = vocab.lex_attr_getters

    lexemes_data = vocab.lexemes_to_bytes()

    return (unpickle_vocab,
        (sstore, morph, data_dir, lex_attr_getters,
            lexemes_data, length))


def unpickle_vocab(sstore, morphology, data_dir,
        lex_attr_getters, bytes lexemes_data, int length):
    cdef Vocab vocab = Vocab()
    vocab.length = length
    vocab.strings = sstore
    vocab.morphology = morphology
    vocab.data_dir = data_dir
    vocab.lex_attr_getters = lex_attr_getters
    vocab.lexemes_from_bytes(lexemes_data)
    vocab.length = length
    return vocab


copy_reg.pickle(Vocab, pickle_vocab, unpickle_vocab)


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
