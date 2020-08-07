import pytest
from thinc.config import Config, ConfigValidationError
import spacy
from spacy.lang.en import English
from spacy.lang.de import German
from spacy.language import Language
from spacy.util import registry, deep_merge_configs, load_model_from_config
from spacy.ml.models import build_Tok2Vec_model, build_tb_parser_model
from spacy.ml.models import MultiHashEmbed, MaxoutWindowEncoder

from ..util import make_tempdir


nlp_config_string = """
[paths]
train = ""
dev = ""

[training]

[training.train_corpus]
@readers = "spacy.Corpus.v1"
path = ${paths:train}

[training.dev_corpus]
@readers = "spacy.Corpus.v1"
path = ${paths:dev}

[training.batcher]
@batchers = "batch_by_words.v1"
size = 666

[nlp]
lang = "en"
pipeline = ["tok2vec", "tagger"]

[components]

[components.tok2vec]
factory = "tok2vec"

[components.tok2vec.model]
@architectures = "spacy.HashEmbedCNN.v1"
pretrained_vectors = null
width = 342
depth = 4
window_size = 1
embed_size = 2000
maxout_pieces = 3
subword_features = true

[components.tagger]
factory = "tagger"

[components.tagger.model]
@architectures = "spacy.Tagger.v1"

[components.tagger.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model:width}
"""


parser_config_string = """
[model]
@architectures = "spacy.TransitionBasedParser.v1"
nr_feature_tokens = 99
hidden_width = 66
maxout_pieces = 2

[model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v1"
pretrained_vectors = null
width = 333
depth = 4
embed_size = 5555
window_size = 1
maxout_pieces = 7
subword_features = false
"""


@registry.architectures.register("my_test_parser")
def my_parser():
    tok2vec = build_Tok2Vec_model(
        MultiHashEmbed(
            width=321,
            rows=5432,
            also_embed_subwords=True,
            also_use_static_vectors=False,
        ),
        MaxoutWindowEncoder(width=321, window_size=3, maxout_pieces=4, depth=2),
    )
    parser = build_tb_parser_model(
        tok2vec=tok2vec, nr_feature_tokens=7, hidden_width=65, maxout_pieces=5
    )
    return parser


def test_create_nlp_from_config():
    config = Config().from_str(nlp_config_string)
    with pytest.raises(ConfigValidationError):
        nlp, _ = load_model_from_config(config, auto_fill=False)
    nlp, resolved = load_model_from_config(config, auto_fill=True)
    assert nlp.config["training"]["batcher"]["size"] == 666
    assert len(nlp.config["training"]) > 1
    assert nlp.pipe_names == ["tok2vec", "tagger"]
    assert len(nlp.config["components"]) == 2
    assert len(nlp.config["nlp"]["pipeline"]) == 2
    nlp.remove_pipe("tagger")
    assert len(nlp.config["components"]) == 1
    assert len(nlp.config["nlp"]["pipeline"]) == 1
    with pytest.raises(ValueError):
        bad_cfg = {"yolo": {}}
        load_model_from_config(Config(bad_cfg), auto_fill=True)
    with pytest.raises(ValueError):
        bad_cfg = {"pipeline": {"foo": "bar"}}
        load_model_from_config(Config(bad_cfg), auto_fill=True)


def test_create_nlp_from_config_multiple_instances():
    """Test that the nlp object is created correctly for a config with multiple
    instances of the same component."""
    config = Config().from_str(nlp_config_string)
    config["components"] = {
        "t2v": config["components"]["tok2vec"],
        "tagger1": config["components"]["tagger"],
        "tagger2": config["components"]["tagger"],
    }
    config["nlp"]["pipeline"] = list(config["components"].keys())
    nlp, _ = load_model_from_config(config, auto_fill=True)
    assert nlp.pipe_names == ["t2v", "tagger1", "tagger2"]
    assert nlp.get_pipe_meta("t2v").factory == "tok2vec"
    assert nlp.get_pipe_meta("tagger1").factory == "tagger"
    assert nlp.get_pipe_meta("tagger2").factory == "tagger"
    pipeline_config = nlp.config["components"]
    assert len(pipeline_config) == 3
    assert list(pipeline_config.keys()) == ["t2v", "tagger1", "tagger2"]
    assert nlp.config["nlp"]["pipeline"] == ["t2v", "tagger1", "tagger2"]


