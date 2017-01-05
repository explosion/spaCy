# coding: utf-8
from __future__ import unicode_literals

import pytest
from ...en import English


@pytest.fixture
def en_tokenizer():
    return English.Defaults.create_tokenizer()
