from pathlib import Path
import numpy as np
import pytest
import srsly
from spacy.vocab import Vocab
from thinc.api import Config

from ..util import make_tempdir
from ... import util
from ...lang.en import English
from ...training.initialize import init_nlp
from ...training.loop import train
from ...training.pretrain import pretrain
from ...tokens import Doc, DocBin
from ...language import DEFAULT_CONFIG_PRETRAIN_PATH, DEFAULT_CONFIG_PATH

pretrain_string_listener = """
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
max_epochs = 5

[training]
max_epochs = 5
"""

pretrain_string_internal = """
[nlp]
lang = "en"
pipeline = ["tagger"]

[components]

[components.tagger]
factory = "tagger"

[components.tagger.model]
@architectures = "spacy.Tagger.v2"

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
max_epochs = 5

[training]
max_epochs = 5
"""


pretrain_string_vectors = """
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
max_epochs = 5

[pretraining.objective]
@architectures = spacy.PretrainVectors.v1
maxout_pieces = 3
hidden_size = 300
loss = cosine

[training]
max_epochs = 5
"""

CHAR_OBJECTIVES = [
    {},
    {"@architectures": "spacy.PretrainCharacters.v1"},
    {
        "@architectures": "spacy.PretrainCharacters.v1",
        "maxout_pieces": 5,
        "hidden_size": 42,
        "n_characters": 2,
    },
]

VECTOR_OBJECTIVES = [
    {
        "@architectures": "spacy.PretrainVectors.v1",
        "maxout_pieces": 3,
        "hidden_size": 300,
        "loss": "cosine",
    },
    {
        "@architectures": "spacy.PretrainVectors.v1",
        "maxout_pieces": 2,
        "hidden_size": 200,
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


@pytest.mark.parametrize("objective", CHAR_OBJECTIVES)
def test_pretraining_tok2vec_characters(objective):
    """Test that pretraining works with the character objective"""
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
        assert Path(tmp_dir / "model4.bin").exists()
        assert not Path(tmp_dir / "model5.bin").exists()


@pytest.mark.parametrize("objective", VECTOR_OBJECTIVES)
def test_pretraining_tok2vec_vectors_fail(objective):
    """Test that pretraining doesn't works with the vectors objective if there are no static vectors"""
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
        assert filled["initialize"]["vectors"] is None
        with pytest.raises(ValueError):
            pretrain(filled, tmp_dir)


@pytest.mark.parametrize("objective", VECTOR_OBJECTIVES)
def test_pretraining_tok2vec_vectors(objective):
    """Test that pretraining works with the vectors objective and static vectors defined"""
    config = Config().from_str(pretrain_string_listener)
    config["pretraining"]["objective"] = objective
    nlp = util.load_model_from_config(config, auto_fill=True, validate=False)
    filled = nlp.config
    pretrain_config = util.load_config(DEFAULT_CONFIG_PRETRAIN_PATH)
    filled = pretrain_config.merge(filled)
    with make_tempdir() as tmp_dir:
        file_path = write_sample_jsonl(tmp_dir)
        filled["paths"]["raw_text"] = file_path
        nlp_path = write_vectors_model(tmp_dir)
        filled["initialize"]["vectors"] = nlp_path
        filled = filled.interpolate()
        pretrain(filled, tmp_dir)


@pytest.mark.parametrize("config", [pretrain_string_internal, pretrain_string_listener])
def test_pretraining_tagger_tok2vec(config):
    """Test pretraining of the tagger's tok2vec layer (via a listener)"""
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
        assert Path(tmp_dir / "model4.bin").exists()
        assert not Path(tmp_dir / "model5.bin").exists()


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


def test_pretraining_training():
    """Test that training can use a pretrained Tok2Vec model"""
    config = Config().from_str(pretrain_string_internal)
    nlp = util.load_model_from_config(config, auto_fill=True, validate=False)
    filled = nlp.config
    pretrain_config = util.load_config(DEFAULT_CONFIG_PRETRAIN_PATH)
    filled = pretrain_config.merge(filled)
    train_config = util.load_config(DEFAULT_CONFIG_PATH)
    filled = train_config.merge(filled)
    with make_tempdir() as tmp_dir:
        pretrain_dir = tmp_dir / "pretrain"
        pretrain_dir.mkdir()
        file_path = write_sample_jsonl(pretrain_dir)
        filled["paths"]["raw_text"] = file_path
        filled["pretraining"]["component"] = "tagger"
        filled["pretraining"]["layer"] = "tok2vec"
        train_dir = tmp_dir / "train"
        train_dir.mkdir()
        train_path, dev_path = write_sample_training(train_dir)
        filled["paths"]["train"] = train_path
        filled["paths"]["dev"] = dev_path
        filled = filled.interpolate()
        P = filled["pretraining"]
        nlp_base = init_nlp(filled)
        model_base = (
            nlp_base.get_pipe(P["component"]).model.get_ref(P["layer"]).get_ref("embed")
        )
        embed_base = None
        for node in model_base.walk():
            if node.name == "hashembed":
                embed_base = node
        pretrain(filled, pretrain_dir)
        pretrained_model = Path(pretrain_dir / "model3.bin")
        assert pretrained_model.exists()
        filled["initialize"]["init_tok2vec"] = str(pretrained_model)
        nlp = init_nlp(filled)
        model = nlp.get_pipe(P["component"]).model.get_ref(P["layer"]).get_ref("embed")
        embed = None
        for node in model.walk():
            if node.name == "hashembed":
                embed = node
        # ensure that the tok2vec weights are actually changed by the pretraining
        assert np.any(np.not_equal(embed.get_param("E"), embed_base.get_param("E")))
        train(nlp, train_dir)


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


def write_sample_training(tmp_dir):
    words = ["The", "players", "start", "."]
    tags = ["DT", "NN", "VBZ", "."]
    doc = Doc(English().vocab, words=words, tags=tags)
    doc_bin = DocBin()
    doc_bin.add(doc)
    train_path = f"{tmp_dir}/train.spacy"
    dev_path = f"{tmp_dir}/dev.spacy"
    doc_bin.to_disk(train_path)
    doc_bin.to_disk(dev_path)
    return train_path, dev_path


def write_vectors_model(tmp_dir):
    import numpy

    vocab = Vocab()
    vector_data = {
        "dog": numpy.random.uniform(-1, 1, (300,)),
        "cat": numpy.random.uniform(-1, 1, (300,)),
        "orange": numpy.random.uniform(-1, 1, (300,)),
    }
    for word, vector in vector_data.items():
        vocab.set_vector(word, vector)
    nlp_path = tmp_dir / "vectors_model"
    nlp = English(vocab)
    nlp.to_disk(nlp_path)
    return str(nlp_path)
