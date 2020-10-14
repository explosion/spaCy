import pytest
from spacy import registry, Vocab
from spacy.pipeline import Tagger, DependencyParser, EntityRecognizer
from spacy.pipeline import TextCategorizer, SentenceRecognizer, TrainablePipe
from spacy.pipeline.dep_parser import DEFAULT_PARSER_MODEL
from spacy.pipeline.tagger import DEFAULT_TAGGER_MODEL
from spacy.pipeline.textcat import DEFAULT_TEXTCAT_MODEL
from spacy.pipeline.senter import DEFAULT_SENTER_MODEL
from spacy.lang.en import English
from thinc.api import Linear
import spacy

from ..util import make_tempdir


test_parsers = [DependencyParser, EntityRecognizer]


@pytest.fixture
def parser(en_vocab):
    config = {
        "learn_tokens": False,
        "min_action_freq": 30,
        "update_with_oracle_cut_size": 100,
    }
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    parser = DependencyParser(en_vocab, model, **config)
    parser.add_label("nsubj")
    return parser


@pytest.fixture
def blank_parser(en_vocab):
    config = {
        "learn_tokens": False,
        "min_action_freq": 30,
        "update_with_oracle_cut_size": 100,
    }
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    parser = DependencyParser(en_vocab, model, **config)
    return parser


