# -*- coding: utf8 -*-

from __future__ import unicode_literals
import pytest

from spacy.orth import asciify


def test_tilde():
    string = u'hõmbre'
    assert asciify(string) == u'hombre'


def test_smart_quote():
    string = u'“'
    assert asciify(string) == '"'
    string = u'”'
    assert asciify(string) == '"'
