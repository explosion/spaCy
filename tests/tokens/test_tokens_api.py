from __future__ import unicode_literals

import pytest


def test_getitem(EN):
    tokens = EN(u'Give it back! He pleaded.')
    assert tokens[0].orth_ == 'Give'
    assert tokens[-1].orth_ == '.'
    with pytest.raises(IndexError):
        tokens[len(tokens)]
