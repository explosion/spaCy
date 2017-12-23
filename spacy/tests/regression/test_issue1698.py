# coding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', ['test@example.com', 'john.doe@example.co.uk'])
def test_issue1698(en_tokenizer, text):
    doc = en_tokenizer(text)
    assert len(doc) == 1
    assert not doc[0].like_url
