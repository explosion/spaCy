import pytest
from catalogue import RegistryError
from thinc.api import Config, ConfigValidationError

import spacy
from spacy.lang.de import German
from spacy.lang.en import English
from spacy.language import DEFAULT_CONFIG, DEFAULT_CONFIG_PRETRAIN_PATH
from spacy.language import Language
from spacy.ml.models import MaxoutWindowEncoder, MultiHashEmbed
from spacy.ml.models import build_tb_parser_model, build_Tok2Vec_model
from spacy.schemas import ConfigSchema, ConfigSchemaPretrain
from spacy.util import load_config, load_config_from_str
from spacy.util import load_model_from_config, registry

from ..util import make_tempdir

nlp_config_string = """
[paths]
train = null
dev = null

[corpora]

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths.train}

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths.dev}

[training]

[training.batcher]
@batchers = "spacy.batch_by_words.v1"
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
@architectures = "spacy.Tagger.v2"

[components.tagger.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model.width}
"""

pretrain_config_string = """
[paths]
train = null
dev = null

[corpora]

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths.train}

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths.dev}

[training]

[training.batcher]
@batchers = "spacy.batch_by_words.v1"
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
@architectures = "spacy.Tagger.v2"

[components.tagger.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model.width}

[pretraining]
"""


parser_config_string_upper = """
[model]
@architectures = "spacy.TransitionBasedParser.v2"
state_type = "parser"
extra_state_tokens = false
hidden_width = 66
maxout_pieces = 2
use_upper = true

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


parser_config_string_no_upper = """
[model]
@architectures = "spacy.TransitionBasedParser.v2"
state_type = "parser"
extra_state_tokens = false
hidden_width = 66
maxout_pieces = 2
use_upper = false

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


@registry.architectures("my_test_parser")
def my_parser():
    tok2vec = build_Tok2Vec_model(
        MultiHashEmbed(
            width=321,
            attrs=["LOWER", "SHAPE"],
            rows=[5432, 5432],
            include_static_vectors=False,
        ),
        MaxoutWindowEncoder(width=321, window_size=3, maxout_pieces=4, depth=2),
    )
    parser = build_tb_parser_model(
        tok2vec=tok2vec,
        state_type="parser",
        extra_state_tokens=True,
        hidden_width=65,
        maxout_pieces=5,
        use_upper=True,
    )
    return parser


@pytest.mark.issue(8190)
def test_issue8190():
    """Test that config overrides are not lost after load is complete."""
    source_cfg = {
        "nlp": {
            "lang": "en",
        },
        "custom": {"key": "value"},
    }
    source_nlp = English.from_config(source_cfg)
    with make_tempdir() as dir_path:
        # We need to create a loadable source pipeline
        source_path = dir_path / "test_model"
        source_nlp.to_disk(source_path)
        nlp = spacy.load(source_path, config={"custom": {"key": "updated_value"}})

        assert nlp.config["custom"]["key"] == "updated_value"


def test_create_nlp_from_config():
    config = Config().from_str(nlp_config_string)
    with pytest.raises(ConfigValidationError):
        load_model_from_config(config, auto_fill=False)
    nlp = load_model_from_config(config, auto_fill=True)
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


def test_create_nlp_from_pretraining_config():
    """Test that the default pretraining config validates properly"""
    config = Config().from_str(pretrain_config_string)
    pretrain_config = load_config(DEFAULT_CONFIG_PRETRAIN_PATH)
    filled = config.merge(pretrain_config)
    registry.resolve(filled["pretraining"], schema=ConfigSchemaPretrain)


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
    nlp = load_model_from_config(config, auto_fill=True)
    assert nlp.pipe_names == ["t2v", "tagger1", "tagger2"]
    assert nlp.get_pipe_meta("t2v").factory == "tok2vec"
    assert nlp.get_pipe_meta("tagger1").factory == "tagger"
    assert nlp.get_pipe_meta("tagger2").factory == "tagger"
    pipeline_config = nlp.config["components"]
    assert len(pipeline_config) == 3
    assert list(pipeline_config.keys()) == ["t2v", "tagger1", "tagger2"]
    assert nlp.config["nlp"]["pipeline"] == ["t2v", "tagger1", "tagger2"]


def test_serialize_nlp():
    """Create a custom nlp pipeline from config and ensure it serializes it correctly"""
    nlp_config = Config().from_str(nlp_config_string)
    nlp = load_model_from_config(nlp_config, auto_fill=True)
    nlp.get_pipe("tagger").add_label("A")
    nlp.initialize()
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
    """Create a custom nlp pipeline and ensure it serializes it correctly"""
    nlp = English()
    parser_cfg = dict()
    parser_cfg["model"] = {"@architectures": "my_test_parser"}
    nlp.add_pipe("parser", config=parser_cfg)
    nlp.initialize()

    with make_tempdir() as d:
        nlp.to_disk(d)
        nlp2 = spacy.load(d)
        model = nlp2.get_pipe("parser").model
        model.get_ref("tok2vec")
        # check that we have the correct settings, not the default ones
        assert model.get_ref("upper").get_dim("nI") == 65
        assert model.get_ref("lower").get_dim("nI") == 65


@pytest.mark.parametrize(
    "parser_config_string", [parser_config_string_upper, parser_config_string_no_upper]
)
def test_serialize_parser(parser_config_string):
    """Create a non-default parser config to check nlp serializes it correctly"""
    nlp = English()
    model_config = Config().from_str(parser_config_string)
    parser = nlp.add_pipe("parser", config=model_config)
    parser.add_label("nsubj")
    nlp.initialize()

    with make_tempdir() as d:
        nlp.to_disk(d)
        nlp2 = spacy.load(d)
        model = nlp2.get_pipe("parser").model
        model.get_ref("tok2vec")
        # check that we have the correct settings, not the default ones
        if model.attrs["has_upper"]:
            assert model.get_ref("upper").get_dim("nI") == 66
        assert model.get_ref("lower").get_dim("nI") == 66


