# coding: utf-8
from __future__ import unicode_literals

from spacy.lang.en import English


def test_issue3289():
    """Test that Language.to_bytes handles serializing a pipeline component
    with an uninitialized model."""
    nlp = English()
    nlp.add_pipe(nlp.create_pipe("textcat"))
    bytes_data = nlp.to_bytes()
    new_nlp = English()
    new_nlp.add_pipe(nlp.create_pipe("textcat"))
    new_nlp.from_bytes(bytes_data)
