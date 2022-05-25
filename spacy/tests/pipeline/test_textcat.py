import random

import numpy.random
import pytest
from numpy.testing import assert_almost_equal
from thinc.api import Config, compounding, fix_random_seed, get_current_ops
from wasabi import msg

import spacy
from spacy import util
from spacy.cli.evaluate import print_prf_per_type, print_textcats_auc_per_cat
from spacy.lang.en import English
from spacy.language import Language
from spacy.pipeline import TextCategorizer
from spacy.pipeline.textcat import single_label_bow_config
from spacy.pipeline.textcat import single_label_cnn_config
from spacy.pipeline.textcat import single_label_default_config
from spacy.pipeline.textcat_multilabel import multi_label_bow_config
from spacy.pipeline.textcat_multilabel import multi_label_cnn_config
from spacy.pipeline.textcat_multilabel import multi_label_default_config
from spacy.pipeline.tok2vec import DEFAULT_TOK2VEC_MODEL
from spacy.scorer import Scorer
from spacy.tokens import Doc, DocBin
from spacy.training import Example
from spacy.training.initialize import init_nlp

from ..util import make_tempdir

TRAIN_DATA_SINGLE_LABEL = [
    ("I'm so happy.", {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}),
    ("I'm so angry", {"cats": {"POSITIVE": 0.0, "NEGATIVE": 1.0}}),
]

TRAIN_DATA_MULTI_LABEL = [
    ("I'm angry and confused", {"cats": {"ANGRY": 1.0, "CONFUSED": 1.0, "HAPPY": 0.0}}),
    ("I'm confused but happy", {"cats": {"ANGRY": 0.0, "CONFUSED": 1.0, "HAPPY": 1.0}}),
]


def make_get_examples_single_label(nlp):
    train_examples = []
    for t in TRAIN_DATA_SINGLE_LABEL:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))

    def get_examples():
        return train_examples

    return get_examples


def make_get_examples_multi_label(nlp):
    train_examples = []
    for t in TRAIN_DATA_MULTI_LABEL:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))

    def get_examples():
        return train_examples

    return get_examples


@pytest.mark.issue(3611)
def test_issue3611():
    """Test whether adding n-grams in the textcat works even when n > token length of some docs"""
    unique_classes = ["offensive", "inoffensive"]
    x_train = [
        "This is an offensive text",
        "This is the second offensive text",
        "inoff",
    ]
    y_train = ["offensive", "offensive", "inoffensive"]
    nlp = spacy.blank("en")
    # preparing the data
    train_data = []
    for text, train_instance in zip(x_train, y_train):
        cat_dict = {label: label == train_instance for label in unique_classes}
        train_data.append(Example.from_dict(nlp.make_doc(text), {"cats": cat_dict}))
    # add a text categorizer component
    model = {
        "@architectures": "spacy.TextCatBOW.v1",
        "exclusive_classes": True,
        "ngram_size": 2,
        "no_output_layer": False,
    }
    textcat = nlp.add_pipe("textcat", config={"model": model}, last=True)
    for label in unique_classes:
        textcat.add_label(label)
    # training the network
    with nlp.select_pipes(enable="textcat"):
        optimizer = nlp.initialize()
        for i in range(3):
            losses = {}
            batches = util.minibatch(train_data, size=compounding(4.0, 32.0, 1.001))

            for batch in batches:
                nlp.update(examples=batch, sgd=optimizer, drop=0.1, losses=losses)


@pytest.mark.issue(4030)
def test_issue4030():
    """Test whether textcat works fine with empty doc"""
    unique_classes = ["offensive", "inoffensive"]
    x_train = [
        "This is an offensive text",
        "This is the second offensive text",
        "inoff",
    ]
    y_train = ["offensive", "offensive", "inoffensive"]
    nlp = spacy.blank("en")
    # preparing the data
    train_data = []
    for text, train_instance in zip(x_train, y_train):
        cat_dict = {label: label == train_instance for label in unique_classes}
        train_data.append(Example.from_dict(nlp.make_doc(text), {"cats": cat_dict}))
    # add a text categorizer component
    model = {
        "@architectures": "spacy.TextCatBOW.v1",
        "exclusive_classes": True,
        "ngram_size": 2,
        "no_output_layer": False,
    }
    textcat = nlp.add_pipe("textcat", config={"model": model}, last=True)
    for label in unique_classes:
        textcat.add_label(label)
    # training the network
    with nlp.select_pipes(enable="textcat"):
        optimizer = nlp.initialize()
        for i in range(3):
            losses = {}
            batches = util.minibatch(train_data, size=compounding(4.0, 32.0, 1.001))

            for batch in batches:
                nlp.update(examples=batch, sgd=optimizer, drop=0.1, losses=losses)
    # processing of an empty doc should result in 0.0 for all categories
    doc = nlp("")
    assert doc.cats["offensive"] == 0.0
    assert doc.cats["inoffensive"] == 0.0


