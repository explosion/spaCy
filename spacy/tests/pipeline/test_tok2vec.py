import pytest
from numpy.testing import assert_array_equal
from thinc.api import Config, get_current_ops

from spacy import util
from spacy.lang.en import English
from spacy.ml.models.tok2vec import (
    MaxoutWindowEncoder,
    MultiHashEmbed,
    build_Tok2Vec_model,
)
from spacy.pipeline.tok2vec import Tok2Vec, Tok2VecListener
from spacy.tokens import Doc
from spacy.training import Example
from spacy.util import registry
from spacy.vocab import Vocab

from ..util import add_vecs_to_vocab, get_batch, make_tempdir


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


@pytest.mark.slow
@pytest.mark.parametrize("width", [8])
@pytest.mark.parametrize(
    "embed_arch,embed_config",
    # fmt: off
    [
        ("spacy.MultiHashEmbed.v1", {"rows": [100, 100], "attrs": ["SHAPE", "LOWER"], "include_static_vectors": False}),
        ("spacy.MultiHashEmbed.v1", {"rows": [100, 20], "attrs": ["ORTH", "PREFIX"], "include_static_vectors": False}),
        ("spacy.CharacterEmbed.v1", {"rows": 100, "nM": 64, "nC": 8, "include_static_vectors": False}),
        ("spacy.CharacterEmbed.v1", {"rows": 100, "nM": 16, "nC": 2, "include_static_vectors": False}),
    ],
    # fmt: on
)
@pytest.mark.parametrize(
    "tok2vec_arch,encode_arch,encode_config",
    # fmt: off
    [
        ("spacy.Tok2Vec.v1", "spacy.MaxoutWindowEncoder.v1", {"window_size": 1, "maxout_pieces": 3, "depth": 2}),
        ("spacy.Tok2Vec.v2", "spacy.MaxoutWindowEncoder.v2", {"window_size": 1, "maxout_pieces": 3, "depth": 2}),
        ("spacy.Tok2Vec.v1", "spacy.MishWindowEncoder.v1", {"window_size": 1, "depth": 6}),
        ("spacy.Tok2Vec.v2", "spacy.MishWindowEncoder.v2", {"window_size": 1, "depth": 6}),
    ],
    # fmt: on
)
def test_tok2vec_configs(
    width, tok2vec_arch, embed_arch, embed_config, encode_arch, encode_config
):
    embed = registry.get("architectures", embed_arch)
    encode = registry.get("architectures", encode_arch)
    tok2vec_model = registry.get("architectures", tok2vec_arch)

    embed_config["width"] = width
    encode_config["width"] = width
    docs = get_batch(3)
    tok2vec = tok2vec_model(embed(**embed_config), encode(**encode_config))
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
    @architectures = "spacy.Tagger.v2"
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


@pytest.mark.parametrize("with_vectors", (False, True))
def test_tok2vec_listener(with_vectors):
    orig_config = Config().from_str(cfg_string)
    orig_config["components"]["tok2vec"]["model"]["embed"][
        "include_static_vectors"
    ] = with_vectors
    nlp = util.load_model_from_config(orig_config, auto_fill=True, validate=True)

    if with_vectors:
        ops = get_current_ops()
        vectors = [
            ("apple", ops.asarray([1, 2, 3])),
            ("orange", ops.asarray([-1, -2, -3])),
            ("and", ops.asarray([-1, -1, -1])),
            ("juice", ops.asarray([5, 5, 10])),
            ("pie", ops.asarray([7, 6.3, 8.9])),
        ]
        add_vecs_to_vocab(nlp.vocab, vectors)

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

    # Check that the Tok2Vec component finds its listeners
    optimizer = nlp.initialize(lambda: train_examples)
    assert tok2vec.listeners == [tagger_tok2vec]

    for i in range(5):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)

    doc = nlp("Running the pipeline as a whole.")
    doc_tensor = tagger_tok2vec.predict([doc])[0]
    ops = get_current_ops()
    assert_array_equal(ops.to_numpy(doc.tensor), ops.to_numpy(doc_tensor))

    # test with empty doc
    doc = nlp("")

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


def test_tok2vec_listener_overfitting():
    """Test that a pipeline with a listener properly overfits, even if 'tok2vec' is in the annotating components"""
    orig_config = Config().from_str(cfg_string)
    nlp = util.load_model_from_config(orig_config, auto_fill=True, validate=True)
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    optimizer = nlp.initialize(get_examples=lambda: train_examples)

    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses, annotates=["tok2vec"])
    assert losses["tagger"] < 0.00001

    # test the trained model
    test_text = "I like blue eggs"
    doc = nlp(test_text)
    assert doc[0].tag_ == "N"
    assert doc[1].tag_ == "V"
    assert doc[2].tag_ == "J"
    assert doc[3].tag_ == "N"

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        assert doc2[0].tag_ == "N"
        assert doc2[1].tag_ == "V"
        assert doc2[2].tag_ == "J"
        assert doc2[3].tag_ == "N"


def test_tok2vec_frozen_not_annotating():
    """Test that a pipeline with a frozen tok2vec raises an error when the tok2vec is not annotating"""
    orig_config = Config().from_str(cfg_string)
    nlp = util.load_model_from_config(orig_config, auto_fill=True, validate=True)
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    optimizer = nlp.initialize(get_examples=lambda: train_examples)

    for i in range(2):
        losses = {}
        with pytest.raises(
            ValueError, match=r"the tok2vec embedding layer is not updated"
        ):
            nlp.update(
                train_examples, sgd=optimizer, losses=losses, exclude=["tok2vec"]
            )


