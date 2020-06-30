from spacy.pipeline.pipes import DependencyParser
from spacy.vocab import Vocab

from spacy.pipeline.defaults import default_parser


def test_issue3830_no_subtok():
    """Test that the parser doesn't have subtok label if not learn_tokens"""
    config = {
        "learn_tokens": False,
        "min_action_freq": 30,
        "beam_width": 1,
        "beam_update_prob": 1.0,
    }
    parser = DependencyParser(Vocab(), default_parser(), **config)
    parser.add_label("nsubj")
    assert "subtok" not in parser.labels
    parser.begin_training(lambda: [])
    assert "subtok" not in parser.labels


def test_issue3830_with_subtok():
    """Test that the parser does have subtok label if learn_tokens=True."""
    config = {
        "learn_tokens": True,
        "min_action_freq": 30,
        "beam_width": 1,
        "beam_update_prob": 1.0,
    }
    parser = DependencyParser(Vocab(), default_parser(), **config)
    parser.add_label("nsubj")
    assert "subtok" not in parser.labels
    parser.begin_training(lambda: [])
    assert "subtok" in parser.labels
