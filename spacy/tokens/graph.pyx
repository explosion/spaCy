# cython: infer_types=True, cdivision=True, boundscheck=False, binding=True
from typing import Generator, List, Tuple

cimport cython
from cython.operator cimport dereference
from libc.stdint cimport int32_t, int64_t
from libcpp.pair cimport pair
from libcpp.unordered_map cimport unordered_map
from libcpp.unordered_set cimport unordered_set

import weakref

from murmurhash.mrmr cimport hash64
from preshed.maps cimport map_get_unless_missing

from .. import Errors

from ..typedefs cimport hash_t

from ..strings import get_string_id

from ..structs cimport EdgeC, GraphC

from .token import Token


@cython.freelist(8)
cdef class Edge:
    cdef readonly Graph graph
    cdef readonly int i
    
    def __init__(self, Graph graph, int i):
        self.graph = graph
        self.i = i

    @property
    def is_none(self) -> bool:
        return False

    @property
    def doc(self) -> "Doc":
        return self.graph.doc

    @property
    def head(self) -> "Node":
        return Node(self.graph, self.graph.c.edges[self.i].head)
    
    @property
    def tail(self) -> "Tail":
        return Node(self.graph, self.graph.c.edges[self.i].tail)

    @property
    def label(self) -> int:
        return self.graph.c.edges[self.i].label

    @property
    def weight(self) -> float:
        return self.graph.c.weights[self.i]

    @property
    def label_(self) -> str:
        return self.doc.vocab.strings[self.label]