def test_tok2vec_frozen_overfitting():
    """Test that a pipeline with a frozen & annotating tok2vec can still overfit"""
    orig_config = Config().from_str(cfg_string)
    nlp = util.load_model_from_config(orig_config, auto_fill=True, validate=True)
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    optimizer = nlp.initialize(get_examples=lambda: train_examples)

    for i in range(100):
        losses = {}
        nlp.update(
            train_examples,
            sgd=optimizer,
            losses=losses,
            exclude=["tok2vec"],
            annotates=["tok2vec"],
        )
    assert losses["tagger"] < 0.0001

    # test the trained model
    test_text = "I like blue eggs"
    doc = nlp(test_text)
    assert doc[0].tag_ == "N"
    assert doc[1].tag_ == "V"
    assert doc[2].tag_ == "J"
    assert doc[3].tag_ == "N"

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        assert doc2[0].tag_ == "N"
        assert doc2[1].tag_ == "V"
        assert doc2[2].tag_ == "J"
        assert doc2[3].tag_ == "N"


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
    @architectures = "spacy.Tagger.v2"
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
            "nlp": {
                "lang": "en",
                "pipeline": ["tok2vec", "tagger2", "ner3", "tagger4"],
            },
            "components": {
                "tok2vec": {"source": base_model},
                "tagger2": {
                    "source": base_model,
                    "component": "tagger",
                    "replace_listeners": ["model.tok2vec"],
                },
                "ner3": {
                    "source": base_model,
                    "component": "ner",
                },
                "tagger4": {
                    "source": base_model,
                    "component": "tagger",
                },
            },
        }
        new_nlp = util.load_model_from_config(new_config, auto_fill=True)
    new_nlp.initialize(lambda: examples)
    tok2vec = new_nlp.get_pipe("tok2vec")
    tagger = new_nlp.get_pipe("tagger2")
    ner = new_nlp.get_pipe("ner3")
    assert "ner" not in new_nlp.pipe_names
    assert "tagger" not in new_nlp.pipe_names
    assert tok2vec.listening_components == ["ner3", "tagger4"]
    assert any(isinstance(node, Tok2VecListener) for node in ner.model.walk())
    assert not any(isinstance(node, Tok2VecListener) for node in tagger.model.walk())
    t2v_cfg = new_nlp.config["components"]["tok2vec"]["model"]
    assert t2v_cfg["@architectures"] == "spacy.Tok2Vec.v2"
    assert new_nlp.config["components"]["tagger2"]["model"]["tok2vec"] == t2v_cfg
    assert (
        new_nlp.config["components"]["ner3"]["model"]["tok2vec"]["@architectures"]
        == "spacy.Tok2VecListener.v1"
    )
    assert (
        new_nlp.config["components"]["tagger4"]["model"]["tok2vec"]["@architectures"]
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
    @architectures = "spacy.Tagger.v2"
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


def test_tok2vec_listener_source_link_name():
    """The component's internal name and the tok2vec listener map correspond
    to the most recently modified pipeline.
    """
    orig_config = Config().from_str(cfg_string_multi)
    nlp1 = util.load_model_from_config(orig_config, auto_fill=True, validate=True)
    assert nlp1.get_pipe("tok2vec").listening_components == ["tagger", "ner"]

    nlp2 = English()
    nlp2.add_pipe("tok2vec", source=nlp1)
    nlp2.add_pipe("tagger", name="tagger2", source=nlp1)

    # there is no way to have the component have the right name for both
    # pipelines, right now the most recently modified pipeline is prioritized
    assert nlp1.get_pipe("tagger").name == nlp2.get_pipe("tagger2").name == "tagger2"

    # there is no way to have the tok2vec have the right listener map for both
    # pipelines, right now the most recently modified pipeline is prioritized
    assert nlp2.get_pipe("tok2vec").listening_components == ["tagger2"]
    nlp2.add_pipe("ner", name="ner3", source=nlp1)
    assert nlp2.get_pipe("tok2vec").listening_components == ["tagger2", "ner3"]
    nlp2.remove_pipe("ner3")
    assert nlp2.get_pipe("tok2vec").listening_components == ["tagger2"]
    nlp2.remove_pipe("tagger2")
    assert nlp2.get_pipe("tok2vec").listening_components == []

    # at this point the tok2vec component corresponds to nlp2
    assert nlp1.get_pipe("tok2vec").listening_components == []

    # modifying the nlp1 pipeline syncs the tok2vec listener map back to nlp1
    nlp1.add_pipe("sentencizer")
    assert nlp1.get_pipe("tok2vec").listening_components == ["tagger", "ner"]

    # modifying nlp2 syncs it back to nlp2
    nlp2.add_pipe("sentencizer")
    assert nlp1.get_pipe("tok2vec").listening_components == []


def test_tok2vec_listener_source_replace_listeners():
    orig_config = Config().from_str(cfg_string_multi)
    nlp1 = util.load_model_from_config(orig_config, auto_fill=True, validate=True)
    assert nlp1.get_pipe("tok2vec").listening_components == ["tagger", "ner"]
    nlp1.replace_listeners("tok2vec", "tagger", ["model.tok2vec"])
    assert nlp1.get_pipe("tok2vec").listening_components == ["ner"]

    nlp2 = English()
    nlp2.add_pipe("tok2vec", source=nlp1)
    assert nlp2.get_pipe("tok2vec").listening_components == []
    nlp2.add_pipe("tagger", source=nlp1)
    assert nlp2.get_pipe("tok2vec").listening_components == []
    nlp2.add_pipe("ner", name="ner2", source=nlp1)
    assert nlp2.get_pipe("tok2vec").listening_components == ["ner2"]