def test_config_nlp_roundtrip():
    """Test that a config produced by the nlp object passes training config
    validation."""
    nlp = English()
    nlp.add_pipe("entity_ruler")
    nlp.add_pipe("ner")
    new_nlp = load_model_from_config(nlp.config, auto_fill=False)
    assert new_nlp.config == nlp.config
    assert new_nlp.pipe_names == nlp.pipe_names
    assert new_nlp._pipe_configs == nlp._pipe_configs
    assert new_nlp._pipe_meta == nlp._pipe_meta
    assert new_nlp._factory_meta == nlp._factory_meta


def test_config_nlp_roundtrip_bytes_disk():
    """Test that the config is serialized correctly and not interpolated
    by mistake."""
    nlp = English()
    nlp_bytes = nlp.to_bytes()
    new_nlp = English().from_bytes(nlp_bytes)
    assert new_nlp.config == nlp.config
    nlp = English()
    with make_tempdir() as d:
        nlp.to_disk(d)
        new_nlp = spacy.load(d)
    assert new_nlp.config == nlp.config


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
    nlp = load_model_from_config(config, auto_fill=True)
    assert isinstance(nlp, German)
    assert nlp.pipe_names == ["tagger"]
    # Serialized roundtrip with config passed in
    base_config = Config().from_str(nlp_config_string)
    base_nlp = load_model_from_config(base_config, auto_fill=True)
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


def test_config_interpolation():
    config = Config().from_str(nlp_config_string, interpolate=False)
    assert config["corpora"]["train"]["path"] == "${paths.train}"
    interpolated = config.interpolate()
    assert interpolated["corpora"]["train"]["path"] is None
    nlp = English.from_config(config)
    assert nlp.config["corpora"]["train"]["path"] == "${paths.train}"
    # Ensure that variables are preserved in nlp config
    width = "${components.tok2vec.model.width}"
    assert config["components"]["tagger"]["model"]["tok2vec"]["width"] == width
    assert nlp.config["components"]["tagger"]["model"]["tok2vec"]["width"] == width
    interpolated2 = nlp.config.interpolate()
    assert interpolated2["corpora"]["train"]["path"] is None
    assert interpolated2["components"]["tagger"]["model"]["tok2vec"]["width"] == 342
    nlp2 = English.from_config(interpolated)
    assert nlp2.config["corpora"]["train"]["path"] is None
    assert nlp2.config["components"]["tagger"]["model"]["tok2vec"]["width"] == 342


def test_config_optional_sections():
    config = Config().from_str(nlp_config_string)
    config = DEFAULT_CONFIG.merge(config)
    assert "pretraining" not in config
    filled = registry.fill(config, schema=ConfigSchema, validate=False)
    # Make sure that optional "pretraining" block doesn't default to None,
    # which would (rightly) cause error because it'd result in a top-level
    # key that's not a section (dict). Note that the following roundtrip is
    # also how Config.interpolate works under the hood.
    new_config = Config().from_str(filled.to_str())
    assert new_config["pretraining"] == {}


def test_config_auto_fill_extra_fields():
    config = Config({"nlp": {"lang": "en"}, "training": {}})
    assert load_model_from_config(config, auto_fill=True)
    config = Config({"nlp": {"lang": "en"}, "training": {"extra": "hello"}})
    nlp = load_model_from_config(config, auto_fill=True, validate=False)
    assert "extra" not in nlp.config["training"]
    # Make sure the config generated is valid
    load_model_from_config(nlp.config)


@pytest.mark.parametrize(
    "parser_config_string", [parser_config_string_upper, parser_config_string_no_upper]
)
def test_config_validate_literal(parser_config_string):
    nlp = English()
    config = Config().from_str(parser_config_string)
    config["model"]["state_type"] = "nonsense"
    with pytest.raises(ConfigValidationError):
        nlp.add_pipe("parser", config=config)
    config["model"]["state_type"] = "ner"
    nlp.add_pipe("parser", config=config)


def test_config_only_resolve_relevant_blocks():
    """Test that only the relevant blocks are resolved in the different methods
    and that invalid blocks are ignored if needed. For instance, the [initialize]
    shouldn't be resolved at runtime.
    """
    nlp = English()
    config = nlp.config
    config["training"]["before_to_disk"] = {"@misc": "nonexistent"}
    config["initialize"]["lookups"] = {"@misc": "nonexistent"}
    # This shouldn't resolve [training] or [initialize]
    nlp = load_model_from_config(config, auto_fill=True)
    # This will raise for nonexistent value
    with pytest.raises(RegistryError):
        nlp.initialize()
    nlp.config["initialize"]["lookups"] = None
    nlp.initialize()


def test_hyphen_in_config():
    hyphen_config_str = """
    [nlp]
    lang = "en"
    pipeline = ["my_punctual_component"]

    [components]

    [components.my_punctual_component]
    factory = "my_punctual_component"
    punctuation = ["?","-"]
    """

    @spacy.Language.factory("my_punctual_component")
    class MyPunctualComponent(object):
        name = "my_punctual_component"

        def __init__(
            self,
            nlp,
            name,
            punctuation,
        ):
            self.punctuation = punctuation

    nlp = English.from_config(load_config_from_str(hyphen_config_str))
    assert nlp.get_pipe("my_punctual_component").punctuation == ["?", "-"]
