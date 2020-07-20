import pytest

from spacy.ml.models.tok2vec import build_Tok2Vec_model
from spacy.vocab import Vocab
from spacy.tokens import Doc

from .util import get_batch


# This fails in Thinc v7.3.1. Need to push patch
@pytest.mark.xfail
def test_empty_doc():
    width = 128
    embed_size = 2000
    vocab = Vocab()
    doc = Doc(vocab, words=[])
    # TODO: fix tok2vec arguments
    tok2vec = build_Tok2Vec_model(width, embed_size, dropout=None)
    vectors, backprop = tok2vec.begin_update([doc])
    assert len(vectors) == 1
    assert vectors[0].shape == (0, width)


@pytest.mark.parametrize(
    "batch_size,width,embed_size", [[1, 128, 2000], [2, 128, 2000], [3, 8, 63]]
)
def test_tok2vec_batch_sizes(batch_size, width, embed_size):
    batch = get_batch(batch_size)
    tok2vec = build_Tok2Vec_model(
        width,
        embed_size,
        pretrained_vectors=None,
        conv_depth=4,
        bilstm_depth=0,
        window_size=1,
        maxout_pieces=3,
        subword_features=True,
        char_embed=False,
        nM=64,
        nC=8,
        dropout=None,
    )
    tok2vec.initialize()
    vectors, backprop = tok2vec.begin_update(batch)
    assert len(vectors) == len(batch)
    for doc_vec, doc in zip(vectors, batch):
        assert doc_vec.shape == (len(doc), width)


# fmt: off
@pytest.mark.parametrize(
    "tok2vec_config",
    [
        {"width": 8, "embed_size": 100, "char_embed": False, "nM": 64, "nC": 8, "pretrained_vectors": None, "window_size": 1, "conv_depth": 2, "bilstm_depth": 0, "maxout_pieces": 3, "subword_features": True, "dropout": None},
        {"width": 8, "embed_size": 100, "char_embed": True, "nM": 64, "nC": 8, "pretrained_vectors": None, "window_size": 1, "conv_depth": 2, "bilstm_depth": 0, "maxout_pieces": 3, "subword_features": True, "dropout": None},
        {"width": 8, "embed_size": 100, "char_embed": False, "nM": 64, "nC": 8, "pretrained_vectors": None, "window_size": 1, "conv_depth": 6, "bilstm_depth": 0, "maxout_pieces": 3, "subword_features": True, "dropout": None},
        {"width": 8, "embed_size": 100, "char_embed": False, "nM": 64, "nC": 8, "pretrained_vectors": None, "window_size": 1, "conv_depth": 6, "bilstm_depth": 0, "maxout_pieces": 3, "subword_features": True, "dropout": None},
        {"width": 8, "embed_size": 100, "char_embed": False, "nM": 64, "nC": 8, "pretrained_vectors": None, "window_size": 1, "conv_depth": 2, "bilstm_depth": 0, "maxout_pieces": 3, "subword_features": False, "dropout": None},
        {"width": 8, "embed_size": 100, "char_embed": False, "nM": 64, "nC": 8, "pretrained_vectors": None, "window_size": 3, "conv_depth": 2, "bilstm_depth": 0, "maxout_pieces": 3, "subword_features": False, "dropout": None},
        {"width": 8, "embed_size": 100, "char_embed": True, "nM": 81, "nC": 8, "pretrained_vectors": None, "window_size": 3, "conv_depth": 2, "bilstm_depth": 0, "maxout_pieces": 3, "subword_features": False, "dropout": None},
        {"width": 8, "embed_size": 100, "char_embed": True, "nM": 81, "nC": 9, "pretrained_vectors": None, "window_size": 3, "conv_depth": 2, "bilstm_depth": 0, "maxout_pieces": 3, "subword_features": False, "dropout": None},
    ],
)
# fmt: on
def test_tok2vec_configs(tok2vec_config):
    docs = get_batch(3)
    tok2vec = build_Tok2Vec_model(**tok2vec_config)
    tok2vec.initialize(docs)
    vectors, backprop = tok2vec.begin_update(docs)
    assert len(vectors) == len(docs)
    assert vectors[0].shape == (len(docs[0]), tok2vec_config["width"])
    backprop(vectors)
