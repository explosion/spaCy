from __future__ import unicode_literals

import pytest

@pytest.mark.models
def test_space_attachment(EN):
    sentence = 'This is a test.\nTo ensure  spaces are attached well.'
    doc = EN(sentence)

    for sent in doc.sents:
        if len(sent) == 1:
            assert not sent[-1].is_space
