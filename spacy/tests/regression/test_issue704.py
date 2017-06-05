# coding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.xfail
@pytest.mark.models('en')
def test_issue704(EN):
    """Test that sentence boundaries are detected correctly."""

    text = '“Atticus said to Jem one day, “I’d rather you shot at tin cans in the backyard, but I know you’ll go after birds. Shoot all the blue jays you want, if you can hit ‘em, but remember it’s a sin to kill a mockingbird.”'
    doc = EN(text)
    sents = list([sent for sent in doc.sents])
    assert len(sents) == 3
