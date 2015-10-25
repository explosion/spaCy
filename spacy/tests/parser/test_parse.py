import pytest


@pytest.mark.models
def test_root(EN):
    tokens = EN(u"i don't have other assistance")
    for t in tokens:
        assert t.dep != 0, t.orth_
