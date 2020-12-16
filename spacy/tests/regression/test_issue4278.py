# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.language import Language
from spacy.pipeline import Pipe


class DummyPipe(Pipe):
    def __init__(self):
        self.model = "dummy_model"

    def predict(self, docs):
        return ([1, 2, 3], [4, 5, 6])

    def set_annotations(self, docs, scores, tensors=None):
        return docs


@pytest.fixture
def nlp():
    return Language()


def test_multiple_predictions(nlp):
    doc = nlp.make_doc("foo")
    dummy_pipe = DummyPipe()
    dummy_pipe(doc)
