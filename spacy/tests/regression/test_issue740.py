# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', ["3/4/2012", "01/12/1900"])
def test_issue740(en_tokenizer, text):
    """Test that dates are not split and kept as one token. This behaviour is currently inconsistent, since dates separated by hyphens are still split.
    This will be hard to prevent without causing clashes with numeric ranges."""
    tokens = en_tokenizer(text)
    assert len(tokens) == 1
