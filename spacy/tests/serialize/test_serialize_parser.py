# coding: utf-8
from __future__ import unicode_literals

from ..util import make_tempdir
from ...pipeline import NeuralDependencyParser as Parser

import pytest


def test_serialize_parser_roundtrip_bytes(en_vocab):
    parser = Parser(en_vocab)
    parser.model, _ = parser.Model(0)
    parser_b = parser.to_bytes()
    new_parser = Parser(en_vocab)
    new_parser.model, _ = new_parser.Model(0)
    new_parser = new_parser.from_bytes(parser_b)
    assert new_parser.to_bytes() == parser_b


def test_serialize_parser_roundtrip_disk(en_vocab):
    parser = Parser(en_vocab)
    parser.model, _ = parser.Model(0)
    with make_tempdir() as d:
        file_path = d / 'parser'
        parser.to_disk(file_path)
        parser_d = Parser(en_vocab)
        parser_d.model, _ = parser_d.Model(0)
        parser_d = parser_d.from_disk(file_path)
        assert parser.to_bytes() == parser_d.to_bytes()
