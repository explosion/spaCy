# coding: utf8
from __future__ import unicode_literals

import pytest

from ...language import Language
from ...vocab import Vocab


@pytest.mark.xfail
def test_issue1654():
    nlp = Language(Vocab())
    assert not nlp.pipeline
    nlp.add_pipe(lambda doc: doc, name='1')
    nlp.add_pipe(lambda doc: doc, name='2', after='1')
    nlp.add_pipe(lambda doc: doc, name='3', after='2')
    assert nlp.pipe_names == ['1', '2', '3']
