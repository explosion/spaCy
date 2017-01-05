# coding: utf-8
from __future__ import unicode_literals

import pytest

from ...hu import Hungarian


@pytest.fixture
def hu_tokenizer():
    return Hungarian.Defaults.create_tokenizer()
