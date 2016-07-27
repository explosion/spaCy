from libc.string cimport memcpy, memset
from libc.stdlib cimport malloc, calloc, free
from libc.stdint cimport uint32_t
from ..vocab cimport EMPTY_LEXEME
from ..structs cimport TokenC, Entity
from ..lexeme cimport Lexeme
from ..symbols cimport punct
from ..attrs cimport IS_SPACE


cdef inline bint is_space_token(const TokenC* token) nogil:
    return Lexeme.c_check_flag(token.lex, IS_SPACE)


cdef cppclass StateC:
    int* _stack
    int* _buffer
    bint* shifted
    TokenC* _sent
    Entity* _ents
    TokenC _empty_token
    int length
    int _s_i
    int _b_i
    int _e_i
    int _break

    __init__(const TokenC* sent, int length) nogil:
        cdef int PADDING = 5
        this._buffer = <int*>calloc(length + (PADDING * 2), sizeof(int))
        this._stack = <int*>calloc(length + (PADDING * 2), sizeof(int))
        this.shifted = <bint*>calloc(length + (PADDING * 2), sizeof(bint))
        this._sent = <TokenC*>calloc(length + (PADDING * 2), sizeof(TokenC))
        this._ents = <Entity*>calloc(length + (PADDING * 2), sizeof(Entity))
        cdef int i
        for i in range(length + (PADDING * 2)):
            this._ents[i].end = -1
            this._sent[i].l_edge = i
            this._sent[i].r_edge = i
        for i in range(length, length + (PADDING * 2)):
            this._sent[i].lex = &EMPTY_LEXEME
        this._sent += PADDING
        this._ents += PADDING
        this._buffer += PADDING
        this._stack += PADDING
        this.shifted += PADDING
        this.length = length
        this._break = -1
        this._s_i = 0
        this._b_i = 0
        this._e_i = 0
        for i in range(length):
            this._buffer[i] = i
        memset(&this._empty_token, 0, sizeof(TokenC))
        this._empty_token.lex = &EMPTY_LEXEME
        for i in range(length):
            this._sent[i] = sent[i]
            this._buffer[i] = i
        for i in range(length, length + 5):
            this._sent[i].lex = &EMPTY_LEXEME

    __dealloc__():
        cdef int PADDING = 5
        free(this._sent - PADDING)
        free(this._ents - PADDING)
        free(this._buffer - PADDING)
        free(this._stack - PADDING)
        free(this.shifted - PADDING)

    int S(int i) nogil const:
        if i >= this._s_i:
            return -1
        return this._stack[this._s_i - (i+1)]

    int B(int i) nogil const:
        if (i + this._b_i) >= this.length:
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

    int H(int i) nogil const:
        if i < 0 or i >= this.length:
            return -1
        return this._sent[i].head + i

    int E(int i) nogil const:
        if this._e_i <= 0 or this._e_i >= this.length:
            return 0
        if i < 0 or i >= this._e_i:
            return 0
        return this._ents[this._e_i - (i+1)].start

    int L(int i, int idx) nogil const:
        if idx < 1:
            return -1
        if i < 0 or i >= this.length:
            return -1
        cdef const TokenC* target = &this._sent[i]
        if target.l_kids < <uint32_t>idx:
            return -1
        cdef const TokenC* ptr = &this._sent[target.l_edge]

        while ptr < target:
            # If this head is still to the right of us, we can skip to it
            # No token that's between this token and this head could be our
            # child.
            if (ptr.head >= 1) and (ptr + ptr.head) < target:
                ptr += ptr.head

            elif ptr + ptr.head == target:
                idx -= 1
                if idx == 0:
                    return ptr - this._sent
                ptr += 1
            else:
                ptr += 1
        return -1
    
    int R(int i, int idx) nogil const:
        if idx < 1:
            return -1
        if i < 0 or i >= this.length:
            return -1
        cdef const TokenC* target = &this._sent[i]
        if target.r_kids < <uint32_t>idx:
            return -1
        cdef const TokenC* ptr = &this._sent[target.r_edge]
        while ptr > target:
            # If this head is still to the right of us, we can skip to it
            # No token that's between this token and this head could be our
            # child.
            if (ptr.head < 0) and ((ptr + ptr.head) > target):
                ptr += ptr.head
            elif ptr + ptr.head == target:
                idx -= 1
                if idx == 0:
                    return ptr - this._sent
                ptr -= 1
            else:
                ptr -= 1
        return -1

    bint empty() nogil const:
        return this._s_i <= 0

    bint eol() nogil const:
        return this.buffer_length() == 0

    bint at_break() nogil const:
        return this._break != -1

    bint is_final() nogil const:
        return this.stack_depth() <= 0 and this._b_i >= this.length

    bint has_head(int i) nogil const:
        return this.safe_get(i).head != 0

    int n_L(int i) nogil const:
        return this.safe_get(i).l_kids

    int n_R(int i) nogil const:
        return this.safe_get(i).r_kids

    bint stack_is_connected() nogil const:
        return False

    bint entity_is_open() nogil const:
        if this._e_i < 1:
            return False
        return this._ents[this._e_i-1].end == -1

    int stack_depth() nogil const:
        return this._s_i

    int buffer_length() nogil const:
        if this._break != -1:
            return this._break - this._b_i
        else:
            return this.length - this._b_i

    void push() nogil:
        if this.B(0) != -1:
            this._stack[this._s_i] = this.B(0)
        this._s_i += 1
        this._b_i += 1
        if this._b_i > this._break:
            this._break = -1

    void pop() nogil:
        if this._s_i >= 1:
            this._s_i -= 1
    
    void unshift() nogil:
        this._b_i -= 1
        this._buffer[this._b_i] = this.S(0)
        this._s_i -= 1
        this.shifted[this.B(0)] = True

    void add_arc(int head, int child, int label) nogil:
        if this.has_head(child):
            this.del_arc(this.H(child), child)

        cdef int dist = head - child
        this._sent[child].head = dist
        this._sent[child].dep = label
        cdef int i
        if child > head:
            this._sent[head].r_kids += 1
            # Some transition systems can have a word in the buffer have a
            # rightward child, e.g. from Unshift.
            this._sent[head].r_edge = this._sent[child].r_edge
            i = 0
            while this.has_head(head) and i < this.length:
                head = this.H(head)
                this._sent[head].r_edge = this._sent[child].r_edge
                i += 1 # Guard against infinite loops
        else:
            this._sent[head].l_kids += 1
            this._sent[head].l_edge = this._sent[child].l_edge

    void del_arc(int h_i, int c_i) nogil:
        cdef int dist = h_i - c_i
        cdef TokenC* h = &this._sent[h_i]
        cdef int i = 0
        if c_i > h_i:
            # this.R_(h_i, 2) returns the second-rightmost child token of h_i
            # If we have more than 2 rightmost children, our 2nd rightmost child's
            # rightmost edge is going to be our new rightmost edge.
            h.r_edge = this.R_(h_i, 2).r_edge if h.r_kids >= 2 else h_i
            h.r_kids -= 1
            new_edge = h.r_edge
            # Correct upwards in the tree --- see Issue #251
            while h.head < 0 and i < this.length: # Guard infinite loop
                h += h.head
                h.r_edge = new_edge
                i += 1
        else:
            # Same logic applies for left edge, but we don't need to walk up
            # the tree, as the head is off the stack.
            h.l_edge = this.L_(h_i, 2).l_edge if h.l_kids >= 2 else h_i
            h.l_kids -= 1

    void open_ent(int label) nogil:
        this._ents[this._e_i].start = this.B(0)
        this._ents[this._e_i].label = label
        this._ents[this._e_i].end = -1
        this._e_i += 1

    void close_ent() nogil:
        # Note that we don't decrement _e_i here! We want to maintain all
        # entities, not over-write them...
        this._ents[this._e_i-1].end = this.B(0)+1
        this._sent[this.B(0)].ent_iob = 1

    void set_ent_tag(int i, int ent_iob, int ent_type) nogil:
        if 0 <= i < this.length:
            this._sent[i].ent_iob = ent_iob
            this._sent[i].ent_type = ent_type

    void set_break(int i) nogil:
        if 0 <= i < this.length: 
            this._sent[i].sent_start = True
            this._break = this._b_i

    void clone(const StateC* src) nogil:
        memcpy(this._sent, src._sent, this.length * sizeof(TokenC))
        memcpy(this._stack, src._stack, this.length * sizeof(int))
        memcpy(this._buffer, src._buffer, this.length * sizeof(int))
        memcpy(this._ents, src._ents, this.length * sizeof(Entity))
        this._b_i = src._b_i
        this._s_i = src._s_i
        this._e_i = src._e_i
        this._break = src._break

    void fast_forward() nogil:
        # space token attachement policy:
        # - attach space tokens always to the last preceding real token
        # - except if it's the beginning of a sentence, then attach to the first following
        # - boundary case: a document containing multiple space tokens but nothing else,
        #   then make the last space token the head of all others

        while is_space_token(this.B_(0)) \
        or this.buffer_length() == 0 \
        or this.stack_depth() == 0:
            if this.buffer_length() == 0:
                # remove the last sentence's root from the stack
                if this.stack_depth() == 1:
                    this.pop()
                # parser got stuck: reduce stack or unshift
                elif this.stack_depth() > 1:
                    if this.has_head(this.S(0)):
                        this.pop()
                    else:
                        this.unshift()
                # stack is empty but there is another sentence on the buffer
                elif (this.length - this._b_i) >= 1:
                    this.push()
                else: # stack empty and nothing else coming
                    break

            elif is_space_token(this.B_(0)):
                # the normal case: we're somewhere inside a sentence
                if this.stack_depth() > 0:
                    # assert not is_space_token(this.S_(0))
                    # attach all coming space tokens to their last preceding
                    # real token (which should be on the top of the stack)
                    while is_space_token(this.B_(0)):
                        this.add_arc(this.S(0),this.B(0),0)
                        this.push()
                        this.pop()
                # the rare case: we're at the beginning of a document:
                # space tokens are attached to the first real token on the buffer
                elif this.stack_depth() == 0:
                    # store all space tokens on the stack until a real token shows up
                    # or the last token on the buffer is reached
                    while is_space_token(this.B_(0)) and this.buffer_length() > 1:
                        this.push()
                    # empty the stack by attaching all space tokens to the
                    # first token on the buffer
                    # boundary case: if all tokens are space tokens, the last one
                    # becomes the head of all others
                    while this.stack_depth() > 0:
                        this.add_arc(this.B(0),this.S(0),0)
                        this.pop()
                    # move the first token onto the stack
                    this.push()

            elif this.stack_depth() == 0:
                # for one token sentences (?)
                if this.buffer_length() == 1:
                    this.push()
                    this.pop()
                # with an empty stack and a non-empty buffer
                # only shift is valid anyway
                elif (this.length - this._b_i) >= 1:
                    this.push()

            else: # can this even happen?
                break
