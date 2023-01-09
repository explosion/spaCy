import pickle

import pytest
import srsly
from thinc.api import Linear

import spacy
from spacy import Vocab, load, registry
from spacy.lang.en import English
from spacy.language import Language
from spacy.pipeline import DependencyParser, EntityRecognizer, EntityRuler
from spacy.pipeline import SentenceRecognizer, Tagger, TextCategorizer
from spacy.pipeline import TrainablePipe
from spacy.pipeline.dep_parser import DEFAULT_PARSER_MODEL
from spacy.pipeline.senter import DEFAULT_SENTER_MODEL
from spacy.pipeline.tagger import DEFAULT_TAGGER_MODEL
from spacy.pipeline.textcat import DEFAULT_SINGLE_TEXTCAT_MODEL
from spacy.util import ensure_path, load_model
from spacy.tokens import Span

from ..util import make_tempdir

test_parsers = [DependencyParser, EntityRecognizer]


@pytest.fixture
def parser(en_vocab):
    config = {
        "learn_tokens": False,
        "min_action_freq": 30,
        "update_with_oracle_cut_size": 100,
        "beam_width": 1,
        "beam_update_prob": 1.0,
        "beam_density": 0.0,
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
        "beam_width": 1,
        "beam_update_prob": 1.0,
        "beam_density": 0.0,
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


@pytest.mark.issue(3456)
def test_issue3456():
    # this crashed because of a padding error in layer.ops.unflatten in thinc
    nlp = English()
    tagger = nlp.add_pipe("tagger")
    tagger.add_label("A")
    nlp.initialize()
    list(nlp.pipe(["hi", ""]))


@pytest.mark.issue(3526)
def test_issue_3526_1(en_vocab):
    patterns = [
        {"label": "HELLO", "pattern": "hello world"},
        {"label": "BYE", "pattern": [{"LOWER": "bye"}, {"LOWER": "bye"}]},
        {"label": "HELLO", "pattern": [{"ORTH": "HELLO"}]},
        {"label": "COMPLEX", "pattern": [{"ORTH": "foo", "OP": "*"}]},
        {"label": "TECH_ORG", "pattern": "Apple", "id": "a1"},
    ]
    nlp = Language(vocab=en_vocab)
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    ruler_bytes = ruler.to_bytes()
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    assert ruler.overwrite
    new_ruler = EntityRuler(nlp)
    new_ruler = new_ruler.from_bytes(ruler_bytes)
    assert len(new_ruler) == len(ruler)
    assert len(new_ruler.labels) == 4
    assert new_ruler.overwrite == ruler.overwrite
    assert new_ruler.ent_id_sep == ruler.ent_id_sep


@pytest.mark.issue(3526)
def test_issue_3526_2(en_vocab):
    patterns = [
        {"label": "HELLO", "pattern": "hello world"},
        {"label": "BYE", "pattern": [{"LOWER": "bye"}, {"LOWER": "bye"}]},
        {"label": "HELLO", "pattern": [{"ORTH": "HELLO"}]},
        {"label": "COMPLEX", "pattern": [{"ORTH": "foo", "OP": "*"}]},
        {"label": "TECH_ORG", "pattern": "Apple", "id": "a1"},
    ]
    nlp = Language(vocab=en_vocab)
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    bytes_old_style = srsly.msgpack_dumps(ruler.patterns)
    new_ruler = EntityRuler(nlp)
    new_ruler = new_ruler.from_bytes(bytes_old_style)
    assert len(new_ruler) == len(ruler)
    for pattern in ruler.patterns:
        assert pattern in new_ruler.patterns
    assert new_ruler.overwrite is not ruler.overwrite


@pytest.mark.issue(3526)
def test_issue_3526_3(en_vocab):
    patterns = [
        {"label": "HELLO", "pattern": "hello world"},
        {"label": "BYE", "pattern": [{"LOWER": "bye"}, {"LOWER": "bye"}]},
        {"label": "HELLO", "pattern": [{"ORTH": "HELLO"}]},
        {"label": "COMPLEX", "pattern": [{"ORTH": "foo", "OP": "*"}]},
        {"label": "TECH_ORG", "pattern": "Apple", "id": "a1"},
    ]
    nlp = Language(vocab=en_vocab)
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    with make_tempdir() as tmpdir:
        out_file = tmpdir / "entity_ruler"
        srsly.write_jsonl(out_file.with_suffix(".jsonl"), ruler.patterns)
        new_ruler = EntityRuler(nlp).from_disk(out_file)
        for pattern in ruler.patterns:
            assert pattern in new_ruler.patterns
        assert len(new_ruler) == len(ruler)
        assert new_ruler.overwrite is not ruler.overwrite


@pytest.mark.issue(3526)
def test_issue_3526_4(en_vocab):
    nlp = Language(vocab=en_vocab)
    patterns = [{"label": "ORG", "pattern": "Apple"}]
    config = {"overwrite_ents": True}
    ruler = nlp.add_pipe("entity_ruler", config=config)
    ruler.add_patterns(patterns)
    with make_tempdir() as tmpdir:
        nlp.to_disk(tmpdir)
        ruler = nlp.get_pipe("entity_ruler")
        assert ruler.patterns == [{"label": "ORG", "pattern": "Apple"}]
        assert ruler.overwrite is True
        nlp2 = load(tmpdir)
        new_ruler = nlp2.get_pipe("entity_ruler")
        assert new_ruler.patterns == [{"label": "ORG", "pattern": "Apple"}]
        assert new_ruler.overwrite is True


@pytest.mark.issue(4042)
def test_issue4042():
    """Test that serialization of an EntityRuler before NER works fine."""
    nlp = English()
    # add ner pipe
    ner = nlp.add_pipe("ner")
    ner.add_label("SOME_LABEL")
    nlp.initialize()
    # Add entity ruler
    patterns = [
        {"label": "MY_ORG", "pattern": "Apple"},
        {"label": "MY_GPE", "pattern": [{"lower": "san"}, {"lower": "francisco"}]},
    ]
    # works fine with "after"
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    ruler.add_patterns(patterns)
    doc1 = nlp("What do you think about Apple ?")
    assert doc1.ents[0].label_ == "MY_ORG"

    with make_tempdir() as d:
        output_dir = ensure_path(d)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        nlp2 = load_model(output_dir)
        doc2 = nlp2("What do you think about Apple ?")
        assert doc2.ents[0].label_ == "MY_ORG"


@pytest.mark.issue(4042)
def test_issue4042_bug2():
    """
    Test that serialization of an NER works fine when new labels were added.
    This is the second bug of two bugs underlying the issue 4042.
    """
    nlp1 = English()
    # add ner pipe
    ner1 = nlp1.add_pipe("ner")
    ner1.add_label("SOME_LABEL")
    nlp1.initialize()
    # add a new label to the doc
    doc1 = nlp1("What do you think about Apple ?")
    assert len(ner1.labels) == 1
    assert "SOME_LABEL" in ner1.labels
    apple_ent = Span(doc1, 5, 6, label="MY_ORG")
    doc1.ents = list(doc1.ents) + [apple_ent]
    # Add the label explicitly. Previously we didn't require this.
    ner1.add_label("MY_ORG")
    ner1(doc1)
    assert len(ner1.labels) == 2
    assert "SOME_LABEL" in ner1.labels
    assert "MY_ORG" in ner1.labels
    with make_tempdir() as d:
        # assert IO goes fine
        output_dir = ensure_path(d)
        if not output_dir.exists():
            output_dir.mkdir()
        ner1.to_disk(output_dir)
        config = {}
        ner2 = nlp1.create_pipe("ner", config=config)
        ner2.from_disk(output_dir)
        assert len(ner2.labels) == 2


@pytest.mark.issue(4725)
def test_issue4725_1():
    """Ensure the pickling of the NER goes well"""
    vocab = Vocab(vectors_name="test_vocab_add_vector")
    nlp = English(vocab=vocab)
    config = {
        "update_with_oracle_cut_size": 111,
    }
    ner = nlp.create_pipe("ner", config=config)
    with make_tempdir() as tmp_path:
        with (tmp_path / "ner.pkl").open("wb") as file_:
            pickle.dump(ner, file_)
            assert ner.cfg["update_with_oracle_cut_size"] == 111

        with (tmp_path / "ner.pkl").open("rb") as file_:
            ner2 = pickle.load(file_)
            assert ner2.cfg["update_with_oracle_cut_size"] == 111


@pytest.mark.parametrize("Parser", test_parsers)
def test_serialize_parser_roundtrip_bytes(en_vocab, Parser):
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    parser = Parser(en_vocab, model)
    new_parser = Parser(en_vocab, model)
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
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    parser1 = Parser(vocab1, model)
    parser1.add_label(label)
    assert label in parser1.vocab.strings
    vocab2 = Vocab()
    assert label not in vocab2.strings
    parser2 = Parser(vocab2, model)
    parser2 = parser2.from_bytes(parser1.to_bytes(exclude=["vocab"]))
    assert label in parser2.vocab.strings


@pytest.mark.parametrize("Parser", test_parsers)
def test_serialize_parser_roundtrip_disk(en_vocab, Parser):
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    parser = Parser(en_vocab, model)
    with make_tempdir() as d:
        file_path = d / "parser"
        parser.to_disk(file_path)
        parser_d = Parser(en_vocab, model)
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


@pytest.mark.issue(1105)
def test_serialize_textcat_empty(en_vocab):
    # See issue #1105
    cfg = {"model": DEFAULT_SINGLE_TEXTCAT_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    textcat = TextCategorizer(en_vocab, model, threshold=0.5)
    textcat.to_bytes(exclude=["vocab"])


@pytest.mark.parametrize("Parser", test_parsers)
def test_serialize_pipe_exclude(en_vocab, Parser):
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]

    def get_new_parser():
        new_parser = Parser(en_vocab, model)
        return new_parser

    parser = Parser(en_vocab, model)
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


def test_load_without_strings():
    nlp = spacy.blank("en")
    orig_strings_length = len(nlp.vocab.strings)
    word = "unlikely_word_" * 20
    nlp.vocab.strings.add(word)
    assert len(nlp.vocab.strings) == orig_strings_length + 1
    with make_tempdir() as d:
        nlp.to_disk(d)
        # reload with strings
        reloaded_nlp = load(d)
        assert len(nlp.vocab.strings) == len(reloaded_nlp.vocab.strings)
        assert word in reloaded_nlp.vocab.strings
        # reload without strings
        reloaded_nlp = load(d, exclude=["strings"])
        assert orig_strings_length == len(reloaded_nlp.vocab.strings)
        assert word not in reloaded_nlp.vocab.strings
