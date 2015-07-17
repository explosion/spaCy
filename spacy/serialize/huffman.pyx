cimport cython

from ..typedefs cimport attr_t

from .bits cimport bit_append
from .bits cimport BitArray


cdef class HuffmanCodec:
    """Create a Huffman code table, and use it to pack and unpack sequences into
    byte strings. Emphasis is on efficiency, so API is quite strict:

    Messages will be encoded/decoded as indices that refer to the probability sequence.
    For instance, the sequence [5, 10, 8] indicates the 5th most frequent item,
    the 10th most frequent item, the 8th most frequent item.

    Arguments:
        weights (float[:]): A descending-sorted sequence of probabilities/weights.
          Must include a weight for an EOL symbol.

    """
    def __init__(self, float[:] weights):
        self.codes.resize(len(weights))
        for i in range(len(self.codes)):
            self.codes[i].bits = 0
            self.codes[i].length = 0
        populate_nodes(self.nodes, weights)
        cdef Code path
        path.bits = 0
        path.length = 0
        assign_codes(self.nodes, self.codes, len(self.nodes) - 1, path)

    def encode(self, attr_t[:] msg, BitArray into_bits):
        cdef int i
        for i in range(len(msg)):
            into_bits.extend(self.codes[msg[i]].bits, self.codes[msg[i]].length)

    def decode(self, bits, attr_t[:] into_msg):
        node = self.nodes.back()
        cdef int i = 0
        cdef int n = len(into_msg)
        for bit in bits:
            branch = node.right if bit else node.left
            if branch >= 0:
                node = self.nodes.at(branch)
            else:
                into_msg[i] = -(branch + 1)
                node = self.nodes.back()
                i += 1
                if i == n:
                    break
        else:
            raise Exception(
                "Buffer exhausted at %d/%d symbols read." % (i, len(into_msg)))

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
    """Introduce a new non-terminal, over two non-terminals)"""
    cdef Node node
    node.left = j
    node.right = j+1
    node.prob = nodes[j].prob + nodes[j+1].prob
    nodes.push_back(node)


cdef int _cover_one_word_one_node(vector[Node]& nodes, int j, int id_, float prob) nogil:
    """Introduce a new non-terminal, over one terminal and one non-terminal."""
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
    """Introduce a new node, over two non-terminals."""
    cdef Node node
    node.left = -(id1+1)
    node.right = -(id2+1)
    node.prob = prob
    nodes.push_back(node)


cdef int assign_codes(vector[Node]& nodes, vector[Code]& codes, int i, Code path) except -1:
    """Recursively assign paths, from the top down. At the end, the entry codes[i]
    knows the bit-address of the node[j] that points to entry i in the vocabulary.
    So, to encode i, we go to codes[i] and read its bit-string. To decode, we
    navigate nodes recursively.
    """
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
