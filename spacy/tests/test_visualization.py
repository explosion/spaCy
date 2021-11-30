import pytest
from spacy.visualization import Visualizer
from spacy.tokens import Span, Doc


def test_dependency_tree_basic(en_vocab):
    """Test basic dependency tree display."""
    doc = Doc(
        en_vocab,
        words=[
            "The",
            "big",
            "dog",
            "chased",
            "the",
            "frightened",
            "cat",
            "mercilessly",
            ".",
        ],
        heads=[2, 2, 3, None, 6, 6, 3, 3, 3],
        deps=["dep"] * 9,
    )
    dep_tree = Visualizer.render_dependency_tree(doc[0 : len(doc)], True)
    assert dep_tree == [
        "<╗  ",
        "<╣  ",
        "═╝<╗",
        "═══╣",
        "<╗ ║",
        "<╣ ║",
        "═╝<╣",
        "<══╣",
        "<══╝",
    ]
    dep_tree = Visualizer.render_dependency_tree(doc[0 : len(doc)], False)
    assert dep_tree == [
        "  ╔>",
        "  ╠>",
        "╔>╚═",
        "╠═══",
        "║ ╔>",
        "║ ╠>",
        "╠>╚═",
        "╠══>",
        "╚══>",
    ]


def test_dependency_tree_non_initial_sentence(en_vocab):
    """Test basic dependency tree display."""
    doc = Doc(
        en_vocab,
        words=[
            "Something",
            "happened",
            ".",
            "The",
            "big",
            "dog",
            "chased",
            "the",
            "frightened",
            "cat",
            "mercilessly",
            ".",
        ],
        heads=[0, None, 0, 5, 5, 6, None, 9, 9, 6, 6, 6],
        deps=["dep"] * 12,
    )
    dep_tree = Visualizer.render_dependency_tree(doc[3 : len(doc)], True)
    assert dep_tree == [
        "<╗  ",
        "<╣  ",
        "═╝<╗",
        "═══╣",
        "<╗ ║",
        "<╣ ║",
        "═╝<╣",
        "<══╣",
        "<══╝",
    ]
    dep_tree = Visualizer.render_dependency_tree(doc[3 : len(doc)], False)
    assert dep_tree == [
        "  ╔>",
        "  ╠>",
        "╔>╚═",
        "╠═══",
        "║ ╔>",
        "║ ╠>",
        "╠>╚═",
        "╠══>",
        "╚══>",
    ]


def test_dependency_tree_non_projective(en_vocab):
    """Test dependency tree display with a non-prejective dependency."""
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )
    dep_tree = Visualizer.render_dependency_tree(doc[0 : len(doc)], True)
    assert dep_tree == [
        "<╗    ",
        "═╩═══╗",
        "<╗   ║",
        "═╩═╗<╣",
        "<══║═╣",
        "<╗ ║ ║",
        "<╣ ║ ║",
        "═╝<╝ ║",
        "<════╝",
    ]
    dep_tree = Visualizer.render_dependency_tree(doc[0 : len(doc)], False)
    assert dep_tree == [
        "    ╔>",
        "╔═══╩═",
        "║   ╔>",
        "╠>╔═╩═",
        "╠═║══>",
        "║ ║ ╔>",
        "║ ║ ╠>",
        "║ ╚>╚═",
        "╚════>",
    ]


def test_dependency_tree_input_not_span(en_vocab):
    """Test dependency tree display behaviour when the input is not a Span."""
    doc = Doc(
        en_vocab,
        words=[
            "I",
            "saw",
            "a",
            "horse",
            "yesterday",
            "that",
            "was",
            "injured",
            ".",
        ],
        heads=[1, None, 3, 1, 1, 7, 7, 3, 1],
        deps=["dep"] * 9,
    )

    with pytest.raises(AssertionError):
        Visualizer.render_dependency_tree(doc[1:3], True)
