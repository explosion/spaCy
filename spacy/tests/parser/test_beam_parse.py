# coding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.models('en')
def test_beam_parse(EN):
    doc = EN(u'Australia is a country', disable=['ner'])
    ents = EN.entity(doc, beam_width=2)
    print(ents)
