# coding: utf8
from __future__ import unicode_literals

from spacy.lang.en import English


def test_issue3880():
    """Test that `nlp.pipe()` works when an empty string ends the batch.

    Fixed in v7.0.5 of Thinc.
    """
    texts = ["hello", "world", "", ""]
    nlp = English()
    nlp.add_pipe(nlp.create_pipe("parser"))
    nlp.add_pipe(nlp.create_pipe("ner"))
    nlp.add_pipe(nlp.create_pipe("tagger"))
    nlp.get_pipe("parser").add_label("dep")
    nlp.get_pipe("ner").add_label("PERSON")
    nlp.get_pipe("tagger").add_label("NN")
    nlp.begin_training()
    for doc in nlp.pipe(texts):
        pass
