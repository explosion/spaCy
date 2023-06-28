# cython: profile=True
from libc.string cimport memcpy

import functools

import numpy
import srsly
from thinc.api import get_array_module, get_current_ops

from .attrs cimport LANG, ORTH
from .lexeme cimport EMPTY_LEXEME, OOV_RANK, Lexeme
from .tokens.token cimport Token
from .typedefs cimport attr_t

from . import util
from .attrs import IS_STOP, NORM, intify_attrs
from .compat import copy_reg
from .errors import Errors
from .lang.lex_attrs import LEX_ATTRS, get_lang, is_stop
from .lang.norm_exceptions import BASE_NORMS
from .lookups import Lookups
from .util import registry
from .vectors import Mode as VectorsMode
from .vectors import Vectors


def create_vocab(lang, defaults, vectors_name=None):
    # If the spacy-lookups-data package is installed, we pre-populate the lookups
    # with lexeme data, if available
    lex_attrs = {**LEX_ATTRS, **defaults.lex_attr_getters}
    # This is messy, but it's the minimal working fix to Issue #639.
    lex_attrs[IS_STOP] = functools.partial(is_stop, stops=defaults.stop_words)
    # Ensure that getter can be pickled
    lex_attrs[LANG] = functools.partial(get_lang, lang=lang)
    lex_attrs[NORM] = util.add_lookups(
        lex_attrs.get(NORM, LEX_ATTRS[NORM]),
        BASE_NORMS,
    )
    return Vocab(
        lex_attr_getters=lex_attrs,
        writing_system=defaults.writing_system,
        get_noun_chunks=defaults.syntax_iterators.get("noun_chunks"),
        vectors_name=vectors_name,
    )


