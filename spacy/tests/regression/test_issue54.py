# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.models('en')
def test_issue54(EN):
    text = "Talks given by women had a slightly higher number of questions asked (3.2$\pm$0.2) than talks given by men (2.6$\pm$0.1)."
    tokens = EN(text)
