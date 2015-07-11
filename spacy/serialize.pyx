from libcpp.vector cimport vector
from libc.stdint cimport uint32_t
from libc.stdint cimport int64_t
from libc.stdint cimport uint64_t

import numpy


cdef struct Node:
    float prob
    int left
    int right


cdef struct BitArray:
    uint64_t data


cdef BitArray set_bit(BitArray barray, unsigned char id_) nogil:
    cdef uint64_t one = 1
    barray.data |= one << id_
    return barray


cdef BitArray clear_bit(BitArray barray, unsigned char id_) nogil:
    cdef uint64_t one = 1
    barray.data ^= one << id_
    return barray


cpdef uint64_t[:] huffman_encode(float[:] probs):
    assert len(probs) >= 3

    output = numpy.zeros(shape=(len(probs),), dtype=numpy.uint64)
 
    cdef int size = len(probs)
    cdef vector[Node] nodes
    cdef int i = size - 1
    cdef int j = 0
    
    append_two(nodes, i, i-1, probs[i] + probs[i-1])
    i -= 2
    append_one(nodes, 0, i, probs[i])
    j += 1
    i -= 1
    while i >= 0 or j < len(nodes):
        if i < 0:
            append_zero(nodes, j)
            j += 2
        elif j >= len(nodes):
            append_two(nodes, i, i-1, probs[i]+probs[i-1])
        elif i >= 1 and (j == len(nodes) or probs[i-1] < nodes[j].prob):
            append_two(nodes, i, i-1, probs[i] + probs[i-1])
            i -= 2
        elif (j+1) < len(nodes) and nodes[j+1].prob < probs[i]:
            append_zero(nodes, j)
            j += 2
        else:
            append_one(nodes, j, i, probs[i])
            i -= 1
            j += 1
    cdef vector[BitArray] codes
    codes.resize(len(probs))
    for i in range(len(probs)):
        codes[i].data = 0
    assign_codes(nodes, codes, len(nodes) - 2, BitArray(data=0), 0)
    output = numpy.zeros(shape=(len(codes),), dtype=numpy.uint64)
    for i in range(len(codes)):
        output[i] = codes[i].data
    return output


cdef int assign_codes(vector[Node]& nodes, vector[BitArray]& codes, int i,
                      BitArray code, int bit) except -1:
    cdef BitArray left_code = clear_bit(code, bit)
    if nodes[i].left >= 0:
        if nodes[i].left != i:
            assign_codes(nodes, codes, nodes[i].left, left_code, bit+1)
    else:
        id_ = -(nodes[i].left + 1)
        codes[id_] = left_code
    cdef BitArray right_code = set_bit(code, bit)
    if nodes[i].right >= 0:
        if nodes[i].right != i:
            assign_codes(nodes, codes, nodes[i].right, right_code, bit+1)
    else:
        id_ = -(nodes[i].right + 1)
        codes[id_] = right_code


cdef int append_zero(vector[Node]& nodes, int j) nogil:
    cdef Node node
    node.left = j
    node.right = j+1
    node.prob = nodes[j].prob + nodes[j+1].prob
    nodes.push_back(node)


cdef int append_one(vector[Node]& nodes, int j, int id_, float prob) except -1:
    cdef Node node
    # Encode leaves as negative integers, where the integer is the index of the
    # word in the vocabulary.
    leaf_id = - <int64_t>(id_ + 1)
    new_prob = prob + nodes[j].prob
    if prob < nodes[j].prob:
        node.left = leaf_id
        node.right = j
        node.prob = new_prob
        nodes.push_back(node)
    else:
        node.left = j
        node.right = leaf_id
        node.prob = new_prob
        nodes.push_back(node)


cdef int append_two(vector[Node]& nodes, int id1, int id2, float prob) except -1:
    cdef Node node
    node.left = -<int64_t>(id1 + 1)
    node.right = -<int64_t>(id2 + 1)
    node.prob = prob
    nodes.push_back(node)
