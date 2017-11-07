import pytest

from ...pipeline import DependencyParser


@pytest.fixture
def parser(en_vocab):
    parser = DependencyParser(en_vocab)
    parser.add_label('nsubj')
    parser.model, cfg = parser.Model(parser.moves.n_moves)
    parser.cfg.update(cfg)
    return parser


@pytest.fixture
def blank_parser(en_vocab):
    parser = DependencyParser(en_vocab)
    return parser


def test_to_from_bytes(parser, blank_parser):
    assert parser.model is not True
    assert blank_parser.model is True
    assert blank_parser.moves.n_moves != parser.moves.n_moves
    bytes_data = parser.to_bytes()
    blank_parser.from_bytes(bytes_data)
    assert blank_parser.model is not True
    assert blank_parser.moves.n_moves == parser.moves.n_moves
