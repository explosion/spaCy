import pytest

from spacy.ml.models.tok2vec import build_Tok2Vec_model
from spacy.ml.models.tok2vec import MultiHashEmbed, CharacterEmbed
from spacy.ml.models.tok2vec import MishWindowEncoder, MaxoutWindowEncoder
from spacy.vocab import Vocab
from spacy.tokens import Doc

from .util import get_batch


def test_empty_doc():
    width = 128
    embed_size = 2000
    vocab = Vocab()
    doc = Doc(vocab, words=[])
    tok2vec = build_Tok2Vec_model(
        MultiHashEmbed(
            width=width,
            rows=embed_size,
            also_use_static_vectors=False,
            also_embed_subwords=True,
        ),
        MaxoutWindowEncoder(width=width, depth=4, window_size=1, maxout_pieces=3),
    )
    tok2vec.initialize()
    vectors, backprop = tok2vec.begin_update([doc])
    assert len(vectors) == 1
    assert vectors[0].shape == (0, width)


@pytest.mark.parametrize(
    "batch_size,width,embed_size", [[1, 128, 2000], [2, 128, 2000], [3, 8, 63]]
)
def test_tok2vec_batch_sizes(batch_size, width, embed_size):
    batch = get_batch(batch_size)
    tok2vec = build_Tok2Vec_model(
        MultiHashEmbed(
            width=width,
            rows=embed_size,
            also_use_static_vectors=False,
            also_embed_subwords=True,
        ),
        MaxoutWindowEncoder(width=width, depth=4, window_size=1, maxout_pieces=3,),
    )
    tok2vec.initialize()
    vectors, backprop = tok2vec.begin_update(batch)
    assert len(vectors) == len(batch)
    for doc_vec, doc in zip(vectors, batch):
        assert doc_vec.shape == (len(doc), width)


# fmt: off
@pytest.mark.parametrize(
    "width,embed_arch,embed_config,encode_arch,encode_config",
    [
        (8, MultiHashEmbed, {"rows": 100, "also_embed_subwords": True, "also_use_static_vectors": False}, MaxoutWindowEncoder, {"window_size": 1, "maxout_pieces": 3, "depth": 2}),
        (8, MultiHashEmbed, {"rows": 100, "also_embed_subwords": True, "also_use_static_vectors": False}, MishWindowEncoder, {"window_size": 1, "depth": 6}),
        (8, CharacterEmbed, {"rows": 100, "nM": 64, "nC": 8}, MaxoutWindowEncoder, {"window_size": 1, "maxout_pieces": 3, "depth": 3}),
        (8, CharacterEmbed, {"rows": 100, "nM": 16, "nC": 2}, MishWindowEncoder, {"window_size": 1, "depth": 3}),
    ],
)
# fmt: on
def test_tok2vec_configs(width, embed_arch, embed_config, encode_arch, encode_config):
    embed_config["width"] = width
    encode_config["width"] = width
    docs = get_batch(3)
    tok2vec = build_Tok2Vec_model(
        embed_arch(**embed_config),
        encode_arch(**encode_config)
    )
    tok2vec.initialize(docs)
    vectors, backprop = tok2vec.begin_update(docs)
    assert len(vectors) == len(docs)
    assert vectors[0].shape == (len(docs[0]), width)
    backprop(vectors)
