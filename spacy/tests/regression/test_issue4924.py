import pytest
from spacy.language import Language


def test_issue4924():
    nlp = Language()
    docs_golds = [("", {})]
    with pytest.raises(ValueError):
        nlp.evaluate(docs_golds)
