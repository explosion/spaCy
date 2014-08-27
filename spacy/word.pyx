# cython: profile=True
# cython: embedsignature=True


from libc.stdlib cimport calloc, free, realloc

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
    def __cinit__(self, unicode string, prob, cluster, case_stats,
                  tag_stats, flag_checkers, string_transformers):
        self.prob = prob
        self.cluster = cluster
        self.length = len(string)
        self.id = hash(string)

        self.nr_views = len(string_transformers)
        self.views = []
        cdef unicode view
        for i, string_transformer in enumerate(string_transformers):
            view = string_transformer(string, prob, case_stats, tag_stats)
            self.views.append(view)

        for i, flag_checker in enumerate(flag_checkers):
            if flag_checker(string, prob, case_stats, tag_stats):
                self.set_flag(i)

    def __dealloc__(self):
        pass

    property string:
        def __get__(self):
            return self.views[0]

    cpdef unicode get_view_string(self, size_t i):
        assert i < self.nr_views
        return self.views[i]

    cpdef id_t get_view_id(self, size_t i) except 0:
        return <id_t>hash(self.views[i])

    cpdef int add_view(self, unicode view) except -1:
        self.nr_views += 1
        self.views.append(view)

    cpdef bint check_flag(self, size_t flag_id) except *:
        """Access the value of one of the pre-computed boolean distribution features.

        Meanings depend on the language-specific distributional features being loaded.
        The suggested features for latin-alphabet languages are: TODO
        """
        return self.flags & (1 << flag_id)

    cpdef int set_flag(self, size_t flag_id) except -1:
        self.flags |= (1 << flag_id)
