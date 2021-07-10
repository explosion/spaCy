import pytest
from spacy.ml.models.tok2vec import build_Tok2Vec_model
from spacy.ml.models.tok2vec import MultiHashEmbed, CharacterEmbed
from spacy.ml.models.tok2vec import MishWindowEncoder, MaxoutWindowEncoder
from spacy.pipeline.tok2vec import Tok2Vec, Tok2VecListener
from spacy.vocab import Vocab
from spacy.tokens import Doc
from spacy.training import Example
from spacy import util
from spacy.lang.en import English
from thinc.api import Config, get_current_ops
from numpy.testing import assert_array_equal

from ..util import get_batch, make_tempdir


def test_empty_doc():
    width = 128
    embed_size = 2000
    vocab = Vocab()
    doc = Doc(vocab, words=[])
    tok2vec = build_Tok2Vec_model(
        MultiHashEmbed(
            width=width,
            rows=[embed_size, embed_size, embed_size, embed_size],
            include_static_vectors=False,
            attrs=["NORM", "PREFIX", "SUFFIX", "SHAPE"],
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
            rows=[embed_size] * 4,
            include_static_vectors=False,
            attrs=["NORM", "PREFIX", "SUFFIX", "SHAPE"],
        ),
        MaxoutWindowEncoder(width=width, depth=4, window_size=1, maxout_pieces=3),
    )
    tok2vec.initialize()
    vectors, backprop = tok2vec.begin_update(batch)
    assert len(vectors) == len(batch)
    for doc_vec, doc in zip(vectors, batch):
        assert doc_vec.shape == (len(doc), width)


@pytest.mark.parametrize(
    "width,embed_arch,embed_config,encode_arch,encode_config",
    # fmt: off
    [
        (8, MultiHashEmbed, {"rows": [100, 100], "attrs": ["SHAPE", "LOWER"], "include_static_vectors": False}, MaxoutWindowEncoder, {"window_size": 1, "maxout_pieces": 3, "depth": 2}),
        (8, MultiHashEmbed, {"rows": [100, 20], "attrs": ["ORTH", "PREFIX"], "include_static_vectors": False}, MishWindowEncoder, {"window_size": 1, "depth": 6}),
        (8, CharacterEmbed, {"rows": 100, "nM": 64, "nC": 8, "include_static_vectors": False}, MaxoutWindowEncoder, {"window_size": 1, "maxout_pieces": 3, "depth": 3}),
        (8, CharacterEmbed, {"rows": 100, "nM": 16, "nC": 2, "include_static_vectors": False}, MishWindowEncoder, {"window_size": 1, "depth": 3}),
    ],
    # fmt: on
)
def test_tok2vec_configs(width, embed_arch, embed_config, encode_arch, encode_config):
    embed_config["width"] = width
    encode_config["width"] = width
    docs = get_batch(3)
    tok2vec = build_Tok2Vec_model(
        embed_arch(**embed_config), encode_arch(**encode_config)
    )
    tok2vec.initialize(docs)
    vectors, backprop = tok2vec.begin_update(docs)
    assert len(vectors) == len(docs)
    assert vectors[0].shape == (len(docs[0]), width)
    backprop(vectors)


