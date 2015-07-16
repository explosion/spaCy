from libcpp.vector cimport vector
from libc.stdint cimport uint32_t
from libc.stdint cimport int64_t
from libc.stdint cimport int32_t
from libc.stdint cimport uint64_t

from preshed.maps cimport PreshMap
from murmurhash.mrmr cimport hash64

import numpy

cimport cython

ctypedef unsigned char uchar

# Format
# - Total number of bytes in message (32 bit int)
# - Words, terminating in an EOL symbol, huffman coded ~12 bits per word
# - Spaces ~1 bit per word
# - Parse: Huffman coded head offset / dep label / POS tag / entity IOB tag
#          combo. ? bits per word. 40 * 80 * 40 * 12 = 1.5m symbol vocab


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


cdef class BitArray:
    cdef bytes data
    cdef unsigned char byte
    cdef unsigned char bit_of_byte
    cdef uint32_t i
    def __init__(self):
        self.data = b''
        self.byte = 0
        self.bit_of_byte = 0
        self.i = 0

    def __iter__(self):
        cdef uchar byte, i
        cdef uchar one = 1
        start_byte = self.i // 8
        if (self.i % 8) != 0:
            for i in range(self.i % 8):
                yield 1 if (self.data[start_byte] & (one << i)) else 0
            start_byte += 1
        for byte in self.data[start_byte:]:
            for i in range(8):
                yield 1 if byte & (one << i) else 0
        for i in range(self.bit_of_byte):
            yield 1 if self.byte & (one << i) else 0

    def as_bytes(self):
        if self.bit_of_byte != 0:
            return self.data + chr(self.byte)
        else:
            return self.data

    def append(self, bint bit):
        cdef uint64_t one = 1
        if bit:
            self.byte |= one << self.bit_of_byte
        else:
            self.byte &= ~(one << self.bit_of_byte)
        self.bit_of_byte += 1
        if self.bit_of_byte == 8:
            self.data += chr(self.byte)
            self.byte = 0
            self.bit_of_byte = 0

    cdef int extend(self, uint64_t code, char n_bits) except -1:
        cdef uint64_t one = 1
        cdef unsigned char bit_of_code
        for bit_of_code in range(n_bits):
            if code & (one << bit_of_code):
                self.byte |= one << self.bit_of_byte
            else:
                self.byte &= ~(one << self.bit_of_byte)
            self.bit_of_byte += 1
            if self.bit_of_byte == 8:
                self.data += chr(self.byte)
                self.byte = 0
                self.bit_of_byte = 0
    

cdef class Serializer:
    # Manage codecs, maintain consistent format for io
    def __init__(self, Vocab vocab, data_dir):
        model_dir = path.join(data_dir, 'bitter')
        self.vocab = vocab # Vocab owns the word codec, the big one
        self.cfg = Config.read(model_dir, 'config')
        self.codecs = tuple([CodecWrapper(attr) for attr in self.cfg.attrs])

    def __call__(self, doc_or_bits):
        if isinstance(doc_or_bits, Doc):
            return self.serialize(doc_or_bits)
        elif isinstance(doc_or_bits, BitArray):
            return self.deserialize(doc_or_bits)
        else:
            raise ValueError(doc_or_bits)

    def train(self, doc):
        array = doc.to_array([codec.id for codec in self.codecs])
        for i, codec in enumerate(self.codecs):
            codec.count(array[i]) 

    def serialize(self, doc):
        bits = BitArray()
        array = doc.to_array(self.attrs)
        for i, codec in enumerate(self.codecs):
            codec.encode(array[i,], bits)
        return bits

    @cython.boundscheck(False)
    def deserialize(self, bits):
        biterator = iter(bits)
        cdef Doc doc = Doc(self.vocab)
        ids = self.vocab.codec.decode(biterator)
        cdef int id_
        cdef bint is_spacy
        for id_ in ids:
            is_spacy = biterator.next()
            doc.push_back(vocab.lexemes.at(id_), is_spacy)

        cdef int length = doc.length
        array = numpy.zeros(shape=(length, len(self.codecs)), dtype=numpy.int)
        for i, codec in enumerate(self.codecs):
            array[i] = codec.decode(biterator)
        doc.from_array([c.id for c in self.codecs], array)
        return doc


cdef class AttributeEncoder:
    """Wrapper around HuffmanCodec"""
    def __init__(self, freqs, id=0):
        cdef uint64_t key
        cdef uint64_t count
        cdef pair[uint64_t] item
        cdef priority_queue[pair[uint64_t]] items
        for key, count in freqs:
            item.first = count
            item.second = key
            items.push(item)
        
        weights = array('f')
        keys = array('i')
        key_to_i = PreshMap()
        i = 0
        while not items.empty():
            item = items.top()
            weights.append(item.first)
            keys.append(item.second)
            key_to_i[item.second] = i
            i += 1
            items.pop()

    def encode(self, symbols):
        indices = [self.table[symbol] for symbol in symbols]
        return self._codec.encode(indices)

    def decode(self, bits):
        indices = self._codec.decode(bits)
        return [self.symbols[i] for i in indices]


cdef class HuffmanCodec:
    """Create a Huffman code table, and use it to pack and unpack sequences into
    byte strings. Emphasis is on efficiency, so API is quite strict:

    Messages will be encoded/decoded as indices that refer to the probability sequence.
    For instance, the sequence [5, 10, 8] indicates the 5th most frequent item,
    the 10th most frequent item, the 8th most frequent item.  The codec will add
    the EOL symbol to your message. An exception will be raised if you include
    the EOL symbol in your message.

    Arguments:
        weights (float[:]): A descending-sorted sequence of probabilities/weights.
          Must include a weight for an EOL symbol.

        eol (uint32_t): The index of the weight of the EOL symbol.
    """
    def __init__(self, float[:] weights, unt32_t eol):
        self.codes.resize(len(probs))
        for i in range(len(self.codes)):
            self.codes[i].bits = 0
            self.codes[i].length = 0
        populate_nodes(self.nodes, weights)
        cdef Code path
        path.bits = 0
        path.length = 0
        assign_codes(self.nodes, self.codes, len(self.nodes) - 1, path)

    def encode(self, uint32_t[:] sequence, BitArray bits=None):
        if bits is None:
            bits = BitArray()
        for i in sequence:
            bits.extend(self.codes[i].bits, self.codes[i].length) 
        bits.extend(self.codes[self.eol].bits, self.codes[self.eol].length)
        return bits

    def decode(self, bits):
        node = self.nodes.back()
        symbols = []
        for bit in bits:
            branch = node.right if bit else node.left
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