def test_serialize_nlp():
    """ Create a custom nlp pipeline from config and ensure it serializes it correctly """
    nlp_config = Config().from_str(nlp_config_string)
    nlp, _ = load_model_from_config(nlp_config, auto_fill=True)
    nlp.begin_training()
    assert "tok2vec" in nlp.pipe_names
    assert "tagger" in nlp.pipe_names
    assert "parser" not in nlp.pipe_names
    assert nlp.get_pipe("tagger").model.get_ref("tok2vec").get_dim("nO") == 342

    with make_tempdir() as d:
        nlp.to_disk(d)
        nlp2 = spacy.load(d)
        assert "tok2vec" in nlp2.pipe_names
        assert "tagger" in nlp2.pipe_names
        assert "parser" not in nlp2.pipe_names
        assert nlp2.get_pipe("tagger").model.get_ref("tok2vec").get_dim("nO") == 342


def test_serialize_custom_nlp():
    """ Create a custom nlp pipeline and ensure it serializes it correctly"""
    nlp = English()
    parser_cfg = dict()
    parser_cfg["model"] = {"@architectures": "my_test_parser"}
    nlp.add_pipe("parser", config=parser_cfg)
    nlp.begin_training()

    with make_tempdir() as d:
        nlp.to_disk(d)
        nlp2 = spacy.load(d)
        model = nlp2.get_pipe("parser").model
        model.get_ref("tok2vec")
        upper = model.get_ref("upper")
        # check that we have the correct settings, not the default ones
        assert upper.get_dim("nI") == 65


def test_serialize_parser():
    """ Create a non-default parser config to check nlp serializes it correctly """
    nlp = English()
    model_config = Config().from_str(parser_config_string)
    parser = nlp.add_pipe("parser", config=model_config)
    parser.add_label("nsubj")
    nlp.begin_training()

    with make_tempdir() as d:
        nlp.to_disk(d)
        nlp2 = spacy.load(d)
        model = nlp2.get_pipe("parser").model
        model.get_ref("tok2vec")
        upper = model.get_ref("upper")
        # check that we have the correct settings, not the default ones
        assert upper.get_dim("nI") == 66


def test_deep_merge_configs():
    config = {"a": "hello", "b": {"c": "d"}}
    defaults = {"a": "world", "b": {"c": "e", "f": "g"}}
    merged = deep_merge_configs(config, defaults)
    assert len(merged) == 2
    assert merged["a"] == "hello"
    assert merged["b"] == {"c": "d", "f": "g"}
    config = {"a": "hello", "b": {"@test": "x", "foo": 1}}
    defaults = {"a": "world", "b": {"@test": "x", "foo": 100, "bar": 2}, "c": 100}
    merged = deep_merge_configs(config, defaults)
    assert len(merged) == 3
    assert merged["a"] == "hello"
    assert merged["b"] == {"@test": "x", "foo": 1, "bar": 2}
    assert merged["c"] == 100
    config = {"a": "hello", "b": {"@test": "x", "foo": 1}, "c": 100}
    defaults = {"a": "world", "b": {"@test": "y", "foo": 100, "bar": 2}}
    merged = deep_merge_configs(config, defaults)
    assert len(merged) == 3
    assert merged["a"] == "hello"
    assert merged["b"] == {"@test": "x", "foo": 1}
    assert merged["c"] == 100
    # Test that leaving out the factory just adds to existing
    config = {"a": "hello", "b": {"foo": 1}, "c": 100}
    defaults = {"a": "world", "b": {"@test": "y", "foo": 100, "bar": 2}}
    merged = deep_merge_configs(config, defaults)
    assert len(merged) == 3
    assert merged["a"] == "hello"
    assert merged["b"] == {"@test": "y", "foo": 1, "bar": 2}
    assert merged["c"] == 100


