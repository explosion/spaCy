import pytest

from spacy import util
from spacy.gold import Example
from spacy.lang.en import English
from spacy.language import Language
from spacy.tests.util import make_tempdir


def test_label_types():
    nlp = Language()
    nlp.add_pipe(nlp.create_pipe("morphologizer"))
    nlp.get_pipe("morphologizer").add_label("Feat=A")
    with pytest.raises(ValueError):
        nlp.get_pipe("morphologizer").add_label(9)


TRAIN_DATA = [
    (
        "I like green eggs",
        {
            "morphs": ["Feat=N", "Feat=V", "Feat=J", "Feat=N"],
            "pos": ["NOUN", "VERB", "ADJ", "NOUN"],
        },
    ),
    (
        "Eat blue ham",
        {"morphs": ["Feat=V", "Feat=J", "Feat=N"], "pos": ["VERB", "ADJ", "NOUN"]},
    ),
]


def test_overfitting_IO():
    # Simple test to try and quickly overfit the morphologizer - ensuring the ML models work correctly
    nlp = English()
    morphologizer = nlp.create_pipe("morphologizer")
    train_examples = []
    for inst in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(inst[0]), inst[1]))
        for morph, pos in zip(inst[1]["morphs"], inst[1]["pos"]):
            morphologizer.add_label(morph + "|POS=" + pos)
    nlp.add_pipe(morphologizer)
    optimizer = nlp.begin_training()

    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["morphologizer"] < 0.00001

    # test the trained model
    test_text = "I like blue eggs"
    doc = nlp(test_text)
    gold_morphs = [
        "Feat=N|POS=NOUN",
        "Feat=V|POS=VERB",
        "Feat=J|POS=ADJ",
        "Feat=N|POS=NOUN",
    ]
    assert [t.morph_ for t in doc] == gold_morphs

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        assert gold_morphs == [t.morph_ for t in doc2]
