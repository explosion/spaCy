from libcpp.vector cimport vector
from libc.stdint cimport uint32_t
from libc.stdint cimport int64_t
from libc.stdint cimport int32_t
from libc.stdint cimport uint64_t

from preshed.maps cimport PreshMap
from murmurhash.mrmr cimport hash64

import numpy

cimport cython

# Format
# - Total number of bytes in message (32 bit int)
# - Words, terminating in an EOL symbol, huffman coded ~12 bits per word
# - Spaces ~1 bit per word
# - Parse: Huffman coded head offset / dep label / POS tag / entity IOB tag
#          combo. ? bits per word. 40 * 80 * 40 * 12 = 1.5m symbol vocab


cdef struct Node:
    float prob
    int32_t left
    int32_t right


cdef struct Code:
    uint64_t bits
    char length


# Note that we're setting the most significant bits here first, when in practice
# we're actually wanting the last bit to be most significant (for Huffman coding,
# anyway).
cdef Code bit_append(Code code, bint bit) nogil:
    cdef uint64_t one = 1
    if bit:
        code.bits |= one << code.length
    else:
        code.bits &= ~(one << code.length)
    code.length += 1
    return code
    

cdef class HuffmanCodec:
    """Create a Huffman code table, and use it to pack and unpack sequences into
    byte strings. Emphasis is on efficiency, so API is quite strict:

    Messages will be encoded/decoded as indices that refer to the probability sequence.
    For instance, the sequence [5, 10, 8] indicates the 5th most frequent item,
    the 10th most frequent item, the 8th most frequent item.  The codec will add
    the EOL symbol to your message. An exception will be raised if you include
    the EOL symbol in your message.

    Arguments:
        probs (float[:]): A descending-sorted sequence of probabilities/weights.
          Must include a weight for an EOL symbol.

        eol (uint32_t): The index of the weight of the EOL symbol.
    """
    cdef vector[Node] nodes
    cdef vector[Code] codes
    cdef uint32_t eol
    def __init__(self, float[:] probs, uint32_t eol):
        self.eol = eol
        self.codes.resize(len(probs))
        for i in range(len(self.codes)):
            self.codes[i].bits = 0
            self.codes[i].length = 0
        populate_nodes(self.nodes, probs)
        cdef Code path
        path.bits = 0
        path.length = 0
        assign_codes(self.nodes, self.codes, len(self.nodes) - 1, path)

    def encode(self, uint32_t[:] sequence):
        cdef Code code
        cdef bytes output = b''
        cdef unsigned char byte = 0
        cdef uint64_t one = 1
        cdef unsigned char i_of_byte = 0
        cdef unsigned char i_of_code = 0
        for index in list(sequence) + [self.eol]:
            code = self.codes[index]
            for i_of_code in range(code.length):
                if code.bits & (one << i_of_code):
                    byte |= one << i_of_byte
                else:
                    byte &= ~(one << i_of_byte)
                i_of_byte += 1
                if i_of_byte == 8:
                    output += chr(byte)
                    byte = 0
                    i_of_byte = 0
        if i_of_byte != 0:
            output += chr(byte)
        return output

    def decode(self, bytes data):
        node = self.nodes.back()
        symbols = [] 
        cdef unsigned char byte
        cdef unsigned char i = 0
        cdef unsigned char one = 1
        for byte in data:
            for i in range(8):
                branch = node.right if (byte & (one << i)) else node.left
                if branch >= 0:
                    node = self.nodes.at(branch)
                else:
                    symbol = -(branch + 1)
                    if symbol == self.eol:
                        return symbols
                    else:
                        symbols.append(symbol)
                    node = self.nodes.back()
        return symbols

    property strings:
        @cython.boundscheck(False)
        @cython.wraparound(False)
        @cython.nonecheck(False)
        def __get__(self):
            output = []
            cdef int i, j
            cdef bytes string
            cdef Code code
            for i in range(self.codes.size()):
                code = self.codes[i]
                string = b'{0:b}'.format(code.bits).rjust(code.length, '0')
                string = string[::-1]
                output.append(string)
            return output


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef int populate_nodes(vector[Node]& nodes, float[:] probs) except -1:
    assert len(probs) >= 3
    cdef int size = len(probs)
    cdef int i = size - 1
    cdef int j = 0
    
    while i >= 0 or (j+1) < nodes.size():
        if i < 0:
            _cover_two_nodes(nodes, j)
            j += 2
        elif j >= nodes.size():
            _cover_two_words(nodes, i, i-1, probs[i] + probs[i-1])
            i -= 2
        elif i >= 1 and (j == nodes.size() or probs[i-1] < nodes[j].prob):
            _cover_two_words(nodes, i, i-1, probs[i] + probs[i-1])
            i -= 2
        elif (j+1) < nodes.size() and nodes[j+1].prob < probs[i]:
            _cover_two_nodes(nodes, j)
            j += 2
        else:
            _cover_one_word_one_node(nodes, j, i, probs[i])
            i -= 1
            j += 1
    return 0

cdef int _cover_two_nodes(vector[Node]& nodes, int j) nogil:
    cdef Node node
    node.left = j
    node.right = j+1
    node.prob = nodes[j].prob + nodes[j+1].prob
    nodes.push_back(node)


cdef int _cover_one_word_one_node(vector[Node]& nodes, int j, int id_, float prob) nogil:
    cdef Node node
    # Encode leaves as negative integers, where the integer is the index of the
    # word in the vocabulary.
    cdef int64_t leaf_id = - <int64_t>(id_ + 1)
    cdef float new_prob = prob + nodes[j].prob
    if prob < nodes[j].prob:
        node.left = leaf_id
        node.right = j
        node.prob = new_prob
    else:
        node.left = j
        node.right = leaf_id
        node.prob = new_prob
    nodes.push_back(node)


cdef int _cover_two_words(vector[Node]& nodes, int id1, int id2, float prob) nogil:
    cdef Node node
    node.left = -(id1+1)
    node.right = -(id2+1)
    node.prob = prob
    nodes.push_back(node)


cdef int assign_codes(vector[Node]& nodes, vector[Code]& codes, int i, Code path) except -1:
    cdef Code left_path = bit_append(path, 0)
    cdef Code right_path = bit_append(path, 1)
    
    # Assign down left branch
    if nodes[i].left >= 0:
        assign_codes(nodes, codes, nodes[i].left, left_path)
    else:
        # Leaf on left
        id_ = -(nodes[i].left + 1)
        codes[id_] = left_path
    # Assign down right branch
    if nodes[i].right >= 0:
        assign_codes(nodes, codes, nodes[i].right, right_path)
    else:
        # Leaf on right
        id_ = -(nodes[i].right + 1)
        codes[id_] = right_path
