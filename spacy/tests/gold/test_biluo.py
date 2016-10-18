from __future__ import unicode_literals

from ...gold import biluo_tags_from_offsets
from ...vocab import Vocab
from ...tokens.doc import Doc

import pytest


@pytest.fixture
def vocab():
    return Vocab()


def test_U(vocab):
    orths_and_spaces = [('I', True), ('flew', True), ('to', True), ('London', False),
                        ('.', True)]
    doc = Doc(vocab, orths_and_spaces=orths_and_spaces)
    entities = [(len("I flew to "), len("I flew to London"), 'LOC')]
    tags = biluo_tags_from_offsets(doc, entities)
    assert tags == ['O', 'O', 'O', 'U-LOC', 'O']


def test_BL(vocab):
    orths_and_spaces = [('I', True), ('flew', True), ('to', True), ('San', True),
                        ('Francisco', False), ('.', True)]
    doc = Doc(vocab, orths_and_spaces=orths_and_spaces)
    entities = [(len("I flew to "), len("I flew to San Francisco"), 'LOC')]
    tags = biluo_tags_from_offsets(doc, entities)
    assert tags == ['O', 'O', 'O', 'B-LOC', 'L-LOC', 'O']


def test_BIL(vocab):
    orths_and_spaces = [('I', True), ('flew', True), ('to', True), ('San', True),
                        ('Francisco', True), ('Valley', False), ('.', True)]
    doc = Doc(vocab, orths_and_spaces=orths_and_spaces)
    entities = [(len("I flew to "), len("I flew to San Francisco Valley"), 'LOC')]
    tags = biluo_tags_from_offsets(doc, entities)
    assert tags == ['O', 'O', 'O', 'B-LOC', 'I-LOC', 'L-LOC', 'O']


def test_misalign(vocab):
    orths_and_spaces = [('I', True), ('flew', True), ('to', True), ('San', True),
                        ('Francisco', True), ('Valley.', False)]
    doc = Doc(vocab, orths_and_spaces=orths_and_spaces)
    entities = [(len("I flew to "), len("I flew to San Francisco Valley"), 'LOC')]
    tags = biluo_tags_from_offsets(doc, entities)
    assert tags == ['O', 'O', 'O', '-', '-', '-']
