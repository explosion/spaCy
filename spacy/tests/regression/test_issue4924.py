from spacy.gold import Example
from spacy.language import Language


def test_issue4924():
    nlp = Language()
    docs_golds = [Example.from_dict(nlp.make_doc(""), {})]
    nlp.evaluate(docs_golds)
