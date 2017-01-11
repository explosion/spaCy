# coding: utf-8
from __future__ import unicode_literals

from ...en import English

import pytest


@pytest.fixture
def en_tokenizer():
    return English.Defaults.create_tokenizer()


def test_big_ellipsis(en_tokenizer):
    tokens = en_tokenizer('$45...............Asking')
    assert len(tokens) > 2
