# coding: utf-8
from __future__ import unicode_literals

from ...vocab import Vocab


def test_issue617():
    """Test loading Vocab with string"""
    try:
        vocab = Vocab.load('/tmp/vocab')
    except IOError:
        pass
