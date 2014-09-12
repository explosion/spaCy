# cython: profile=True
# cython: embedsignature=True
'''Tokenize English text, using a scheme that differs from the Penn Treebank 3
scheme in several important respects:

* Whitespace is added as tokens, except for single spaces. e.g.,

    >>> [w.string for w in EN.tokenize(u'\\nHello  \\tThere')]
    [u'\\n', u'Hello', u' ', u'\\t', u'There']

* Contractions are normalized, e.g.

    >>> [w.string for w in EN.tokenize(u"isn't ain't won't he's")]
    [u'is', u'not', u'are', u'not', u'will', u'not', u'he', u"__s"]
  
* Hyphenated words are split, with the hyphen preserved, e.g.:
    
    >>> [w.string for w in EN.tokenize(u'New York-based')]
    [u'New', u'York', u'-', u'based']

Other improvements:

* Email addresses, URLs, European-formatted dates and other numeric entities not
  found in the PTB are tokenized correctly
* Heuristic handling of word-final periods (PTB expects sentence boundary detection
  as a pre-process before tokenization.)

Take care to ensure your training and run-time data is tokenized according to the
same scheme. Tokenization problems are a major cause of poor performance for
NLP tools. If you're using a pre-trained model, the :py:mod:`spacy.ptb3` module
provides a fully Penn Treebank 3-compliant tokenizer.
'''
# TODO
#The script translate_treebank_tokenization can be used to transform a treebank's
#annotation to use one of the spacy tokenization schemes.


from __future__ import unicode_literals

from libc.stdlib cimport malloc, calloc, free
from libc.stdint cimport uint64_t

cimport lang
from spacy.lexeme cimport lexeme_check_flag
from spacy.lexeme cimport lexeme_string_view

from spacy import util

from spacy import orth


cdef enum Flags:
    Flag_IsAlpha
    Flag_IsAscii
    Flag_IsDigit
    Flag_IsLower
    Flag_IsPunct
    Flag_IsSpace
    Flag_IsTitle
    Flag_IsUpper

    Flag_CanAdj
    Flag_CanAdp
    Flag_CanAdv
    Flag_CanConj
    Flag_CanDet
    Flag_CanNoun
    Flag_CanNum
    Flag_CanPdt
    Flag_CanPos
    Flag_CanPron
    Flag_CanPrt
    Flag_CanPunct
    Flag_CanVerb

    Flag_OftLower
    Flag_OftTitle
    Flag_OftUpper
    Flag_N


cdef enum Views:
    View_CanonForm
    View_WordShape
    View_NonSparse
    View_Asciied
    View_N


# Assign the flag and view functions by enum value.
# This is verbose, but it ensures we don't get nasty order sensitivities.
STRING_VIEW_FUNCS = [None] * View_N
STRING_VIEW_FUNCS[View_CanonForm] = orth.canon_case
STRING_VIEW_FUNCS[View_WordShape] = orth.word_shape
STRING_VIEW_FUNCS[View_NonSparse] = orth.non_sparse
STRING_VIEW_FUNCS[View_Asciied] = orth.asciied

FLAG_FUNCS = [None] * Flag_N
FLAG_FUNCS[Flag_IsAlpha] = orth.is_alpha
FLAG_FUNCS[Flag_IsAscii] = orth.is_ascii
FLAG_FUNCS[Flag_IsDigit] = orth.is_digit
FLAG_FUNCS[Flag_IsLower] = orth.is_lower
FLAG_FUNCS[Flag_IsPunct] = orth.is_punct
FLAG_FUNCS[Flag_IsSpace] = orth.is_space
FLAG_FUNCS[Flag_IsTitle] = orth.is_title
FLAG_FUNCS[Flag_IsUpper] = orth.is_upper

FLAG_FUNCS[Flag_CanAdj] = orth.can_tag('ADJ')
FLAG_FUNCS[Flag_CanAdp] = orth.can_tag('ADP')
FLAG_FUNCS[Flag_CanAdv] = orth.can_tag('ADV')
FLAG_FUNCS[Flag_CanConj] = orth.can_tag('CONJ')
FLAG_FUNCS[Flag_CanDet] = orth.can_tag('DET')
FLAG_FUNCS[Flag_CanNoun] = orth.can_tag('NOUN')
FLAG_FUNCS[Flag_CanNum] = orth.can_tag('NUM')
FLAG_FUNCS[Flag_CanPdt] = orth.can_tag('PDT')
FLAG_FUNCS[Flag_CanPos] = orth.can_tag('POS')
FLAG_FUNCS[Flag_CanPron] = orth.can_tag('PRON')
FLAG_FUNCS[Flag_CanPrt] = orth.can_tag('PRT')
FLAG_FUNCS[Flag_CanPunct] = orth.can_tag('PUNCT')
FLAG_FUNCS[Flag_CanVerb] = orth.can_tag('VERB')

