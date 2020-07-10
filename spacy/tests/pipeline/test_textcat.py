import pytest
import random
import numpy.random
from thinc.api import fix_random_seed
from spacy import util
from spacy.lang.en import English
from spacy.language import Language
from spacy.pipeline import TextCategorizer
from spacy.tokens import Doc
from spacy.pipeline.defaults import default_tok2vec

from ..util import make_tempdir
from ...gold import Example


TRAIN_DATA = [
    ("I'm so happy.", {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}),
    ("I'm so angry", {"cats": {"POSITIVE": 0.0, "NEGATIVE": 1.0}}),
]


@pytest.mark.skip(reason="Test is flakey when run with others")
def test_simple_train():
    nlp = Language()
    nlp.add_pipe(nlp.create_pipe("textcat"))
    nlp.get_pipe("textcat").add_label("answer")
    nlp.begin_training()
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
    optimizer = textcat.begin_training()
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
    nlp.add_pipe(nlp.create_pipe("textcat"))
    nlp.get_pipe("textcat").add_label("answer")
    with pytest.raises(ValueError):
        nlp.get_pipe("textcat").add_label(9)


def test_overfitting_IO():
    # Simple test to try and quickly overfit the textcat component - ensuring the ML models work correctly
    fix_random_seed(0)
    nlp = English()
    textcat = nlp.create_pipe("textcat", config={"exclusive_classes": True})
    train_examples = []
    for text, annotations in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for label, value in annotations.get("cats").items():
            textcat.add_label(label)
    nlp.add_pipe(textcat)
    optimizer = nlp.begin_training()

    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["textcat"] < 0.01

    # test the trained model
    test_text = "I am happy."
    doc = nlp(test_text)
    cats = doc.cats
    # note that by default, exclusive_classes = false so we need a bigger error margin
    assert cats["POSITIVE"] > 0.9
    assert cats["POSITIVE"] + cats["NEGATIVE"] == pytest.approx(1.0, 0.1)

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        cats2 = doc2.cats
        assert cats2["POSITIVE"] > 0.9
        assert cats2["POSITIVE"] + cats2["NEGATIVE"] == pytest.approx(1.0, 0.1)


# fmt: off
@pytest.mark.parametrize(
    "textcat_config",
    [
        {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": False, "ngram_size": 1, "no_output_layer": False},
        {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": True, "ngram_size": 4, "no_output_layer": False},
        {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": False, "ngram_size": 3, "no_output_layer": True},
        {"@architectures": "spacy.TextCatBOW.v1", "exclusive_classes": True, "ngram_size": 2, "no_output_layer": True},
        {"@architectures": "spacy.TextCat.v1", "exclusive_classes": False, "ngram_size": 1, "pretrained_vectors": False, "width": 64, "conv_depth": 2, "embed_size": 2000, "window_size": 2, "dropout": None},
        {"@architectures": "spacy.TextCat.v1", "exclusive_classes": True, "ngram_size": 5, "pretrained_vectors": False, "width": 128, "conv_depth": 2, "embed_size": 2000, "window_size": 1, "dropout": None},
        {"@architectures": "spacy.TextCat.v1", "exclusive_classes": True, "ngram_size": 2, "pretrained_vectors": False, "width": 32, "conv_depth": 3, "embed_size": 500, "window_size": 3, "dropout": None},
        {"@architectures": "spacy.TextCatCNN.v1", "tok2vec": default_tok2vec(), "exclusive_classes": True},
        {"@architectures": "spacy.TextCatCNN.v1", "tok2vec": default_tok2vec(), "exclusive_classes": False},
    ],
)
# fmt: on
def test_textcat_configs(textcat_config):
    pipe_config = {"model": textcat_config}
    nlp = English()
    textcat = nlp.create_pipe("textcat", pipe_config)
    train_examples = []
    for text, annotations in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for label, value in annotations.get("cats").items():
            textcat.add_label(label)
    nlp.add_pipe(textcat)
    optimizer = nlp.begin_training()
    for i in range(5):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
