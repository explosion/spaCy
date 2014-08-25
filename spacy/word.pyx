# cython: profile=True
# cython: embedsignature=True


from libc.stdlib cimport calloc, free

from spacy cimport flags


cdef class Lexeme:
    """A lexical type.

    Clients should avoid instantiating Lexemes directly, and instead use get_lexeme
    from a language module, e.g. spacy.en.get_lexeme . This allows us to use only
    one Lexeme object per lexical type.

    Attributes:
        id (view_id_t):
            A unique ID of the word's string.

            Implemented as the memory-address of the string,
            as we use Python's string interning to guarantee that only one copy
            of each string is seen.

        string (unicode):
            The unicode string.
            
            Implemented as a property; relatively expensive.

        length (size_t):
            The number of unicode code-points in the string.

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
    def __cinit__(self, utf8_t string, size_t length, list views, prob=0.0,
                  cluster=0, orth_flags=0, dist_flags=0, possible_tags=0):
        self.id = <id_t>&string
        self.length = length
        self.nr_strings = 0
        self.add_views(views)

    def __dealloc__(self):
        free(self.views)

    property string:
        def __get__(self):
            return self.strings[0].decode('utf8')

    cpdef unicode get_view_string(self, size_t i) except *:
        assert i < self.nr_strings
        return self.strings[i].decode('utf8')

    cpdef intptr_t get_view_id(self, size_t i) except 0:
        assert i < self.nr_strings
        return <string_id_t>&self.views[i]

    cpdef int add_views(self, list views) except -1:
        self.nr_views += len(strings)
        self.views = <char**>realloc(self.views, self.nr_views * sizeof(utf8_t))
        cdef unicode view
        cdef bytes utf8_string
        for i, view in enumerate(strings):
            view = string_views[i]
            utf8_string = view.encode('utf8')
            # Intern strings, allowing pointer comparison
            utf8_string = intern(utf8_string)
            self.views[i] = utf8_string

    cpdef bint check_flag(self, size_t flag_id) except *:
        """Access the value of one of the pre-computed boolean distribution features.

        Meanings depend on the language-specific distributional features being loaded.
        The suggested features for latin-alphabet languages are: TODO
        """
        assert flag_id < flags.MAX_FLAG
        return self.flags & (1 << flag_id)

    cpdef int set_flag(self, size_t flag_id) except -1:
        assert flag_id < flags.MAX_FLAG
        self.flags |= (1 << flag_id)


#
#cdef class CasedWord(Word):
#    def __cinit__(self, bytes string, list views):
#        Word.__cinit__(self, string, string_views)
#    
#    cpdef bint is_often_uppered(self) except *:
#        '''Check the OFT_UPPER distributional flag for the word.
#    
#        The OFT_UPPER flag records whether a lower-cased version of the word
#        is found in all-upper case frequently in a large sample of text, where
#        "frequently" is defined as P >= 0.95 (chosen for high mutual information for
#        POS tagging).
#    
#        Case statistics are estimated from a large text corpus. Estimates are read
#        from data/en/case_stats, and can be replaced using spacy.en.load_case_stats.
#    
#        >>> is_often_uppered(lookup(u'nato'))
#        True
#        >>> is_often_uppered(lookup(u'the')) 
#        False
#        '''
#        return self.dist_flags & (1 << OFT_UPPER)
#
#
#    cpdef bint is_often_titled(self) except *:
#        '''Check the OFT_TITLE distributional flag for the word.
#    
#        The OFT_TITLE flag records whether a lower-cased version of the word
#        is found title-cased (see string.istitle) frequently in a large sample of text,
#        where "frequently" is defined as P >= 0.3 (chosen for high mutual information for
#        POS tagging).
#    
#        Case statistics are estimated from a large text corpus. Estimates are read
#        from data/en/case_stats, and can be replaced using spacy.en.load_case_stats.
#    
#        >>> is_oft_upper(lookup(u'john'))
#        True
#        >>> is_oft_upper(lookup(u'Bill')) 
#        False
#        '''
#        return self.dist_flags & (1 << OFT_TITLE)
#
#
#    cpdef bint is_alpha(self) except *:
#        """Check whether all characters in the word's string are alphabetic.
#        
#        Should match the :py:func:`unicode.isalpha()` function.
#
#        >>> is_alpha(lookup(u'Hello'))
#        True
#        >>> is_alpha(lookup(u'العرب'))
#        True
#        >>> is_alpha(lookup(u'10'))
#        False
#        """
#        return self.orth_flags & 1 << IS_ALPHA
#
#    cpdef bint is_digit(self) except *:
#        """Check whether all characters in the word's string are numeric.
#    
#        Should match the :py:func:`unicode.isdigit()` function.
#
#        >>> is_digit(lookup(u'10'))
#        True
#        >>> is_digit(lookup(u'๐'))
#        True
#        >>> is_digit(lookup(u'one'))
#        False
#        """
#        return self.orth_flags & 1 << IS_DIGIT
#
#    cpdef bint is_punct(self) except *:
#        """Check whether all characters belong to a punctuation unicode data category
#        for a Lexeme ID.
#
#        >>> is_punct(lookup(u'.'))
#        True
#        >>> is_punct(lookup(u'⁒'))
#        True
#        >>> is_punct(lookup(u' '))
#        False
#        """
#        return self.orth_flags & 1 << IS_PUNCT
#
#    cpdef bint is_space(self) except *:
#        """Give the result of unicode.isspace() for a Lexeme ID.
#
#        >>> is_space(lookup(u'\\t'))
#        True
#        >>> is_space(lookup(u'<unicode space>'))
#        True
#        >>> is_space(lookup(u'Hi\\n'))
#        False
#        """
#        return self.orth_flags & 1 << IS_SPACE
#
#    cpdef bint is_lower(self) except *:
#        """Give the result of unicode.islower() for a Lexeme ID.
#
#        >>> is_lower(lookup(u'hi'))
#        True
#        >>> is_lower(lookup(<unicode>))
#        True
#        >>> is_lower(lookup(u'10'))
#        False
#        """
#        return self.orth_flags & 1 << IS_LOWER
#
#    cpdef bint is_upper(self) except *:
#        """Give the result of unicode.isupper() for a Lexeme ID.
#
#        >>> is_upper(lookup(u'HI'))
#        True
#        >>> is_upper(lookup(u'H10'))
#        True
#        >>> is_upper(lookup(u'10'))
#        False
#        """
#        return self.orth_flags & 1 << IS_UPPER
#
#    cpdef bint is_title(self) except *:
#        """Give the result of unicode.istitle() for a Lexeme ID.
#
#        >>> is_title(lookup(u'Hi'))
#        True
#        >>> is_title(lookup(u'Hi1'))
#        True
#        >>> is_title(lookup(u'1'))
#        False
#        """
#        return self.orth_flags & 1 << IS_TITLE
#
#    cpdef bint is_ascii(self) except *:
#        """Give the result of checking whether all characters in the string are ascii.
#
#        >>> is_ascii(lookup(u'Hi'))
#        True
#        >>> is_ascii(lookup(u' '))
#        True
#        >>> is_title(lookup(u'<unicode>'))
#        False
#        """
#        return self.orth_flags & 1 << IS_ASCII
