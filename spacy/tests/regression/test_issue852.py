# coding: utf8
from __future__ import unicode_literals

import pytest

from ... import util

@pytest.fixture(scope='module')
def fr_tokenizer():
    return util.get_lang_class('fr').Defaults.create_tokenizer()



@pytest.mark.parametrize('text', ["au-delàs", "pair-programmâmes",
                                  "terra-formées", "σ-compacts"])
def test_issue852(fr_tokenizer, text):
    """Test that French tokenizer exceptions are imported correctly."""
    tokens = fr_tokenizer(text)
    assert len(tokens) == 1
