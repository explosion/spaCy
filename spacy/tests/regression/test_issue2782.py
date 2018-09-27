# coding: utf8
from __future__ import unicode_literals

from spacy.util import get_lang_class
import pytest


@pytest.mark.parametrize('text', ['-0.23', '+123,456', '±1'])
@pytest.mark.parametrize('lang', ['en', 'xx'])
def test_issue2782(text, lang):
    """Check that like_num handles + and - before number."""
    cls = get_lang_class(lang)
    nlp = cls()
    doc = nlp(text)
    assert len(doc) == 1
    assert doc[0].like_num