cdef class Vocab:
    """A look-up table that allows you to access `Lexeme` objects. The `Vocab`
    instance also provides access to the `StringStore`, and owns underlying
    C-data that is shared between `Doc` objects.

    DOCS: https://spacy.io/api/vocab
    """
    def __init__(self, lex_attr_getters=None, strings=tuple(), lookups=None,
                 oov_prob=-20., vectors_name=None, writing_system={},
                 get_noun_chunks=None, **deprecated_kwargs):
        """Create the vocabulary.

        lex_attr_getters (dict): A dictionary mapping attribute IDs to
            functions to compute them. Defaults to `None`.
        strings (StringStore): StringStore that maps strings to integers, and
            vice versa.
        lookups (Lookups): Container for large lookup tables and dictionaries.
        oov_prob (float): Default OOV probability.
        vectors_name (str): Optional name to identify the vectors table.
        get_noun_chunks (Optional[Callable[[Union[Doc, Span], Iterator[Tuple[int, int, int]]]]]):
            A function that yields base noun phrases used for Doc.noun_chunks.
        """
        lex_attr_getters = lex_attr_getters if lex_attr_getters is not None else {}
        if lookups in (None, True, False):
            lookups = Lookups()
        self.cfg = {'oov_prob': oov_prob}
        self.mem = Pool()
        self._by_orth = PreshMap()
        self.strings = StringStore()
        self.length = 0
        if strings:
            for string in strings:
                _ = self[string]
        self.lex_attr_getters = lex_attr_getters
        self.morphology = Morphology(self.strings)
        self.vectors = Vectors(strings=self.strings, name=vectors_name)
        self.lookups = lookups
        self.writing_system = writing_system
        self.get_noun_chunks = get_noun_chunks

    property vectors:
        def __get__(self):
            return self._vectors

        def __set__(self, vectors):
            for s in vectors.strings:
                self.strings.add(s)
            self._vectors = vectors
            self._vectors.strings = self.strings

    @property
    def lang(self):
        langfunc = None
        if self.lex_attr_getters:
            langfunc = self.lex_attr_getters.get(LANG, None)
        return langfunc("_") if langfunc else ""

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

        flag_getter (callable): A function `f(str) -> bool`, to get the
            flag value.
        flag_id (int): An integer between 1 and 63 (inclusive), specifying
            the bit at which the flag will be stored. If -1, the lowest
            available bit will be chosen.
        RETURNS (int): The integer ID by which the flag value can be checked.

        DOCS: https://spacy.io/api/vocab#add_flag
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

    cdef const LexemeC* get(self, Pool mem, str string) except NULL:
        """Get a pointer to a `LexemeC` from the lexicon, creating a new
        `Lexeme` if necessary using memory acquired from the given pool. If the
        pool is the lexicon's own memory, the lexeme is saved in the lexicon.
        """
        if string == "":
            return &EMPTY_LEXEME
        cdef LexemeC* lex
        cdef hash_t key = self.strings[string]
        lex = <LexemeC*>self._by_orth.get(key)
        cdef size_t addr
        if lex != NULL:
            assert lex.orth in self.strings
            if lex.orth != key:
                raise KeyError(Errors.E064.format(string=lex.orth,
                                                  orth=key, orth_id=string))
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

    cdef const LexemeC* _new_lexeme(self, Pool mem, str string) except NULL:
        # I think this heuristic is bad, and the Vocab should always
        # own the lexemes. It avoids weird bugs this way, as it's how the thing
        # was originally supposed to work. The best solution to the growing
        # memory use is to periodically reset the vocab, which is an action
        # that should be up to the user to do (so we don't need to keep track
        # of the doc ownership).
        # TODO: Change the C API so that the mem isn't passed in here.
        mem = self.mem
        #if len(string) < 3 or self.length < 10000:
        #    mem = self.mem
        cdef bint is_oov = mem is not self.mem
        lex = <LexemeC*>mem.alloc(1, sizeof(LexemeC))
        lex.orth = self.strings.add(string)
        lex.length = len(string)
        if self.vectors is not None:
            lex.id = self.vectors.key2row.get(lex.orth, OOV_RANK)
        else:
            lex.id = OOV_RANK
        if self.lex_attr_getters is not None:
            for attr, func in self.lex_attr_getters.items():
                value = func(string)
                if isinstance(value, str):
                    value = self.strings.add(value)
                if value is not None:
                    Lexeme.set_struct_attr(lex, attr, value)
        if not is_oov:
            self._add_lex_to_vocab(lex.orth, lex)
        if lex == NULL:
            raise ValueError(Errors.E085.format(string=string))
        return lex

    cdef int _add_lex_to_vocab(self, hash_t key, const LexemeC* lex) except -1:
        self._by_orth.set(lex.orth, <void*>lex)
        self.length += 1

    def __contains__(self, key):
        """Check whether the string or int key has an entry in the vocabulary.

        string (str): The ID string.
        RETURNS (bool) Whether the string has an entry in the vocabulary.

        DOCS: https://spacy.io/api/vocab#contains
        """
        cdef hash_t int_key
        if isinstance(key, bytes):
            int_key = self.strings[key.decode("utf8")]
        elif isinstance(key, str):
            int_key = self.strings[key]
        else:
            int_key = key
        lex = self._by_orth.get(int_key)
        return lex is not NULL

    def __iter__(self):
        """Iterate over the lexemes in the vocabulary.

        YIELDS (Lexeme): An entry in the vocabulary.

        DOCS: https://spacy.io/api/vocab#iter
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

        id_or_string (int or str): The integer ID of a word, or its unicode
            string. If `int >= Lexicon.size`, `IndexError` is raised. If
            `id_or_string` is neither an int nor a unicode string, `ValueError`
            is raised.
        RETURNS (Lexeme): The lexeme indicated by the given ID.

        EXAMPLE:
            >>> apple = nlp.vocab.strings["apple"]
            >>> assert nlp.vocab[apple] == nlp.vocab[u"apple"]

        DOCS: https://spacy.io/api/vocab#getitem
        """
        cdef attr_t orth
        if isinstance(id_or_string, str):
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
            for attr_id, value in props.items():
                Token.set_struct_attr(token, attr_id, value)
                # NORM is the only one that overlaps between the two
                # (which is maybe not great?)
                if attr_id != NORM:
                    Lexeme.set_struct_attr(lex, attr_id, value)
        return tokens

    @property
    def vectors_length(self):
        return self.vectors.shape[1]

    def reset_vectors(self, *, width=None, shape=None):
        """Drop the current vector table. Because all vectors must be the same
        width, you have to call this to change the size of the vectors.
        """
        if width is not None and shape is not None:
            raise ValueError(Errors.E065.format(width=width, shape=shape))
        elif shape is not None:
            self.vectors = Vectors(strings=self.strings, shape=shape)
        else:
            width = width if width is not None else self.vectors.shape[1]
            self.vectors = Vectors(strings=self.strings, shape=(self.vectors.shape[0], width))

    def deduplicate_vectors(self):
        if self.vectors.mode != VectorsMode.default:
            raise ValueError(Errors.E858.format(
                mode=self.vectors.mode,
                alternative=""
            ))
        ops = get_current_ops()
        xp = get_array_module(self.vectors.data)
        filled = xp.asarray(
            sorted(list({row for row in self.vectors.key2row.values()}))
        )
        # deduplicate data and remap keys
        data = numpy.unique(ops.to_numpy(self.vectors.data[filled]), axis=0)
        data = ops.asarray(data)
        if data.shape == self.vectors.data.shape:
            # nothing to deduplicate
            return
        row_by_bytes = {row.tobytes(): i for i, row in enumerate(data)}
        key2row = {
            key: row_by_bytes[self.vectors.data[row].tobytes()]
            for key, row in self.vectors.key2row.items()
        }
        # replace vectors with deduplicated version
        self.vectors = Vectors(strings=self.strings, data=data, name=self.vectors.name)
        for key, row in key2row.items():
            self.vectors.add(key, row=row)

    def prune_vectors(self, nr_row, batch_size=1024):
        """Reduce the current vector table to `nr_row` unique entries. Words
        mapped to the discarded vectors will be remapped to the closest vector
        among those remaining.

        For example, suppose the original table had vectors for the words:
        ['sat', 'cat', 'feline', 'reclined']. If we prune the vector table to
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

        DOCS: https://spacy.io/api/vocab#prune_vectors
        """
        if self.vectors.mode != VectorsMode.default:
            raise ValueError(Errors.E858.format(
                mode=self.vectors.mode,
                alternative=""
            ))
        ops = get_current_ops()
        xp = get_array_module(self.vectors.data)
        # Make sure all vectors are in the vocab
        for orth in self.vectors:
            self[orth]
        # Make prob negative so it sorts by rank ascending
        # (key2row contains the rank)
        priority = []
        cdef Lexeme lex
        cdef attr_t value
        for lex in self:
            value = Lexeme.get_struct_attr(lex.c, self.vectors.attr)
            if value in self.vectors.key2row:
                priority.append((-lex.prob, self.vectors.key2row[value], value))
        priority.sort()
        indices = xp.asarray([i for (prob, i, key) in priority], dtype="uint64")
        keys = xp.asarray([key for (prob, i, key) in priority], dtype="uint64")
        keep = xp.ascontiguousarray(self.vectors.data[indices[:nr_row]])
        toss = xp.ascontiguousarray(self.vectors.data[indices[nr_row:]])
        self.vectors = Vectors(strings=self.strings, data=keep, keys=keys[:nr_row], name=self.vectors.name)
        syn_keys, syn_rows, scores = self.vectors.most_similar(toss, batch_size=batch_size)
        syn_keys = ops.to_numpy(syn_keys)
        remap = {}
        for i, key in enumerate(ops.to_numpy(keys[nr_row:])):
            self.vectors.add(key, row=syn_rows[i][0])
            word = self.strings[key]
            synonym = self.strings[syn_keys[i][0]]
            score = scores[i][0]
            remap[word] = (synonym, score)
        return remap

    def get_vector(self, orth):
        """Retrieve a vector for a word in the vocabulary. Words can be looked
        up by string or int ID. If the current vectors do not contain an entry
        for the word, a 0-vector with the same number of dimensions as the
        current vectors is returned.

        orth (int / unicode): The hash value of a word, or its unicode string.
        RETURNS (numpy.ndarray or cupy.ndarray): A word vector. Size
            and shape determined by the `vocab.vectors` instance. Usually, a
            numpy ndarray of shape (300,) and dtype float32.

        DOCS: https://spacy.io/api/vocab#get_vector
        """
        if isinstance(orth, str):
            orth = self.strings.add(orth)
        cdef Lexeme lex = self[orth]
        key = Lexeme.get_struct_attr(lex.c, self.vectors.attr)
        if self.has_vector(key):
            return self.vectors[key]
        xp = get_array_module(self.vectors.data)
        vectors = xp.zeros((self.vectors_length,), dtype="f")
        return vectors

    def set_vector(self, orth, vector):
        """Set a vector for a word in the vocabulary. Words can be referenced
        by string or int ID.

        orth (int / str): The word.
        vector (numpy.ndarray or cupy.nadarry[ndim=1, dtype='float32']): The vector to set.

        DOCS: https://spacy.io/api/vocab#set_vector
        """
        if isinstance(orth, str):
            orth = self.strings.add(orth)
        cdef Lexeme lex = self[orth]
        key = Lexeme.get_struct_attr(lex.c, self.vectors.attr)
        if self.vectors.is_full and key not in self.vectors:
            new_rows = max(100, int(self.vectors.shape[0]*1.3))
            if self.vectors.shape[1] == 0:
                width = vector.size
            else:
                width = self.vectors.shape[1]
            self.vectors.resize((new_rows, width))
        row = self.vectors.add(key, vector=vector)
        if row >= 0:
            lex.rank = row

    def has_vector(self, orth):
        """Check whether a word has a vector. Returns False if no vectors have
        been loaded. Words can be looked up by string or int ID.

        orth (int / str): The word.
        RETURNS (bool): Whether the word has a vector.

        DOCS: https://spacy.io/api/vocab#has_vector
        """
        if isinstance(orth, str):
            orth = self.strings.add(orth)
        cdef Lexeme lex = self[orth]
        key = Lexeme.get_struct_attr(lex.c, self.vectors.attr)
        return key in self.vectors

    property lookups:
        def __get__(self):
            return self._lookups

        def __set__(self, lookups):
            self._lookups = lookups
            if lookups.has_table("lexeme_norm"):
                self.lex_attr_getters[NORM] = util.add_lookups(
                    self.lex_attr_getters.get(NORM, LEX_ATTRS[NORM]),
                    self.lookups.get_table("lexeme_norm"),
                )


    def to_disk(self, path, *, exclude=tuple()):
        """Save the current state to a directory.

        path (str or Path): A path to a directory, which will be created if
            it doesn't exist.
        exclude (Iterable[str]): String names of serialization fields to exclude.

        DOCS: https://spacy.io/api/vocab#to_disk
        """
        path = util.ensure_path(path)
        if not path.exists():
            path.mkdir()
        setters = ["strings", "vectors"]
        if "strings" not in exclude:
            self.strings.to_disk(path / "strings.json")
        if "vectors" not in exclude:
            self.vectors.to_disk(path, exclude=["strings"])
        if "lookups" not in exclude:
            self.lookups.to_disk(path)

    def from_disk(self, path, *, exclude=tuple()):
        """Loads state from a directory. Modifies the object in place and
        returns it.

        path (str or Path): A path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (Vocab): The modified `Vocab` object.

        DOCS: https://spacy.io/api/vocab#to_disk
        """
        path = util.ensure_path(path)
        getters = ["strings", "vectors"]
        if "strings" not in exclude:
            self.strings.from_disk(path / "strings.json")  # TODO: add exclude?
        if "vectors" not in exclude:
            if self.vectors is not None:
                self.vectors.from_disk(path, exclude=["strings"])
        if "lookups" not in exclude:
            self.lookups.from_disk(path)
        if "lexeme_norm" in self.lookups:
            self.lex_attr_getters[NORM] = util.add_lookups(
                self.lex_attr_getters.get(NORM, LEX_ATTRS[NORM]), self.lookups.get_table("lexeme_norm")
            )
        self.length = 0
        self._by_orth = PreshMap()
        return self

    def to_bytes(self, *, exclude=tuple()):
        """Serialize the current state to a binary string.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized form of the `Vocab` object.

        DOCS: https://spacy.io/api/vocab#to_bytes
        """
        def deserialize_vectors():
            if self.vectors is None:
                return None
            else:
                return self.vectors.to_bytes(exclude=["strings"])

        getters = {
            "strings": lambda: self.strings.to_bytes(),
            "vectors": deserialize_vectors,
            "lookups": lambda: self.lookups.to_bytes(),
        }
        return util.to_bytes(getters, exclude)

    def from_bytes(self, bytes_data, *, exclude=tuple()):
        """Load state from a binary string.

        bytes_data (bytes): The data to load from.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (Vocab): The `Vocab` object.

        DOCS: https://spacy.io/api/vocab#from_bytes
        """
        def serialize_vectors(b):
            if self.vectors is None:
                return None
            else:
                return self.vectors.from_bytes(b, exclude=["strings"])

        setters = {
            "strings": lambda b: self.strings.from_bytes(b),
            "vectors": lambda b: serialize_vectors(b),
            "lookups": lambda b: self.lookups.from_bytes(b),
        }
        util.from_bytes(bytes_data, setters, exclude)
        if "lexeme_norm" in self.lookups:
            self.lex_attr_getters[NORM] = util.add_lookups(
                self.lex_attr_getters.get(NORM, LEX_ATTRS[NORM]), self.lookups.get_table("lexeme_norm")
            )
        self.length = 0
        self._by_orth = PreshMap()
        return self

    def _reset_cache(self, keys, strings):
        # I'm not sure this made sense. Disable it for now.
        raise NotImplementedError


def pickle_vocab(vocab):
    sstore = vocab.strings
    vectors = vocab.vectors
    morph = vocab.morphology
    _unused_object = vocab._unused_object
    lex_attr_getters = srsly.pickle_dumps(vocab.lex_attr_getters)
    lookups = vocab.lookups
    get_noun_chunks = vocab.get_noun_chunks
    return (unpickle_vocab,
            (sstore, vectors, morph, _unused_object, lex_attr_getters, lookups, get_noun_chunks))


def unpickle_vocab(sstore, vectors, morphology, _unused_object,
                   lex_attr_getters, lookups, get_noun_chunks):
    cdef Vocab vocab = Vocab()
    vocab.vectors = vectors
    vocab.strings = sstore
    vocab.morphology = morphology
    vocab._unused_object = _unused_object
    vocab.lex_attr_getters = srsly.pickle_loads(lex_attr_getters)
    vocab.lookups = lookups
    vocab.get_noun_chunks = get_noun_chunks
    return vocab


copy_reg.pickle(Vocab, pickle_vocab, unpickle_vocab)
