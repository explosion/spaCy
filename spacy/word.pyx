# cython: profile=True
# cython: embedsignature=True


from libc.stdlib cimport calloc, free


# Python-visible enum for POS tags
PUNCT = 0
CONJ = 1
NUM = 2
X = 3
DET = 4
ADP = 5
ADJ = 6
ADV = 7
VERB = 8
NOUN = 9
PDT = 10
POS = 11
PRON = 12
PRT = 13


DEF OFT_UPPER = 1
DEF OFT_TITLE = 2


cdef class Word:
    """A lexical type.

    Attributes:
        string (bytes):
            A utf8-encoded byte-string for the word.
        
        lex (StringHash):
            A hash of the word.
        length (size_t):
            The (unicode) length of the word.
        
        prob (double):
            An estimate of the word's unigram log probability.

            Probabilities are calculated from a large text corpus, and smoothed using
            simple Good-Turing.  Estimates are read from data/en/probabilities, and
            can be replaced using spacy.en.load_probabilities.
        
        cluster (int):
            An integer representation of the word's Brown cluster.

            A Brown cluster is an address into a binary tree, which gives some (noisy)
            information about the word's distributional context.
    
            >>> strings = (u'pineapple', u'apple', u'dapple', u'scalable')
            >>> print ["{0:b"} % lookup(s).cluster for s in strings]
            ["100111110110", "100111100100", "01010111011001", "100111110110"]

            The clusterings are unideal, but often slightly useful.
            "pineapple" and "apple" share a long prefix, indicating a similar meaning,
            while "dapple" is totally different. On the other hand, "scalable" receives
            the same cluster ID as "pineapple", which is not what we'd like.
    """
    def __cinit__(self, bytes string, list string_views, prob=0.0, cluster=0,
                  orth_flags=0, dist_flags=0, possible_tags=0):
        self.string = <char*>string
        self.length = len(string)
        self.views = <char**>calloc(len(string_views), sizeof(StringHash))
        cdef unicode view
        for i in range(len(string_views)):
            view = string_views[i]
            self.string_views[i] = hash(view)

    def __dealloc__(self):
        free(self.string_views)

    cpdef StringHash get_view(self, size_t i) except 0:
        return self.string_views[i]

    cpdef bint check_orth_flag(self, OrthFlags flag) except *:
        """Access the value of one of the pre-computed boolean orthographic features.

        Meanings depend on the language-specific orthographic features being loaded.
        The suggested features for latin-alphabet languages are: TODO
        """
        return self.orth_flags & (1 << flag)

    cpdef bint check_dist_flag(self, DistFlags flag) except *:
        """Access the value of one of the pre-computed boolean distribution features.

        Meanings depend on the language-specific distributional features being loaded.
        The suggested features for latin-alphabet languages are: TODO
        """
 
        return self.dist_flags & (1 << flag)

    cpdef bint can_tag(self, TagFlags flag) except *:
        """Check whether the word often receives a particular tag in a large text
        corpus. "Often" is chosen by heuristic.
        """
        return self.possible_tags & (1 << flag)


cdef class CasedWord(Word):
    def __cinit__(self, bytes string):
        string_views = [get_normaized(string), get_word_shape(string), string[-3:]]
        Word.__cinit__(self, string, string_views)
    
    cpdef bint is_often_uppered(self) except *:
        '''Check the OFT_UPPER distributional flag for the word.
    
        The OFT_UPPER flag records whether a lower-cased version of the word
        is found in all-upper case frequently in a large sample of text, where
        "frequently" is defined as P >= 0.95 (chosen for high mutual information for
        POS tagging).
    
        Case statistics are estimated from a large text corpus. Estimates are read
        from data/en/case_stats, and can be replaced using spacy.en.load_case_stats.
    
        >>> is_often_uppered(lookup(u'nato'))
        True
        >>> is_often_uppered(lookup(u'the')) 
        False
        '''
        return self.dist_flags & (1 << OFT_UPPER)


    cpdef bint is_often_titled(self) except *:
        '''Check the OFT_TITLE distributional flag for the word.
    
        The OFT_TITLE flag records whether a lower-cased version of the word
        is found title-cased (see string.istitle) frequently in a large sample of text,
        where "frequently" is defined as P >= 0.3 (chosen for high mutual information for
        POS tagging).
    
        Case statistics are estimated from a large text corpus. Estimates are read
        from data/en/case_stats, and can be replaced using spacy.en.load_case_stats.
    
        >>> is_oft_upper(lookup(u'john'))
        True
        >>> is_oft_upper(lookup(u'Bill')) 
        False
        '''
        return self.dist_flags & (1 << OFT_TITLE)


    cpdef bint is_alpha(self) except *:
        """Check whether all characters in the word's string are alphabetic.
        
        Should match the :py:func:`unicode.isalpha()` function.

        >>> is_alpha(lookup(u'Hello'))
        True
        >>> is_alpha(lookup(u'العرب'))
        True
        >>> is_alpha(lookup(u'10'))
        False
        """
        return self.orth_flags & 1 << IS_ALPHA

    cpdef bint is_digit(self) except *:
        """Check whether all characters in the word's string are numeric.
    
        Should match the :py:func:`unicode.isdigit()` function.

        >>> is_digit(lookup(u'10'))
        True
        >>> is_digit(lookup(u'๐'))
        True
        >>> is_digit(lookup(u'one'))
        False
        """
        return self.orth_flags & 1 << IS_DIGIT

    cpdef bint is_punct(self) except *:
        """Check whether all characters belong to a punctuation unicode data category
        for a Lexeme ID.

        >>> is_punct(lookup(u'.'))
        True
        >>> is_punct(lookup(u'⁒'))
        True
        >>> is_punct(lookup(u' '))
        False
        """
        return self.orth_flags & 1 << IS_PUNCT

    cpdef bint is_space(self) except *:
        """Give the result of unicode.isspace() for a Lexeme ID.

        >>> is_space(lookup(u'\\t'))
        True
        >>> is_space(lookup(u'<unicode space>'))
        True
        >>> is_space(lookup(u'Hi\\n'))
        False
        """
        return self.orth_flags & 1 << IS_SPACE

    cpdef bint is_lower(self) except *:
        """Give the result of unicode.islower() for a Lexeme ID.

        >>> is_lower(lookup(u'hi'))
        True
        >>> is_lower(lookup(<unicode>))
        True
        >>> is_lower(lookup(u'10'))
        False
        """
        return self.orth_flags & 1 << IS_LOWER

    cpdef bint is_upper(self) except *:
        """Give the result of unicode.isupper() for a Lexeme ID.

        >>> is_upper(lookup(u'HI'))
        True
        >>> is_upper(lookup(u'H10'))
        True
        >>> is_upper(lookup(u'10'))
        False
        """
        return self.orth_flags & 1 << IS_UPPER

    cpdef bint is_title(self) except *:
        """Give the result of unicode.istitle() for a Lexeme ID.

        >>> is_title(lookup(u'Hi'))
        True
        >>> is_title(lookup(u'Hi1'))
        True
        >>> is_title(lookup(u'1'))
        False
        """
        return self.orth_flags & 1 << IS_TITLE

    cpdef bint is_ascii(self) except *:
        """Give the result of checking whether all characters in the string are ascii.

        >>> is_ascii(lookup(u'Hi'))
        True
        >>> is_ascii(lookup(u' '))
        True
        >>> is_title(lookup(u'<unicode>'))
        False
        """
        return self.orth_flags & 1 << IS_ASCII
