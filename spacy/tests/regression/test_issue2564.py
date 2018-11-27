# coding: utf8
from __future__ import unicode_literals

from spacy.language import Language


def test_issue2564():
    """Test the tagger sets is_tagged correctly when used via Language.pipe."""
    nlp = Language()
    tagger = nlp.create_pipe("tagger")
    tagger.begin_training()  # initialise weights
    nlp.add_pipe(tagger)
    doc = nlp("hello world")
    assert doc.is_tagged
    docs = nlp.pipe(["hello", "world"])
    piped_doc = next(docs)
    assert piped_doc.is_tagged
