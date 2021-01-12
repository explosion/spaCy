from spacy.vocab import Vocab
from spacy.tokens.doc import Doc
from spacy.tokens.graph import Graph


def test_graph_init():
    doc = Doc(Vocab(), words=["a", "b", "c", "d"])
    graph = Graph(doc, name="hello")
    assert graph.name == "hello"
    assert graph.doc is doc


def test_graph_edges_and_nodes():
    doc = Doc(Vocab(), words=["a", "b", "c", "d"])
    graph = Graph(doc, name="hello")
    node1 = graph.node((0,))
    assert graph.node((0,)) == node1
    node2 = graph.node((1, 3))
    graph.add_edge(
        node1,
        node2,
        label="one",
        weight=-10.5
    )
    assert graph.has_edge(
        node1,
        node2,
        label="one"
    )
    assert graph.head_nodes(node1) == []
    assert graph.head_nodes(node2) == [(0,)]
    assert graph.tail_nodes(node1) == [(1, 3)]
    assert graph.tail_nodes(node2) == []


def test_graph_walk():
    doc = Doc(Vocab(), words=["a", "b", "c", "d"])
    graph = Graph(
        doc,
        name="hello",
        nodes=[(0,), (1,), (2,), (3,)],
        edges=[(0, 1), (0, 2), (0, 3), (3, 0)]
    )
    assert graph.head_nodes(0) == [(3,)]
    assert graph.head_nodes(1) == [(0,)]
    assert graph.walk_head_nodes(0) == [(3,), (0,)]
    assert graph.walk_head_nodes(1) == [(0,), (3,), (0,)]
    assert graph.walk_head_nodes(2) == [(0,), (3,), (0,)]
    assert graph.walk_head_nodes(3) == [(0,), (3,)]
    assert graph.walk_tail_nodes(0) == [(1,), (2,), (3,), (0,)]
    assert graph.walk_tail_nodes(1) == []
    assert graph.walk_tail_nodes(2) == []
    assert graph.walk_tail_nodes(3) == [(0,), (1,), (2,), (3,)]
