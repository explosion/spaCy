# coding: utf-8
from __future__ import unicode_literals

from spacy.gold import biluo_tags_from_offsets, offsets_from_biluo_tags
from spacy.gold import docs_to_json
from spacy.tokens import Doc
from .util import get_doc


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

def test_docs_to_json(en_vocab):
    '''Test we can convert a list of Doc objects into the JSON-serializable
    format we use for training.
    '''
    docs = [
        get_doc(
            en_vocab,
            words=['a', 'b'],
            pos=['VBP', 'NN'],
            heads=[0, -1],
            deps=['ROOT', 'dobj'],
            ents=[]),
        get_doc(
            en_vocab,
            words=['c', 'd', 'e'],
            pos=['VBP', 'NN', 'NN'],
            heads=[0, -1, -2],
            deps=['ROOT', 'dobj', 'dobj'],
            ents=[(1, 2, 'ORG')]),
    ]
    json_doc = docs_to_json(0, docs)
    assert json_doc['id'] == 0
    assert len(json_doc['paragraphs']) == 2
    assert len(json_doc['paragraphs'][0]['sentences']) == 1
    assert len(json_doc['paragraphs'][1]['sentences']) == 1
    assert len(json_doc['paragraphs'][0]['sentences'][0]['tokens']) == 2
    assert len(json_doc['paragraphs'][1]['sentences'][0]['tokens']) == 3
