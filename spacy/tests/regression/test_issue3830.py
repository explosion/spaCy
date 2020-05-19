from spacy.pipeline.pipes import DependencyParser
from spacy.vocab import Vocab

from spacy.pipeline.defaults import default_parser


def test_issue3830_no_subtok():
    """Test that the parser doesn't have subtok label if not learn_tokens"""
    parser = DependencyParser(Vocab(), default_parser())
    parser.add_label("nsubj")
    assert "subtok" not in parser.labels
    parser.begin_training(lambda: [])
    assert "subtok" not in parser.labels


def test_issue3830_with_subtok():
    """Test that the parser does have subtok label if learn_tokens=True."""
    parser = DependencyParser(Vocab(), default_parser(), learn_tokens=True)
    parser.add_label("nsubj")
    assert "subtok" not in parser.labels
    parser.begin_training(lambda: [])
    assert "subtok" in parser.labels