@pytest.fixture
def taggers(en_vocab):
    cfg = {"model": DEFAULT_TAGGER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    tagger1 = Tagger(en_vocab, model)
    tagger2 = Tagger(en_vocab, model)
    return tagger1, tagger2


@pytest.mark.parametrize("Parser", test_parsers)
def test_serialize_parser_roundtrip_bytes(en_vocab, Parser):
    config = {
        "learn_tokens": False,
        "min_action_freq": 0,
        "update_with_oracle_cut_size": 100,
    }
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    parser = Parser(en_vocab, model, **config)
    new_parser = Parser(en_vocab, model, **config)
    new_parser = new_parser.from_bytes(parser.to_bytes(exclude=["vocab"]))
    bytes_2 = new_parser.to_bytes(exclude=["vocab"])
    bytes_3 = parser.to_bytes(exclude=["vocab"])
    assert len(bytes_2) == len(bytes_3)
    assert bytes_2 == bytes_3


@pytest.mark.parametrize("Parser", test_parsers)
def test_serialize_parser_strings(Parser):
    vocab1 = Vocab()
    label = "FunnyLabel"
    assert label not in vocab1.strings
    config = {
        "learn_tokens": False,
        "min_action_freq": 0,
        "update_with_oracle_cut_size": 100,
    }
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    parser1 = Parser(vocab1, model, **config)
    parser1.add_label(label)
    assert label in parser1.vocab.strings
    vocab2 = Vocab()
    assert label not in vocab2.strings
    parser2 = Parser(vocab2, model, **config)
    parser2 = parser2.from_bytes(parser1.to_bytes(exclude=["vocab"]))
    assert label in parser2.vocab.strings


@pytest.mark.parametrize("Parser", test_parsers)
def test_serialize_parser_roundtrip_disk(en_vocab, Parser):
    config = {
        "learn_tokens": False,
        "min_action_freq": 0,
        "update_with_oracle_cut_size": 100,
    }
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    parser = Parser(en_vocab, model, **config)
    with make_tempdir() as d:
        file_path = d / "parser"
        parser.to_disk(file_path)
        parser_d = Parser(en_vocab, model, **config)
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
    cfg = {"model": DEFAULT_TAGGER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    new_tagger1 = Tagger(en_vocab, model).from_bytes(tagger1_b)
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
        cfg = {"model": DEFAULT_TAGGER_MODEL}
        model = registry.resolve(cfg, validate=True)["model"]
        tagger1_d = Tagger(en_vocab, model).from_disk(file_path1)
        tagger2_d = Tagger(en_vocab, model).from_disk(file_path2)
        assert tagger1_d.to_bytes() == tagger2_d.to_bytes()


def test_serialize_tagger_strings(en_vocab, de_vocab, taggers):
    label = "SomeWeirdLabel"
    assert label not in en_vocab.strings
    assert label not in de_vocab.strings
    tagger = taggers[0]
    assert label not in tagger.vocab.strings
    with make_tempdir() as d:
        # check that custom labels are serialized as part of the component's strings.jsonl
        tagger.add_label(label)
        assert label in tagger.vocab.strings
        file_path = d / "tagger1"
        tagger.to_disk(file_path)
        # ensure that the custom strings are loaded back in when using the tagger in another pipeline
        cfg = {"model": DEFAULT_TAGGER_MODEL}
        model = registry.resolve(cfg, validate=True)["model"]
        tagger2 = Tagger(de_vocab, model).from_disk(file_path)
        assert label in tagger2.vocab.strings


def test_serialize_textcat_empty(en_vocab):
    # See issue #1105
    cfg = {"model": DEFAULT_TEXTCAT_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    textcat = TextCategorizer(en_vocab, model, threshold=0.5)
    textcat.to_bytes(exclude=["vocab"])


@pytest.mark.parametrize("Parser", test_parsers)
def test_serialize_pipe_exclude(en_vocab, Parser):
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    config = {
        "learn_tokens": False,
        "min_action_freq": 0,
        "update_with_oracle_cut_size": 100,
    }

    def get_new_parser():
        new_parser = Parser(en_vocab, model, **config)
        return new_parser

    parser = Parser(en_vocab, model, **config)
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
    cfg = {"model": DEFAULT_SENTER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    sr = SentenceRecognizer(en_vocab, model)
    sr_b = sr.to_bytes()
    sr_d = SentenceRecognizer(en_vocab, model).from_bytes(sr_b)
    assert sr.to_bytes() == sr_d.to_bytes()


def test_serialize_pipeline_disable_enable():
    nlp = English()
    nlp.add_pipe("ner")
    nlp.add_pipe("tagger")
    nlp.disable_pipe("tagger")
    assert nlp.config["nlp"]["disabled"] == ["tagger"]
    config = nlp.config.copy()
    nlp2 = English.from_config(config)
    assert nlp2.pipe_names == ["ner"]
    assert nlp2.component_names == ["ner", "tagger"]
    assert nlp2.disabled == ["tagger"]
    assert nlp2.config["nlp"]["disabled"] == ["tagger"]
    with make_tempdir() as d:
        nlp2.to_disk(d)
        nlp3 = spacy.load(d)
    assert nlp3.pipe_names == ["ner"]
    assert nlp3.component_names == ["ner", "tagger"]
    with make_tempdir() as d:
        nlp3.to_disk(d)
        nlp4 = spacy.load(d, disable=["ner"])
    assert nlp4.pipe_names == []
    assert nlp4.component_names == ["ner", "tagger"]
    assert nlp4.disabled == ["ner", "tagger"]
    with make_tempdir() as d:
        nlp.to_disk(d)
        nlp5 = spacy.load(d, exclude=["tagger"])
    assert nlp5.pipe_names == ["ner"]
    assert nlp5.component_names == ["ner"]
    assert nlp5.disabled == []


def test_serialize_custom_trainable_pipe():
    class BadCustomPipe1(TrainablePipe):
        def __init__(self, vocab):
            pass

    class BadCustomPipe2(TrainablePipe):
        def __init__(self, vocab):
            self.vocab = vocab
            self.model = None

    class CustomPipe(TrainablePipe):
        def __init__(self, vocab, model):
            self.vocab = vocab
            self.model = model

    pipe = BadCustomPipe1(Vocab())
    with pytest.raises(ValueError):
        pipe.to_bytes()
    with make_tempdir() as d:
        with pytest.raises(ValueError):
            pipe.to_disk(d)
    pipe = BadCustomPipe2(Vocab())
    with pytest.raises(ValueError):
        pipe.to_bytes()
    with make_tempdir() as d:
        with pytest.raises(ValueError):
            pipe.to_disk(d)
    pipe = CustomPipe(Vocab(), Linear())
    pipe_bytes = pipe.to_bytes()
    new_pipe = CustomPipe(Vocab(), Linear()).from_bytes(pipe_bytes)
    assert new_pipe.to_bytes() == pipe_bytes
    with make_tempdir() as d:
        pipe.to_disk(d)
        new_pipe = CustomPipe(Vocab(), Linear()).from_disk(d)
    assert new_pipe.to_bytes() == pipe_bytes
