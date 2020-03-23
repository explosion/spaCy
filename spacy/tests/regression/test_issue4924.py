import pytest
from spacy.language import Language


def test_evaluate():
    nlp = Language()
    docs_golds = [("", {})]
    nlp.evaluate(docs_golds)
