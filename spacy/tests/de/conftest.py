# coding: utf-8
from __future__ import unicode_literals

import pytest

from ...de import German


@pytest.fixture
def de_tokenizer():
    return German.Defaults.create_tokenizer()
