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
    node1 = graph.add_node((0,))
    assert graph.get_node((0,)) == node1
    node2 = graph.add_node((1, 3))
    assert list(node2) == [1, 3]
    graph.add_edge(node1, node2, label="one", weight=-10.5)
    assert graph.has_edge(node1, node2, label="one")
    assert node1.heads() == []
    assert [tuple(h) for h in node2.heads()] == [(0,)]
    assert [tuple(t) for t in node1.tails()] == [(1, 3)]
    assert [tuple(t) for t in node2.tails()] == []


def test_graph_walk():
    doc = Doc(Vocab(), words=["a", "b", "c", "d"])
    graph = Graph(
        doc,
        name="hello",
        nodes=[(0,), (1,), (2,), (3,)],
        edges=[(0, 1), (0, 2), (0, 3), (3, 0)],
        labels=None,
        weights=None,
    )
    node0, node1, node2, node3 = list(graph.nodes)
    assert [tuple(h) for h in node0.heads()] == [(3,)]
    assert [tuple(h) for h in node1.heads()] == [(0,)]
    assert [tuple(h) for h in node0.walk_heads()] == [(3,), (0,)]
    assert [tuple(h) for h in node1.walk_heads()] == [(0,), (3,), (0,)]
    assert [tuple(h) for h in node2.walk_heads()] == [(0,), (3,), (0,)]
    assert [tuple(h) for h in node3.walk_heads()] == [(0,), (3,)]
    assert [tuple(t) for t in node0.walk_tails()] == [(1,), (2,), (3,), (0,)]
    assert [tuple(t) for t in node1.walk_tails()] == []
    assert [tuple(t) for t in node2.walk_tails()] == []
    assert [tuple(t) for t in node3.walk_tails()] == [(0,), (1,), (2,), (3,)]
