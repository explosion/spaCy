import pytest

from spacy.ml.models.tok2vec import build_Tok2Vec_model
from spacy.ml.models.tok2vec import MultiHashEmbed, CharacterEmbed
from spacy.ml.models.tok2vec import MishWindowEncoder, MaxoutWindowEncoder
from spacy.pipeline.tok2vec import Tok2Vec, Tok2VecListener
from spacy.vocab import Vocab
from spacy.tokens import Doc
from spacy.gold import Example
from spacy import util

from ..util import get_batch

from thinc.api import Config

from numpy.testing import assert_equal

from ...lang.en import English


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
        MaxoutWindowEncoder(width=width, depth=4, window_size=1, maxout_pieces=3),
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


def test_init_tok2vec():
    # Simple test to train the default tok2vec
    nlp = English()
    tok2vec = nlp.add_pipe("tok2vec")
    assert tok2vec.annotation_setter is not None
    nlp.begin_training()


def test_tok2vec_listener():
    cfg_string = """
    [nlp]
    lang = "en"
    pipeline = ["tok2vec","tagger"]

    [components]
    
    [components.tagger]
    factory = "tagger"
    
    [components.tagger.model]
    @architectures = "spacy.Tagger.v1"
    nO = null

    [components.tagger.model.tok2vec]
    @architectures = "spacy.Tok2VecListener.v1"
    width = ${components.tok2vec.model.encode.width}

    [components.tok2vec]
    factory = "tok2vec"
    
    [components.tok2vec.annotation_setter]
    @annotation_setters = spacy.tensor_setter.v1

    [components.tok2vec.model]
    @architectures = "spacy.Tok2Vec.v1"

    [components.tok2vec.model.embed]
    @architectures = "spacy.MultiHashEmbed.v1"
    width = ${components.tok2vec.model.encode.width}
    rows = 2000
    also_embed_subwords = true
    also_use_static_vectors = false

    [components.tok2vec.model.encode]
    @architectures = "spacy.MaxoutWindowEncoder.v1"
    width = 96
    depth = 4
    window_size = 1
    maxout_pieces = 3
    """

    TRAIN_DATA = [
        ("I like green eggs", {"tags": ["N", "V", "J", "N"]}),
        ("Eat blue ham", {"tags": ["V", "J", "N"]}),
    ]

    orig_config = Config().from_str(cfg_string)
    nlp, config = util.load_model_from_config(orig_config, auto_fill=True, validate=True)
    tagger = nlp.get_pipe("tagger")
    tok2vec = nlp.get_pipe("tok2vec")
    tok2vec_listener = tagger.model.get_ref("tok2vec")
    assert isinstance(tok2vec, Tok2Vec)
    assert isinstance(tok2vec_listener, Tok2VecListener)
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
        for tag in t[1]["tags"]:
            tagger.add_label(tag)

    # Check that the Tok2Vec component finds it listeners
    assert tok2vec.listeners == []
    optimizer = nlp.begin_training()
    assert tok2vec.listeners == [tok2vec_listener]

    for i in range(5):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)

    doc = nlp("Testing this document")
    doc_tensor = tok2vec_listener.predict([doc])[0]
    assert_equal(doc.tensor, doc_tensor)
