# coding: utf-8
from __future__ import unicode_literals

import six
import pytest


@pytest.mark.models
def test_tag_names(EN):
    text = "I ate pizzas with anchovies."
    doc = EN(text, parse=False, tag=True)
    assert type(doc[2].pos) == int
    assert isinstance(doc[2].pos_, six.text_type)
    assert type(doc[2].dep) == int
    assert isinstance(doc[2].dep_, six.text_type)
    assert doc[2].tag_ == u'NNS'
