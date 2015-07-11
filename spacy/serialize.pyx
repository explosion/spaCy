cdef class HuffmanTable:
    def __init__(self, Vocab vocab):
        cdef int i = vocab.lexemes.size()-1
        j = 0
        cdef vector[Node] nodes
        while i >= 0 and j < size:
            if i >= 1 and lexemes[i-1].prob < nodes[j].prob:
                append_two(&nodes, j, lexemes[i].id, lexemes[i+1].id,
                           lexemes[i].prob + lexemes[i+1].prob)
                i -= 2
            elif (j + 1) < size and nodes[j+1].prob < lexemes[i].prob:
                append_zero(&nodes, j)
                j += 2
            else:
                append_one(&nodes, j, lexemes[i].id, lexemes[i].prob)
                i -= 1
                j += 1
        assign_codes(&nodes, j, 0, 0)
        i = 0
        for i in range(nodes.length):
            node = nodes[i]
            if node.left < 0:
                vocab.codes[- node.left] = node.code
            if nodes[i].right < 0:
                vocab.codes[- node.right] = set_another_bit(node.code)


cdef int assign_codes(vector[Node]* nodes, int i, uint32_t code, uint32_t j) except -1:
    nodes[i].code = code
    if nodes[i].left >= 0:
        assign_codes(nodes, nodes[i].left, code, j+1)
    if nodes[i].right >= 0:
        assign_codes(nodes, nodes[i].right, code | ((<uint32_t>1) << j), j+1)


cdef int append_zero(vector[Node]* nodes, int j) except -1:
    nodes.push_back(Node(left=j, right=j+1, prob=nodes[j].prob+nodes[j+1].prob))


cdef int append_one(vector[Node]* nodes, int j, attr_t id_, weight_t prob) except -1:
    # Encode leaves as negative integers, where the integer is the index of the
    # word in the vocabulary.
    leaf_id = - <int64_t>id_
    new_prob = prob + nodes[j].prob
    if prob < nodes[j].prob:
        nodes.push_back(Node(left=leaf_id, right=j, prob=new_prob))
    else:
        nodes.push_back(Node(left=j, right=leaf_id, prob=new_prob))


cdef int append_two(vector[Node]* nodes, attr_t id1, attr_t id2, weight_t prob) except -1:
    nodes.push_back(Node(left=- <int64_t>id1, right=- <int64_t>id2, prob=prob))
