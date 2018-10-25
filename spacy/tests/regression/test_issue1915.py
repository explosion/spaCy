# coding: utf8

from __future__ import unicode_literals
from ...language import Language


def test_simple_ner():
    cfg = {
        'hidden_depth': 2,  # should error out
    }

    nlp = Language()
    nlp.add_pipe(nlp.create_pipe('ner'))
    nlp.get_pipe('ner').add_label('answer')
    try:
        nlp.begin_training(**cfg)
        assert False  # should error out
    except ValueError:
        assert True
