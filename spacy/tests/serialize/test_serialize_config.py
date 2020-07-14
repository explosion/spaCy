import pytest
from thinc.api import Config
import spacy
from spacy import util
from spacy.lang.en import English
from spacy.util import registry, deep_merge_configs

from ..util import make_tempdir
from ...ml.models import build_Tok2Vec_model, build_tb_parser_model

nlp_config_string = """
[nlp]
lang = "en"

[nlp.pipeline]

[nlp.pipeline.tok2vec]
@factories = "tok2vec"

[nlp.pipeline.tok2vec.model]
@architectures = "spacy.HashEmbedCNN.v1"
pretrained_vectors = null
width = 342
depth = 4
window_size = 1
embed_size = 2000
maxout_pieces = 3
subword_features = true
dropout = null

[nlp.pipeline.tagger]
@factories = "tagger"

[nlp.pipeline.tagger.model]
@architectures = "spacy.Tagger.v1"

[nlp.pipeline.tagger.model.tok2vec]
@architectures = "spacy.Tok2VecTensors.v1"
width = ${nlp.pipeline.tok2vec.model:width}
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
dropout = null
"""


@registry.architectures.register("my_test_parser")
def my_parser():
    tok2vec = build_Tok2Vec_model(
        width=321,
        embed_size=5432,
        pretrained_vectors=None,
        window_size=3,
        maxout_pieces=4,
        subword_features=True,
        char_embed=True,
        nM=64,
        nC=8,
        conv_depth=2,
        bilstm_depth=0,
        dropout=None,
    )
    parser = build_tb_parser_model(
        tok2vec=tok2vec, nr_feature_tokens=7, hidden_width=65, maxout_pieces=5
    )
    return parser


def test_create_nlp_from_config():
    config = Config().from_str(nlp_config_string)
    nlp = util.load_model_from_config(config)
    assert nlp.pipe_names == ["tok2vec", "tagger"]
    assert len(nlp.config["nlp"]["pipeline"]) == 2
    nlp.remove_pipe("tagger")
    assert len(nlp.config["nlp"]["pipeline"]) == 1
    with pytest.raises(ValueError):
        bad_cfg = {"pipeline": {}}
        util.load_model_from_config(Config(bad_cfg))
    with pytest.raises(ValueError):
        bad_cfg = {"nlp": {"pipeline": {"foo": "bar"}}}
        util.load_model_from_config(Config(bad_cfg))


def test_serialize_nlp():
    """ Create a custom nlp pipeline from config and ensure it serializes it correctly """
    nlp_config = Config().from_str(nlp_config_string)
    nlp = util.load_model_from_config(nlp_config)
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
