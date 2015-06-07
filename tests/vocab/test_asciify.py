# -*- coding: utf8 -*-

from __future__ import unicode_literals
import pytest

from spacy.orth import asciied


def test_tilde():
    string = u'hõmbre'
    assert asciied(string) == b'hombre'


def test_smart_quote():
    string = u'“'
    assert asciied(string) == b'"'
    string = u'”'
    assert asciied(string) == b'"'
