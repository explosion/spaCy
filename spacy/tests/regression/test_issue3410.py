# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.lang.en import English
from spacy.matcher import Matcher, PhraseMatcher


def test_issue3410():
    texts = ["Hello world", "This is a test"]
    nlp = English()
    matcher = Matcher(nlp.vocab)
    phrasematcher = PhraseMatcher(nlp.vocab)
    with pytest.deprecated_call():
        docs = list(nlp.pipe(texts, n_threads=4))
    with pytest.deprecated_call():
        docs = list(nlp.tokenizer.pipe(texts, n_threads=4))
    with pytest.deprecated_call():
        list(matcher.pipe(docs, n_threads=4))
    with pytest.deprecated_call():
        list(phrasematcher.pipe(docs, n_threads=4))