@pytest.mark.parametrize(
    "textcat_config",
    [
        single_label_default_config,
        single_label_bow_config,
        single_label_cnn_config,
        multi_label_default_config,
        multi_label_bow_config,
        multi_label_cnn_config,
    ],
)
@pytest.mark.issue(5551)
def test_issue5551(textcat_config):
    """Test that after fixing the random seed, the results of the pipeline are truly identical"""
    component = "textcat"

    pipe_cfg = Config().from_str(textcat_config)
    results = []
    for i in range(3):
        fix_random_seed(0)
        nlp = English()
        text = "Once hot, form ping-pong-ball-sized balls of the mixture, each weighing roughly 25 g."
        annots = {"cats": {"Labe1": 1.0, "Label2": 0.0, "Label3": 0.0}}
        pipe = nlp.add_pipe(component, config=pipe_cfg, last=True)
        for label in set(annots["cats"]):
            pipe.add_label(label)
        # Train
        nlp.initialize()
        doc = nlp.make_doc(text)
        nlp.update([Example.from_dict(doc, annots)])
        # Store the result of each iteration
        result = pipe.model.predict([doc])
        results.append(result[0])
    # All results should be the same because of the fixed seed
    assert len(results) == 3
    ops = get_current_ops()
    assert_almost_equal(ops.to_numpy(results[0]), ops.to_numpy(results[1]), decimal=5)
    assert_almost_equal(ops.to_numpy(results[0]), ops.to_numpy(results[2]), decimal=5)


CONFIG_ISSUE_6908 = """
[paths]
train = "TRAIN_PLACEHOLDER"
raw = null
init_tok2vec = null
vectors = null

[system]
seed = 0
gpu_allocator = null

[nlp]
lang = "en"
pipeline = ["textcat"]
tokenizer = {"@tokenizers":"spacy.Tokenizer.v1"}
disabled = []
before_creation = null
after_creation = null
after_pipeline_creation = null
batch_size = 1000

[components]

[components.textcat]
factory = "TEXTCAT_PLACEHOLDER"

[corpora]

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths:train}

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths:train}


[training]
train_corpus = "corpora.train"
dev_corpus = "corpora.dev"
seed = ${system.seed}
gpu_allocator = ${system.gpu_allocator}
frozen_components = []
before_to_disk = null

[pretraining]

[initialize]
vectors = ${paths.vectors}
init_tok2vec = ${paths.init_tok2vec}
vocab_data = null
lookups = null
before_init = null
after_init = null

[initialize.components]

[initialize.components.textcat]
labels = ['label1', 'label2']

[initialize.tokenizer]
"""


@pytest.mark.parametrize(
    "component_name",
    ["textcat", "textcat_multilabel"],
)
@pytest.mark.issue(6908)
def test_issue6908(component_name):
    """Test intializing textcat with labels in a list"""

    def create_data(out_file):
        nlp = spacy.blank("en")
        doc = nlp.make_doc("Some text")
        doc.cats = {"label1": 0, "label2": 1}
        out_data = DocBin(docs=[doc]).to_bytes()
        with out_file.open("wb") as file_:
            file_.write(out_data)

    with make_tempdir() as tmp_path:
        train_path = tmp_path / "train.spacy"
        create_data(train_path)
        config_str = CONFIG_ISSUE_6908.replace("TEXTCAT_PLACEHOLDER", component_name)
        config_str = config_str.replace("TRAIN_PLACEHOLDER", train_path.as_posix())
        config = util.load_config_from_str(config_str)
        init_nlp(config)


@pytest.mark.issue(7019)
def test_issue7019():
    scores = {"LABEL_A": 0.39829102, "LABEL_B": 0.938298329382, "LABEL_C": None}
    print_textcats_auc_per_cat(msg, scores)
    scores = {
        "LABEL_A": {"p": 0.3420302, "r": 0.3929020, "f": 0.49823928932},
        "LABEL_B": {"p": None, "r": None, "f": None},
    }
    print_prf_per_type(msg, scores, name="foo", type="bar")


