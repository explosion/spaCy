# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.language import Language
from spacy.pipeline import Tagger


def test_label_types():
    nlp = Language()
    nlp.add_pipe(nlp.create_pipe("tagger"))
    nlp.get_pipe("tagger").add_label("A")
    with pytest.raises(ValueError):
        nlp.get_pipe("tagger").add_label(9)
