from pathlib import Path

import pytest
import srsly
from thinc.api import Config
from spacy.language import DEFAULT_CONFIG_PRETRAIN_PATH


from ..util import make_tempdir
from ... import util
from ...training.pretrain import pretrain

pretrain_string_listener = """
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
@architectures = "spacy.Tagger.v1"

[components.tagger.model.tok2vec]
@architectures = "spacy.Tok2VecListener.v1"
width = ${components.tok2vec.model.width}

[pretraining]
max_epochs = 10
"""

pretrain_string_internal = """
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
pipeline = ["tagger"]

[components]

[components.tagger]
factory = "tagger"

[components.tagger.model]
@architectures = "spacy.Tagger.v1"

[components.tagger.model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v1"
pretrained_vectors = null
width = 342
depth = 4
window_size = 1
embed_size = 2000
maxout_pieces = 3
subword_features = true

[pretraining]
max_epochs = 10
"""

OBJECTIVES = [
    {"@architectures": "spacy.PretrainCharacters.v1"},  # default configuration
    {
        "@architectures": "spacy.PretrainCharacters.v1",
        "maxout_pieces": 5,
        "hidden_size": 42,
        "n_characters": 2,
    },
    {
        "@architectures": "spacy.PretrainVectors.v1",
        "maxout_pieces": 3,
        "hidden_size": 300,
        "loss": "cosine",
    },
    {
        "@architectures": "spacy.PretrainVectors.v1",
        "maxout_pieces": 3,
        "hidden_size": 300,
        "loss": "L2",
    },
]


def test_pretraining_default():
    """Test that pretraining defaults to a character objective"""
    config = Config().from_str(pretrain_string_internal)
    nlp = util.load_model_from_config(config, auto_fill=True, validate=False)
    filled = nlp.config
    pretrain_config = util.load_config(DEFAULT_CONFIG_PRETRAIN_PATH)
    filled = pretrain_config.merge(filled)
    assert "PretrainCharacters" in filled["pretraining"]["objective"]["@architectures"]


@pytest.mark.parametrize("objective", OBJECTIVES)
def test_pretraining_tok2vec_objectives(objective):
    """Test that pretraining works for the tok2vec component with different objectives"""
    config = Config().from_str(pretrain_string_listener)
    config["pretraining"]["objective"] = objective
    nlp = util.load_model_from_config(config, auto_fill=True, validate=False)
    filled = nlp.config
    pretrain_config = util.load_config(DEFAULT_CONFIG_PRETRAIN_PATH)
    filled = pretrain_config.merge(filled)
    with make_tempdir() as tmp_dir:
        file_path = write_sample_jsonl(tmp_dir)
        filled["paths"]["raw_text"] = file_path
        filled = filled.interpolate()
        assert filled["pretraining"]["component"] == "tok2vec"
        pretrain(filled, tmp_dir)
        assert Path(tmp_dir / "model0.bin").exists()
        assert Path(tmp_dir / "model9.bin").exists()
        assert not Path(tmp_dir / "model10.bin").exists()


@pytest.mark.parametrize("config", [pretrain_string_internal, pretrain_string_listener])
def test_pretraining_tagger_tok2vec(config):
    """Test pretraining of the tagger's tok2vec layer"""
    config = Config().from_str(pretrain_string_listener)
    nlp = util.load_model_from_config(config, auto_fill=True, validate=False)
    filled = nlp.config
    pretrain_config = util.load_config(DEFAULT_CONFIG_PRETRAIN_PATH)
    filled = pretrain_config.merge(filled)
    with make_tempdir() as tmp_dir:
        file_path = write_sample_jsonl(tmp_dir)
        filled["paths"]["raw_text"] = file_path
        filled["pretraining"]["component"] = "tagger"
        filled["pretraining"]["layer"] = "tok2vec"
        filled = filled.interpolate()
        pretrain(filled, tmp_dir)
        assert Path(tmp_dir / "model0.bin").exists()
        assert Path(tmp_dir / "model9.bin").exists()
        assert not Path(tmp_dir / "model10.bin").exists()


def test_pretraining_tagger():
    """Test pretraining of the tagger itself will throw an error (not an appropriate tok2vec layer)"""
    config = Config().from_str(pretrain_string_internal)
    nlp = util.load_model_from_config(config, auto_fill=True, validate=False)
    filled = nlp.config
    pretrain_config = util.load_config(DEFAULT_CONFIG_PRETRAIN_PATH)
    filled = pretrain_config.merge(filled)
    with make_tempdir() as tmp_dir:
        file_path = write_sample_jsonl(tmp_dir)
        filled["paths"]["raw_text"] = file_path
        filled["pretraining"]["component"] = "tagger"
        filled = filled.interpolate()
        with pytest.raises(ValueError):
            pretrain(filled, tmp_dir)


def write_sample_jsonl(tmp_dir):
    data = [
        {
            "meta": {"id": "1"},
            "text": "This is the best TV you'll ever buy!",
            "cats": {"pos": 1, "neg": 0},
        },
        {
            "meta": {"id": "2"},
            "text": "I wouldn't buy this again.",
            "cats": {"pos": 0, "neg": 1},
        },
    ]
    file_path = f"{tmp_dir}/text.jsonl"
    srsly.write_jsonl(file_path, data)
    return file_path
