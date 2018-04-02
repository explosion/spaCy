# cython: infer_types=True
'''Do Levenshtein alignment, for evaluation of tokenized input.

Random notes:

  r i n g
  0 1 2 3 4
r 1 0 1 2 3
a 2 1 1 2 3
n 3 2 2 1 2
g 4 3 3 2 1

0,0: (1,1)=min(0+0,1+1,1+1)=0 S
1,0: (2,1)=min(1+1,0+1,2+1)=1 D
2,0: (3,1)=min(2+1,3+1,1+1)=2 D
3,0: (4,1)=min(3+1,4+1,2+1)=3 D
0,1: (1,2)=min(1+1,2+1,0+1)=1 D
1,1: (2,2)=min(0+1,1+1,1+1)=1 S
2,1: (3,2)=min(1+1,1+1,2+1)=2 S or I
3,1: (4,2)=min(2+1,2+1,3+1)=3 S or I
0,2: (1,3)=min(2+1,3+1,1+1)=2 I
1,2: (2,3)=min(1+1,2+1,1+1)=2 S or I
2,2: (3,3)
3,2: (4,3)
At state (i, j) we're asking "How do I transform S[:i+1] to T[:j+1]?"

We know the costs to transition:

S[:i]   -> T[:j]   (at D[i,j])
S[:i+1] -> T[:j]   (at D[i+1,j])
S[:i]   -> T[:j+1] (at D[i,j+1])
    
Further, we now we can tranform:
S[:i+1] -> S[:i] (DEL) for 1,
T[:j+1] -> T[:j] (INS) for 1.
S[i+1]  -> T[j+1] (SUB) for 0 or 1

Therefore we have the costs:
SUB: Cost(S[:i]->T[:j])   + Cost(S[i]->S[j])
i.e. D[i, j] + S[i+1] != T[j+1]
INS: Cost(S[:i+1]->T[:j]) + Cost(T[:j+1]->T[:j])
i.e. D[i+1,j] + 1
DEL: Cost(S[:i]->T[:j+1]) + Cost(S[:i+1]->S[:i]) 
i.e. D[i,j+1] + 1

    Source string S has length m, with index i
    Target string T has length n, with index j

    Output two alignment vectors: i2j (length m) and j2i (length n)
    # function LevenshteinDistance(char s[1..m], char t[1..n]):
    # for all i and j, d[i,j] will hold the Levenshtein distance between
    # the first i characters of s and the first j characters of t
    # note that d has (m+1)*(n+1) values
    # set each element in d to zero
    ring rang
      - r i n g
    - 0 0 0 0 0
    r 0 0 0 0 0
    a 0 0 0 0 0
    n 0 0 0 0 0
    g 0 0 0 0 0

    # source prefixes can be transformed into empty string by
    # dropping all characters
    # d[i, 0] := i
    ring rang
      - r i n g
    - 0 0 0 0 0
    r 1 0 0 0 0
    a 2 0 0 0 0
    n 3 0 0 0 0
    g 4 0 0 0 0

    # target prefixes can be reached from empty source prefix
    # by inserting every character
    # d[0, j] := j
      - r i n g
    - 0 1 2 3 4
    r 1 0 0 0 0
    a 2 0 0 0 0
    n 3 0 0 0 0
    g 4 0 0 0 0

'''
from __future__ import unicode_literals
from libc.stdint cimport uint32_t
import numpy
import copy
cimport numpy as np
from .compat import unicode_
from murmurhash.mrmr cimport hash32
from collections import Counter


