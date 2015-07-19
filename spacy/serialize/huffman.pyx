cimport cython
from libcpp.queue cimport priority_queue
from libcpp.pair cimport pair

from ..typedefs cimport attr_t

from .bits cimport bit_append
from .bits cimport BitArray


cdef class HuffmanCodec:
    def __init__(self, freqs):
        cdef float count
        cdef Code code

        cdef pair[float, int] item
        cdef pair[float, int] item1
        cdef pair[float, int] item2
        cdef priority_queue[pair[float, int]] queue
        cdef int i = 0
        self._map = {}
        self.leaves = []
        for word, weight in freqs:
            item.first = -weight
            item.second = -(i+1)
            queue.push(item)
            
            self.leaves.append(word)
            code.bits = 0
            code.length = 0
            self.codes.push_back(code)
            self._map[word] = i
            i += 1

        cdef Node node
        while queue.size() >= 2:
            item1 = queue.top(); queue.pop()
            item2 = queue.top(); queue.pop()
            
            node = Node(left=item1.second, right=item2.second)
            self.nodes.push_back(node)

            item.first = item1.first + item2.first
            item.second = self.nodes.size()-1
            queue.push(item)
        item = queue.top()
        self.root = self.nodes[item.second]
        cdef Code path
        path.bits = 0
        path.length = 0
        assign_codes(self.nodes, self.codes, item.second, path)

    def encode(self, msg, BitArray bits=None):
        if bits is None:
            bits = BitArray()
        cdef int i
        for word in msg:
            i = self._map[word]
            bits.extend(self.codes[i].bits, self.codes[i].length)
        return bits

    def decode(self, bits, msg):
        node = self.root
        cdef int i = 0
        cdef int n = len(msg)
        for bit in bits:
            branch = node.right if bit else node.left
            if branch >= 0:
                node = self.nodes.at(branch)
            else:
                msg[i] = self.leaves[-(branch + 1)]
                node = self.nodes.back()
                i += 1
                if i == n:
                    break
        else:
            raise Exception(
                "Buffer exhausted at %d/%d symbols read." % (i, len(msg)))

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
