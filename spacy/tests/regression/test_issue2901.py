# coding: utf8
from __future__ import unicode_literals

import pytest

from ...lang.ja import Japanese


def test_issue2901():
    """Test that `nlp` doesn't fail."""
    try:
        nlp = Japanese()
    except ImportError:
        pytest.skip()

    doc = nlp("pythonが大好きです")
    assert doc
