# cython: infer_types=True, cdivision=True, boundscheck=False, binding=True
from libc.stdint cimport int32_t, int64_t
from libcpp.pair cimport pair
from libcpp.unordered_map cimport unordered_map
from libcpp.unordered_set cimport unordered_set
from cython.operator cimport dereference
import weakref
from preshed.maps cimport map_get_unless_missing
from murmurhash.mrmr cimport hash64
from ..typedefs cimport hash_t
from ..strings import get_string_id
from ..structs cimport EdgeC, GraphC


class Edge:
    def __init__(self, doc, head, tail, label, weight):
        self.doc = doc
        self.head_indices = head
        self.tail_indices = tail
        self.label = label
        self.weight = weight

    @property
    def head(self):
        return tuple([self.doc[i] for i in self.head_indices])
    
    @property
    def tail(self):
        return tuple([self.doc[i] for i in self.tail_indices])

    @property
    def label_(self):
        return self.doc.vocab.strings[self.label]


cdef class Graph:
    """A set of directed labelled relationships between sets of tokens."""
    def __init__(self, doc, name=""):
        self.c.node_map = unordered_map[hash_t, int]()
        self.c.edge_map = unordered_map[hash_t, int]()
        self.c.roots = unordered_set[int]()
        self.name = name
        self.doc_ref = weakref.ref(doc)

    @property
    def doc(self):
        return self.doc_ref()

    def __iter__(self):
        doc = self.doc
        for i in range(self.c.edges.size()):
            edge = self.c.edges[i]
            yield Edge(
                doc,
                tuple(self.c.nodes[edge.head]),
                tuple(self.c.nodes[edge.tail]),
                label=edge.label,
                weight=self.c.weights[i]
            )

    def node(self, tuple indices):
        cdef vector[int32_t] node 
        node.reserve(len(indices))
        for i, idx in enumerate(indices):
            node.push_back(idx)
        return add_node(&self.c, node)

    def edge(self, int i):
        edge = self.c.edges[i]
        return Edge(
            self.doc,
            self.c.nodes[edge.head],
            tuple(self.c.nodes[edge.tail]),
            label=edge.label,
            weight=self.c.weights[i]
        )

    def siblings(self, tuple indices):
        cdef vector[int] siblings
        get_sibling_nodes(siblings, &self.c, self.node(indices))
        return [tuple(self.c.nodes[siblings[i]]) for i in range(siblings.size())]
   
    def head_nodes(self, int node):
        cdef vector[int] output
        size = get_head_nodes(output, &self.c, node)
        return [tuple(self.c.nodes[output[i]]) for i in range(output.size())]

    def tail_nodes(self, int node):
        cdef vector[int] output
        size = get_tail_nodes(output, &self.c, node)
        return [tuple(self.c.nodes[output[i]]) for i in range(output.size())]

    def head_edges(self, int node):
        cdef vector[int] edge_indices
        get_head_edges(edge_indices, &self.c, node)
        return [self.edge(edge_indices[i]) for i in range(edge_indices.size())]

    def tail_edges(self, int node):
        cdef vector[int] edge_indices
        get_tail_edges(edge_indices, &self.c, node)
        return [self.edge(edge_indices[i]) for i in range(edge_indices.size())]
 
    def walk_head_edges(self, int node):
        queue = self.heads(node)
        for edge in queue:
            yield edge
            queue.extend(self.heads(edge.head_index))

    def walk_tail_edges(self, int node):
        queue = self.tails(node)
        for edge in queue:
            yield edge
            queue.extend(self.tails(edge.tail_index))

    def has_edge(self, int head, int tail, label=""):
        return has_edge(
            &self.c,
            EdgeC(head=head, tail=tail, label=get_string_id(label))
        )
    
    def add_edge(self, int head, int tail, *, label="", weight=None):
        """Add an arc to the graph, connecting two spans or tokens."""
        label_hash = self.doc.vocab.strings.as_int(label)
        weight_float = weight if weight is not None else 0.0
        add_edge(&self.c, EdgeC(head=head, tail=tail, label=label_hash), weight_float)
    

cdef int add_node(GraphC* graph, vector[int32_t]& node) nogil:
    key = hash64(&node[0], node.size() * sizeof(node[0]), 0)
    it = graph.node_map.find(key)
    if it != graph.node_map.end():
        # Item found. Convert the iterator to an index value.
        return dereference(it).second
    else:
        index = graph.nodes.size()
        graph.nodes.push_back(node)
        graph.n_heads.push_back(0)
        graph.n_tails.push_back(0)
        graph.first_head.push_back(0)
        graph.first_tail.push_back(0)
        graph.roots.insert(index)
        graph.node_map.insert(pair[hash_t, int](key, index))
        return index
 

