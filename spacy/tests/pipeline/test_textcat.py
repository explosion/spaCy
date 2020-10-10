import pytest
import random
import numpy.random
from thinc.api import fix_random_seed
from spacy import util
from spacy.lang.en import English
from spacy.language import Language
from spacy.pipeline import TextCategorizer
from spacy.tokens import Doc
from spacy.pipeline.tok2vec import DEFAULT_TOK2VEC_MODEL
from spacy.scorer import Scorer
from spacy.training import Example

from ..util import make_tempdir


TRAIN_DATA = [
    ("I'm so happy.", {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}),
    ("I'm so angry", {"cats": {"POSITIVE": 0.0, "NEGATIVE": 1.0}}),
]


def make_get_examples(nlp):
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))

    def get_examples():
        return train_examples

    return get_examples


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


def test_label_types():
    nlp = Language()
    textcat = nlp.add_pipe("textcat")
    textcat.add_label("answer")
    with pytest.raises(ValueError):
        textcat.add_label(9)


def test_no_label():
    nlp = Language()
    nlp.add_pipe("textcat")
    with pytest.raises(ValueError):
        nlp.initialize()


def test_implicit_label():
    nlp = Language()
    nlp.add_pipe("textcat")
    nlp.initialize(get_examples=make_get_examples(nlp))


def test_no_resize():
    nlp = Language()
    textcat = nlp.add_pipe("textcat")
    textcat.add_label("POSITIVE")
    textcat.add_label("NEGATIVE")
    nlp.initialize()
    assert textcat.model.get_dim("nO") == 2
    # this throws an error because the textcat can't be resized after initialization
    with pytest.raises(ValueError):
        textcat.add_label("NEUTRAL")


def test_initialize_examples():
    nlp = Language()
    textcat = nlp.add_pipe("textcat")
    for text, annotations in TRAIN_DATA:
        for label, value in annotations.get("cats").items():
            textcat.add_label(label)
    # you shouldn't really call this more than once, but for testing it should be fine
    nlp.initialize()
    get_examples = make_get_examples(nlp)
    nlp.initialize(get_examples=get_examples)
    with pytest.raises(TypeError):
        nlp.initialize(get_examples=lambda: None)
    with pytest.raises(TypeError):
        nlp.initialize(get_examples=get_examples())


def test_overfitting_IO():
    # Simple test to try and quickly overfit the textcat component - ensuring the ML models work correctly
    fix_random_seed(0)
    nlp = English()
    nlp.config["initialize"]["components"]["textcat"] = {"positive_label": "POSITIVE"}
    # Set exclusive labels
    config = {"model": {"exclusive_classes": True}}
    textcat = nlp.add_pipe("textcat", config=config)
    train_examples = []
    for text, annotations in TRAIN_DATA:
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
    assert scores["cats_score"] == 1.0
    assert "cats_score_desc" in scores


# fmt: off
@pytest.mark.parametrize(
    "textcat_config",
    [
        {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": False, "ngram_size": 1, "no_output_layer": False},
        {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": True, "ngram_size": 4, "no_output_layer": False},
        {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": False, "ngram_size": 3, "no_output_layer": True},
        {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": True, "ngram_size": 2, "no_output_layer": True},
        {"@architectures": "spacy.TextCatEnsemble.v1", "exclusive_classes": False, "ngram_size": 1, "pretrained_vectors": False, "width": 64, "conv_depth": 2, "embed_size": 2000, "window_size": 2, "dropout": None},
        {"@architectures": "spacy.TextCatEnsemble.v1", "exclusive_classes": True, "ngram_size": 5, "pretrained_vectors": False, "width": 128, "conv_depth": 2, "embed_size": 2000, "window_size": 1, "dropout": None},
        {"@architectures": "spacy.TextCatEnsemble.v1", "exclusive_classes": True, "ngram_size": 2, "pretrained_vectors": False, "width": 32, "conv_depth": 3, "embed_size": 500, "window_size": 3, "dropout": None},
        {"@architectures": "spacy.TextCatCNN.v1", "tok2vec": DEFAULT_TOK2VEC_MODEL, "exclusive_classes": True},
        {"@architectures": "spacy.TextCatCNN.v1", "tok2vec": DEFAULT_TOK2VEC_MODEL, "exclusive_classes": False},
    ],
)
# fmt: on
def test_textcat_configs(textcat_config):
    pipe_config = {"model": textcat_config}
    nlp = English()
    textcat = nlp.add_pipe("textcat", config=pipe_config)
    train_examples = []
    for text, annotations in TRAIN_DATA:
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
    get_examples = make_get_examples(nlp)
    textcat.initialize(get_examples, labels=["POS", "NEG"], positive_label="POS")
    assert textcat.labels == ("POS", "NEG")


def test_positive_class_not_present():
    nlp = English()
    textcat = nlp.add_pipe("textcat")
    get_examples = make_get_examples(nlp)
    with pytest.raises(ValueError):
        textcat.initialize(get_examples, labels=["SOME", "THING"], positive_label="POS")


def test_positive_class_not_binary():
    nlp = English()
    textcat = nlp.add_pipe("textcat")
    get_examples = make_get_examples(nlp)
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
