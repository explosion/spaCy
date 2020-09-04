from spacy.lang.en import English
from spacy.gold import Example
from spacy import util
from ..util import make_tempdir


TRAIN_DATA = [
    ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
    ("I like London and Berlin.", {"entities": [(7, 13, "LOC"), (18, 24, "LOC")]}),
]


def test_overfitting_IO():
    # Simple test to try and quickly overfit the SimpleNER component - ensuring the ML models work correctly
    nlp = English()
    ner = nlp.add_pipe("simple_ner")
    train_examples = []
    for text, annotations in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    optimizer = nlp.begin_training()

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