@cython.freelist(8)
cdef class Node:
    cdef readonly Graph graph
    cdef readonly int i

    def __init__(self, Graph graph, int i):
        """A reference to a node of an annotation graph. Each node is made up of
        an ordered set of zero or more token indices.
        
        Node references are usually created by the Graph object itself, or from
        the Node or Edge objects. You usually won't need to instantiate this
        class yourself.
        """
        cdef int length = graph.c.nodes.size()
        if i >= length or -i >= length:
            raise IndexError(Errors.E1034.format(i=i, length=length))
        if i < 0:
            i += length
        self.graph = graph
        self.i = i

    def __eq__(self, other):
        if self.graph is not other.graph:
            return False
        else:
            return self.i == other.i

    def __iter__(self) -> Generator[int]:
        for i in self.graph.c.nodes[self.i]:
            yield i

    def __getitem__(self, int i) -> int:
        """Get a token index from the node's set of tokens."""
        length = self.graph.c.nodes[self.i].size()
        if i >= length or -i >= length:
            raise IndexError(Errors.E1035.format(i=i, length=length))
        if i < 0:
            i += length
        return self.graph.c.nodes[self.i][i]

    def __len__(self) -> int:
        """The number of tokens that make up the node."""
        return self.graph.c.nodes[self.i].size()

    @property
    def is_none(self) -> bool:
        """Whether the node is a special value, indicating 'none'.
        
        The NoneNode type is returned by the Graph, Edge and Node objects when
        there is no match to a query. It has the same API as Node, but it always
        returns NoneNode, NoneEdge or empty lists for its queries.
        """
        return False
 
    @property
    def doc(self) -> "Doc":
        """The Doc object that the graph refers to."""
        return self.graph.doc

    @property
    def tokens(self) -> Tuple[Token]:
        """A tuple of Token objects that make up the node."""
        doc = self.doc
        return tuple([doc[i] for i in self])

    def head(self, i=None, label=None) -> "Node":
        """Get the head of the first matching edge, searching by index, label,
        both or neither.
        
        For instance, `node.head(i=1)` will get the head of the second edge that
        this node is a tail of. `node.head(i=1, label="ARG0")` will further
        check that the second edge has the label `"ARG0"`. 
        
        If no matching node can be found, the graph's NoneNode is returned. 
        """
        return self.headed(i=i, label=label)
    
    def tail(self, i=None, label=None) -> "Node":
        """Get the tail of the first matching edge, searching by index, label,
        both or neither.
 
        If no matching node can be found, the graph's NoneNode is returned. 
        """
        return self.tailed(i=i, label=label).tail

    def sibling(self, i=None, label=None):
        """Get the first matching sibling node. Two nodes are siblings if they
        are both tails of the same head.
        If no matching node can be found, the graph's NoneNode is returned. 
        """
        if i is None:
            siblings = self.siblings(label=label)
            return siblings[0] if siblings else NoneNode(self)
        else:
            edges = []
            for h in self.headed():
                edges.extend([e for e in h.tailed() if e.tail.i != self.i])
            if i >= len(edges):
                return NoneNode(self)
            elif label is not None and edges[i].label != label:
                return NoneNode(self)
            else:
                return edges[i].tail

    def heads(self, label=None) -> List["Node"]:
        """Find all matching heads of this node."""
        cdef vector[int] edge_indices
        self._find_edges(edge_indices, "head", label)
        return [Node(self.graph, self.graph.c.edges[i].head) for i in edge_indices]
     
    def tails(self, label=None) -> List["Node"]:
        """Find all matching tails of this node."""
        cdef vector[int] edge_indices
        self._find_edges(edge_indices, "tail", label)
        return [Node(self.graph, self.graph.c.edges[i].tail) for i in edge_indices]

    def siblings(self, label=None) -> List["Node"]:
        """Find all maching siblings of this node. Two nodes are siblings if they
        are tails of the same head.
        """
        edges = []
        for h in self.headed():
            edges.extend([e for e in h.tailed() if e.tail.i != self.i])
        if label is None:
            return [e.tail for e in edges]
        else:
            return [e.tail for e in edges if e.label == label]

    def headed(self, i=None, label=None) -> Edge:
        """Find the first matching edge headed by this node.
        If no matching edge can be found, the graph's NoneEdge is returned.
        """
        start, end = self._find_range(i, self.c.n_head[self.i])
        idx = self._find_edge("head", start, end, label)
        if idx == -1:
            return NoneEdge(self.graph)
        else:
            return Edge(self.graph, idx)
    
    def tailed(self, i=None, label=None) -> Edge:
        """Find the first matching edge tailed by this node.
        If no matching edge can be found, the graph's NoneEdge is returned.
        """
        start, end = self._find_range(i, self.c.n_tail[self.i])
        idx = self._find_edge("tail", start, end, label)
        if idx == -1:
            return NoneEdge(self.graph)
        else:
            return Edge(self.graph, idx)

    def headeds(self, label=None) -> List[Edge]:
        """Find all matching edges headed by this node."""
        cdef vector[int] edge_indices
        self._find_edges(edge_indices, "head", label)
        return [Edge(self.graph, i) for i in edge_indices]

    def taileds(self, label=None) -> List["Edge"]:
        """Find all matching edges headed by this node."""
        cdef vector[int] edge_indices
        self._find_edges(edge_indices, "tail", label)
        return [Edge(self.graph, i) for i in edge_indices]

    def walk_heads(self):
        cdef vector[int] node_indices
        walk_head_nodes(node_indices, &self.graph.c, self.i)
        for i in node_indices:
            yield Node(self.graph, i)

    def walk_tails(self):
        cdef vector[int] node_indices
        walk_tail_nodes(node_indices, &self.graph.c, self.i)
        for i in node_indices:
            yield Node(self.graph, i)

    cdef (int, int) _get_range(self, i, n):
        if i is None:
            return (0, n)
        elif i < n:
            return (i, i+1)
        else:
            return (0, 0)

    cdef int _find_edge(self, str direction, int start, int end, label) except -2:
        if direction == "head":
            get_edges = get_head_edges
        else:
            get_edges = get_tail_edges
        cdef vector[int] edge_indices
        get_edges(edge_indices, &self.graph.c, self.i)
        if label is None:
            return edge_indices[start]
        for edge_index in edge_indices[start:end]:
            if self.graph.c.edges[edge_index].label == label:
                return edge_index
        else:
            return -1

    cdef int _find_edges(self, vector[int]& edge_indices, str direction, label):
        if direction == "head":
            get_edges = get_head_edges
        else:
            get_edges = get_tail_edges
        if label is None:
            get_edges(edge_indices, &self.graph.c, self.i)
            return edge_indices.size()
        cdef vector[int] unfiltered
        get_edges(unfiltered, &self.graph.c, self.i)
        for edge_index in unfiltered:
            if self.graph.c.edges[edge_index].label == label:
                edge_indices.push_back(edge_index)
        return edge_indices.size()


