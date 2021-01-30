import pytest
from spacy.lang.en import English
import numpy as np


@pytest.mark.parametrize(
    "sentence, start_idx,end_idx,label",
    [("Welcome to Mumbai, my friend", 11, 17, "GPE")],
)
def test_char_span_label(sentence, start_idx, end_idx, label):
    nlp = English()
    doc = nlp(sentence)
    span = doc[:].char_span(start_idx, end_idx, label=label)
    assert span.label_ == label


@pytest.mark.parametrize(
    "sentence, start_idx,end_idx,kb_id", [("Welcome to Mumbai, my friend", 11, 17, 5)]
)
def test_char_span_kb_id(sentence, start_idx, end_idx, kb_id):
    nlp = English()
    doc = nlp(sentence)
    span = doc[:].char_span(start_idx, end_idx, kb_id=kb_id)
    assert span.kb_id == kb_id


@pytest.mark.parametrize(
    "sentence, start_idx,end_idx,vector",
    [("Welcome to Mumbai, my friend", 11, 17, np.array([0.1, 0.2, 0.3]))],
)
def test_char_span_vector(sentence, start_idx, end_idx, vector):
    nlp = English()
    doc = nlp(sentence)
    span = doc[:].char_span(start_idx, end_idx, vector=vector)
    assert (span.vector == vector).all()
