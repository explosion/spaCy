from __future__ import unicode_literals

import pytest


@pytest.mark.models
def test_root(EN):
    tokens = EN(u"i don't have other assistance")
    for t in tokens:
        assert t.dep != 0, t.orth_


@pytest.mark.models
def test_one_word_sentence(EN):
	# one word sentence
	doc = EN.tokenizer.tokens_from_list(['Hello'])
	EN.tagger(doc)
	assert len(doc) == 1
	with EN.parser.step_through(doc) as _:
		pass
	assert doc[0].dep != 0


def apply_transition_sequence(model, doc, sequence):
    with model.parser.step_through(doc) as stepwise:
        for transition in sequence:
            stepwise.transition(transition)
