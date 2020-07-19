import pytest

from spacy import util
from spacy.gold import Example
from spacy.lang.en import English
from spacy.language import Language
from spacy.tests.util import make_tempdir
from spacy.morphology import Morphology


def test_label_types():
    nlp = Language()
    morphologizer = nlp.add_pipe("morphologizer")
    morphologizer.add_label("Feat=A")
    with pytest.raises(ValueError):
        morphologizer.add_label(9)


TRAIN_DATA = [
    (
        "I like green eggs",
        {
            "morphs": ["Feat=N", "Feat=V", "Feat=J", "Feat=N"],
            "pos": ["NOUN", "VERB", "ADJ", "NOUN"],
        },
    ),
    # test combinations of morph+POS
    ("Eat blue ham", {"morphs": ["Feat=V", "", ""], "pos": ["", "ADJ", ""]},),
]


def test_overfitting_IO():
    # Simple test to try and quickly overfit the morphologizer - ensuring the ML models work correctly
    nlp = English()
    morphologizer = nlp.add_pipe("morphologizer")
    train_examples = []
    for inst in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(inst[0]), inst[1]))
        for morph, pos in zip(inst[1]["morphs"], inst[1]["pos"]):
            if morph and pos:
                morphologizer.add_label(
                    morph + Morphology.FEATURE_SEP + "POS" + Morphology.FIELD_SEP + pos
                )
            elif pos:
                morphologizer.add_label("POS" + Morphology.FIELD_SEP + pos)
            elif morph:
                morphologizer.add_label(morph)
    optimizer = nlp.begin_training()

    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["morphologizer"] < 0.00001

    # test the trained model
    test_text = "I like blue ham"
    doc = nlp(test_text)
    gold_morphs = [
        "Feat=N",
        "Feat=V",
        "",
        "",
    ]
    gold_pos_tags = [
        "NOUN",
        "VERB",
        "ADJ",
        "",
    ]
    assert [t.morph_ for t in doc] == gold_morphs
    assert [t.pos_ for t in doc] == gold_pos_tags

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        assert [t.morph_ for t in doc2] == gold_morphs
        assert [t.pos_ for t in doc2] == gold_pos_tags
