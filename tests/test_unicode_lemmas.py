# encoding=utf8
from __future__ import unicode_literals

from spacy.en import English
import pytest


@pytest.fixture
def tokens():
    return English()(u'ćode codé')


def test_unicode(tokens):
    assert tokens[0].lemma_ == u'ćode'
    assert tokens[1].lemma_ == u'codé'
