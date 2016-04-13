from __future__ import unicode_literals

import pytest
import numpy
from spacy.attrs import HEAD

def make_doc(EN, sentstr):
	sent = sentstr.split(' ')
	doc = EN.tokenizer.tokens_from_list(sent)
	EN.tagger(doc)
	return doc


@pytest.mark.models
def test_space_attachment(EN):
    sentence = 'This is a test.\nTo ensure  spaces are attached well.'
    doc = EN(sentence)

    for sent in doc.sents:
        if len(sent) == 1:
            assert not sent[-1].is_space


@pytest.mark.models
def test_sentence_space(EN):
    text = ('''I look forward to using Thingamajig.  I've been told it will '''
            '''make my life easier...''')
    doc = EN(text)
    assert len(list(doc.sents)) == 2


@pytest.mark.models
def test_space_attachment_leading_space(EN):
	# leading space token
	doc = make_doc(EN, '\t \n This is a sentence .')
	assert doc[0].is_space
	assert doc[1].is_space
	assert doc[2].orth_ == 'This'
	with EN.parser.step_through(doc) as stepwise:
		pass
	assert doc[0].head.i == 2
	assert doc[1].head.i == 2
	assert stepwise.stack == set([2])


@pytest.mark.models
def test_space_attachment_intermediate_and_trailing_space(EN):
	# intermediate and trailing space tokens
	doc = make_doc(EN, 'This is \t a \t\n \n sentence . \n\n \n')
	assert doc[2].is_space
	assert doc[4].is_space
	assert doc[5].is_space
	assert doc[8].is_space
	assert doc[9].is_space
	with EN.parser.step_through(doc) as stepwise:
		stepwise.transition('L-nsubj')
		stepwise.transition('S')
		stepwise.transition('L-det')
		stepwise.transition('R-attr')
		stepwise.transition('D')
		stepwise.transition('R-punct')
	assert stepwise.stack == set([])
	for tok in doc:
		assert tok.dep != 0 or tok.is_space
	assert [ tok.head.i for tok in doc ] == [1,1,1,6,3,3,1,1,7,7]


@pytest.mark.models
def test_space_attachment_one_space_sentence(EN):
	# one space token sentence
	doc = make_doc(EN, '\n')
	assert len(doc) == 1
	with EN.parser.step_through(doc) as _:
		pass
	assert doc[0].is_space
	assert doc[0].head.i == 0


@pytest.mark.models
def test_space_attachment_only_space_sentence(EN):
	# space-exclusive sentence
	doc = make_doc(EN, '\n \t \n\n \t')
	assert len(doc) == 4
	for tok in doc:
		assert tok.is_space
	with EN.parser.step_through(doc) as _:
		pass
	# all tokens are attached to the last one
	for tok in doc:
		assert tok.head.i == 3
