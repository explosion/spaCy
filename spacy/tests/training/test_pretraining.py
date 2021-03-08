from pathlib import Path

import srsly
from thinc.api import Config
from spacy.language import DEFAULT_CONFIG_PRETRAIN_PATH


from ..util import make_tempdir
from ... import util
from ...training.pretrain import pretrain

pretrain_string = """
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


def test_pretraining_tok2vec_layer():
    """Test that pretraining works for the tok2vec component"""
    config = Config().from_str(pretrain_string)
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


def test_pretraining_tagger_tok2vec():
    """Test that the pretraining works when referring to the tagger's tok2vec layer"""
    config = Config().from_str(pretrain_string)
    nlp = util.load_model_from_config(config, auto_fill=True, validate=False)
    filled = nlp.config
    pretrain_config = util.load_config(DEFAULT_CONFIG_PRETRAIN_PATH)
    filled = pretrain_config.merge(filled)
    with make_tempdir() as tmp_dir:
        file_path = write_sample_jsonl(tmp_dir)
        filled["paths"]["raw_text"] = file_path
        filled["pretraining"]["component"] = "tagger"
        filled = filled.interpolate()
        pretrain(filled, tmp_dir)
        assert Path(tmp_dir / "model0.bin").exists()
        assert Path(tmp_dir / "model9.bin").exists()
        assert not Path(tmp_dir / "model10.bin").exists()


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