def test_config_nlp_roundtrip():
    """Test that a config prduced by the nlp object passes training config
    validation."""
    nlp = English()
    nlp.add_pipe("entity_ruler")
    nlp.add_pipe("ner")
    new_nlp, new_config = load_model_from_config(nlp.config, auto_fill=False)
    assert new_nlp.config == nlp.config
    assert new_nlp.pipe_names == nlp.pipe_names
    assert new_nlp._pipe_configs == nlp._pipe_configs
    assert new_nlp._pipe_meta == nlp._pipe_meta
    assert new_nlp._factory_meta == nlp._factory_meta


def test_serialize_config_language_specific():
    """Test that config serialization works as expected with language-specific
    factories."""
    name = "test_serialize_config_language_specific"

    @English.factory(name, default_config={"foo": 20})
    def custom_factory(nlp: Language, name: str, foo: int):
        return lambda doc: doc

    nlp = Language()
    assert not nlp.has_factory(name)
    nlp = English()
    assert nlp.has_factory(name)
    nlp.add_pipe(name, config={"foo": 100}, name="bar")
    pipe_config = nlp.config["components"]["bar"]
    assert pipe_config["foo"] == 100
    assert pipe_config["factory"] == name

    with make_tempdir() as d:
        nlp.to_disk(d)
        nlp2 = spacy.load(d)
    assert nlp2.has_factory(name)
    assert nlp2.pipe_names == ["bar"]
    assert nlp2.get_pipe_meta("bar").factory == name
    pipe_config = nlp2.config["components"]["bar"]
    assert pipe_config["foo"] == 100
    assert pipe_config["factory"] == name

    config = Config().from_str(nlp2.config.to_str())
    config["nlp"]["lang"] = "de"
    with pytest.raises(ValueError):
        # German doesn't have a factory, only English does
        load_model_from_config(config)


def test_serialize_config_missing_pipes():
    config = Config().from_str(nlp_config_string)
    config["components"].pop("tok2vec")
    assert "tok2vec" in config["nlp"]["pipeline"]
    assert "tok2vec" not in config["components"]
    with pytest.raises(ValueError):
        load_model_from_config(config, auto_fill=True)


def test_config_overrides():
    overrides_nested = {"nlp": {"lang": "de", "pipeline": ["tagger"]}}
    overrides_dot = {"nlp.lang": "de", "nlp.pipeline": ["tagger"]}
    # load_model from config with overrides passed directly to Config
    config = Config().from_str(nlp_config_string, overrides=overrides_dot)
    nlp, _ = load_model_from_config(config, auto_fill=True)
    assert isinstance(nlp, German)
    assert nlp.pipe_names == ["tagger"]
    # Serialized roundtrip with config passed in
    base_config = Config().from_str(nlp_config_string)
    base_nlp, _ = load_model_from_config(base_config, auto_fill=True)
    assert isinstance(base_nlp, English)
    assert base_nlp.pipe_names == ["tok2vec", "tagger"]
    with make_tempdir() as d:
        base_nlp.to_disk(d)
        nlp = spacy.load(d, config=overrides_nested)
    assert isinstance(nlp, German)
    assert nlp.pipe_names == ["tagger"]
    with make_tempdir() as d:
        base_nlp.to_disk(d)
        nlp = spacy.load(d, config=overrides_dot)
    assert isinstance(nlp, German)
    assert nlp.pipe_names == ["tagger"]
    with make_tempdir() as d:
        base_nlp.to_disk(d)
        nlp = spacy.load(d)
    assert isinstance(nlp, English)
    assert nlp.pipe_names == ["tok2vec", "tagger"]
