from libcpp.vector cimport vector
from libc.stdint cimport uint32_t
from libc.stdint cimport int64_t
from libc.stdint cimport uint64_t

import numpy

cimport cython


cdef struct Node:
    float prob
    int left
    int right


cdef struct Code:
    uint64_t bits
    int length


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cpdef list huffman_encode(float[:] probs):
    assert len(probs) >= 3

    output = numpy.zeros(shape=(len(probs),), dtype=numpy.uint64)
 
    cdef int size = len(probs)
    cdef vector[Node] nodes
    cdef int i = size - 1
    cdef int j = 0
    
    while i >= 0 or (j+1) < nodes.size():
        if i < 0:
            cover_two_nodes(nodes, j)
            j += 2
        elif j >= nodes.size():
            cover_two_words(nodes, i, i-1, probs[i]+probs[i-1])
            i -= 2
        elif i >= 1 and (j == nodes.size() or probs[i-1] < nodes[j].prob):
            cover_two_words(nodes, i, i-1, probs[i] + probs[i-1])
            i -= 2
        elif (j+1) < nodes.size() and nodes[j+1].prob < probs[i]:
            cover_two_nodes(nodes, j)
            j += 2
        else:
            cover_one_word_one_node(nodes, j, i, probs[i])
            i -= 1
            j += 1
    cdef vector[Code] codes
    codes.resize(len(probs))
    assign_codes(nodes, codes, len(nodes) - 1, b'')
    output = []
    for i in range(len(codes)):
        out_str = '{0:b}'.format(codes[i].bits).rjust(codes[i].length, '0')
        output.append(out_str)
    return output


cdef int assign_codes(vector[Node]& nodes, vector[Code]& codes, int i, bytes path) except -1:
    left_path = path + b'0'
    right_path = path + b'1'
    # Assign down left branch
    if nodes[i].left >= 0:
        assign_codes(nodes, codes, nodes[i].left, left_path)
    else:
        # Leaf on left
        id_ = -(nodes[i].left + 1)
        codes[id_].length = len(left_path)
        codes[id_].bits = <uint64_t>int(left_path, 2)
    # Assign down right branch
    if nodes[i].right >= 0:
        assign_codes(nodes, codes, nodes[i].right, right_path)
    else:
        # Leaf on right
        id_ = -(nodes[i].right + 1)
        codes[id_].length = len(right_path)
        codes[id_].bits = <uint64_t>int(right_path, 2)


cdef int cover_two_nodes(vector[Node]& nodes, int j) nogil:
    cdef Node node
    node.left = j
    node.right = j+1
    node.prob = nodes[j].prob + nodes[j+1].prob
    nodes.push_back(node)


cdef int cover_one_word_one_node(vector[Node]& nodes, int j, int id_, float prob) nogil:
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


cdef int cover_two_words(vector[Node]& nodes, int id1, int id2, float prob) nogil:
    cdef Node node
    node.left = -(id1+1)
    node.right = -(id2+1)
    node.prob = prob
    nodes.push_back(node)
