from libc.stdint cimport int32_t, int64_t
import weakref
from preshed.maps cimport map_get_unless_missing
from murmurhash.mrmr cimport hash64
from ..strings import get_string_id
from ..structs cimport EdgeC


class Edge:
    def __init__(self, doc, parent, child, label, weight):
        self.doc = doc
        self.parent_indices = parent
        self.child_indices = child
        self.label = label
        self.weight = weight

    @property
    def parent(self):
        return tuple([self.doc[i] for i in self.parent_indices])
    
    @property
    def child(self):
        return tuple([self.doc[i] for i in self.child_indices])

    @property
    def label_(self):
        return self.doc.vocab.strings[self.label]


cdef class Graph:
    """A set of relationships between tokens. Relationships (edges)
    can be anchored by sequences of tokens (nodes). Nodes can be empty, so the
    graph can attach labels to a group of tokens that aren't connected to
    another group."""
    def __init__(self, doc, name=""):
        self.mem = Pool()
        self.name = name
        self.doc_ref = weakref.ref(doc)
        self.node_map = PreshMap()
        self.edge_map = PreshMap()

    @property
    def doc(self):
        return self.doc_ref()

    def __iter__(self):
        doc = self.doc
        for i in range(self.c.edges.size()):
            edge = self.c.edges[i]
            yield Edge(
                doc,
                tuple(self.c.nodes[edge.parent]),
                tuple(self.c.nodes[edge.child]),
                label=edge.label,
                weight=self.c.weights[i]
            )

    def get_edge(self, int i):
        edge = self.c.edges[i]
        return Edge(
            self.doc,
            self.c.nodes[edge.parent],
            tuple(self.c.nodes[edge.child]),
            label=edge.label,
            weight=self.c.weights[i]
        )

    def parents(self, int node):
        output = []
        n_parents = self.c.n_parents[node]
        for i in range(self.c.first_parent[node], self.c.edges.size()):
            if len(output) >= n_parents:
                break
            output.append(self.get_edge(i))
        return output

    def children(self, int node):
        output = []
        n_children = self.c.n_children[node]
        for i in range(self.c.first_children[node], self.c.edges.size()):
            if len(output) >= n_children:
                break
            output.append(self.get_edge(i))
        return output
 
    def ancestors(self, int node):
        queue = self.parents(node)
        for edge in queue:
            yield edge
            queue.extend(self.parents(edge.parent_index))

    def descendents(self, int node):
        queue = self.children(node)
        for edge in queue:
            yield edge
            queue.extend(self.children(edge.child_index))

    def has_edge(self, int parent, int child, label=""):
        cdef EdgeC edge
        edge.parent = parent
        edge.child = child
        edge.label = get_string_id(label)
        key = hash64(&edge, sizeof(edge), 0)
        return key in self.edge_map

    def add_edge(self, int parent, int child, *, label="", weight=None):
        """Add an arc to the graph, connecting two spans or tokens."""
        doc = self.doc
        cdef EdgeC edge
        edge.parent = parent
        edge.child = child
        edge.label = doc.vocab.strings.as_int(label)
        key = hash64(&edge, sizeof(edge), 0)
        # Avoid adding duplicate edges.
        result = map_get_unless_missing(self.edge_map.c_map, key)
        if result.found:
            edge_index = <int64_t>result.value
            if weight is not None:
                # Set the weight to the last seen value.
                self.c.weights[edge_index] = weight
        else:
            edge_index = self.c.edges.size()
            self.edge_map[key] = edge_index
            self.c.edges.push_back(edge)
            if self.c.n_children[edge.parent] == 0:
                self.c.first_child[edge.parent] = edge_index
            if self.c.n_parents[edge.child] == 0:
                self.c.first_parent[edge.child] = edge_index
            self.c.n_children[edge.parent] += 1
            self.c.n_parents[edge.child] += 1
            self.c.weights.push_back(weight if weight is not None else 0.0)
            if child in self.roots:
                self.roots.pop(child)
            if self.c.n_parents[edge.parent] == 0:
                self.roots.add(edge.parent)

    def add_node(self, tuple indices):
        cdef vector[int32_t] node 
        node.reserve(len(indices))
        for i, idx in enumerate(indices):
            node[i] = idx
        key = hash64(&node[0], sizeof(node[0]), 0)
        result = map_get_unless_missing(self.node_map.c_map, key)
        if result.found:
            return <int64_t>result.value
        else:
            index = self.c.nodes.size()
            self.c.nodes.push_back(node)
            self.node_map[key] = index
            self.c.n_parents.push_back(0)
            self.c.n_children.push_back(0)
            self.c.first_parent.push_back(0)
            self.c.first_child.push_back(0)
            return index
