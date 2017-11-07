# coding: utf-8
from __future__ import unicode_literals

from ..util import make_tempdir
from ...pipeline import DependencyParser
from ...pipeline import EntityRecognizer

import pytest


test_parsers = [DependencyParser, EntityRecognizer]


@pytest.mark.parametrize('Parser', test_parsers)
def test_serialize_parser_roundtrip_bytes(en_vocab, Parser):
    parser = Parser(en_vocab)
    parser.model, _ = parser.Model(10)
    new_parser = Parser(en_vocab)
    new_parser.model, _ = new_parser.Model(10)
    new_parser = new_parser.from_bytes(parser.to_bytes())
    assert new_parser.to_bytes() == parser.to_bytes()


@pytest.mark.parametrize('Parser', test_parsers)
def test_serialize_parser_roundtrip_disk(en_vocab, Parser):
    parser = Parser(en_vocab)
    parser.model, _ = parser.Model(0)
    with make_tempdir() as d:
        file_path = d / 'parser'
        parser.to_disk(file_path)
        parser_d = Parser(en_vocab)
        parser_d.model, _ = parser_d.Model(0)
        parser_d = parser_d.from_disk(file_path)
        assert parser.to_bytes(model=False) == parser_d.to_bytes(model=False)
