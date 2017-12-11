# coding: utf-8
from __future__ import unicode_literals

from ...gold import biluo_tags_from_offsets, offsets_from_biluo_tags
from ...tokens.doc import Doc

import pytest


def test_gold_biluo_U(en_vocab):
    orths_and_spaces = [('I', True), ('flew', True), ('to', True),
                        ('London', False), ('.', True)]
    doc = Doc(en_vocab, orths_and_spaces=orths_and_spaces)
    entities = [(len("I flew to "), len("I flew to London"), 'LOC')]
    tags = biluo_tags_from_offsets(doc, entities)
    assert tags == ['O', 'O', 'O', 'U-LOC', 'O']


def test_gold_biluo_BL(en_vocab):
    orths_and_spaces = [('I', True), ('flew', True), ('to', True), ('San', True),
                        ('Francisco', False), ('.', True)]
    doc = Doc(en_vocab, orths_and_spaces=orths_and_spaces)
    entities = [(len("I flew to "), len("I flew to San Francisco"), 'LOC')]
    tags = biluo_tags_from_offsets(doc, entities)
    assert tags == ['O', 'O', 'O', 'B-LOC', 'L-LOC', 'O']


def test_gold_biluo_BIL(en_vocab):
    orths_and_spaces = [('I', True), ('flew', True), ('to', True), ('San', True),
                        ('Francisco', True), ('Valley', False), ('.', True)]
    doc = Doc(en_vocab, orths_and_spaces=orths_and_spaces)
    entities = [(len("I flew to "), len("I flew to San Francisco Valley"), 'LOC')]
    tags = biluo_tags_from_offsets(doc, entities)
    assert tags == ['O', 'O', 'O', 'B-LOC', 'I-LOC', 'L-LOC', 'O']


def test_gold_biluo_misalign(en_vocab):
    orths_and_spaces = [('I', True), ('flew', True), ('to', True), ('San', True),
                        ('Francisco', True), ('Valley.', False)]
    doc = Doc(en_vocab, orths_and_spaces=orths_and_spaces)
    entities = [(len("I flew to "), len("I flew to San Francisco Valley"), 'LOC')]
    tags = biluo_tags_from_offsets(doc, entities)
    assert tags == ['O', 'O', 'O', '-', '-', '-']


def test_roundtrip_offsets_biluo_conversion(en_tokenizer):
    text = "I flew to Silicon Valley via London."
    biluo_tags = ['O', 'O', 'O', 'B-LOC', 'L-LOC', 'O', 'U-GPE', 'O']
    offsets = [(10, 24, 'LOC'), (29, 35, 'GPE')]
    doc = en_tokenizer(text)
    biluo_tags_converted = biluo_tags_from_offsets(doc, offsets)
    assert biluo_tags_converted == biluo_tags
    offsets_converted = offsets_from_biluo_tags(doc, biluo_tags)
    assert offsets_converted == offsets
