from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as inc


from spacy.lexeme cimport Lexeme
#from spacy.lexeme cimport attr_of, lex_of, norm_of, shape_of
from spacy.spacy cimport StringHash


cdef class Tokens:
    def __cinit__(self, Language lang):
        self.lang = lang
        self.vctr = new vector[Lexeme_addr]()
        self.length = 0

    def __dealloc__(self):
        del self.vctr

    def __iter__(self):
        cdef vector[Lexeme_addr].iterator it = self.vctr[0].begin()
        while it != self.vctr[0].end():
            yield deref(it)
            inc(it)

    def __getitem__(self, size_t idx):
        return self.vctr[0].at(idx)

    def __len__(self):
        return self.length

    cpdef int append(self, Lexeme_addr token):
        self.vctr[0].push_back(token)
        self.length += 1

    cpdef int extend(self, Tokens other) except -1:
        cdef Lexeme_addr el
        for el in other:
            self.append(el)

    cpdef object group_by(self, size_t attr):
        '''Group tokens that share the property attr into Tokens instances, and
        return a list of them. Returns a tuple of three lists:
        
        (string names, hashes, tokens)

        The lists are aligned, so the ith entry in string names is the string
        that the ith entry in hashes unhashes to, which the Tokens instance
        is grouped by.
        
        You can then use count_by or group_by on the Tokens
        for further processing. Calling group_by and then asking the length
        of the Tokens objects is equivalent to count_by, but somewhat slower.
        '''
        # Implementation here is working around some of the constraints in
        # Cython about what type of thing can go in what type of container.
        # Long story short, it's pretty hard to get a Python object like
        # Tokens into a vector or array. If we really need this to run faster,
        # we can be tricky and get the Python list access out of the loop. What
        # we'd do is store pointers to the underlying vectors.
        # So far, speed isn't mattering here.
        cdef dict indices = {}
        cdef list groups = []
        cdef list names = []
        cdef list hashes = []

        cdef StringHash key
        cdef Lexeme_addr t
        for t in self.vctr[0]:
            #key = attr_of(t, attr)
            key = 0
            if key in indices:
                groups[indices[key]].append(t)
            else:
                indices[key] = len(groups)
                groups.append(Tokens(self.lang))
                names.append(self.lang.unhash(key))
                hashes.append(key)
                groups[-1].append(t)
        return names, hashes, groups

    cpdef dict count_by(self, size_t attr):
        counts = {}
        cdef Lexeme_addr t
        cdef StringHash key
        for t in self.vctr[0]:
            #key = attr_of(t, attr)
            key = 0
            if key not in counts:
                counts[key] = 0
            counts[key] += 1
        return counts