cdef int add_edge(GraphC* graph, EdgeC edge, float weight) nogil:
    key = hash64(&edge, sizeof(edge), 0)
    it = graph.edge_map.find(key)
    if it != graph.edge_map.end():
        edge_index = dereference(it).second
        graph.weights[edge_index] = weight
        return edge_index
    else:
        edge_index = graph.edges.size()
        graph.edge_map.insert(pair[hash_t, int](key, edge_index))
        graph.edges.push_back(edge)
        if graph.n_tails[edge.head] == 0:
            graph.first_tail[edge.head] = edge_index
        if graph.n_heads[edge.tail] == 0:
            graph.first_head[edge.tail] = edge_index
        graph.n_tails[edge.head] += 1
        graph.n_heads[edge.tail] += 1
        graph.weights.push_back(weight)
        # If we had the tail marked as a root, remove it.
        tail_root_index = graph.roots.find(edge.tail)
        if tail_root_index != graph.roots.end():
            graph.roots.erase(tail_root_index)
        return edge_index


cdef int has_edge(const GraphC* graph, EdgeC edge) nogil:
    key = hash64(&edge, sizeof(edge), 0)
    return graph.edge_map.find(key) != graph.edge_map.end()


cdef int has_node(const GraphC* graph, vector[int32_t] node) nogil:
    key = hash64(&node, node.size() * sizeof(node[0]), 0)
    return graph.node_map.find(key) != graph.edge_map.end()


cdef int get_head_nodes(vector[int]& output, const GraphC* graph, int node) nogil:
    n_head = graph.n_heads[node]
    if n_head == 0:
        return 0
    output.reserve(output.size() + n_head)
    start = graph.first_head[node] 
    end = graph.edges.size()
    for i in range(start, end):
        if output.size() >= n_head:
            break
        output.push_back(graph.edges[i].head)
    return output.size()


cdef int get_tail_nodes(vector[int]& output, const GraphC* graph, int node) nogil:
    n_tail = graph.n_tails[node]
    if n_tail == 0:
        return 0
    output.reserve(output.size() + n_tail)
    start = graph.first_tail[node] 
    end = graph.edges.size()
    for i in range(start, end):
        if output.size() >= n_tail:
            break
        output.push_back(graph.edges[i].tail)
    return output.size()


cdef int get_sibling_nodes(vector[int]& output, const GraphC* graph, int node) nogil:
    cdef vector[int] heads
    cdef vector[int] tails
    get_head_nodes(heads, graph, node)
    for i in range(heads.size()):
        get_tail_nodes(tails, graph, heads[i])
        for j in range(tails.size()):
            if tails[j] != node:
                output.push_back(tails[j])
        tails.clear()
    return output.size()


cdef int get_head_edges(vector[int]& output, const GraphC* graph, int node) nogil:
    n_head = graph.n_heads[node]
    if n_head == 0:
        return 0
    output.reserve(output.size() + n_head)
    start = graph.first_head[node] 
    end = graph.edges.size()
    for i in range(start, end):
        if output.size() >= n_head:
            break
        output.push_back(i)
    return output.size()


cdef int get_tail_edges(vector[int]& output, const GraphC* graph, int node) nogil:
    n_tail = graph.n_tails[node]
    if n_tail == 0:
        return 0
    output.reserve(output.size() + n_tail)
    cdef int start = graph.first_tail[node] 
    cdef int end = graph.edges.size()
    for i in range(start, end):
        if output.size() >= n_tail:
            break
        output.push_back(i)
    return output.size()


cdef int walk_head_nodes(vector[int]& output, const GraphC* graph, int node) nogil:
    cdef unordered_set[int] seen = unordered_set[int]()
    output.push_back(node)
    cdef int i = 0
    while i < output.size():
        if seen.find(output[i]) == seen.end():
            seen.insert(output[i])
            get_head_nodes(output, graph, output[i])
        i += 1
    return i


cdef int walk_tail_nodes(vector[int]& output, const GraphC* graph, int node) nogil:
    cdef unordered_set[int] seen = unordered_set[int]()
    output.push_back(node)
    cdef int i = 0
    while i < output.size():
        if seen.find(output[i]) == seen.end():
            seen.insert(output[i])
            get_tail_nodes(output, graph, output[i])
        i += 1
    return i


cdef int walk_head_edges(vector[int]& output, const GraphC* graph, int node) nogil:
    cdef unordered_set[int] seen = unordered_set[int]()
    get_head_edges(output, graph, node)
    i = 0
    while i < output.size():
        if seen.find(output[i]) == seen.end():
            seen.insert(output[i])
            get_head_edges(output, graph, graph.edges[output[i]].head)
        i += 1
    return i


cdef int walk_tail_edges(vector[int]& output, const GraphC* graph, int node) nogil:
    cdef unordered_set[int] seen = unordered_set[int]()
    get_tail_edges(output, graph, node)
    i = 0
    while i < output.size():
        if seen.find(output[i]) == seen.end():
            seen.insert(output[i])
            get_tail_edges(output, graph, graph.edges[output[i]].tail)
        i += 1
    return i
