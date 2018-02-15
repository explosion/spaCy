# coding: utf8
from __future__ import unicode_literals
import pytest

from ..util import load_test_model


@pytest.mark.models('en')
def test_issue1959():
    texts = ['Apple is looking at buying U.K. startup for $1 billion.']
    nlp = load_test_model('en_core_web_sm')
    nlp.add_pipe(clean_component, name='cleaner', after='ner')
    doc = nlp(texts[0])
    doc_pipe = [doc_pipe for doc_pipe in nlp.pipe(texts)]
    assert doc == doc_pipe[0]


def clean_component(doc):
    """ Clean up text. Make lowercase and remove punctuation and stopwords """
    # Remove punctuation, symbols (#) and stopwords
    doc = [tok.text.lower() for tok in doc if (not tok.is_stop
                                               and tok.pos_ != 'PUNCT' and
                                               tok.pos_ != 'SYM')]
    doc = ' '.join(doc)
    return doc