@pytest.mark.issue(9904)
def test_issue9904():
    nlp = Language()
    textcat = nlp.add_pipe("textcat")
    get_examples = make_get_examples_single_label(nlp)
    nlp.initialize(get_examples)

    examples = get_examples()
    scores = textcat.predict([eg.predicted for eg in examples])

    loss = textcat.get_loss(examples, scores)[0]
    loss_double_bs = textcat.get_loss(examples * 2, scores.repeat(2, axis=0))[0]
    assert loss == pytest.approx(loss_double_bs)


@pytest.mark.skip(reason="Test is flakey when run with others")
def test_simple_train():
    nlp = Language()
    textcat = nlp.add_pipe("textcat")
    textcat.add_label("answer")
    nlp.initialize()
    for i in range(5):
        for text, answer in [
            ("aaaa", 1.0),
            ("bbbb", 0),
            ("aa", 1.0),
            ("bbbbbbbbb", 0.0),
            ("aaaaaa", 1),
        ]:
            nlp.update((text, {"cats": {"answer": answer}}))
    doc = nlp("aaa")
    assert "answer" in doc.cats
    assert doc.cats["answer"] >= 0.5


@pytest.mark.skip(reason="Test is flakey when run with others")
def test_textcat_learns_multilabel():
    random.seed(5)
    numpy.random.seed(5)
    docs = []
    nlp = Language()
    letters = ["a", "b", "c"]
    for w1 in letters:
        for w2 in letters:
            cats = {letter: float(w2 == letter) for letter in letters}
            docs.append((Doc(nlp.vocab, words=["d"] * 3 + [w1, w2] + ["d"] * 3), cats))
    random.shuffle(docs)
    textcat = TextCategorizer(nlp.vocab, width=8)
    for letter in letters:
        textcat.add_label(letter)
    optimizer = textcat.initialize(lambda: [])
    for i in range(30):
        losses = {}
        examples = [Example.from_dict(doc, {"cats": cats}) for doc, cat in docs]
        textcat.update(examples, sgd=optimizer, losses=losses)
        random.shuffle(docs)
    for w1 in letters:
        for w2 in letters:
            doc = Doc(nlp.vocab, words=["d"] * 3 + [w1, w2] + ["d"] * 3)
            truth = {letter: w2 == letter for letter in letters}
            textcat(doc)
            for cat, score in doc.cats.items():
                if not truth[cat]:
                    assert score < 0.5
                else:
                    assert score > 0.5


@pytest.mark.parametrize("name", ["textcat", "textcat_multilabel"])
def test_label_types(name):
    nlp = Language()
    textcat = nlp.add_pipe(name)
    textcat.add_label("answer")
    with pytest.raises(ValueError):
        textcat.add_label(9)
    # textcat requires at least two labels
    if name == "textcat":
        with pytest.raises(ValueError):
            nlp.initialize()
    else:
        nlp.initialize()


@pytest.mark.parametrize("name", ["textcat", "textcat_multilabel"])
def test_no_label(name):
    nlp = Language()
    nlp.add_pipe(name)
    with pytest.raises(ValueError):
        nlp.initialize()


@pytest.mark.parametrize(
    "name,get_examples",
    [
        ("textcat", make_get_examples_single_label),
        ("textcat_multilabel", make_get_examples_multi_label),
    ],
)
def test_implicit_label(name, get_examples):
    nlp = Language()
    nlp.add_pipe(name)
    nlp.initialize(get_examples=get_examples(nlp))


