import pytest
from spacy.lang.en import English
from spacy.gold import Example
from spacy import util
from ..util import make_tempdir


TRAIN_DATA = [
    ("Who is Shaka S Khan?", {"entities": [(7, 19, "PERSON")]}),
    ("I like London and Berlin.", {"entities": [(7, 13, "LOC"), (18, 24, "LOC")]}),
]


def test_no_label():
    nlp = English()
    nlp.add_pipe("simple_ner")
    with pytest.raises(ValueError):
        nlp.begin_training()


def test_implicit_label():
    nlp = English()
    ner = nlp.add_pipe("simple_ner")
    train_examples = []
    ner.add_label("ORG")
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    nlp.begin_training(get_examples=lambda: train_examples)


@pytest.mark.skip(reason="Should be fixed")
def test_untrained():
    # This shouldn't crash, but it does when the simple_ner produces an invalid sequence like ['L-PERSON', 'L-ORG']
    nlp = English()
    ner = nlp.add_pipe("simple_ner")
    ner.add_label("PERSON")
    ner.add_label("LOC")
    ner.add_label("ORG")
    nlp.begin_training()
    nlp("Example sentence")


def test_resize():
    nlp = English()
    ner = nlp.add_pipe("simple_ner")
    ner.add_label("PERSON")
    ner.add_label("LOC")
    nlp.begin_training()
    assert len(ner.labels) == 2
    ner.add_label("ORG")
    nlp.begin_training()
    assert len(ner.labels) == 3


def test_begin_training_examples():
    nlp = English()
    ner = nlp.add_pipe("simple_ner")
    train_examples = []
    for text, annotations in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    # you shouldn't really call this more than once, but for testing it should be fine
    nlp.begin_training()
    nlp.begin_training(get_examples=lambda: train_examples)
    with pytest.raises(TypeError):
        nlp.begin_training(get_examples=lambda: None)
    with pytest.raises(TypeError):
        nlp.begin_training(get_examples=lambda: train_examples[0])
    with pytest.raises(ValueError):
        nlp.begin_training(get_examples=lambda: [])
    with pytest.raises(ValueError):
        nlp.begin_training(get_examples=train_examples)


def test_overfitting_IO():
    # Simple test to try and quickly overfit the SimpleNER component - ensuring the ML models work correctly
    nlp = English()
    ner = nlp.add_pipe("simple_ner")
    train_examples = []
    for text, annotations in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
    optimizer = nlp.begin_training(get_examples=lambda: train_examples)

    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["ner"] < 0.0001

    # test the trained model
    test_text = "I like London."
    doc = nlp(test_text)
    ents = doc.ents
    assert len(ents) == 1
    assert ents[0].text == "London"
    assert ents[0].label_ == "LOC"

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        ents2 = doc2.ents
        assert len(ents2) == 1
        assert ents2[0].text == "London"
        assert ents2[0].label_ == "LOC"