def test_init_tok2vec():
    # Simple test to initialize the default tok2vec
    nlp = English()
    tok2vec = nlp.add_pipe("tok2vec")
    assert tok2vec.listeners == []
    nlp.initialize()
    assert tok2vec.model.get_dim("nO")


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

    [components.tok2vec.model]
    @architectures = "spacy.Tok2Vec.v2"

    [components.tok2vec.model.embed]
    @architectures = "spacy.MultiHashEmbed.v1"
    width = ${components.tok2vec.model.encode.width}
    rows = [2000, 1000, 1000, 1000]
    attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
    include_static_vectors = false

    [components.tok2vec.model.encode]
    @architectures = "spacy.MaxoutWindowEncoder.v2"
    width = 96
    depth = 4
    window_size = 1
    maxout_pieces = 3
    """

TRAIN_DATA = [
    (
        "I like green eggs",
        {"tags": ["N", "V", "J", "N"], "cats": {"preference": 1.0, "imperative": 0.0}},
    ),
    (
        "Eat blue ham",
        {"tags": ["V", "J", "N"], "cats": {"preference": 0.0, "imperative": 1.0}},
    ),
]


def test_tok2vec_listener():
    orig_config = Config().from_str(cfg_string)
    nlp = util.load_model_from_config(orig_config, auto_fill=True, validate=True)
    assert nlp.pipe_names == ["tok2vec", "tagger"]
    tagger = nlp.get_pipe("tagger")
    tok2vec = nlp.get_pipe("tok2vec")
    tagger_tok2vec = tagger.model.get_ref("tok2vec")
    assert isinstance(tok2vec, Tok2Vec)
    assert isinstance(tagger_tok2vec, Tok2VecListener)
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
        for tag in t[1]["tags"]:
            tagger.add_label(tag)

    # Check that the Tok2Vec component finds it listeners
    assert tok2vec.listeners == []
    optimizer = nlp.initialize(lambda: train_examples)
    assert tok2vec.listeners == [tagger_tok2vec]

    for i in range(5):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)

    doc = nlp("Running the pipeline as a whole.")
    doc_tensor = tagger_tok2vec.predict([doc])[0]
    ops = get_current_ops()
    assert_array_equal(ops.to_numpy(doc.tensor), ops.to_numpy(doc_tensor))

    # TODO: should this warn or error?
    nlp.select_pipes(disable="tok2vec")
    assert nlp.pipe_names == ["tagger"]
    nlp("Running the pipeline with the Tok2Vec component disabled.")


def test_tok2vec_listener_callback():
    orig_config = Config().from_str(cfg_string)
    nlp = util.load_model_from_config(orig_config, auto_fill=True, validate=True)
    assert nlp.pipe_names == ["tok2vec", "tagger"]
    tagger = nlp.get_pipe("tagger")
    tok2vec = nlp.get_pipe("tok2vec")
    nlp._link_components()
    docs = [nlp.make_doc("A random sentence")]
    tok2vec.model.initialize(X=docs)
    gold_array = [[1.0 for tag in ["V", "Z"]] for word in docs]
    label_sample = [tagger.model.ops.asarray(gold_array, dtype="float32")]
    tagger.model.initialize(X=docs, Y=label_sample)
    docs = [nlp.make_doc("Another entirely random sentence")]
    tok2vec.update([Example.from_dict(x, {}) for x in docs])
    Y, get_dX = tagger.model.begin_update(docs)
    # assure that the backprop call works (and doesn't hit a 'None' callback)
    assert get_dX(Y) is not None


def test_replace_listeners():
    orig_config = Config().from_str(cfg_string)
    nlp = util.load_model_from_config(orig_config, auto_fill=True, validate=True)
    examples = [Example.from_dict(nlp.make_doc("x y"), {"tags": ["V", "Z"]})]
    nlp.initialize(lambda: examples)
    tok2vec = nlp.get_pipe("tok2vec")
    tagger = nlp.get_pipe("tagger")
    assert isinstance(tagger.model.layers[0], Tok2VecListener)
    assert tok2vec.listener_map["tagger"][0] == tagger.model.layers[0]
    assert (
        nlp.config["components"]["tok2vec"]["model"]["@architectures"]
        == "spacy.Tok2Vec.v2"
    )
    assert (
        nlp.config["components"]["tagger"]["model"]["tok2vec"]["@architectures"]
        == "spacy.Tok2VecListener.v1"
    )
    nlp.replace_listeners("tok2vec", "tagger", ["model.tok2vec"])
    assert not isinstance(tagger.model.layers[0], Tok2VecListener)
    t2v_cfg = nlp.config["components"]["tok2vec"]["model"]
    assert t2v_cfg["@architectures"] == "spacy.Tok2Vec.v2"
    assert nlp.config["components"]["tagger"]["model"]["tok2vec"] == t2v_cfg
    with pytest.raises(ValueError):
        nlp.replace_listeners("invalid", "tagger", ["model.tok2vec"])
    with pytest.raises(ValueError):
        nlp.replace_listeners("tok2vec", "parser", ["model.tok2vec"])
    with pytest.raises(ValueError):
        nlp.replace_listeners("tok2vec", "tagger", ["model.yolo"])
    with pytest.raises(ValueError):
        nlp.replace_listeners("tok2vec", "tagger", ["model.tok2vec", "model.yolo"])
    # attempt training with the new pipeline
    optimizer = nlp.initialize(lambda: examples)
    for i in range(2):
        losses = {}
        nlp.update(examples, sgd=optimizer, losses=losses)
        assert losses["tok2vec"] == 0.0
        assert losses["tagger"] > 0.0


cfg_string_multi = """
    [nlp]
    lang = "en"
    pipeline = ["tok2vec","tagger", "ner"]

    [components]

    [components.tagger]
    factory = "tagger"

    [components.tagger.model]
    @architectures = "spacy.Tagger.v1"
    nO = null

    [components.tagger.model.tok2vec]
    @architectures = "spacy.Tok2VecListener.v1"
    width = ${components.tok2vec.model.encode.width}

    [components.ner]
    factory = "ner"

    [components.ner.model]
    @architectures = "spacy.TransitionBasedParser.v2"

    [components.ner.model.tok2vec]
    @architectures = "spacy.Tok2VecListener.v1"
    width = ${components.tok2vec.model.encode.width}

    [components.tok2vec]
    factory = "tok2vec"

    [components.tok2vec.model]
    @architectures = "spacy.Tok2Vec.v2"

    [components.tok2vec.model.embed]
    @architectures = "spacy.MultiHashEmbed.v1"
    width = ${components.tok2vec.model.encode.width}
    rows = [2000, 1000, 1000, 1000]
    attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
    include_static_vectors = false

    [components.tok2vec.model.encode]
    @architectures = "spacy.MaxoutWindowEncoder.v2"
    width = 96
    depth = 4
    window_size = 1
    maxout_pieces = 3
    """


def test_replace_listeners_from_config():
    orig_config = Config().from_str(cfg_string_multi)
    nlp = util.load_model_from_config(orig_config, auto_fill=True)
    annots = {"tags": ["V", "Z"], "entities": [(0, 1, "A"), (1, 2, "B")]}
    examples = [Example.from_dict(nlp.make_doc("x y"), annots)]
    nlp.initialize(lambda: examples)
    tok2vec = nlp.get_pipe("tok2vec")
    tagger = nlp.get_pipe("tagger")
    ner = nlp.get_pipe("ner")
    assert tok2vec.listening_components == ["tagger", "ner"]
    assert any(isinstance(node, Tok2VecListener) for node in ner.model.walk())
    assert any(isinstance(node, Tok2VecListener) for node in tagger.model.walk())
    with make_tempdir() as dir_path:
        nlp.to_disk(dir_path)
        base_model = str(dir_path)
        new_config = {
            "nlp": {"lang": "en", "pipeline": ["tok2vec", "tagger", "ner"]},
            "components": {
                "tok2vec": {"source": base_model},
                "tagger": {
                    "source": base_model,
                    "replace_listeners": ["model.tok2vec"],
                },
                "ner": {"source": base_model},
            },
        }
        new_nlp = util.load_model_from_config(new_config, auto_fill=True)
    new_nlp.initialize(lambda: examples)
    tok2vec = new_nlp.get_pipe("tok2vec")
    tagger = new_nlp.get_pipe("tagger")
    ner = new_nlp.get_pipe("ner")
    assert tok2vec.listening_components == ["ner"]
    assert any(isinstance(node, Tok2VecListener) for node in ner.model.walk())
    assert not any(isinstance(node, Tok2VecListener) for node in tagger.model.walk())
    t2v_cfg = new_nlp.config["components"]["tok2vec"]["model"]
    assert t2v_cfg["@architectures"] == "spacy.Tok2Vec.v2"
    assert new_nlp.config["components"]["tagger"]["model"]["tok2vec"] == t2v_cfg
    assert (
        new_nlp.config["components"]["ner"]["model"]["tok2vec"]["@architectures"]
        == "spacy.Tok2VecListener.v1"
    )


cfg_string_multi_textcat = """
    [nlp]
    lang = "en"
    pipeline = ["tok2vec","textcat_multilabel","tagger"]

    [components]

    [components.textcat_multilabel]
    factory = "textcat_multilabel"

    [components.textcat_multilabel.model]
    @architectures = "spacy.TextCatEnsemble.v2"
    nO = null

    [components.textcat_multilabel.model.tok2vec]
    @architectures = "spacy.Tok2VecListener.v1"
    width = ${components.tok2vec.model.encode.width}

    [components.textcat_multilabel.model.linear_model]
    @architectures = "spacy.TextCatBOW.v1"
    exclusive_classes = false
    ngram_size = 1
    no_output_layer = false

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

    [components.tok2vec.model]
    @architectures = "spacy.Tok2Vec.v2"

    [components.tok2vec.model.embed]
    @architectures = "spacy.MultiHashEmbed.v1"
    width = ${components.tok2vec.model.encode.width}
    rows = [2000, 1000, 1000, 1000]
    attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
    include_static_vectors = false

    [components.tok2vec.model.encode]
    @architectures = "spacy.MaxoutWindowEncoder.v2"
    width = 96
    depth = 4
    window_size = 1
    maxout_pieces = 3
    """


def test_tok2vec_listeners_textcat():
    orig_config = Config().from_str(cfg_string_multi_textcat)
    nlp = util.load_model_from_config(orig_config, auto_fill=True, validate=True)
    assert nlp.pipe_names == ["tok2vec", "textcat_multilabel", "tagger"]
    tagger = nlp.get_pipe("tagger")
    textcat = nlp.get_pipe("textcat_multilabel")
    tok2vec = nlp.get_pipe("tok2vec")
    tagger_tok2vec = tagger.model.get_ref("tok2vec")
    textcat_tok2vec = textcat.model.get_ref("tok2vec")
    assert isinstance(tok2vec, Tok2Vec)
    assert isinstance(tagger_tok2vec, Tok2VecListener)
    assert isinstance(textcat_tok2vec, Tok2VecListener)
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))

    optimizer = nlp.initialize(lambda: train_examples)
    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)

    docs = list(nlp.pipe(["Eat blue ham", "I like green eggs"]))
    cats0 = docs[0].cats
    assert cats0["preference"] < 0.1
    assert cats0["imperative"] > 0.9
    cats1 = docs[1].cats
    assert cats1["preference"] > 0.1
    assert cats1["imperative"] < 0.9
    assert [t.tag_ for t in docs[0]] == ["V", "J", "N"]
    assert [t.tag_ for t in docs[1]] == ["N", "V", "J", "N"]
