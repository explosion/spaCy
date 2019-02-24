# coding: utf8
from __future__ import unicode_literals

from spacy.lang.en import English


def test_issue3209():
    """Test issue that occurred in spaCy nightly where NER labels were being
    mapped to classes incorrectly after loading the model, when the labels
    were added using ner.add_label().
    """
    nlp = English()
    ner = nlp.create_pipe("ner")
    nlp.add_pipe(ner)

    ner.add_label("ANIMAL")
    nlp.begin_training()
    move_names = ["O", "B-ANIMAL", "I-ANIMAL", "L-ANIMAL", "U-ANIMAL"]
    assert ner.move_names == move_names
    nlp2 = English()
    nlp2.add_pipe(nlp2.create_pipe("ner"))
    nlp2.from_bytes(nlp.to_bytes())
    assert nlp2.get_pipe("ner").move_names == move_names
