# coding: utf8
from __future__ import unicode_literals


def test_issue2835(en_tokenizer):
    """Check that sentence doesn't cause an infinite loop in the tokenizer."""
    text = """
    oow.jspsearch.eventoracleopenworldsearch.technologyoraclesolarissearch.technologystoragesearch.technologylinuxsearch.technologyserverssearch.technologyvirtualizationsearch.technologyengineeredsystemspcodewwmkmppscem:
    """
    doc = en_tokenizer(text)
    assert doc

