from __future__ import unicode_literals

import pytest

@pytest.mark.models
def test_space_attachment(EN):
    sentence = 'This is a test.\nTo ensure  spaces are attached well.'
    doc = EN(sentence)

    for word in doc:
        if word.is_space:
            assert word.head.i == (word.i - 1)