class Alignment(object):
    def __init__(self, your_words, their_words):
        cost, your2their, their2your = self._align(your_words, their_words)
        self.cost = cost
        self._y2t = your2their
        self._t2y = their2your

    def to_yours(self, items):
        '''Translate a list of token annotations into your tokenization. Returns
        a list of length equal to your tokens. When one of your tokens aligns
        to multiple items, the entry will be a list. When multiple of your 
        tokens align to one item, you'll get a tuple (value, index, n_to_go),
        where index is an int starting from 0, and n_to_go tells you how
        many remaining subtokens align to the same value.
        '''
        output = []
        for i, alignment in enumerate(self._y2t):
            if alignment is None:
                output.append(None)
            elif isinstance(alignment, int):
                output.append(items[alignment])
            elif isinstance(alignment, tuple):
                output.append((items[alignment[0]], alignment[1]))
            else:
                output.append([])
                for entry in alignment:
                    if isinstance(entry, int):
                        output[-1].append(items[entry])
                    else:
                        output[-1].append((items[entry[0]], entry[1]))
        return output

    def index_to_yours(self, index):
        '''Translate an index that points into their tokens to point into yours'''
        if index is None:
            return None
        else:
            alignment = self._t2y[index]
            return alignment
        #if isinstance(alignment, int):
        #    return alignment
        #elif len(alignment) == 1 and isinstance(alignment, int):
        #    return alignment[0]
        #elif len(alignment) == 1:
        #    return alignment[0][0]
        #if len(alignment) == 1 and alignment[0][2] == 0:
        #    return alignment[0][0]
        #else:
        #    output = []
        #    for i1, i2, n_to_go in alignment:
        #        output.append((i1, i2, n_to_go))
        #    return output
    
    def to_theirs(self, items):
        raise NotImplementedError

    def index_to_theirs(self, index):
        raise NotImplementedError

    @classmethod
    def _align(cls, cand_words, gold_words):
        '''Find best alignment between candidate tokenization and gold tokenization.

        Returns the alignment cost and alignment tables in both directions:
        cand_to_gold and gold_to_cand

        Alignment entries are lists of addresses, where an address is a tuple
        (position, subtoken). This allows one-to-many and many-to-one alignment.

        For instance, let's say we align:

        Cand: ['ab', 'c', 'd']
        Gold: ['a', 'b', 'cd']

        The cand_to_gold alignment would be:

        [[0, 0], (2, 0), (2, 1)]

        And the gold_to_cand alignment:

        [(0, 0), (0, 1), [1, 2]]
        '''
        if cand_words == gold_words:
            return 0, list(range(len(cand_words))), list(range(len(cand_words)))
        cand_words = [w.replace(' ', '') for w in cand_words]
        gold_words = [w.replace(' ', '') for w in gold_words]
        cost, i2j, j2i, matrix = levenshtein_align(cand_words, gold_words)

        i_lengths = [len(w) for w in cand_words]
        j_lengths = [len(w) for w in gold_words]

        cand2gold, gold2cand = multi_align(i2j, j2i, i_lengths, j_lengths)
        return cost, cand2gold, gold2cand

    @staticmethod
    def flatten(heads):
        '''Let's say we have a heads array with fused tokens. We might have
        something like:
        
        [[(0, 1), 1], 1]

        This indicates that token 0 aligns to two gold tokens. The head of the
        first subtoken is the second subtoken. The head of the second subtoken
        is the second token.

        So we expand to a tree:

        [1, 2, 2]

        This is helpful for preventing other functions from knowing our weird
        format.
        '''
        # Get an alignment -- normalize to the more complicated format; so
        # if we have an int i, treat it as [(i, 0)]
        j = 0
        alignment = {(None, 0): None}
        for i, tokens in enumerate(heads):
            if not isinstance(tokens, list):
                alignment[(i, 0)] = j
                j += 1
            else:
                for sub_i in range(len(tokens)):
                    alignment[(i, sub_i)] = j
                    j += 1
        # Apply the alignment to get the new values
        new = []
        for head_vals in heads:
            if isinstance(head_vals, int):
                head_vals = [(head_vals, 0)]
            elif head_vals is None or isinstance(head_vals, tuple):
                new.append(None)
                continue
            for head_val in head_vals:
                if not isinstance(head_val, tuple):
                    head_val = (head_val, 0)
                new.append(alignment[head_val])
        return new


def levenshtein_align(S, T):
    cdef int m = len(S)
    cdef int n = len(T)
    cdef np.ndarray matrix = numpy.zeros((m+1, n+1), dtype='int32')
    cdef np.ndarray i2j = numpy.zeros((m,), dtype='i')
    cdef np.ndarray j2i = numpy.zeros((n,), dtype='i')

    cdef np.ndarray S_arr = _convert_sequence(S)
    cdef np.ndarray T_arr = _convert_sequence(T)

    fill_matrix(<int*>matrix.data,
        <const int*>S_arr.data, m, <const int*>T_arr.data, n)
    fill_i2j(i2j, matrix)
    fill_j2i(j2i, matrix)
    for i in range(i2j.shape[0]):
        if i2j[i] >= 0 and len(S[i]) != len(T[i2j[i]]):
            i2j[i] = -1
    for j in range(j2i.shape[0]):
        if j2i[j] >= 0 and len(T[j]) != len(S[j2i[j]]):
            j2i[j] = -1
    return matrix[-1,-1], i2j, j2i, matrix


def multi_align(np.ndarray i2j, np.ndarray j2i, i_lengths, j_lengths):
    '''Let's say we had:

    Guess: [aa bb cc dd]
    Truth: [aa bbcc dd]
    i2j: [0, None, -2, 2]
    j2i: [0, -2, 3]

    We want:

    i2j_multi: {1: 1, 2: 1}
    j2i_multi: {}
    '''
    i2j_miss = _get_regions(i2j, i_lengths)
    j2i_miss = _get_regions(j2i, j_lengths)
    
    i2j_many2one = _get_many2one(i2j_miss, j2i_miss, i_lengths, j_lengths)
    j2i_many2one = _get_many2one(j2i_miss, i2j_miss, j_lengths, i_lengths)
    i2j_one2many = _get_one2many(j2i_many2one)
    j2i_one2many = _get_one2many(i2j_many2one)
    i2j_one2part = _get_one2part(j2i_many2one)
    j2i_one2part = _get_one2part(i2j_many2one)

    # Now get the more usable format we'll return
    cand2gold = _convert_multi_align(i2j, i2j_many2one, i2j_one2many, i2j_one2part)
    gold2cand = _convert_multi_align(j2i, j2i_many2one, j2i_one2many, j2i_one2part)
    return cand2gold, gold2cand


