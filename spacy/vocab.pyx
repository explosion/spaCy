# coding: utf8
# cython: profile=True
from __future__ import unicode_literals
from libc.string cimport memcpy

import srsly
from collections import OrderedDict
from thinc.neural.util import get_array_module

from .lexeme cimport EMPTY_LEXEME, OOV_RANK
from .lexeme cimport Lexeme
from .typedefs cimport attr_t
from .tokens.token cimport Token
from .attrs cimport LANG, ORTH, TAG, POS

from .compat import copy_reg, basestring_
from .errors import Errors
from .lemmatizer import Lemmatizer
from .attrs import intify_attrs, NORM
from .vectors import Vectors
from ._ml import link_vectors_to_models
from .lookups import Lookups
from . import util
from .lang.norm_exceptions import BASE_NORMS
from .lang.lex_attrs import LEX_ATTRS


cdef class Vocab:
    """A look-up table that allows you to access `Lexeme` objects. The `Vocab`
    instance also provides access to the `StringStore`, and owns underlying
    C-data that is shared between `Doc` objects.

    DOCS: https://spacy.io/api/vocab
    """
    def __init__(self, lex_attr_getters=None, tag_map=None, lemmatizer=None,
                 strings=tuple(), lookups=None, lookups_extra=None,
                 oov_prob=-20., vectors_name=None, **deprecated_kwargs):
        """Create the vocabulary.

        lex_attr_getters (dict): A dictionary mapping attribute IDs to
            functions to compute them. Defaults to `None`.
        tag_map (dict): Dictionary mapping fine-grained tags to coarse-grained
            parts-of-speech, and optionally morphological attributes.
        lemmatizer (object): A lemmatizer. Defaults to `None`.
        strings (StringStore): StringStore that maps strings to integers, and
            vice versa.
        lookups (Lookups): Container for large lookup tables and dictionaries.
        lookups_extra (Lookups): Container for optional lookup tables and dictionaries.
        oov_prob (float): Default OOV probability.
        vectors_name (unicode): Optional name to identify the vectors table.
        RETURNS (Vocab): The newly constructed object.
        """
        lex_attr_getters = lex_attr_getters if lex_attr_getters is not None else {}
        tag_map = tag_map if tag_map is not None else {}
        if lookups in (None, True, False):
            lookups = Lookups()
        if "lexeme_norm" not in lookups:
            lookups.add_table("lexeme_norm")
        if lemmatizer in (None, True, False):
            lemmatizer = Lemmatizer(lookups)
        if lookups_extra in (None, True, False):
            lookups_extra = Lookups()
        self.cfg = {'oov_prob': oov_prob}
        self.mem = Pool()
        self._by_orth = PreshMap()
        self.strings = StringStore()
        self.length = 0
        if strings:
            for string in strings:
                _ = self[string]
        self.lex_attr_getters = lex_attr_getters
        self.morphology = Morphology(self.strings, tag_map, lemmatizer)
        self.vectors = Vectors(name=vectors_name)
        self.lookups = lookups
        self.lookups_extra = lookups_extra

    @property
    def lang(self):
        langfunc = None
        if self.lex_attr_getters:
            langfunc = self.lex_attr_getters.get(LANG, None)
        return langfunc("_") if langfunc else ""

    property writing_system:
        """A dict with information about the language's writing system. To get
        the data, we use the vocab.lang property to fetch the Language class.
        If the Language class is not loaded, an empty dict is returned.
        """
        def __get__(self):
            if not util.lang_class_is_loaded(self.lang):
                return {}
            lang_class = util.get_lang_class(self.lang)
            return dict(lang_class.Defaults.writing_system)

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

    cdef const LexemeC* get(self, Pool mem, unicode string) except NULL:
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

    cdef const LexemeC* _new_lexeme(self, Pool mem, unicode string) except NULL:
        if len(string) < 3 or self.length < 10000:
            mem = self.mem
        cdef bint is_oov = mem is not self.mem
        lex = <LexemeC*>mem.alloc(sizeof(LexemeC), 1)
        lex.orth = self.strings.add(string)
        lex.length = len(string)
        if self.vectors is not None:
            lex.id = self.vectors.key2row.get(lex.orth, OOV_RANK)
        else:
            lex.id = OOV_RANK
        if self.lex_attr_getters is not None:
            for attr, func in self.lex_attr_getters.items():
                value = func(string)
                if isinstance(value, unicode):
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

        string (unicode): The ID string.
        RETURNS (bool) Whether the string has an entry in the vocabulary.

        DOCS: https://spacy.io/api/vocab#contains
        """
        cdef hash_t int_key
        if isinstance(key, bytes):
            int_key = self.strings[key.decode("utf8")]
        elif isinstance(key, unicode):
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

        id_or_string (int or unicode): The integer ID of a word, or its unicode
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
            elif POS in props:
                # Don't allow POS to be set without TAG -- this causes problems,
                # see #1773
                props.pop(POS)
            for attr_id, value in props.items():
                Token.set_struct_attr(token, attr_id, value)
                # NORM is the only one that overlaps between the two
                # (which is maybe not great?)
                if attr_id != NORM:
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

        DOCS: https://spacy.io/api/vocab#prune_vectors
        """
        xp = get_array_module(self.vectors.data)
        # Make prob negative so it sorts by rank ascending
        # (key2row contains the rank)
        priority = [(-lex.prob, self.vectors.key2row[lex.orth], lex.orth)
                    for lex in self if lex.orth in self.vectors.key2row]
        priority.sort()
        indices = xp.asarray([i for (prob, i, key) in priority], dtype="uint64")
        keys = xp.asarray([key for (prob, i, key) in priority], dtype="uint64")
        keep = xp.ascontiguousarray(self.vectors.data[indices[:nr_row]])
        toss = xp.ascontiguousarray(self.vectors.data[indices[nr_row:]])
        self.vectors = Vectors(data=keep, keys=keys[:nr_row], name=self.vectors.name)
        syn_keys, syn_rows, scores = self.vectors.most_similar(toss, batch_size=batch_size)
        remap = {}
        for i, key in enumerate(keys[nr_row:]):
            self.vectors.add(key, row=syn_rows[i][0])
            word = self.strings[key]
            synonym = self.strings[syn_keys[i][0]]
            score = scores[i][0]
            remap[word] = (synonym, score)
        link_vectors_to_models(self)
        return remap

    def get_vector(self, orth, minn=None, maxn=None):
        """Retrieve a vector for a word in the vocabulary. Words can be looked
        up by string or int ID. If no vectors data is loaded, ValueError is
        raised.
        
        If `minn` is defined, then the resulting vector uses Fasttext's 
        subword features by average over ngrams of `orth`.

        orth (int / unicode): The hash value of a word, or its unicode string.
        minn (int): Minimum n-gram length used for Fasttext's ngram computation. 
            Defaults to the length of `orth`.
        maxn (int): Maximum n-gram length used for Fasttext's ngram computation. 
            Defaults to the length of `orth`.
        RETURNS (numpy.ndarray): A word vector. Size
            and shape determined by the `vocab.vectors` instance. Usually, a
            numpy ndarray of shape (300,) and dtype float32.

        DOCS: https://spacy.io/api/vocab#get_vector
        """
        if isinstance(orth, basestring_):
            orth = self.strings.add(orth)
        word = self[orth].orth_
        if orth in self.vectors.key2row:
            return self.vectors[orth]
        # Assign default ngram limits to minn and maxn which is the length of the word.
        if minn is None:
            minn = len(word)
        if maxn is None:
            maxn = len(word)
        xp = get_array_module(self.vectors.data)
        vectors = xp.zeros((self.vectors_length,), dtype="f")
        # Fasttext's ngram computation taken from
        # https://github.com/facebookresearch/fastText
        ngrams_size = 0;
        for i in range(len(word)):
            ngram = ""
            if (word[i] and 0xC0) == 0x80:
                continue
            n = 1
            j = i
            while (j < len(word) and n <= maxn):
                if n > maxn:
                    break
                ngram += word[j]
                j = j + 1
                while (j < len(word) and (word[j] and 0xC0) == 0x80):
                    ngram += word[j]
                    j = j + 1
                if (n >= minn and not (n == 1 and (i == 0 or j == len(word)))):
                    if self.strings[ngram] in self.vectors.key2row:
                        vectors = xp.add(self.vectors[self.strings[ngram]], vectors)
                        ngrams_size += 1
                n = n + 1
        if ngrams_size > 0:
            vectors = vectors * (1.0/ngrams_size)
        return vectors

    def set_vector(self, orth, vector):
        """Set a vector for a word in the vocabulary. Words can be referenced
        by string or int ID.

        orth (int / unicode): The word.
        vector (numpy.ndarray[ndim=1, dtype='float32']): The vector to set.

        DOCS: https://spacy.io/api/vocab#set_vector
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
        lex = self[orth]  # Add word to vocab if necessary
        row = self.vectors.add(orth, vector=vector)
        lex.rank = row

    def has_vector(self, orth):
        """Check whether a word has a vector. Returns False if no vectors have
        been loaded. Words can be looked up by string or int ID.

        orth (int / unicode): The word.
        RETURNS (bool): Whether the word has a vector.

        DOCS: https://spacy.io/api/vocab#has_vector
        """
        if isinstance(orth, basestring_):
            orth = self.strings.add(orth)
        return orth in self.vectors

    def to_disk(self, path, exclude=tuple(), **kwargs):
        """Save the current state to a directory.

        path (unicode or Path): A path to a directory, which will be created if
            it doesn't exist.
        exclude (list): String names of serialization fields to exclude.

        DOCS: https://spacy.io/api/vocab#to_disk
        """
        path = util.ensure_path(path)
        if not path.exists():
            path.mkdir()
        setters = ["strings", "vectors"]
        exclude = util.get_serialization_exclude(setters, exclude, kwargs)
        if "strings" not in exclude:
            self.strings.to_disk(path / "strings.json")
        if "vectors" not in "exclude" and self.vectors is not None:
            self.vectors.to_disk(path)
        if "lookups" not in "exclude" and self.lookups is not None:
            self.lookups.to_disk(path)
        if "lookups_extra" not in "exclude" and self.lookups_extra is not None:
            self.lookups_extra.to_disk(path, filename="lookups_extra.bin")

    def from_disk(self, path, exclude=tuple(), **kwargs):
        """Loads state from a directory. Modifies the object in place and
        returns it.

        path (unicode or Path): A path to a directory.
        exclude (list): String names of serialization fields to exclude.
        RETURNS (Vocab): The modified `Vocab` object.

        DOCS: https://spacy.io/api/vocab#to_disk
        """
        path = util.ensure_path(path)
        getters = ["strings", "vectors"]
        exclude = util.get_serialization_exclude(getters, exclude, kwargs)
        if "strings" not in exclude:
            self.strings.from_disk(path / "strings.json")  # TODO: add exclude?
        if "vectors" not in exclude:
            if self.vectors is not None:
                self.vectors.from_disk(path, exclude=["strings"])
            if self.vectors.name is not None:
                link_vectors_to_models(self)
        if "lookups" not in exclude:
            self.lookups.from_disk(path)
        if "lookups_extra" not in exclude:
            self.lookups_extra.from_disk(path, filename="lookups_extra.bin")
        if "lexeme_norm" in self.lookups:
            self.lex_attr_getters[NORM] = util.add_lookups(
                self.lex_attr_getters.get(NORM, LEX_ATTRS[NORM]), self.lookups.get_table("lexeme_norm")
            )
        self.length = 0
        self._by_orth = PreshMap()
        return self

    def to_bytes(self, exclude=tuple(), **kwargs):
        """Serialize the current state to a binary string.

        exclude (list): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized form of the `Vocab` object.

        DOCS: https://spacy.io/api/vocab#to_bytes
        """
        def deserialize_vectors():
            if self.vectors is None:
                return None
            else:
                return self.vectors.to_bytes()

        getters = OrderedDict((
            ("strings", lambda: self.strings.to_bytes()),
            ("vectors", deserialize_vectors),
            ("lookups", lambda: self.lookups.to_bytes()),
            ("lookups_extra", lambda: self.lookups_extra.to_bytes())
        ))
        exclude = util.get_serialization_exclude(getters, exclude, kwargs)
        return util.to_bytes(getters, exclude)

    def from_bytes(self, bytes_data, exclude=tuple(), **kwargs):
        """Load state from a binary string.

        bytes_data (bytes): The data to load from.
        exclude (list): String names of serialization fields to exclude.
        RETURNS (Vocab): The `Vocab` object.

        DOCS: https://spacy.io/api/vocab#from_bytes
        """
        def serialize_vectors(b):
            if self.vectors is None:
                return None
            else:
                return self.vectors.from_bytes(b)

        setters = OrderedDict((
            ("strings", lambda b: self.strings.from_bytes(b)),
            ("vectors", lambda b: serialize_vectors(b)),
            ("lookups", lambda b: self.lookups.from_bytes(b)),
            ("lookups_extra", lambda b: self.lookups_extra.from_bytes(b))
        ))
        exclude = util.get_serialization_exclude(setters, exclude, kwargs)
        util.from_bytes(bytes_data, setters, exclude)
        if "lexeme_norm" in self.lookups:
            self.lex_attr_getters[NORM] = util.add_lookups(
                self.lex_attr_getters.get(NORM, LEX_ATTRS[NORM]), self.lookups.get_table("lexeme_norm")
            )
        self.length = 0
        self._by_orth = PreshMap()
        if self.vectors.name is not None:
            link_vectors_to_models(self)
        return self

    def _reset_cache(self, keys, strings):
        # I'm not sure this made sense. Disable it for now.
        raise NotImplementedError


    def load_extra_lookups(self, table_name):
        if table_name not in self.lookups_extra:
            if self.lang + "_extra" in util.registry.lookups:
                tables = util.registry.lookups.get(self.lang + "_extra")
                for name, filename in tables.items():
                    if table_name == name:
                        data = util.load_language_data(filename)
                        self.lookups_extra.add_table(name, data)
        if table_name not in self.lookups_extra:
            self.lookups_extra.add_table(table_name)
        return self.lookups_extra.get_table(table_name)


def pickle_vocab(vocab):
    sstore = vocab.strings
    vectors = vocab.vectors
    morph = vocab.morphology
    data_dir = vocab.data_dir
    lex_attr_getters = srsly.pickle_dumps(vocab.lex_attr_getters)
    lookups = vocab.lookups
    lookups_extra = vocab.lookups_extra
    return (unpickle_vocab,
            (sstore, vectors, morph, data_dir, lex_attr_getters, lookups, lookups_extra))


def unpickle_vocab(sstore, vectors, morphology, data_dir,
                   lex_attr_getters, lookups, lookups_extra):
    cdef Vocab vocab = Vocab()
    vocab.vectors = vectors
    vocab.strings = sstore
    vocab.morphology = morphology
    vocab.data_dir = data_dir
    vocab.lex_attr_getters = srsly.pickle_loads(lex_attr_getters)
    vocab.lookups = lookups
    vocab.lookups_extra = lookups_extra
    return vocab


copy_reg.pickle(Vocab, pickle_vocab, unpickle_vocab)