cdef class NoneEdge(Edge):
    """An Edge subclass, representing a non-result. The NoneEdge has the same
    API as other Edge instances, but always returns NoneEdge, NoneNode, or empty
    lists.
    """
    def __init__(self, graph):
        self.graph = graph
        self.i = -1
   
    @property
    def doc(self) -> "Doc":
        return self.graph.doc

    @property
    def head(self) -> "NoneNode":
        return NoneNode(self.graph)
    
    @property
    def tail(self) -> "NoneNode":
        return NoneNode(self.graph)

    @property
    def label(self) -> int:
        return 0

    @property
    def weight(self) -> float:
        return 0.0

    @property
    def label_(self) -> str:
        return ""


cdef class NoneNode(Node):
    def __init__(self, graph):
        self.graph = graph
        self.i = -1

    def __getitem__(self, int i):
        raise IndexError(Errors.E1036)

    def __len__(self):
        return 0
 
    @property
    def is_none(self):
        return -1

    @property
    def doc(self):
        return self.graph.doc

    @property
    def tokens(self):
        return tuple()

    def head(self, i=None, label=None):
        return self

    def tail(self, i=None, label=None):
        return self

    def walk_heads(self):
        yield from [] 
    
    def walk_tails(self):
        yield from [] 
 

cdef class Graph:
    """A set of directed labelled relationships between sets of tokens.
    
    EXAMPLE:
        Construction 1
        >>> graph = Graph(doc, name="srl")

        Construction 2
        >>> graph = Graph(
            doc,
            name="srl",
            nodes=[(0,), (1, 3), (,)],
            edges=[(0, 2), (2, 1)]
        )

        Construction 3
        >>> graph = Graph(
            doc,
            name="srl",
            nodes=[(0,), (1, 3), (,)],
            edges=[(2, 0), (0, 1)],
            labels=["word sense ID 1675", "agent"],
            weights=[-42.6, -1.7]
        )
        >>> assert graph.has_node((0,))
        >>> assert graph.has_edge((0,), (1,3), label="agent")
    """
    def __init__(self, doc, *, name="", nodes=[], edges=[], labels=None, weights=None):
        """Create a Graph object.

        doc (Doc): The Doc object the graph will refer to.
        name (str): A string name to help identify the graph. Defaults to "".
        nodes (List[Tuple[int]]): A list of token-index tuples to add to the graph
            as nodes. Defaults to [].
        edges (List[Tuple[int, int]]): A list of edges between the provided nodes.
            Each edge should be a (head, tail) tuple, where `head` and `tail`
            are integers pointing into the `nodes` list. Defaults to [].
        labels (Optional[List[str]]): A list of labels for the provided edges.
            If None, all of the edges specified by the edges argument will have
            be labelled with the empty string (""). If `labels` is not `None`,
            it must have the same length as the `edges` argument.
        weights (Optional[List[float]]): A list of weights for the provided edges.
            If None, all of the edges specified by the edges argument will 
            have the weight 0.0. If `weights` is not `None`, it must have the
            same length as the `edges` argument.
        """
        if weights is not None:
            assert len(weights) == len(edges)
        else:
            weights = [0.0] * len(edges)
        if labels is not None:
            assert len(labels) == len(edges)
        else:
            labels = [""] * len(edges)
        self.c.node_map = new unordered_map[hash_t, int]()
        self.c.edge_map = new unordered_map[hash_t, int]()
        self.c.roots = new unordered_set[int]()
        self.name = name
        self.doc_ref = weakref.ref(doc)
        for node in nodes:
            self.add_node(node)
        for (head, tail), label, weight in zip(edges, labels, weights):
            self.add_edge(
                Node(self, head),
                Node(self, tail),
                label=label,
                weight=weight
            )

    def __dealloc__(self):
        del self.c.node_map
        del self.c.edge_map
        del self.c.roots

    @property
    def doc(self) -> "Doc":
        """The Doc object the graph refers to."""
        return self.doc_ref()

    @property
    def edges(self) -> Generator[Edge]:
        """Iterate over the edges in the graph."""
        for i in range(self.c.edges.size()):
            yield Edge(self, i)

    @property
    def nodes(self) -> Generator[Node]:
        """Iterate over the nodes in the graph."""
        for i in range(self.c.nodes.size()):
            yield Node(self, i)

    def add_edge(self, head, tail, *, label="", weight=None) -> Edge:
        """Add an edge to the graph, connecting two groups of tokens.
       
        If there is already an edge for the (head, tail, label) triple, it will
        be returned, and no new edge will be created. The weight of the edge
        will be updated if a weight is specified.
        """
        label_hash = self.doc.vocab.strings.as_int(label)
        weight_float = weight if weight is not None else 0.0
        edge_index = add_edge(
            &self.c,
            EdgeC(
                head=self.add_node(head).i,
                tail=self.add_node(tail).i,
                label=self.doc.vocab.strings.as_int(label),
            ),
            weight=weight if weight is not None else 0.0
        )
        return Edge(self, edge_index)

    def get_edge(self, head, tail, *, label="") -> Edge:
        """Look up an edge in the graph. If the graph has no matching edge,
        the NoneEdge object is returned.
        """
        head_node = self.get_node(head)
        if head_node.is_none:
            return NoneEdge(self)
        tail_node = self.get_node(tail)
        if tail_node.is_none:
            return NoneEdge(self)
        edge_index = get_edge(
            &self.c,
            EdgeC(head=head_node.i, tail=tail_node.i, label=get_string_id(label))
        )
        if edge_index < 0:
            return NoneEdge(self)
        else:
            return Edge(self, edge_index)

    def has_edge(self, head, tail, label) -> bool:
        """Check whether a (head, tail, label) triple is an edge in the graph."""
        return not self.get_edge(head, tail, label=label).is_none
    
    def add_node(self, indices) -> Node:
        """Add a node to the graph and return it. Nodes refer to ordered sets
        of token indices.
        
        This method is idempotent: if there is already a node for the given
        indices, it is returned without a new node being created.
        """
        if isinstance(indices, Node):
            return indices
        cdef vector[int32_t] node 
        node.reserve(len(indices))
        for idx in indices:
            node.push_back(idx)
        i = add_node(&self.c, node)
        return Node(self, i)

    def get_node(self, indices) -> Node:
        """Get a node from the graph, or the NoneNode if there is no node for
        the given indices.
        """
        if isinstance(indices, Node):
            return indices
        cdef vector[int32_t] node 
        node.reserve(len(indices))
        for idx in indices:
            node.push_back(idx)
        node_index = get_node(&self.c, node)
        if node_index < 0:
            return NoneNode(self)
        else:
            return Node(self, node_index)
 
    def has_node(self, tuple indices) -> bool:
        """Check whether the graph has a node for the given indices."""
        return not self.get_node(indices).is_none


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


