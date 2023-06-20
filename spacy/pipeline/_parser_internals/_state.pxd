cimport libcpp
from cpython.exc cimport PyErr_CheckSignals, PyErr_SetFromErrno
from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as incr
from libc.stdint cimport uint32_t, uint64_t
from libc.stdlib cimport calloc, free
from libc.string cimport memcpy, memset
from libcpp.set cimport set
from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector
from murmurhash.mrmr cimport hash64

from ...attrs cimport IS_SPACE
from ...lexeme cimport Lexeme
from ...structs cimport SpanC, TokenC
from ...typedefs cimport attr_t
from ...vocab cimport EMPTY_LEXEME


cdef inline bint is_space_token(const TokenC* token) nogil:
    return Lexeme.c_check_flag(token.lex, IS_SPACE)

cdef struct ArcC:
    int head
    int child
    attr_t label


cdef cppclass StateC:
    int* _heads
    const TokenC* _sent
    vector[int] _stack
    vector[int] _rebuffer
    vector[SpanC] _ents
    unordered_map[int, vector[ArcC]] _left_arcs
    unordered_map[int, vector[ArcC]] _right_arcs
    vector[libcpp.bool] _unshiftable
    set[int] _sent_starts
    TokenC _empty_token
    int length
    int offset
    int _b_i

    __init__(const TokenC* sent, int length) nogil:
        this._sent = sent
        this._heads = <int*>calloc(length, sizeof(int))
        if not (this._sent and this._heads):
            with gil:
                PyErr_SetFromErrno(MemoryError)
                PyErr_CheckSignals()
        this.offset = 0
        this.length = length
        this._b_i = 0
        for i in range(length):
            this._heads[i] = -1
            this._unshiftable.push_back(0)
        memset(&this._empty_token, 0, sizeof(TokenC))
        this._empty_token.lex = &EMPTY_LEXEME

    __dealloc__():
        free(this._heads)

    void set_context_tokens(int* ids, int n) nogil:
        cdef int i, j
        if n == 1:
            if this.B(0) >= 0:
                ids[0] = this.B(0)
            else:
                ids[0] = -1
        elif n == 2:
            ids[0] = this.B(0)
            ids[1] = this.S(0)
        elif n == 3:
            if this.B(0) >= 0:
                ids[0] = this.B(0)
            else:
                ids[0] = -1
            # First word of entity, if any
            if this.entity_is_open():
                ids[1] = this.E(0)
            else:
                ids[1] = -1
            # Last word of entity, if within entity
            if ids[0] == -1 or ids[1] == -1:
                ids[2] = -1
            else:
                ids[2] = ids[0] - 1
        elif n == 8:
            ids[0] = this.B(0)
            ids[1] = this.B(1)
            ids[2] = this.S(0)
            ids[3] = this.S(1)
            ids[4] = this.S(2)
            ids[5] = this.L(this.B(0), 1)
            ids[6] = this.L(this.S(0), 1)
            ids[7] = this.R(this.S(0), 1)
        elif n == 13:
            ids[0] = this.B(0)
            ids[1] = this.B(1)
            ids[2] = this.S(0)
            ids[3] = this.S(1)
            ids[4] = this.S(2)
            ids[5] = this.L(this.S(0), 1)
            ids[6] = this.L(this.S(0), 2)
            ids[6] = this.R(this.S(0), 1)
            ids[7] = this.L(this.B(0), 1)
            ids[8] = this.R(this.S(0), 2)
            ids[9] = this.L(this.S(1), 1)
            ids[10] = this.L(this.S(1), 2)
            ids[11] = this.R(this.S(1), 1)
            ids[12] = this.R(this.S(1), 2)
        elif n == 6:
            for i in range(6):
                ids[i] = -1
            if this.B(0) >= 0:
                ids[0] = this.B(0)
            if this.entity_is_open():
                ent = this.get_ent()
                j = 1
                for i in range(ent.start, this.B(0)):
                    ids[j] = i
                    j += 1
                    if j >= 6:
                        break
        else:
            # TODO error =/
            pass
        for i in range(n):
            if ids[i] >= 0:
                ids[i] += this.offset
            else:
                ids[i] = -1

    int S(int i) nogil const:
        if i >= this._stack.size():
            return -1
        elif i < 0:
            return -1
        return this._stack.at(this._stack.size() - (i+1))

    int B(int i) nogil const:
        if i < 0:
            return -1
        elif i < this._rebuffer.size():
            return this._rebuffer.at(this._rebuffer.size() - (i+1))
        else:
            b_i = this._b_i + (i - this._rebuffer.size())
            if b_i >= this.length:
                return -1
            else:
                return b_i

    const TokenC* B_(int i) nogil const:
        return this.safe_get(this.B(i))

    const TokenC* E_(int i) nogil const:
        return this.safe_get(this.E(i))

    const TokenC* safe_get(int i) nogil const:
        if i < 0 or i >= this.length:
            return &this._empty_token
        else:
            return &this._sent[i]

    void map_get_arcs(const unordered_map[int, vector[ArcC]] &heads_arcs, vector[ArcC]* out) nogil const:
        cdef const vector[ArcC]* arcs
        head_arcs_it = heads_arcs.const_begin()
        while head_arcs_it != heads_arcs.const_end():
            arcs = &deref(head_arcs_it).second
            arcs_it = arcs.const_begin()
            while arcs_it != arcs.const_end():
                arc = deref(arcs_it)
                if arc.head != -1 and arc.child != -1:
                    out.push_back(arc)
                incr(arcs_it)
            incr(head_arcs_it)

    void get_arcs(vector[ArcC]* out) nogil const:
        this.map_get_arcs(this._left_arcs, out)
        this.map_get_arcs(this._right_arcs, out)

    int H(int child) nogil const:
        if child >= this.length or child < 0:
            return -1
        else:
            return this._heads[child]

    int E(int i) nogil const:
        if this._ents.size() == 0:
            return -1
        else:
            return this._ents.back().start

    int nth_child(const unordered_map[int, vector[ArcC]]& heads_arcs, int head, int idx) nogil const:
        if idx < 1:
            return -1

        head_arcs_it = heads_arcs.const_find(head)
        if head_arcs_it == heads_arcs.const_end():
            return -1

        cdef const vector[ArcC]* arcs = &deref(head_arcs_it).second

        # Work backwards through arcs to find the arc at the
        # requested index more quickly.
        cdef size_t child_index = 0
        arcs_it = arcs.const_rbegin()
        while arcs_it != arcs.const_rend() and child_index != idx:
            arc = deref(arcs_it)
            if arc.child != -1:
                child_index += 1
                if child_index == idx:
                    return arc.child
            incr(arcs_it)

        return -1

    int L(int head, int idx) nogil const:
        return this.nth_child(this._left_arcs, head, idx)

    int R(int head, int idx) nogil const:
        return this.nth_child(this._right_arcs, head, idx)

    bint empty() nogil const:
        return this._stack.size() == 0

    bint eol() nogil const:
        return this.buffer_length() == 0

    bint is_final() nogil const:
        return this.stack_depth() <= 0 and this.eol()

    int cannot_sent_start(int word) nogil const:
        if word < 0 or word >= this.length:
            return 0
        elif this._sent[word].sent_start == -1:
            return 1
        else:
            return 0

    int is_sent_start(int word) nogil const:
        if word < 0 or word >= this.length:
            return 0
        elif this._sent[word].sent_start == 1:
            return 1
        elif this._sent_starts.count(word) >= 1:
            return 1
        else:
            return 0

    void set_sent_start(int word, int value) nogil:
        if value >= 1:
            this._sent_starts.insert(word)

    bint has_head(int child) nogil const:
        return this._heads[child] >= 0

    int l_edge(int word) nogil const:
        return word

    int r_edge(int word) nogil const:
        return word

    int n_arcs(const unordered_map[int, vector[ArcC]] &heads_arcs, int head) nogil const:
        cdef int n = 0
        head_arcs_it = heads_arcs.const_find(head)
        if head_arcs_it == heads_arcs.const_end():
            return n

        cdef const vector[ArcC]* arcs = &deref(head_arcs_it).second
        arcs_it = arcs.const_begin()
        while arcs_it != arcs.end():
            arc = deref(arcs_it)
            if arc.child != -1:
                n += 1
            incr(arcs_it)

        return n


    int n_L(int head) nogil const:
        return n_arcs(this._left_arcs, head)

    int n_R(int head) nogil const:
        return n_arcs(this._right_arcs, head)

    bint stack_is_connected() nogil const:
        return False

    bint entity_is_open() nogil const:
        if this._ents.size() == 0:
            return False
        else:
            return this._ents.back().end == -1

    int stack_depth() nogil const:
        return this._stack.size()

    int buffer_length() nogil const:
        return (this.length - this._b_i) + this._rebuffer.size()

    void push() nogil:
        b0 = this.B(0)
        if this._rebuffer.size():
            b0 = this._rebuffer.back()
            this._rebuffer.pop_back()
        else:
            b0 = this._b_i
            this._b_i += 1
        this._stack.push_back(b0)

    void pop() nogil:
        this._stack.pop_back()

    void force_final() nogil:
        # This should only be used in desperate situations, as it may leave
        # the analysis in an unexpected state.
        this._stack.clear()
        this._b_i = this.length

    void unshift() nogil:
        s0 = this._stack.back()
        this._unshiftable[s0] = 1
        this._rebuffer.push_back(s0)
        this._stack.pop_back()

    int is_unshiftable(int item) nogil const:
        if item >= this._unshiftable.size():
            return 0
        else:
            return this._unshiftable.at(item)

    void set_reshiftable(int item) nogil:
        if item < this._unshiftable.size():
            this._unshiftable[item] = 0

    void add_arc(int head, int child, attr_t label) nogil:
        if this.has_head(child):
            this.del_arc(this.H(child), child)
        cdef ArcC arc
        arc.head = head
        arc.child = child
        arc.label = label
        if head > child:
            this._left_arcs[arc.head].push_back(arc)
        else:
            this._right_arcs[arc.head].push_back(arc)
        this._heads[child] = head

    void map_del_arc(unordered_map[int, vector[ArcC]]* heads_arcs, int h_i, int c_i) nogil:
        arcs_it = heads_arcs.find(h_i)
        if arcs_it == heads_arcs.end():
            return

        arcs = &deref(arcs_it).second
        if arcs.size() == 0:
            return

        arc = arcs.back()
        if arc.head == h_i and arc.child == c_i:
            arcs.pop_back()
        else:
            for i in range(arcs.size()-1):
                arc = arcs.at(i)
                if arc.head == h_i and arc.child == c_i:
                    arc.head = -1
                    arc.child = -1
                    arc.label = 0
                    break

    void del_arc(int h_i, int c_i) nogil:
        if h_i > c_i:
            this.map_del_arc(&this._left_arcs, h_i, c_i)
        else:
            this.map_del_arc(&this._right_arcs, h_i, c_i)

    SpanC get_ent() nogil const:
        cdef SpanC ent
        if this._ents.size() == 0:
            ent.start = 0
            ent.end = 0
            ent.label = 0
            return ent
        else:
            return this._ents.back()

    void open_ent(attr_t label) nogil:
        cdef SpanC ent
        ent.start = this.B(0)
        ent.label = label
        ent.end = -1
        this._ents.push_back(ent)

    void close_ent() nogil:
        this._ents.back().end = this.B(0)+1

    void clone(const StateC* src) nogil:
        this.length = src.length
        this._sent = src._sent
        this._stack = src._stack
        this._rebuffer = src._rebuffer
        this._sent_starts = src._sent_starts
        this._unshiftable = src._unshiftable
        memcpy(this._heads, src._heads, this.length * sizeof(this._heads[0]))
        this._ents = src._ents
        this._left_arcs = src._left_arcs
        this._right_arcs = src._right_arcs
        this._b_i = src._b_i
        this.offset = src.offset
        this._empty_token = src._empty_token
