# cython: embedsignature=True
# cython: profile=False
# Compiler crashes on memory view coercion without this. Should report bug.
cimport numpy as np
from libc.string cimport memset

np.import_array()

import warnings

import numpy
from thinc.api import get_array_module

from .attrs cimport (
    IS_ALPHA,
    IS_ASCII,
    IS_BRACKET,
    IS_CURRENCY,
    IS_DIGIT,
    IS_LEFT_PUNCT,
    IS_LOWER,
    IS_PUNCT,
    IS_QUOTE,
    IS_RIGHT_PUNCT,
    IS_SPACE,
    IS_STOP,
    IS_TITLE,
    IS_UPPER,
    LIKE_EMAIL,
    LIKE_NUM,
    LIKE_URL,
)
from .typedefs cimport attr_t, flags_t

from .attrs import intify_attrs
from .errors import Errors, Warnings

OOV_RANK = 0xffffffffffffffff  # UINT64_MAX
memset(&EMPTY_LEXEME, 0, sizeof(LexemeC))
EMPTY_LEXEME.id = OOV_RANK


cdef class Lexeme:
    """An entry in the vocabulary. A `Lexeme` has no string context – it's a
    word-type, as opposed to a word token.  It therefore has no part-of-speech
    tag, dependency parse, or lemma (lemmatization depends on the
    part-of-speech tag).

    DOCS: https://spacy.io/api/lexeme
    """
    def __init__(self, Vocab vocab, attr_t orth):
        """Create a Lexeme object.

        vocab (Vocab): The parent vocabulary
        orth (uint64): The orth id of the lexeme.
        Returns (Lexeme): The newly constructd object.
        """
        self.vocab = vocab
        self.orth = orth
        self.c = <LexemeC*><void*>vocab.get_by_orth(vocab.mem, orth)
        if self.c.orth != orth:
            raise ValueError(Errors.E071.format(orth=orth, vocab_orth=self.c.orth))

    def __richcmp__(self, other, int op):
        if other is None:
            if op == 0 or op == 1 or op == 2:
                return False
            else:
                return True
        if isinstance(other, Lexeme):
            a = self.orth
            b = other.orth
        elif isinstance(other, long):
            a = self.orth
            b = other
        elif isinstance(other, str):
            a = self.orth_
            b = other
        else:
            a = 0
            b = 1
        if op == 2:  # ==
            return a == b
        elif op == 3:  # !=
            return a != b
        elif op == 0:  # <
            return a < b
        elif op == 1:  # <=
            return a <= b
        elif op == 4:  # >
            return a > b
        elif op == 5:  # >=
            return a >= b
        else:
            raise NotImplementedError(op)

    def __hash__(self):
        return self.c.orth

    def set_attrs(self, **attrs):
        cdef attr_id_t attr
        attrs = intify_attrs(attrs)
        for attr, value in attrs.items():
            # skip PROB, e.g. from lexemes.jsonl
            if isinstance(value, float):
                continue
            elif isinstance(value, (int, long)):
                Lexeme.set_struct_attr(self.c, attr, value)
            else:
                Lexeme.set_struct_attr(self.c, attr, self.vocab.strings.add(value))

    def set_flag(self, attr_id_t flag_id, bint value):
        """Change the value of a boolean flag.

        flag_id (int): The attribute ID of the flag to set.
        value (bool): The new value of the flag.
        """
        Lexeme.c_set_flag(self.c, flag_id, value)

    def check_flag(self, attr_id_t flag_id):
        """Check the value of a boolean flag.

        flag_id (int): The attribute ID of the flag to query.
        RETURNS (bool): The value of the flag.
        """
        return True if Lexeme.c_check_flag(self.c, flag_id) else False

    def similarity(self, other):
        """Compute a semantic similarity estimate. Defaults to cosine over
        vectors.

        other (object): The object to compare with. By default, accepts `Doc`,
            `Span`, `Token` and `Lexeme` objects.
        RETURNS (float): A scalar similarity score. Higher is more similar.
        """
        # Return 1.0 similarity for matches
        if hasattr(other, "orth"):
            if self.c.orth == other.orth:
                return 1.0
        elif (
            hasattr(other, "__len__") and len(other) == 1
            and hasattr(other[0], "orth")
            and self.c.orth == other[0].orth
        ):
            return 1.0
        if self.vector_norm == 0 or other.vector_norm == 0:
            warnings.warn(Warnings.W008.format(obj="Lexeme"))
            return 0.0
        vector = self.vector
        xp = get_array_module(vector)
        result = xp.dot(vector, other.vector) / (self.vector_norm * other.vector_norm)
        # ensure we get a scalar back (numpy does this automatically but cupy doesn't)
        return result.item()

    @property
    def has_vector(self):
        """RETURNS (bool): Whether a word vector is associated with the object.
        """
        return self.vocab.has_vector(self.c.orth)

    @property
    def vector_norm(self):
        """RETURNS (float): The L2 norm of the vector representation."""
        vector = self.vector
        return numpy.sqrt((vector**2).sum())

    @property
    def vector(self):
        """A real-valued meaning representation.

        RETURNS (numpy.ndarray[ndim=1, dtype='float32']): A 1D numpy array
            representing the lexeme's semantics.
        """
        cdef int length = self.vocab.vectors_length
        if length == 0:
            raise ValueError(Errors.E010)
        return self.vocab.get_vector(self.c.orth)

    @vector.setter
    def vector(self, vector):
        if len(vector) != self.vocab.vectors_length:
            raise ValueError(Errors.E073.format(new_length=len(vector),
                                                length=self.vocab.vectors_length))
        self.vocab.set_vector(self.c.orth, vector)

    @property
    def rank(self):
        """RETURNS (str): Sequential ID of the lexeme's lexical type, used
            to index into tables, e.g. for word vectors."""
        return self.c.id

    @rank.setter
    def rank(self, value):
        self.c.id = value

    @property
    def sentiment(self):
        """RETURNS (float): A scalar value indicating the positivity or
            negativity of the lexeme."""
        sentiment_table = self.vocab.lookups.get_table("lexeme_sentiment", {})
        return sentiment_table.get(self.c.orth, 0.0)

    @sentiment.setter
    def sentiment(self, float x):
        if "lexeme_sentiment" not in self.vocab.lookups:
            self.vocab.lookups.add_table("lexeme_sentiment")
        sentiment_table = self.vocab.lookups.get_table("lexeme_sentiment")
        sentiment_table[self.c.orth] = x

    @property
    def orth_(self):
        """RETURNS (str): The original verbatim text of the lexeme
            (identical to `Lexeme.text`). Exists mostly for consistency with
            the other attributes."""
        return self.vocab.strings[self.c.orth]

    @property
    def text(self):
        """RETURNS (str): The original verbatim text of the lexeme."""
        return self.orth_

    @property
    def lower(self):
        """RETURNS (uint64): Lowercase form of the lexeme."""
        return self.c.lower

    @lower.setter
    def lower(self, attr_t x):
        self.c.lower = x

    @property
    def norm(self):
        """RETURNS (uint64): The lexeme's norm, i.e. a normalised form of the
            lexeme text.
        """
        return self.c.norm

    @norm.setter
    def norm(self, attr_t x):
        if "lexeme_norm" not in self.vocab.lookups:
            self.vocab.lookups.add_table("lexeme_norm")
        norm_table = self.vocab.lookups.get_table("lexeme_norm")
        norm_table[self.c.orth] = self.vocab.strings[x]
        self.c.norm = x

    @property
    def shape(self):
        """RETURNS (uint64): Transform of the word's string, to show
            orthographic features.
        """
        return self.c.shape

    @shape.setter
    def shape(self, attr_t x):
        self.c.shape = x

    @property
    def prefix(self):
        """RETURNS (uint64): Length-N substring from the start of the word.
            Defaults to `N=1`.
        """
        return self.c.prefix

    @prefix.setter
    def prefix(self, attr_t x):
        self.c.prefix = x

    @property
    def suffix(self):
        """RETURNS (uint64): Length-N substring from the end of the word.
            Defaults to `N=3`.
        """
        return self.c.suffix

    @suffix.setter
    def suffix(self, attr_t x):
        self.c.suffix = x

    @property
    def cluster(self):
        """RETURNS (int): Brown cluster ID."""
        cluster_table = self.vocab.lookups.get_table("lexeme_cluster", {})
        return cluster_table.get(self.c.orth, 0)

    @cluster.setter
    def cluster(self, int x):
        cluster_table = self.vocab.lookups.get_table("lexeme_cluster", {})
        cluster_table[self.c.orth] = x

    @property
    def lang(self):
        """RETURNS (uint64): Language of the parent vocabulary."""
        return self.c.lang

    @lang.setter
    def lang(self, attr_t x):
        self.c.lang = x

    @property
    def prob(self):
        """RETURNS (float): Smoothed log probability estimate of the lexeme's
            type."""
        prob_table = self.vocab.lookups.get_table("lexeme_prob", {})
        settings_table = self.vocab.lookups.get_table("lexeme_settings", {})
        default_oov_prob = settings_table.get("oov_prob", -20.0)
        return prob_table.get(self.c.orth, default_oov_prob)

    @prob.setter
    def prob(self, float x):
        prob_table = self.vocab.lookups.get_table("lexeme_prob", {})
        prob_table[self.c.orth] = x

    @property
    def lower_(self):
        """RETURNS (str): Lowercase form of the word."""
        return self.vocab.strings[self.c.lower]

    @lower_.setter
    def lower_(self, str x):
        self.c.lower = self.vocab.strings.add(x)

    @property
    def norm_(self):
        """RETURNS (str): The lexeme's norm, i.e. a normalised form of the
            lexeme text.
        """
        return self.vocab.strings[self.c.norm]

    @norm_.setter
    def norm_(self, str x):
        self.norm = self.vocab.strings.add(x)

    @property
    def shape_(self):
        """RETURNS (str): Transform of the word's string, to show
            orthographic features.
        """
        return self.vocab.strings[self.c.shape]

    @shape_.setter
    def shape_(self, str x):
        self.c.shape = self.vocab.strings.add(x)

    @property
    def prefix_(self):
        """RETURNS (str): Length-N substring from the start of the word.
            Defaults to `N=1`.
        """
        return self.vocab.strings[self.c.prefix]

    @prefix_.setter
    def prefix_(self, str x):
        self.c.prefix = self.vocab.strings.add(x)

    @property
    def suffix_(self):
        """RETURNS (str): Length-N substring from the end of the word.
            Defaults to `N=3`.
        """
        return self.vocab.strings[self.c.suffix]

    @suffix_.setter
    def suffix_(self, str x):
        self.c.suffix = self.vocab.strings.add(x)

    @property
    def lang_(self):
        """RETURNS (str): Language of the parent vocabulary."""
        return self.vocab.strings[self.c.lang]

    @lang_.setter
    def lang_(self, str x):
        self.c.lang = self.vocab.strings.add(x)

    @property
    def flags(self):
        """RETURNS (uint64): Container of the lexeme's binary flags."""
        return self.c.flags

    @flags.setter
    def flags(self, flags_t x):
        self.c.flags = x

    @property
    def is_oov(self):
        """RETURNS (bool): Whether the lexeme is out-of-vocabulary."""
        return self.orth not in self.vocab.vectors

    @property
    def is_stop(self):
        """RETURNS (bool): Whether the lexeme is a stop word."""
        return Lexeme.c_check_flag(self.c, IS_STOP)

    @is_stop.setter
    def is_stop(self, bint x):
        Lexeme.c_set_flag(self.c, IS_STOP, x)

    @property
    def is_alpha(self):
        """RETURNS (bool): Whether the lexeme consists of alphabetic
            characters. Equivalent to `lexeme.text.isalpha()`.
        """
        return Lexeme.c_check_flag(self.c, IS_ALPHA)

    @is_alpha.setter
    def is_alpha(self, bint x):
        Lexeme.c_set_flag(self.c, IS_ALPHA, x)

    @property
    def is_ascii(self):
        """RETURNS (bool): Whether the lexeme consists of ASCII characters.
            Equivalent to `[any(ord(c) >= 128 for c in lexeme.text)]`.
        """
        return Lexeme.c_check_flag(self.c, IS_ASCII)

    @is_ascii.setter
    def is_ascii(self, bint x):
        Lexeme.c_set_flag(self.c, IS_ASCII, x)

    @property
    def is_digit(self):
        """RETURNS (bool): Whether the lexeme consists of digits. Equivalent
            to `lexeme.text.isdigit()`.
        """
        return Lexeme.c_check_flag(self.c, IS_DIGIT)

    @is_digit.setter
    def is_digit(self, bint x):
        Lexeme.c_set_flag(self.c, IS_DIGIT, x)

    @property
    def is_lower(self):
        """RETURNS (bool): Whether the lexeme is in lowercase. Equivalent to
            `lexeme.text.islower()`.
        """
        return Lexeme.c_check_flag(self.c, IS_LOWER)

    @is_lower.setter
    def is_lower(self, bint x):
        Lexeme.c_set_flag(self.c, IS_LOWER, x)

    @property
    def is_upper(self):
        """RETURNS (bool): Whether the lexeme is in uppercase. Equivalent to
            `lexeme.text.isupper()`.
        """
        return Lexeme.c_check_flag(self.c, IS_UPPER)

    @is_upper.setter
    def is_upper(self, bint x):
        Lexeme.c_set_flag(self.c, IS_UPPER, x)

    @property
    def is_title(self):
        """RETURNS (bool): Whether the lexeme is in titlecase. Equivalent to
            `lexeme.text.istitle()`.
        """
        return Lexeme.c_check_flag(self.c, IS_TITLE)

    @is_title.setter
    def is_title(self, bint x):
        Lexeme.c_set_flag(self.c, IS_TITLE, x)

    @property
    def is_punct(self):
        """RETURNS (bool): Whether the lexeme is punctuation."""
        return Lexeme.c_check_flag(self.c, IS_PUNCT)

    @is_punct.setter
    def is_punct(self, bint x):
        Lexeme.c_set_flag(self.c, IS_PUNCT, x)

    @property
    def is_space(self):
        """RETURNS (bool): Whether the lexeme consist of whitespace characters.
            Equivalent to `lexeme.text.isspace()`.
        """
        return Lexeme.c_check_flag(self.c, IS_SPACE)

    @is_space.setter
    def is_space(self, bint x):
        Lexeme.c_set_flag(self.c, IS_SPACE, x)

    @property
    def is_bracket(self):
        """RETURNS (bool): Whether the lexeme is a bracket."""
        return Lexeme.c_check_flag(self.c, IS_BRACKET)

    @is_bracket.setter
    def is_bracket(self, bint x):
        Lexeme.c_set_flag(self.c, IS_BRACKET, x)

    @property
    def is_quote(self):
        """RETURNS (bool): Whether the lexeme is a quotation mark."""
        return Lexeme.c_check_flag(self.c, IS_QUOTE)

    @is_quote.setter
    def is_quote(self, bint x):
        Lexeme.c_set_flag(self.c, IS_QUOTE, x)

    @property
    def is_left_punct(self):
        """RETURNS (bool): Whether the lexeme is left punctuation, e.g. (."""
        return Lexeme.c_check_flag(self.c, IS_LEFT_PUNCT)

    @is_left_punct.setter
    def is_left_punct(self, bint x):
        Lexeme.c_set_flag(self.c, IS_LEFT_PUNCT, x)

    @property
    def is_right_punct(self):
        """RETURNS (bool): Whether the lexeme is right punctuation, e.g. )."""
        return Lexeme.c_check_flag(self.c, IS_RIGHT_PUNCT)

    @is_right_punct.setter
    def is_right_punct(self, bint x):
        Lexeme.c_set_flag(self.c, IS_RIGHT_PUNCT, x)

    @property
    def is_currency(self):
        """RETURNS (bool): Whether the lexeme is a currency symbol, e.g. $, €."""
        return Lexeme.c_check_flag(self.c, IS_CURRENCY)

    @is_currency.setter
    def is_currency(self, bint x):
        Lexeme.c_set_flag(self.c, IS_CURRENCY, x)

    @property
    def like_url(self):
        """RETURNS (bool): Whether the lexeme resembles a URL."""
        return Lexeme.c_check_flag(self.c, LIKE_URL)

    @like_url.setter
    def like_url(self, bint x):
        Lexeme.c_set_flag(self.c, LIKE_URL, x)

    @property
    def like_num(self):
        """RETURNS (bool): Whether the lexeme represents a number, e.g. "10.9",
            "10", "ten", etc.
        """
        return Lexeme.c_check_flag(self.c, LIKE_NUM)

    @like_num.setter
    def like_num(self, bint x):
        Lexeme.c_set_flag(self.c, LIKE_NUM, x)

    @property
    def like_email(self):
        """RETURNS (bool): Whether the lexeme resembles an email address."""
        return Lexeme.c_check_flag(self.c, LIKE_EMAIL)

    @like_email.setter
    def like_email(self, bint x):
        Lexeme.c_set_flag(self.c, LIKE_EMAIL, x)
