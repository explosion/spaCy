# cython: profile=True
# cython: embedsignature=True


from libc.stdlib cimport calloc, free, realloc

cdef class Lexeme:
    """A lexical type --- a word, punctuation symbol, whitespace sequence, etc
    keyed by a case-sensitive unicode string. All tokens with the same string,
    e.g. all instances of "dog", ",", "NASA" etc should be mapped to the same
    Lexeme.

    You should avoid instantiating Lexemes directly, and instead use the
    :py:meth:`space.lang.Language.tokenize` and :py:meth:`spacy.lang.Language.lookup`
    methods on the global object exposed by the language you're working with,
    e.g. :py:data:`spacy.en.EN`.

    Attributes:
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
        
        cluster (size_t):
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
    def __cinit__(self, unicode string, double prob, int cluster, dict case_stats,
                  dict tag_stats, list string_features, list flag_features):
        self.prob = prob
        self.cluster = cluster
        self.length = len(string)
        self.string = string

        self.views = []
        for string_feature in string_features:
            view = string_feature(string, prob, cluster, case_stats, tag_stats)
            self.views.append(view)

        for i, flag_feature in enumerate(flag_features):
            if flag_feature(string, prob, case_stats, tag_stats):
                self.flags |= (1 << i)

    def __dealloc__(self):
        pass

    cpdef bint check_flag(self, size_t flag_id) except *:
        """Lexemes may store language-specific boolean features in a bit-field,
        with values accessed by providing an ID constant to this function.

        The ID constants are exposed as global variables in the language module,
        e.g.

        >>> from spacy.en import EN
        >>> lexeme = EN.lookup(u'Nasa')
        >>> lexeme.check_flag(EN.IS_UPPER)
        False
        >>> lexeme.check_flag(EN.OFT_UPPER)
        True
        """
        return self.flags & (1 << flag_id)

    cpdef unicode string_view(self, size_t view_id):
        """Lexemes may store language-specific string-view features, obtained
        by transforming the string, possibly in light of distributional information.
        The string-view features are accessed by providing an ID constant to this
        function.

        The ID constants are exposed as global variables in the language module,
        e.g.

        >>> from spacy.en import EN
        >>> lexeme = EN.lookup(u'Nasa')
        >>> lexeme.string_view(EN.CANON_CASED)
        u'NASA'
        >>> lexeme.string_view(EN.SHAPE)
        u'Xxxx'
        >>> lexeme.string_view(EN.NON_SPARSE)
        u'Xxxx'
        """
        return self.views[view_id]
