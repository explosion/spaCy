# coding: utf8
# cython: profile=True
from __future__ import unicode_literals

import numpy
import dill

from collections import OrderedDict
from thinc.neural.util import get_array_module
from .lexeme cimport EMPTY_LEXEME
from .lexeme cimport Lexeme
from .strings cimport hash_string
from .typedefs cimport attr_t
from .tokens.token cimport Token
from .attrs cimport PROB, LANG, ORTH, TAG
from .structs cimport SerializedLexemeC

from .compat import copy_reg, basestring_
from .errors import Errors
from .lemmatizer import Lemmatizer
from .attrs import intify_attrs
from .vectors import Vectors
from ._ml import link_vectors_to_models
from . import util


cdef class Vocab:
    """A look-up table that allows you to access `Lexeme` objects. The `Vocab`
    instance also provides access to the `StringStore`, and owns underlying
    C-data that is shared between `Doc` objects.
    """
    def __init__(self, lex_attr_getters=None, tag_map=None, lemmatizer=None,
                 strings=tuple(), oov_prob=-20., **deprecated_kwargs):
        """Create the vocabulary.

        lex_attr_getters (dict): A dictionary mapping attribute IDs to
            functions to compute them. Defaults to `None`.
        tag_map (dict): Dictionary mapping fine-grained tags to coarse-grained
            parts-of-speech, and optionally morphological attributes.
        lemmatizer (object): A lemmatizer. Defaults to `None`.
        strings (StringStore): StringStore that maps strings to integers, and
            vice versa.
        RETURNS (Vocab): The newly constructed object.
        """
        lex_attr_getters = lex_attr_getters if lex_attr_getters is not None else {}
        tag_map = tag_map if tag_map is not None else {}
        if lemmatizer in (None, True, False):
            lemmatizer = Lemmatizer({}, {}, {})
        self.cfg = {'oov_prob': oov_prob}
        self.mem = Pool()
        self._by_hash = PreshMap()
        self._by_orth = PreshMap()
        self.strings = StringStore()
        self.length = 0
        if strings:
            for string in strings:
                _ = self[string]
        self.lex_attr_getters = lex_attr_getters
        self.morphology = Morphology(self.strings, tag_map, lemmatizer)
        self.vectors = Vectors()

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
        to access the flag value on each token using token.check_flag(flag_id).
        See also: `Lexeme.set_flag`, `Lexeme.check_flag`, `Token.set_flag`,
        `Token.check_flag`.

        flag_getter (callable): A function `f(unicode) -> bool`, to get the
            flag value.
        flag_id (int): An integer between 1 and 63 (inclusive), specifying
            the bit at which the flag will be stored. If -1, the lowest
            available bit will be chosen.
        RETURNS (int): The integer ID by which the flag value can be checked.

        EXAMPLE:
            >>> my_product_getter = lambda text: text in ['spaCy', 'dislaCy']
            >>> MY_PRODUCT = nlp.vocab.add_flag(my_product_getter)
            >>> doc = nlp(u'I like spaCy')
            >>> assert doc[2].check_flag(MY_PRODUCT) == True
        """
        if flag_id == -1:
            for bit in range(1, 64):
                if bit not in self.lex_attr_getters:
                    flag_id = bit
                    break
            else:
                raise ValueError(Errors.E062)
        elif flag_id >= 64 or flag_id < 1:
            raise ValueError(Errors.E063.format(value=flag_id))
        for lex in self:
            lex.set_flag(flag_id, flag_getter(lex.orth_))
        self.lex_attr_getters[flag_id] = flag_getter
        return flag_id

    cdef const LexemeC* get(self, Pool mem, unicode string) except NULL:
        """Get a pointer to a `LexemeC` from the lexicon, creating a new
        `Lexeme` if necessary using memory acquired from the given pool. If the
        pool is the lexicon's own memory, the lexeme is saved in the lexicon.
        """
        if string == u'':
            return &EMPTY_LEXEME
        cdef LexemeC* lex
        cdef hash_t key = hash_string(string)
        lex = <LexemeC*>self._by_hash.get(key)
        cdef size_t addr
        if lex != NULL:
            if lex.orth != self.strings[string]:
                raise KeyError(Errors.E064.format(string=lex.orth,
                                                  orth=self.strings[string],
                                                  orth_id=string))
            return lex
        else:
            return self._new_lexeme(mem, string)

    cdef const LexemeC* get_by_orth(self, Pool mem, attr_t orth) except NULL:
        """Get a pointer to a `LexemeC` from the lexicon, creating a new
        `Lexeme` if necessary using memory acquired from the given pool. If the
        pool is the lexicon's own memory, the lexeme is saved in the lexicon.
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
        if self.vectors is not None:
            lex.id = self.vectors.key2row.get(lex.orth, 0)
        else:
            lex.id = 0
        if self.lex_attr_getters is not None:
            for attr, func in self.lex_attr_getters.items():
                value = func(string)
                if isinstance(value, unicode):
                    value = self.strings.add(value)
                if attr == PROB:
                    lex.prob = value
                elif value is not None:
                    Lexeme.set_struct_attr(lex, attr, value)
        if not is_oov:
            key = hash_string(string)
            self._add_lex_to_vocab(key, lex)
        if lex == NULL:
            raise ValueError(Errors.E085.format(string=string))
        return lex

    cdef int _add_lex_to_vocab(self, hash_t key, const LexemeC* lex) except -1:
        self._by_hash.set(key, <void*>lex)
        self._by_orth.set(lex.orth, <void*>lex)
        self.length += 1

    def __contains__(self, key):
        """Check whether the string or int key has an entry in the vocabulary.

        string (unicode): The ID string.
        RETURNS (bool) Whether the string has an entry in the vocabulary.
        """
        cdef hash_t int_key
        if isinstance(key, bytes):
            int_key = hash_string(key.decode('utf8'))
        elif isinstance(key, unicode):
            int_key = hash_string(key)
        else:
            int_key = key
        lex = self._by_hash.get(int_key)
        return lex is not NULL

    def __iter__(self):
        """Iterate over the lexemes in the vocabulary.

        YIELDS (Lexeme): An entry in the vocabulary.
        """
        cdef attr_t key
        cdef size_t addr
        for key, addr in self._by_orth.items():
            lex = Lexeme(self, key)
            yield lex

    def __getitem__(self, id_or_string):
        """Retrieve a lexeme, given an int ID or a unicode string. If a
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
        if isinstance(id_or_string, unicode):
            orth = self.strings.add(id_or_string)
        else:
            orth = id_or_string
        return Lexeme(self, orth)

    cdef const TokenC* make_fused_token(self, substrings) except NULL:
        cdef int i
        tokens = <TokenC*>self.mem.alloc(len(substrings) + 1, sizeof(TokenC))
        for i, props in enumerate(substrings):
            props = intify_attrs(props, strings_map=self.strings,
                                 _do_deprecated=True)
            token = &tokens[i]
            # Set the special tokens up to have arbitrary attributes
            lex = <LexemeC*>self.get_by_orth(self.mem, props[ORTH])
            token.lex = lex
            if TAG in props:
                self.morphology.assign_tag(token, props[TAG])
            for attr_id, value in props.items():
                Token.set_struct_attr(token, attr_id, value)
                Lexeme.set_struct_attr(lex, attr_id, value)
        return tokens

    @property
    def vectors_length(self):
        return self.vectors.data.shape[1]

    def reset_vectors(self, *, width=None, shape=None):
        """Drop the current vector table. Because all vectors must be the same
        width, you have to call this to change the size of the vectors.
        """
        if width is not None and shape is not None:
            raise ValueError(Errors.E065.format(width=width, shape=shape))
        elif shape is not None:
            self.vectors = Vectors(shape=shape)
        else:
            width = width if width is not None else self.vectors.data.shape[1]
            self.vectors = Vectors(shape=(self.vectors.shape[0], width))

    def prune_vectors(self, nr_row, batch_size=1024):
        """Reduce the current vector table to `nr_row` unique entries. Words
        mapped to the discarded vectors will be remapped to the closest vector
        among those remaining.

        For example, suppose the original table had vectors for the words:
        ['sat', 'cat', 'feline', 'reclined']. If we prune the vector table to,
        two rows, we would discard the vectors for 'feline' and 'reclined'.
        These words would then be remapped to the closest remaining vector
        -- so "feline" would have the same vector as "cat", and "reclined"
        would have the same vector as "sat".

        The similarities are judged by cosine. The original vectors may
        be large, so the cosines are calculated in minibatches, to reduce
        memory usage.

        nr_row (int): The number of rows to keep in the vector table.
        batch_size (int): Batch of vectors for calculating the similarities.
            Larger batch sizes might be faster, while temporarily requiring
            more memory.
        RETURNS (dict): A dictionary keyed by removed words mapped to
            `(string, score)` tuples, where `string` is the entry the removed
            word was mapped to, and `score` the similarity score between the
            two words.
        """
        xp = get_array_module(self.vectors.data)
        # Make prob negative so it sorts by rank ascending
        # (key2row contains the rank)
        priority = [(-lex.prob, self.vectors.key2row[lex.orth], lex.orth)
                    for lex in self if lex.orth in self.vectors.key2row]
        priority.sort()
        indices = xp.asarray([i for (prob, i, key) in priority], dtype='i')
        keys = xp.asarray([key for (prob, i, key) in priority], dtype='uint64')

        keep = xp.ascontiguousarray(self.vectors.data[indices[:nr_row]])
        toss = xp.ascontiguousarray(self.vectors.data[indices[nr_row:]])

        self.vectors = Vectors(data=keep, keys=keys)

        syn_keys, syn_rows, scores = self.vectors.most_similar(toss)

        remap = {}
        for i, key in enumerate(keys[nr_row:]):
            self.vectors.add(key, row=syn_rows[i])
            word = self.strings[key]
            synonym = self.strings[syn_keys[i]]
            score = scores[i]
            remap[word] = (synonym, score)
        link_vectors_to_models(self)
        return remap

    def get_vector(self, orth):
        """Retrieve a vector for a word in the vocabulary. Words can be looked
        up by string or int ID. If no vectors data is loaded, ValueError is
        raised.

        RETURNS (numpy.ndarray): A word vector. Size
            and shape determined by the `vocab.vectors` instance. Usually, a
            numpy ndarray of shape (300,) and dtype float32.
        """
        if isinstance(orth, basestring_):
            orth = self.strings.add(orth)
        if orth in self.vectors.key2row:
            return self.vectors[orth]
        else:
            return numpy.zeros((self.vectors_length,), dtype='f')

    def set_vector(self, orth, vector):
        """Set a vector for a word in the vocabulary. Words can be referenced
        by string or int ID.
        """
        if isinstance(orth, basestring_):
            orth = self.strings.add(orth)
        if self.vectors.is_full and orth not in self.vectors:
            new_rows = max(100, int(self.vectors.shape[0]*1.3))
            if self.vectors.shape[1] == 0:
                width = vector.size
            else:
                width = self.vectors.shape[1]
            self.vectors.resize((new_rows, width))
            lex = self[orth] # Adds worse to vocab
            self.vectors.add(orth, vector=vector)
        self.vectors.add(orth, vector=vector)

    def has_vector(self, orth):
        """Check whether a word has a vector. Returns False if no vectors have
        been loaded. Words can be looked up by string or int ID."""
        if isinstance(orth, basestring_):
            orth = self.strings.add(orth)
        return orth in self.vectors

    def to_disk(self, path, **exclude):
        """Save the current state to a directory.

        path (unicode or Path): A path to a directory, which will be created if
            it doesn't exist. Paths may be either strings or Path-like objects.
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
        if self.vectors.name is not None:
            link_vectors_to_models(self)
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
                return self.vectors.to_bytes()

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
                return self.vectors.from_bytes(b)
        setters = OrderedDict((
            ('strings', lambda b: self.strings.from_bytes(b)),
            ('lexemes', lambda b: self.lexemes_from_bytes(b)),
            ('vectors', lambda b: serialize_vectors(b))
        ))
        util.from_bytes(bytes_data, setters, exclude)
        if self.vectors.name is not None:
            link_vectors_to_models(self)
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
        cdef void* ptr
        cdef unsigned char* bytes_ptr = bytes_data
        for i in range(0, len(bytes_data), chunk_size):
            lexeme = <LexemeC*>self.mem.alloc(1, sizeof(LexemeC))
            for j in range(sizeof(lex_data.data)):
                lex_data.data[j] = bytes_ptr[i+j]
            Lexeme.c_from_bytes(lexeme, lex_data)

            ptr = self.strings._map.get(lexeme.orth)
            if ptr == NULL:
                continue
            py_str = self.strings[lexeme.orth]
            if self.strings[py_str] != lexeme.orth:
                raise ValueError(Errors.E086.format(string=py_str,
                                                    orth_id=lexeme.orth,
                                                    hash_id=self.strings[py_str]))
            key = hash_string(py_str)
            self._by_hash.set(key, lexeme)
            self._by_orth.set(lexeme.orth, lexeme)
            self.length += 1

    def _reset_cache(self, keys, strings):
        for k in keys:
            del self._by_hash[k]

        if len(strings) != 0:
            self._by_orth = PreshMap()


def pickle_vocab(vocab):
    sstore = vocab.strings
    vectors = vocab.vectors
    morph = vocab.morphology
    length = vocab.length
    data_dir = vocab.data_dir
    lex_attr_getters = dill.dumps(vocab.lex_attr_getters)
    lexemes_data = vocab.lexemes_to_bytes()
    return (unpickle_vocab,
            (sstore, vectors, morph, data_dir, lex_attr_getters, lexemes_data, length))


def unpickle_vocab(sstore, vectors, morphology, data_dir,
                   lex_attr_getters, bytes lexemes_data, int length):
    cdef Vocab vocab = Vocab()
    vocab.length = length
    vocab.vectors = vectors
    vocab.strings = sstore
    vocab.morphology = morphology
    vocab.data_dir = data_dir
    vocab.lex_attr_getters = dill.loads(lex_attr_getters)
    vocab.lexemes_from_bytes(lexemes_data)
    vocab.length = length
    return vocab


copy_reg.pickle(Vocab, pickle_vocab, unpickle_vocab)
