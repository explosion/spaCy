import pytest
from spacy.tokens import Span

@pytest.fixture
def doc(en_tokenizer):
    text = "0 1 2 3 4 5 6"
    doc = en_tokenizer(text)
    doc.spans['SPANS'] = [Span(doc, 0, 3, 'LABEL', kb_id = 'KB_ID'), Span(doc, 0, 4, 'LABEL', kb_id = 'KB_ID')]
    return doc

def test_span_group_assignment(doc) :
    span_group = doc.spans['SPANS']
    span = span_group[0]
    span.label_ = 'NEW_LABEL'
    span.kb_id_ = 'NEW_KB_ID'
    assert span_group[0].label_ == 'NEW_LABEL'
    assert span_group[0].kb_id_ == 'NEW_KB_ID'
