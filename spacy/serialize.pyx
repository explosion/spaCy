from libcpp.vector cimport vector
from libc.stdint cimport uint32_t
from libc.stdint cimport int64_t
from libc.stdint cimport uint64_t

import numpy


cdef struct Node:
    float prob
    int left
    int right


cpdef list huffman_encode(float[:] probs):
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
    while i >= 0 or (j+1) < len(nodes):
        if i < 0:
            append_zero(nodes, j)
            j += 2
        elif j >= len(nodes):
            append_two(nodes, i, i-1, probs[i]+probs[i-1])
            i -= 2
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
    output = ['' for _ in range(len(probs))]
    assign_codes(nodes, output, len(nodes) - 1, b'')
    return output


cdef int assign_codes(vector[Node]& nodes, list codes, int i, bytes path) except -1:
    left_path = path + b'0'
    right_path = path + b'1'
    # Assign down left branch
    if nodes[i].left >= 0:
        assign_codes(nodes, codes, nodes[i].left, left_path)
    else:
        # Leaf on left
        codes[-(nodes[i].left + 1)] = left_path
    # Assign down right branch
    if nodes[i].right >= 0:
        assign_codes(nodes, codes, nodes[i].right, right_path)
    else:
        # Leaf on right
        codes[-(nodes[i].right + 1)] = right_path


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