FLAG_FUNCS[Flag_OftLower] = orth.oft_case('lower', 0.7)
FLAG_FUNCS[Flag_OftTitle] = orth.oft_case('title', 0.7)
FLAG_FUNCS[Flag_OftUpper] = orth.oft_case('upper', 0.7)


cdef class EnglishTokens(Tokens):
    # Provide accessor methods for the features supported by the language.
    # Without these, clients have to use the underlying string_view and check_flag
    # methods, which requires them to know the IDs.
    cpdef unicode canon_string(self, size_t i):
        return lexeme_string_view(self.lexemes[i], View_CanonForm)

    cpdef unicode shape_string(self, size_t i):
        return lexeme_string_view(self.lexemes[i], View_WordShape)

    cpdef unicode non_sparse_string(self, size_t i):
        return lexeme_string_view(self.lexemes[i], View_NonSparse)

    cpdef unicode asciied_string(self, size_t i):
        return lexeme_string_view(self.lexemes[i], View_Asciied)

    cpdef size_t canon(self, size_t i):
        return id(self.lexemes[i].views[<size_t>View_CanonForm])

    cpdef size_t shape(self, size_t i):
        return id(self.lexemes[i].views[<size_t>View_WordShape])

    cpdef size_t non_sparse(self, size_t i):
        return id(self.lexemes[i].views[<size_t>View_NonSparse])

    cpdef size_t asciied(self, size_t i):
        return id(self.lexemes[i].views[<size_t>View_Asciied])
    
    cpdef bint is_alpha(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsAlpha)

    cpdef bint is_ascii(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsAscii)

    cpdef bint is_digit(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsDigit)

    cpdef bint is_lower(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsLower)

    cpdef bint is_punct(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsPunct)

    cpdef bint is_space(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsSpace)

    cpdef bint is_title(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsTitle)

    cpdef bint is_upper(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsUpper)

    cpdef bint can_adj(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanAdj)

    cpdef bint can_adp(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanAdp)

    cpdef bint can_adv(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanAdv)

    cpdef bint can_conj(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanConj)

    cpdef bint can_det(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanDet)

    cpdef bint can_noun(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanNoun)

    cpdef bint can_num(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanNum)

    cpdef bint can_pdt(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanPdt)

    cpdef bint can_pos(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanPos)

    cpdef bint can_pron(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanPron)

    cpdef bint can_prt(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanPrt)

    cpdef bint can_punct(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanPunct)

    cpdef bint can_verb(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanVerb)

    cpdef bint oft_lower(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_OftLower)

    cpdef bint oft_title(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_OftTitle)

    cpdef bint oft_upper(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_OftUpper)


cdef class English(Language):
    """English tokenizer, tightly coupled to lexicon.

    Attributes:
        name (unicode): The two letter code used by Wikipedia for the language.
        lexicon (Lexicon): The lexicon. Exposes the lookup method.
    """
    fl_is_alpha = Flag_IsAlpha
    fl_is_digit = Flag_IsDigit
    v_shape = View_WordShape
    def __cinit__(self, name, user_string_features, user_flag_features):
        self.cache = {}
        lang_data = util.read_lang_data(name)
        rules, words, probs, clusters, case_stats, tag_stats = lang_data
        self.lexicon = lang.Lexicon(words, probs, clusters, case_stats, tag_stats,
                                     STRING_VIEW_FUNCS + user_string_features,
                                     FLAG_FUNCS + user_flag_features)
        self._load_special_tokenization(rules)
        self.tokens_class = EnglishTokens

    cdef int _split_one(self, Py_UNICODE* characters, size_t length):
        if length == 1:
            return 1
        if characters[0] == "'" and (characters[1] == "s" or characters[1] == "S"):
            return 2
        cdef int i = 0
        # Leading punctuation
        if _check_punct(characters, 0, length):
            return 1
        # Contractions
        elif length >= 3 and characters[length - 2] == "'":
            c2 = characters[length-1]
            if c2 == "s" or c2 == "S":
                return length - 2
        if length >= 1:
            # Split off all trailing punctuation characters
            i = 0
            while i < length and not _check_punct(characters, i, length):
                i += 1
        return i


cdef bint _check_punct(Py_UNICODE* characters, size_t i, size_t length):
    cdef unicode char_i = characters[i]
    cdef unicode char_i1 = characters[i+1]
    # Don't count appostrophes as punct if the next char is a letter
    if characters[i] == "'" and i < (length - 1) and char_i1.isalpha():
        return i == 0
    if characters[i] == "-" and i < (length - 1) and characters[i+1] == '-':
        return False
    # Don't count commas as punct if the next char is a number
    if characters[i] == "," and i < (length - 1) and char_i1.isdigit():
        return False
    # Don't count periods as punct if the next char is not whitespace
    if characters[i] == "." and i < (length - 1) and not char_i1.isspace():
        return False
    return not char_i.isalnum()


EN = English('en', [], [])
