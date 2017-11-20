from __future__ import unicode_literals

import pytest

from ...lang.en import English


def test_issue1612():
    nlp = English()
    doc = nlp('The black cat purrs.')
    span = doc[1: 3]
    assert span.orth_ == span.text