cdef int get_edge(const GraphC* graph, EdgeC edge) nogil:
    key = hash64(&edge, sizeof(edge), 0)
    it = graph.edge_map.find(key)
    if it == graph.edge_map.end():
        return -1
    else:
        return dereference(it).second


cdef int has_edge(const GraphC* graph, EdgeC edge) nogil:
    return get_edge(graph, edge) >= 0


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
 

cdef int get_node(const GraphC* graph, vector[int32_t] node) nogil:
    key = hash64(&node[0], node.size() * sizeof(node[0]), 0)
    it = graph.node_map.find(key)
    if it == graph.node_map.end():
        return -1
    else:
        return dereference(it).second


cdef int has_node(const GraphC* graph, vector[int32_t] node) nogil:
    return get_node(graph, node) >= 0


cdef int get_head_nodes(vector[int]& output, const GraphC* graph, int node) nogil:
    todo = graph.n_heads[node]
    if todo == 0:
        return 0
    output.reserve(output.size() + todo)
    start = graph.first_head[node] 
    end = graph.edges.size()
    for i in range(start, end):
        if todo <= 0:
            break
        elif graph.edges[i].tail == node:
            output.push_back(graph.edges[i].head)
            todo -= 1
    return todo


cdef int get_tail_nodes(vector[int]& output, const GraphC* graph, int node) nogil:
    todo = graph.n_tails[node]
    if todo == 0:
        return 0
    output.reserve(output.size() + todo)
    start = graph.first_tail[node] 
    end = graph.edges.size()
    for i in range(start, end):
        if todo <= 0:
            break
        elif graph.edges[i].head == node:
            output.push_back(graph.edges[i].tail)
            todo -= 1
    return todo


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
    todo = graph.n_heads[node]
    if todo == 0:
        return 0
    output.reserve(output.size() + todo)
    start = graph.first_head[node] 
    end = graph.edges.size()
    for i in range(start, end):
        if todo <= 0:
            break
        elif graph.edges[i].tail == node:
            output.push_back(i)
            todo -= 1
    return todo


