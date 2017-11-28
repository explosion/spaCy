# coding: utf8
from __future__ import unicode_literals

import pytest

from ...language import Language
from ...vocab import Vocab


def test_issue1654():
    nlp = Language(Vocab())
    assert not nlp.pipeline
    nlp.add_pipe(lambda doc: doc, name='1')
    nlp.add_pipe(lambda doc: doc, name='2', after='1')
    nlp.add_pipe(lambda doc: doc, name='3', after='2')
    assert nlp.pipe_names == ['1', '2', '3']

    nlp2 = Language(Vocab())
    assert not nlp2.pipeline
    nlp2.add_pipe(lambda doc: doc, name='3')
    nlp2.add_pipe(lambda doc: doc, name='2', before='3')
    nlp2.add_pipe(lambda doc: doc, name='1', before='2')
    assert nlp2.pipe_names == ['1', '2', '3']
