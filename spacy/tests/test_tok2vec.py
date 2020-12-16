# coding: utf-8
from __future__ import unicode_literals

import pytest

from spacy._ml import Tok2Vec
from spacy.vocab import Vocab
from spacy.tokens import Doc
from spacy.compat import unicode_


def get_batch(batch_size):
    vocab = Vocab()
    docs = []
    start = 0
    for size in range(1, batch_size + 1):
        # Make the words numbers, so that they're distnct
        # across the batch, and easy to track.
        numbers = [unicode_(i) for i in range(start, start + size)]
        docs.append(Doc(vocab, words=numbers))
        start += size
    return docs


# This fails in Thinc v7.3.1. Need to push patch
@pytest.mark.xfail
def test_empty_doc():
    width = 128
    embed_size = 2000
    vocab = Vocab()
    doc = Doc(vocab, words=[])
    tok2vec = Tok2Vec(width, embed_size)
    vectors, backprop = tok2vec.begin_update([doc])
    assert len(vectors) == 1
    assert vectors[0].shape == (0, width)


@pytest.mark.parametrize(
    "batch_size,width,embed_size", [[1, 128, 2000], [2, 128, 2000], [3, 8, 63]]
)
def test_tok2vec_batch_sizes(batch_size, width, embed_size):
    batch = get_batch(batch_size)
    tok2vec = Tok2Vec(width, embed_size)
    vectors, backprop = tok2vec.begin_update(batch)
    assert len(vectors) == len(batch)
    for doc_vec, doc in zip(vectors, batch):
        assert doc_vec.shape == (len(doc), width)


@pytest.mark.parametrize(
    "tok2vec_config",
    [
        {"width": 8, "embed_size": 100, "char_embed": False},
        {"width": 8, "embed_size": 100, "char_embed": True},
        {"width": 8, "embed_size": 100, "conv_depth": 6},
        {"width": 8, "embed_size": 100, "conv_depth": 6},
        {"width": 8, "embed_size": 100, "subword_features": False},
    ],
)
def test_tok2vec_configs(tok2vec_config):
    docs = get_batch(3)
    tok2vec = Tok2Vec(**tok2vec_config)
    vectors, backprop = tok2vec.begin_update(docs)
    assert len(vectors) == len(docs)
    assert vectors[0].shape == (len(docs[0]), tok2vec_config["width"])
    backprop(vectors)
