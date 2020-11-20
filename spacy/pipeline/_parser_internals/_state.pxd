from libc.string cimport memcpy, memset
from libc.stdlib cimport calloc, free
from libc.stdint cimport uint32_t, uint64_t
from libcpp.vector cimport vector
from cpython.exc cimport PyErr_CheckSignals, PyErr_SetFromErrno
from murmurhash.mrmr cimport hash64

from ...vocab cimport EMPTY_LEXEME
from ...structs cimport TokenC, SpanC
from ...lexeme cimport Lexeme
from ...attrs cimport IS_SPACE
from ...typedefs cimport attr_t


cdef inline bint is_space_token(const TokenC* token) nogil:
    return Lexeme.c_check_flag(token.lex, IS_SPACE)

cdef struct ArcC:
    int head
    int child
    attr_t label


cdef cppclass StateC:
    int* _stack
    int* _buffer
    bint* shifted
    bint* sent_starts
    const TokenC* _sent
    vector[SpanC] _ents
    vector[ArcC] _arcs
    TokenC _empty_token
    int length
    int offset
    int _s_i
    int _b_i

    __init__(const TokenC* sent, int length) nogil:
        this._sent = sent
        this._buffer = <int*>calloc(length, sizeof(int))
        this._stack = <int*>calloc(length, sizeof(int))
        this.sent_starts = <bint*>calloc(length, sizeof(bint))
        this.shifted = <bint*>calloc(length, sizeof(bint))
        if not (this._buffer and this._stack and this.shifted
                and this._sent):
            with gil:
                PyErr_SetFromErrno(MemoryError)
                PyErr_CheckSignals()
        this.offset = 0
        this.length = length
        this._s_i = 0
        this._b_i = 0
        for i in range(length):
            this._buffer[i] = i
            this.sent_starts[i] = sent[i].sent_start
        memset(&this._empty_token, 0, sizeof(TokenC))
        this._empty_token.lex = &EMPTY_LEXEME

    __dealloc__():
        free(this._buffer)
        free(this._stack)
        free(this.shifted)
        free(this.sent_starts)

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
        if i >= this._s_i:
            return -1
        elif i < 0:
            return -1
        return this._stack[this._s_i - (i+1)]

    int B(int i) nogil const:
        if (i + this._b_i) >= this.length:
            return -1
        elif i < 0:
            return -1
        return this._buffer[this._b_i + i]

    const TokenC* S_(int i) nogil const:
        return this.safe_get(this.S(i))

    const TokenC* B_(int i) nogil const:
        return this.safe_get(this.B(i))

    const TokenC* H_(int i) nogil const:
        return this.safe_get(this.H(i))

    const TokenC* E_(int i) nogil const:
        return this.safe_get(this.E(i))

    const TokenC* L_(int i, int idx) nogil const:
        return this.safe_get(this.L(i, idx))

    const TokenC* R_(int i, int idx) nogil const:
        return this.safe_get(this.R(i, idx))

    const TokenC* safe_get(int i) nogil const:
        if i < 0 or i >= this.length:
            return &this._empty_token
        else:
            return &this._sent[i]

    int H(int child) nogil const:
        for i in range(this._arcs.size()):
            arc = this._arcs.at(i)
            if arc.head != -1 and arc.child == child:
                return arc.head
        else:
            return -1

    int E(int i) nogil const:
        if this._ents.size() == 0:
            return -1
        else:
            return this._ents.back().start

    int L(int head, int idx) nogil const:
        if idx < 1 or this._arcs.size() == 0:
            return -1
        cdef vector[int] lefts
        for i in range(this._arcs.size()):
            arc = this._arcs.at(i)
            if arc.head == head and arc.child != -1 and arc.child < head:
                lefts.push_back(arc.child)
        if idx > lefts.size():
            return -1
        else:
            return lefts.at(idx-1)

    int R(int head, int idx) nogil const:
        if idx < 1 or this._arcs.size() == 0:
            return -1
        cdef vector[int] rights
        for i in range(this._arcs.size()):
            arc = this._arcs.at(i)
            if arc.head == head and arc.child != -1 and arc.child > head:
                rights.push_back(arc.child)
        if idx > rights.size():
            return -1
        else:
            return rights.at(idx-1)

    bint empty() nogil const:
        return this._s_i <= 0

    bint eol() nogil const:
        return this.buffer_length() == 0

    bint is_final() nogil const:
        return this.stack_depth() <= 0 and this.eol()

    int cannot_sent_start(int word) nogil const:
        return this.sent_starts[word] == -1

    int is_sent_start(int word) nogil const:
        return this.sent_starts[word] == 1

    void set_sent_start(int word, int value) nogil:
        this.sent_starts[word] = value

    bint has_head(int child) nogil const:
        for i in range(this._arcs.size()):
            arc = this._arcs.at(i)
            if arc.child == child and arc.head != -1:
                return True
        else:
            return False

    int l_edge(int word) nogil const:
        return word

    int r_edge(int word) nogil const:
        return word
 
    int n_L(int head) nogil const:
        cdef int n = 0
        for i in range(this._arcs.size()):
            arc = this._arcs.at(i) 
            if arc.head == head and arc.child != -1 and arc.child < arc.head:
                n += 1
        return n

    int n_R(int head) nogil const:
        cdef int n = 0
        for i in range(this._arcs.size()):
            arc = this._arcs.at(i) 
            if arc.head == head and arc.child != -1 and arc.child > arc.head:
                n += 1
        return n

    bint stack_is_connected() nogil const:
        return False

    bint entity_is_open() nogil const:
        if this._ents.size() == 0:
            return False
        else:
            return this._ents.back().end

    int stack_depth() nogil const:
        return this._s_i

    int buffer_length() nogil const:
        return this.length - this._b_i

    void push() nogil:
        if this.B(0) != -1:
            this._stack[this._s_i] = this.B(0)
        this._s_i += 1
        this._b_i += 1

    void pop() nogil:
        if this._s_i >= 1:
            this._s_i -= 1

    void force_final() nogil:
        # This should only be used in desperate situations, as it may leave
        # the analysis in an unexpected state.
        this._s_i = 0
        this._b_i = this.length

    void unshift() nogil:
        this._b_i -= 1
        this._buffer[this._b_i] = this.S(0)
        this._s_i -= 1
        this.shifted[this.B(0)] = True

    void add_arc(int head, int child, attr_t label) nogil:
        if this.has_head(child):
            this.del_arc(this.H(child), child)
        cdef ArcC arc
        arc.head = head
        arc.child = child
        arc.label = label
        this._arcs.push_back(arc)

    void del_arc(int h_i, int c_i) nogil:
        if this._arcs.size() == 0:
            return
        arc = this._arcs.back()
        if arc.head == h_i and arc.child == c_i:
            this._arcs.pop_back()
        else:
            for i in range(this._arcs.size()-1):
                arc = this._arcs.at(i)
                if arc.head == h_i and arc.child == c_i:
                    arc.head = -1
                    arc.child = -1
                    arc.label = 0
                    break

    SpanC get_ent() nogil:
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

    void set_ent_tag(int i, int ent_iob, attr_t ent_type) nogil:
        pass

    void clone(const StateC* src) nogil:
        this.length = src.length
        this._sent = src._sent
        memcpy(this._stack, src._stack, this.length * sizeof(int))
        memcpy(this._buffer, src._buffer, this.length * sizeof(int))
        memcpy(this.shifted, src.shifted, this.length * sizeof(this.shifted[0]))
        memcpy(this.sent_starts, src.sent_starts, this.length * sizeof(this.sent_starts[0]))
        cdef int i
        for i in range(src._ents.size()):
            this._ents.push_back(src._ents.at(i)) 
        for i in range(src._arcs.size()):
            arc = src._arcs.at(i)
            if arc.head != -1:
                this._arcs.push_back(arc)
        this._b_i = src._b_i
        this._s_i = src._s_i
        this.offset = src.offset
        this._empty_token = src._empty_token