cdef int get_tail_edges(vector[int]& output, const GraphC* graph, int node) nogil:
    todo = graph.n_tails[node]
    if todo == 0:
        return 0
    output.reserve(output.size() + todo)
    start = graph.first_tail[node] 
    end = graph.edges.size()
    for i in range(start, end):
        if todo <= 0:
            break
        elif graph.edges[i].head == node:
            output.push_back(i)
            todo -= 1
    return todo


cdef int walk_head_nodes(vector[int]& output, const GraphC* graph, int node) nogil:
    cdef unordered_set[int] seen = unordered_set[int]()
    get_head_nodes(output, graph, node)
    seen.insert(node)
    i = 0
    while i < output.size():
        if seen.find(output[i]) == seen.end():
            seen.insert(output[i])
            get_head_nodes(output, graph, output[i])
        i += 1
    return i


cdef int walk_tail_nodes(vector[int]& output, const GraphC* graph, int node) nogil:
    cdef unordered_set[int] seen = unordered_set[int]()
    get_tail_nodes(output, graph, node)
    seen.insert(node)
    i = 0
    while i < output.size():
        if seen.find(output[i]) == seen.end():
            seen.insert(output[i])
            get_tail_nodes(output, graph, output[i])
        i += 1
    return i


cdef int walk_head_edges(vector[int]& output, const GraphC* graph, int node) nogil:
    cdef unordered_set[int] seen = unordered_set[int]()
    get_head_edges(output, graph, node)
    seen.insert(node)
    i = 0
    while i < output.size():
        if seen.find(output[i]) == seen.end():
            seen.insert(output[i])
            get_head_edges(output, graph, output[i])
        i += 1
    return i


cdef int walk_tail_edges(vector[int]& output, const GraphC* graph, int node) nogil:
    cdef unordered_set[int] seen = unordered_set[int]()
    get_tail_edges(output, graph, node)
    seen.insert(node)
    i = 0
    while i < output.size():
        if seen.find(output[i]) == seen.end():
            seen.insert(output[i])
            get_tail_edges(output, graph, output[i])
        i += 1
    return i
