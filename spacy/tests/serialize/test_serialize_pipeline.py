import pytest
from spacy.pipeline import Tagger, DependencyParser, EntityRecognizer
from spacy.pipeline import TextCategorizer, SentenceRecognizer
from spacy.pipeline.defaults import default_parser, default_tagger
from spacy.pipeline.defaults import default_textcat, default_senter

from ..util import make_tempdir


test_parsers = [DependencyParser, EntityRecognizer]


@pytest.fixture
def parser(en_vocab):
    config = {
        "learn_tokens": False,
        "min_action_freq": 30,
        "beam_width": 1,
        "beam_update_prob": 1.0,
    }
    parser = DependencyParser(en_vocab, default_parser(), **config)
    parser.add_label("nsubj")
    return parser


@pytest.fixture
def blank_parser(en_vocab):
    parser = DependencyParser(en_vocab, default_parser())
    return parser


@pytest.fixture
def taggers(en_vocab):
    model = default_tagger()
    tagger1 = Tagger(en_vocab, model)
    tagger2 = Tagger(en_vocab, model)
    return tagger1, tagger2


@pytest.mark.parametrize("Parser", test_parsers)
def test_serialize_parser_roundtrip_bytes(en_vocab, Parser):
    parser = Parser(en_vocab, default_parser())
    new_parser = Parser(en_vocab, default_parser())
    new_parser = new_parser.from_bytes(parser.to_bytes(exclude=["vocab"]))
    bytes_2 = new_parser.to_bytes(exclude=["vocab"])
    bytes_3 = parser.to_bytes(exclude=["vocab"])
    assert len(bytes_2) == len(bytes_3)
    assert bytes_2 == bytes_3


@pytest.mark.parametrize("Parser", test_parsers)
def test_serialize_parser_roundtrip_disk(en_vocab, Parser):
    parser = Parser(en_vocab, default_parser())
    with make_tempdir() as d:
        file_path = d / "parser"
        parser.to_disk(file_path)
        parser_d = Parser(en_vocab, default_parser())
        parser_d = parser_d.from_disk(file_path)
        parser_bytes = parser.to_bytes(exclude=["model", "vocab"])
        parser_d_bytes = parser_d.to_bytes(exclude=["model", "vocab"])
        assert len(parser_bytes) == len(parser_d_bytes)
        assert parser_bytes == parser_d_bytes


def test_to_from_bytes(parser, blank_parser):
    assert parser.model is not True
    assert blank_parser.model is not True
    assert blank_parser.moves.n_moves != parser.moves.n_moves
    bytes_data = parser.to_bytes(exclude=["vocab"])

    # the blank parser needs to be resized before we can call from_bytes
    blank_parser.model.attrs["resize_output"](blank_parser.model, parser.moves.n_moves)
    blank_parser.from_bytes(bytes_data)
    assert blank_parser.model is not True
    assert blank_parser.moves.n_moves == parser.moves.n_moves


@pytest.mark.skip(
    reason="This seems to be a dict ordering bug somewhere. Only failing on some platforms."
)
def test_serialize_tagger_roundtrip_bytes(en_vocab, taggers):
    tagger1 = taggers[0]
    tagger1_b = tagger1.to_bytes()
    tagger1 = tagger1.from_bytes(tagger1_b)
    assert tagger1.to_bytes() == tagger1_b
    new_tagger1 = Tagger(en_vocab, default_tagger()).from_bytes(tagger1_b)
    new_tagger1_b = new_tagger1.to_bytes()
    assert len(new_tagger1_b) == len(tagger1_b)
    assert new_tagger1_b == tagger1_b


def test_serialize_tagger_roundtrip_disk(en_vocab, taggers):
    tagger1, tagger2 = taggers
    with make_tempdir() as d:
        file_path1 = d / "tagger1"
        file_path2 = d / "tagger2"
        tagger1.to_disk(file_path1)
        tagger2.to_disk(file_path2)
        tagger1_d = Tagger(en_vocab, default_tagger()).from_disk(file_path1)
        tagger2_d = Tagger(en_vocab, default_tagger()).from_disk(file_path2)
        assert tagger1_d.to_bytes() == tagger2_d.to_bytes()


def test_serialize_textcat_empty(en_vocab):
    # See issue #1105
    textcat = TextCategorizer(
        en_vocab, default_textcat(), labels=["ENTITY", "ACTION", "MODIFIER"]
    )
    textcat.to_bytes(exclude=["vocab"])


@pytest.mark.parametrize("Parser", test_parsers)
def test_serialize_pipe_exclude(en_vocab, Parser):
    def get_new_parser():
        new_parser = Parser(en_vocab, default_parser())
        return new_parser

    parser = Parser(en_vocab, default_parser())
    parser.cfg["foo"] = "bar"
    new_parser = get_new_parser().from_bytes(parser.to_bytes(exclude=["vocab"]))
    assert "foo" in new_parser.cfg
    new_parser = get_new_parser().from_bytes(
        parser.to_bytes(exclude=["vocab"]), exclude=["cfg"]
    )
    assert "foo" not in new_parser.cfg
    new_parser = get_new_parser().from_bytes(
        parser.to_bytes(exclude=["cfg"]), exclude=["vocab"]
    )
    assert "foo" not in new_parser.cfg


def test_serialize_sentencerecognizer(en_vocab):
    sr = SentenceRecognizer(en_vocab, default_senter())
    sr_b = sr.to_bytes()
    sr_d = SentenceRecognizer(en_vocab, default_senter()).from_bytes(sr_b)
    assert sr.to_bytes() == sr_d.to_bytes()
