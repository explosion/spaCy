# coding: utf-8
from __future__ import unicode_literals

from ...en import English

import pytest


@pytest.fixture
def en_tokenizer():
    return English.Defaults.create_tokenizer()


def test_issue351(en_tokenizer):
    doc = en_tokenizer("   This is a cat.")
    assert doc[0].idx == 0
    assert len(doc[0]) == 3
    assert doc[1].idx == 3