def _convert_multi_align(one2one, many2one, one2many, one2part):
    output = []
    seen_j = Counter()
    for i, j in enumerate(one2one):
        if j != -1:
            output.append(int(j))
        elif i in many2one:
            j = many2one[i]
            output.append((int(j), seen_j[j]))
            seen_j[j] += 1
        elif i in one2many:
            output.append([])
            for j in one2many[i]:
                output[-1].append(int(j))
        elif i in one2part:
            output.append(one2part[i])
        else:
            output.append(None)
    return output


def _get_regions(alignment, lengths):
    regions = {}
    start = None
    offset = 0
    for i in range(len(alignment)):
        if alignment[i] < 0:
            if start is None:
                start = offset
                regions.setdefault(start, [])
            regions[start].append(i)
        else:
            start = None
        offset += lengths[i]
    return regions


def _get_many2one(miss1, miss2, lengths1, lengths2):
    miss1 = copy.deepcopy(miss1)
    miss2 = copy.deepcopy(miss2)
    i2j_many2one = {}
    for start, region1 in miss1.items():
        if not region1 or start not in miss2:
            continue
        region2 = miss2[start]
        if sum(lengths1[i] for i in region1) == sum(lengths2[i] for i in region2):
            j = region2.pop(0)
            buff = []
            # Consume tokens from region 1, until we meet the length of the
            # first token in region2. If we do, align the tokens. If
            # we exceed the length, break.
            while region1:
                buff.append(region1.pop(0))
                if sum(lengths1[i] for i in buff) == lengths2[j]:
                    for i in buff:
                        i2j_many2one[i] = j
                    j += 1
                    buff = []
                elif sum(lengths1[i] for i in buff) > lengths2[j]:
                    break
            else:
                if buff and sum(lengths1[i] for i in buff) == lengths2[j]:
                    for i in buff:
                        i2j_many2one[i] = j
    return i2j_many2one


def _get_one2many(many2one):
    one2many = {}
    for j, i in many2one.items():
        one2many.setdefault(i, []).append(j)
    return one2many


def _get_one2part(many2one):
    one2part = {}
    seen_j = Counter()
    for i, j in many2one.items():
        one2part[i] = (j, seen_j[j])
        seen_j[j] += 1
    return one2part

def _convert_sequence(seq):
    if isinstance(seq, numpy.ndarray):
        return numpy.ascontiguousarray(seq, dtype='uint32_t')
    cdef np.ndarray output = numpy.zeros((len(seq),), dtype='uint32')
    cdef bytes item_bytes
    for i, item in enumerate(seq):
        if isinstance(item, unicode):
            item_bytes = item.encode('utf8')
        else:
            item_bytes = item
        output[i] = hash32(<void*><char*>item_bytes, len(item_bytes), 0)
    return output


cdef void fill_matrix(int* D, 
        const int* S, int m, const int* T, int n) nogil:
    m1 = m+1
    n1 = n+1
    for i in range(m1*n1):
        D[i] = 0
 
    for i in range(m1):
        D[i*n1] = i
 
    for j in range(n1):
        D[j] = j
 
    cdef int sub_cost, ins_cost, del_cost
    for j in range(n):
        for i in range(m):
            i_j = i*n1 + j
            i1_j1 = (i+1)*n1 + j+1
            i1_j = (i+1)*n1 + j
            i_j1 = i*n1 + j+1
            if S[i] != T[j]:
                sub_cost = D[i_j] + 1
            else:
                sub_cost = D[i_j]
            del_cost = D[i_j1] + 1
            ins_cost = D[i1_j] + 1
            best = min(min(sub_cost, ins_cost), del_cost)
            D[i1_j1] = best


cdef void fill_i2j(np.ndarray i2j, np.ndarray D) except *:
    j = D.shape[1]-2
    cdef int i = D.shape[0]-2
    while i >= 0:
        while D[i+1, j] < D[i+1, j+1]:
            j -= 1
        if D[i, j+1] < D[i+1, j+1]:
            i2j[i] = -1
        else:
            i2j[i] = j
            j -= 1
        i -= 1

cdef void fill_j2i(np.ndarray j2i, np.ndarray D) except *:
    i = D.shape[0]-2
    cdef int j = D.shape[1]-2
    while j >= 0:
        while D[i, j+1] < D[i+1, j+1]:
            i -= 1
        if D[i+1, j] < D[i+1, j+1]:
            j2i[j] = -1
        else:
            j2i[j] = i
            i -= 1
        j -= 1