# fmt: off
@pytest.mark.slow
@pytest.mark.parametrize(
    "name,textcat_config",
    [
        # BOW
        ("textcat", {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": True, "no_output_layer": False, "ngram_size": 3}),
        ("textcat", {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": True, "no_output_layer": True, "ngram_size": 3}),
        ("textcat_multilabel", {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": False, "no_output_layer": False, "ngram_size": 3}),
        ("textcat_multilabel", {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": False, "no_output_layer": True, "ngram_size": 3}),
        # ENSEMBLE V1
        ("textcat", {"@architectures": "spacy.TextCatEnsemble.v1", "exclusive_classes": False, "pretrained_vectors": None, "width": 64, "embed_size": 2000, "conv_depth": 2, "window_size": 1, "ngram_size": 1, "dropout": None}),
        ("textcat_multilabel", {"@architectures": "spacy.TextCatEnsemble.v1", "exclusive_classes": False, "pretrained_vectors": None, "width": 64, "embed_size": 2000, "conv_depth": 2, "window_size": 1, "ngram_size": 1, "dropout": None}),
        # ENSEMBLE V2
        ("textcat", {"@architectures": "spacy.TextCatEnsemble.v2", "tok2vec": DEFAULT_TOK2VEC_MODEL, "linear_model": {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": True, "no_output_layer": False, "ngram_size": 3}}),
        ("textcat", {"@architectures": "spacy.TextCatEnsemble.v2", "tok2vec": DEFAULT_TOK2VEC_MODEL, "linear_model": {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": True, "no_output_layer": True, "ngram_size": 3}}),
        ("textcat_multilabel", {"@architectures": "spacy.TextCatEnsemble.v2", "tok2vec": DEFAULT_TOK2VEC_MODEL, "linear_model": {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": False, "no_output_layer": False, "ngram_size": 3}}),
        ("textcat_multilabel", {"@architectures": "spacy.TextCatEnsemble.v2", "tok2vec": DEFAULT_TOK2VEC_MODEL, "linear_model": {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": False, "no_output_layer": True, "ngram_size": 3}}),
        # CNN
        ("textcat", {"@architectures": "spacy.TextCatCNN.v1", "tok2vec": DEFAULT_TOK2VEC_MODEL, "exclusive_classes": True}),
        ("textcat_multilabel", {"@architectures": "spacy.TextCatCNN.v1", "tok2vec": DEFAULT_TOK2VEC_MODEL, "exclusive_classes": False}),
    ],
)
# fmt: on
def test_no_resize(name, textcat_config):
    """The old textcat architectures weren't resizable"""
    nlp = Language()
    pipe_config = {"model": textcat_config}
    textcat = nlp.add_pipe(name, config=pipe_config)
    textcat.add_label("POSITIVE")
    textcat.add_label("NEGATIVE")
    nlp.initialize()
    assert textcat.model.maybe_get_dim("nO") in [2, None]
    # this throws an error because the textcat can't be resized after initialization
    with pytest.raises(ValueError):
        textcat.add_label("NEUTRAL")


# fmt: off
@pytest.mark.parametrize(
    "name,textcat_config",
    [
        # BOW
        ("textcat", {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": True, "no_output_layer": False, "ngram_size": 3}),
        ("textcat", {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": True, "no_output_layer": True, "ngram_size": 3}),
        ("textcat_multilabel", {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": False, "no_output_layer": False, "ngram_size": 3}),
        ("textcat_multilabel", {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": False, "no_output_layer": True, "ngram_size": 3}),
        # CNN
        ("textcat", {"@architectures": "spacy.TextCatCNN.v2", "tok2vec": DEFAULT_TOK2VEC_MODEL, "exclusive_classes": True}),
        ("textcat_multilabel", {"@architectures": "spacy.TextCatCNN.v2", "tok2vec": DEFAULT_TOK2VEC_MODEL, "exclusive_classes": False}),
    ],
)
# fmt: on
def test_resize(name, textcat_config):
    """The new textcat architectures are resizable"""
    nlp = Language()
    pipe_config = {"model": textcat_config}
    textcat = nlp.add_pipe(name, config=pipe_config)
    textcat.add_label("POSITIVE")
    textcat.add_label("NEGATIVE")
    assert textcat.model.maybe_get_dim("nO") in [2, None]
    nlp.initialize()
    assert textcat.model.maybe_get_dim("nO") in [2, None]
    textcat.add_label("NEUTRAL")
    assert textcat.model.maybe_get_dim("nO") in [3, None]


# fmt: off
@pytest.mark.parametrize(
    "name,textcat_config",
    [
        # BOW
        ("textcat", {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": True, "no_output_layer": False, "ngram_size": 3}),
        ("textcat", {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": True, "no_output_layer": True, "ngram_size": 3}),
        ("textcat_multilabel", {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": False, "no_output_layer": False, "ngram_size": 3}),
        ("textcat_multilabel", {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": False, "no_output_layer": True, "ngram_size": 3}),
        # CNN
        ("textcat", {"@architectures": "spacy.TextCatCNN.v2", "tok2vec": DEFAULT_TOK2VEC_MODEL, "exclusive_classes": True}),
        ("textcat_multilabel", {"@architectures": "spacy.TextCatCNN.v2", "tok2vec": DEFAULT_TOK2VEC_MODEL, "exclusive_classes": False}),
    ],
)
# fmt: on
def test_resize_same_results(name, textcat_config):
    # Ensure that the resized textcat classifiers still produce the same results for old labels
    fix_random_seed(0)
    nlp = English()
    pipe_config = {"model": textcat_config}
    textcat = nlp.add_pipe(name, config=pipe_config)

    train_examples = []
    for text, annotations in TRAIN_DATA_SINGLE_LABEL:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    assert textcat.model.maybe_get_dim("nO") in [2, None]

    for i in range(5):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)

    # test the trained model before resizing
    test_text = "I am happy."
    doc = nlp(test_text)
    assert len(doc.cats) == 2
    pos_pred = doc.cats["POSITIVE"]
    neg_pred = doc.cats["NEGATIVE"]

    # test the trained model again after resizing
    textcat.add_label("NEUTRAL")
    doc = nlp(test_text)
    assert len(doc.cats) == 3
    assert doc.cats["POSITIVE"] == pos_pred
    assert doc.cats["NEGATIVE"] == neg_pred
    assert doc.cats["NEUTRAL"] <= 1

    for i in range(5):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)

    # test the trained model again after training further with new label
    doc = nlp(test_text)
    assert len(doc.cats) == 3
    assert doc.cats["POSITIVE"] != pos_pred
    assert doc.cats["NEGATIVE"] != neg_pred
    for cat in doc.cats:
        assert doc.cats[cat] <= 1


def test_error_with_multi_labels():
    nlp = Language()
    nlp.add_pipe("textcat")
    train_examples = []
    for text, annotations in TRAIN_DATA_MULTI_LABEL:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
    with pytest.raises(ValueError):
        nlp.initialize(get_examples=lambda: train_examples)


@pytest.mark.parametrize(
    "name,get_examples, train_data",
    [
        ("textcat", make_get_examples_single_label, TRAIN_DATA_SINGLE_LABEL),
        ("textcat_multilabel", make_get_examples_multi_label, TRAIN_DATA_MULTI_LABEL),
    ],
)
def test_initialize_examples(name, get_examples, train_data):
    nlp = Language()
    textcat = nlp.add_pipe(name)
    for text, annotations in train_data:
        for label, value in annotations.get("cats").items():
            textcat.add_label(label)
    # you shouldn't really call this more than once, but for testing it should be fine
    nlp.initialize()
    nlp.initialize(get_examples=get_examples(nlp))
    with pytest.raises(TypeError):
        nlp.initialize(get_examples=lambda: None)
    with pytest.raises(TypeError):
        nlp.initialize(get_examples=get_examples())


def test_overfitting_IO():
    # Simple test to try and quickly overfit the single-label textcat component - ensuring the ML models work correctly
    fix_random_seed(0)
    nlp = English()
    textcat = nlp.add_pipe("textcat")

    train_examples = []
    for text, annotations in TRAIN_DATA_SINGLE_LABEL:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    assert textcat.model.get_dim("nO") == 2

    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["textcat"] < 0.01

    # test the trained model
    test_text = "I am happy."
    doc = nlp(test_text)
    cats = doc.cats
    assert cats["POSITIVE"] > 0.9
    assert cats["POSITIVE"] + cats["NEGATIVE"] == pytest.approx(1.0, 0.001)

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        cats2 = doc2.cats
        assert cats2["POSITIVE"] > 0.9
        assert cats2["POSITIVE"] + cats2["NEGATIVE"] == pytest.approx(1.0, 0.001)

    # Test scoring
    scores = nlp.evaluate(train_examples)
    assert scores["cats_micro_f"] == 1.0
    assert scores["cats_macro_f"] == 1.0
    assert scores["cats_macro_auc"] == 1.0
    assert scores["cats_score"] == 1.0
    assert "cats_score_desc" in scores

    # Make sure that running pipe twice, or comparing to call, always amounts to the same predictions
    texts = ["Just a sentence.", "I like green eggs.", "I am happy.", "I eat ham."]
    batch_cats_1 = [doc.cats for doc in nlp.pipe(texts)]
    batch_cats_2 = [doc.cats for doc in nlp.pipe(texts)]
    no_batch_cats = [doc.cats for doc in [nlp(text) for text in texts]]
    for cats_1, cats_2 in zip(batch_cats_1, batch_cats_2):
        for cat in cats_1:
            assert_almost_equal(cats_1[cat], cats_2[cat], decimal=5)
    for cats_1, cats_2 in zip(batch_cats_1, no_batch_cats):
        for cat in cats_1:
            assert_almost_equal(cats_1[cat], cats_2[cat], decimal=5)


def test_overfitting_IO_multi():
    # Simple test to try and quickly overfit the multi-label textcat component - ensuring the ML models work correctly
    fix_random_seed(0)
    nlp = English()
    textcat = nlp.add_pipe("textcat_multilabel")

    train_examples = []
    for text, annotations in TRAIN_DATA_MULTI_LABEL:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    assert textcat.model.get_dim("nO") == 3

    for i in range(100):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["textcat_multilabel"] < 0.01

    # test the trained model
    test_text = "I am confused but happy."
    doc = nlp(test_text)
    cats = doc.cats
    assert cats["HAPPY"] > 0.9
    assert cats["CONFUSED"] > 0.9

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        cats2 = doc2.cats
        assert cats2["HAPPY"] > 0.9
        assert cats2["CONFUSED"] > 0.9

    # Test scoring
    scores = nlp.evaluate(train_examples)
    assert scores["cats_micro_f"] == 1.0
    assert scores["cats_macro_f"] == 1.0
    assert "cats_score_desc" in scores

    # Make sure that running pipe twice, or comparing to call, always amounts to the same predictions
    texts = ["Just a sentence.", "I like green eggs.", "I am happy.", "I eat ham."]
    batch_deps_1 = [doc.cats for doc in nlp.pipe(texts)]
    batch_deps_2 = [doc.cats for doc in nlp.pipe(texts)]
    no_batch_deps = [doc.cats for doc in [nlp(text) for text in texts]]
    for cats_1, cats_2 in zip(batch_deps_1, batch_deps_2):
        for cat in cats_1:
            assert_almost_equal(cats_1[cat], cats_2[cat], decimal=5)
    for cats_1, cats_2 in zip(batch_deps_1, no_batch_deps):
        for cat in cats_1:
            assert_almost_equal(cats_1[cat], cats_2[cat], decimal=5)


# fmt: off
@pytest.mark.slow
@pytest.mark.parametrize(
    "name,train_data,textcat_config",
    [
        # BOW V1
        ("textcat_multilabel", TRAIN_DATA_MULTI_LABEL, {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": False, "ngram_size": 1, "no_output_layer": False}),
        ("textcat", TRAIN_DATA_SINGLE_LABEL, {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": True, "ngram_size": 4, "no_output_layer": False}),
        # ENSEMBLE V1
        ("textcat_multilabel", TRAIN_DATA_MULTI_LABEL, {"@architectures": "spacy.TextCatEnsemble.v1", "exclusive_classes": False, "pretrained_vectors": None, "width": 64, "embed_size": 2000, "conv_depth": 2, "window_size": 1, "ngram_size": 1, "dropout": None}),
        ("textcat", TRAIN_DATA_SINGLE_LABEL, {"@architectures": "spacy.TextCatEnsemble.v1", "exclusive_classes": False, "pretrained_vectors": None, "width": 64, "embed_size": 2000, "conv_depth": 2, "window_size": 1, "ngram_size": 1, "dropout": None}),
        # CNN V1
        ("textcat", TRAIN_DATA_SINGLE_LABEL, {"@architectures": "spacy.TextCatCNN.v1", "tok2vec": DEFAULT_TOK2VEC_MODEL, "exclusive_classes": True}),
        ("textcat_multilabel", TRAIN_DATA_MULTI_LABEL, {"@architectures": "spacy.TextCatCNN.v1", "tok2vec": DEFAULT_TOK2VEC_MODEL, "exclusive_classes": False}),
        # BOW V2
        ("textcat_multilabel", TRAIN_DATA_MULTI_LABEL, {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": False, "ngram_size": 1, "no_output_layer": False}),
        ("textcat", TRAIN_DATA_SINGLE_LABEL, {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": True, "ngram_size": 4, "no_output_layer": False}),
        ("textcat_multilabel", TRAIN_DATA_MULTI_LABEL, {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": False, "ngram_size": 3, "no_output_layer": True}),
        ("textcat", TRAIN_DATA_SINGLE_LABEL, {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": True, "ngram_size": 2, "no_output_layer": True}),
        # ENSEMBLE V2
        ("textcat_multilabel", TRAIN_DATA_MULTI_LABEL, {"@architectures": "spacy.TextCatEnsemble.v2", "tok2vec": DEFAULT_TOK2VEC_MODEL, "linear_model": {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": False, "ngram_size": 1, "no_output_layer": False}}),
        ("textcat", TRAIN_DATA_SINGLE_LABEL, {"@architectures": "spacy.TextCatEnsemble.v2", "tok2vec": DEFAULT_TOK2VEC_MODEL, "linear_model": {"@architectures": "spacy.TextCatBOW.v2", "exclusive_classes": True, "ngram_size": 5, "no_output_layer": False}}),
        # CNN V2
        ("textcat", TRAIN_DATA_SINGLE_LABEL, {"@architectures": "spacy.TextCatCNN.v2", "tok2vec": DEFAULT_TOK2VEC_MODEL, "exclusive_classes": True}),
        ("textcat_multilabel", TRAIN_DATA_MULTI_LABEL, {"@architectures": "spacy.TextCatCNN.v2", "tok2vec": DEFAULT_TOK2VEC_MODEL, "exclusive_classes": False}),
    ],
)
# fmt: on
def test_textcat_configs(name, train_data, textcat_config):
    pipe_config = {"model": textcat_config}
    nlp = English()
    textcat = nlp.add_pipe(name, config=pipe_config)
    train_examples = []
    for text, annotations in train_data:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for label, value in annotations.get("cats").items():
            textcat.add_label(label)
    optimizer = nlp.initialize()
    for i in range(5):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)


def test_positive_class():
    nlp = English()
    textcat = nlp.add_pipe("textcat")
    get_examples = make_get_examples_single_label(nlp)
    textcat.initialize(get_examples, labels=["POS", "NEG"], positive_label="POS")
    assert textcat.labels == ("POS", "NEG")
    assert textcat.cfg["positive_label"] == "POS"

    textcat_multilabel = nlp.add_pipe("textcat_multilabel")
    get_examples = make_get_examples_multi_label(nlp)
    with pytest.raises(TypeError):
        textcat_multilabel.initialize(
            get_examples, labels=["POS", "NEG"], positive_label="POS"
        )
    textcat_multilabel.initialize(get_examples, labels=["FICTION", "DRAMA"])
    assert textcat_multilabel.labels == ("FICTION", "DRAMA")
    assert "positive_label" not in textcat_multilabel.cfg


def test_positive_class_not_present():
    nlp = English()
    textcat = nlp.add_pipe("textcat")
    get_examples = make_get_examples_single_label(nlp)
    with pytest.raises(ValueError):
        textcat.initialize(get_examples, labels=["SOME", "THING"], positive_label="POS")


def test_positive_class_not_binary():
    nlp = English()
    textcat = nlp.add_pipe("textcat")
    get_examples = make_get_examples_multi_label(nlp)
    with pytest.raises(ValueError):
        textcat.initialize(
            get_examples, labels=["SOME", "THING", "POS"], positive_label="POS"
        )


def test_textcat_evaluation():
    train_examples = []
    nlp = English()
    ref1 = nlp("one")
    ref1.cats = {"winter": 1.0, "summer": 1.0, "spring": 1.0, "autumn": 1.0}
    pred1 = nlp("one")
    pred1.cats = {"winter": 1.0, "summer": 0.0, "spring": 1.0, "autumn": 1.0}
    train_examples.append(Example(pred1, ref1))

    ref2 = nlp("two")
    ref2.cats = {"winter": 0.0, "summer": 0.0, "spring": 1.0, "autumn": 1.0}
    pred2 = nlp("two")
    pred2.cats = {"winter": 1.0, "summer": 0.0, "spring": 0.0, "autumn": 1.0}
    train_examples.append(Example(pred2, ref2))

    scores = Scorer().score_cats(
        train_examples, "cats", labels=["winter", "summer", "spring", "autumn"]
    )
    assert scores["cats_f_per_type"]["winter"]["p"] == 1 / 2
    assert scores["cats_f_per_type"]["winter"]["r"] == 1 / 1
    assert scores["cats_f_per_type"]["summer"]["p"] == 0
    assert scores["cats_f_per_type"]["summer"]["r"] == 0 / 1
    assert scores["cats_f_per_type"]["spring"]["p"] == 1 / 1
    assert scores["cats_f_per_type"]["spring"]["r"] == 1 / 2
    assert scores["cats_f_per_type"]["autumn"]["p"] == 2 / 2
    assert scores["cats_f_per_type"]["autumn"]["r"] == 2 / 2

    assert scores["cats_micro_p"] == 4 / 5
    assert scores["cats_micro_r"] == 4 / 6


@pytest.mark.parametrize(
    "multi_label,spring_p",
    [(True, 1 / 1), (False, 1 / 2)],
)
def test_textcat_eval_missing(multi_label: bool, spring_p: float):
    """
    multi-label: the missing 'spring' in gold_doc_2 doesn't incur a penalty
    exclusive labels: the missing 'spring' in gold_doc_2 is interpreted as 0.0"""
    train_examples = []
    nlp = English()

    ref1 = nlp("one")
    ref1.cats = {"winter": 0.0, "summer": 0.0, "autumn": 0.0, "spring": 1.0}
    pred1 = nlp("one")
    pred1.cats = {"winter": 0.0, "summer": 0.0, "autumn": 0.0, "spring": 1.0}
    train_examples.append(Example(ref1, pred1))

    ref2 = nlp("two")
    # reference 'spring' is missing, pred 'spring' is 1
    ref2.cats = {"winter": 0.0, "summer": 0.0, "autumn": 1.0}
    pred2 = nlp("two")
    pred2.cats = {"winter": 0.0, "summer": 0.0, "autumn": 0.0, "spring": 1.0}
    train_examples.append(Example(pred2, ref2))

    scores = Scorer().score_cats(
        train_examples,
        "cats",
        labels=["winter", "summer", "spring", "autumn"],
        multi_label=multi_label,
    )
    assert scores["cats_f_per_type"]["spring"]["p"] == spring_p
    assert scores["cats_f_per_type"]["spring"]["r"] == 1 / 1


@pytest.mark.parametrize(
    "multi_label,expected_loss",
    [(True, 0), (False, 0.125)],
)
def test_textcat_loss(multi_label: bool, expected_loss: float):
    """
    multi-label: the missing 'spring' in gold_doc_2 doesn't incur an increase in loss
    exclusive labels: the missing 'spring' in gold_doc_2 is interpreted as 0.0 and adds to the loss"""
    train_examples = []
    nlp = English()

    doc1 = nlp("one")
    cats1 = {"winter": 0.0, "summer": 0.0, "autumn": 0.0, "spring": 1.0}
    train_examples.append(Example.from_dict(doc1, {"cats": cats1}))

    doc2 = nlp("two")
    cats2 = {"winter": 0.0, "summer": 0.0, "autumn": 1.0}
    train_examples.append(Example.from_dict(doc2, {"cats": cats2}))

    if multi_label:
        textcat = nlp.add_pipe("textcat_multilabel")
    else:
        textcat = nlp.add_pipe("textcat")
    textcat.initialize(lambda: train_examples)
    assert isinstance(textcat, TextCategorizer)
    scores = textcat.model.ops.asarray(
        [[0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 1.0, 1.0]], dtype="f"  # type: ignore
    )
    loss, d_scores = textcat.get_loss(train_examples, scores)
    assert loss == expected_loss


def test_textcat_threshold():
    # Ensure the scorer can be called with a different threshold
    nlp = English()
    nlp.add_pipe("textcat")

    train_examples = []
    for text, annotations in TRAIN_DATA_SINGLE_LABEL:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
    nlp.initialize(get_examples=lambda: train_examples)

    # score the model (it's not actually trained but that doesn't matter)
    scores = nlp.evaluate(train_examples)
    assert 0 <= scores["cats_score"] <= 1

    scores = nlp.evaluate(train_examples, scorer_cfg={"threshold": 1.0})
    assert scores["cats_f_per_type"]["POSITIVE"]["r"] == 0

    scores = nlp.evaluate(train_examples, scorer_cfg={"threshold": 0})
    macro_f = scores["cats_score"]
    assert scores["cats_f_per_type"]["POSITIVE"]["r"] == 1.0

    scores = nlp.evaluate(
        train_examples, scorer_cfg={"threshold": 0, "positive_label": "POSITIVE"}
    )
    pos_f = scores["cats_score"]
    assert scores["cats_f_per_type"]["POSITIVE"]["r"] == 1.0
    assert pos_f > macro_f


def test_textcat_multi_threshold():
    # Ensure the scorer can be called with a different threshold
    nlp = English()
    nlp.add_pipe("textcat_multilabel")

    train_examples = []
    for text, annotations in TRAIN_DATA_SINGLE_LABEL:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
    nlp.initialize(get_examples=lambda: train_examples)

    # score the model (it's not actually trained but that doesn't matter)
    scores = nlp.evaluate(train_examples)
    assert 0 <= scores["cats_score"] <= 1

    scores = nlp.evaluate(train_examples, scorer_cfg={"threshold": 1.0})
    assert scores["cats_f_per_type"]["POSITIVE"]["r"] == 0

    scores = nlp.evaluate(train_examples, scorer_cfg={"threshold": 0})
    assert scores["cats_f_per_type"]["POSITIVE"]["r"] == 1.0
