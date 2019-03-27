# coding: utf-8
from __future__ import unicode_literals

from spacy.matcher import PhraseMatcher
from spacy.lang.en import English
from spacy.compat import pickle


def test_issue3248_1():
    """Test that the PhraseMatcher correctly reports its number of rules, not
    total number of patterns."""
    nlp = English()
    matcher = PhraseMatcher(nlp.vocab)
    matcher.add("TEST1", None, nlp("a"), nlp("b"), nlp("c"))
    matcher.add("TEST2", None, nlp("d"))
    assert len(matcher) == 2


def test_issue3248_2():
    """Test that the PhraseMatcher can be pickled correctly."""
    nlp = English()
    matcher = PhraseMatcher(nlp.vocab)
    matcher.add("TEST1", None, nlp("a"), nlp("b"), nlp("c"))
    matcher.add("TEST2", None, nlp("d"))
    data = pickle.dumps(matcher)
    new_matcher = pickle.loads(data)
    assert len(new_matcher) == len(matcher)
