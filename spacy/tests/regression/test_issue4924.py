import pytest
import spacy


@pytest.fixture
def nlp():
    return spacy.blank("en")


def test_evaluate(nlp):
    docs_golds = [("", {})]
    nlp.evaluate(docs_golds)
