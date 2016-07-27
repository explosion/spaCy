from __future__ import unicode_literals

import pytest
from spacy.tokens import Doc
from spacy.syntax.nonproj import PseudoProjectivity


@pytest.mark.models
def test_single_period(EN):
    string = 'A test sentence.'
    words = EN(string)
    assert len(words) == 4
    assert len(list(words.sents)) == 1
    assert sum(len(sent) for sent in words.sents) == len(words)


@pytest.mark.models
def test_single_no_period(EN):
    string = 'A test sentence'
    words = EN(string)
    assert len(words) == 3
    assert len(list(words.sents)) == 1
    assert sum(len(sent) for sent in words.sents) == len(words)


@pytest.mark.models
def test_single_exclamation(EN):
    string = 'A test sentence!'
    words = EN(string)
    assert len(words) == 4
    assert len(list(words.sents)) == 1
    assert sum(len(sent) for sent in words.sents) == len(words)


@pytest.mark.models
def test_single_question(EN):
    string = 'A test sentence?'
    words = EN(string, tag=False, parse=True)
    assert len(words) == 4
    assert len(list(words.sents)) == 1
    assert sum(len(sent) for sent in words.sents) == len(words)


@pytest.mark.models
def test_sentence_breaks(EN):
    doc = EN.tokenizer.tokens_from_list(u'This is a sentence . This is another one .'.split(' '))
    EN.tagger(doc)
    with EN.parser.step_through(doc) as stepwise:
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('L-nsubj')
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('S')
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('L-det')
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('R-attr')
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('D')
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('R-punct')
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('B-ROOT')
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('L-nsubj')
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('S')
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('L-attr')
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('R-attr')
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('D')
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('R-punct')
    assert len(list(doc.sents)) == 2
    for tok in doc:
        assert tok.dep != 0 or tok.is_space
    assert [ tok.head.i for tok in doc ] == [1,1,3,1,1,6,6,8,6,6]


def apply_transition_sequence(model, doc, sequence):
    with model.parser.step_through(doc) as stepwise:
        for transition in sequence:
            stepwise.transition(transition)


@pytest.mark.models
def test_sbd_serialization_projective(EN):
    """
    test that before and after serialization, the sentence boundaries are the same.
    """

    example = EN.tokenizer.tokens_from_list(u"I bought a couch from IKEA. It was n't very comfortable .".split(' '))
    EN.tagger(example)
    apply_transition_sequence(EN, example, ['L-nsubj','S','L-det','R-dobj','D','R-prep','R-pobj','B-ROOT','L-nsubj','R-neg','D','S','L-advmod','R-acomp','D','R-punct'])

    example_serialized = Doc(EN.vocab).from_bytes(example.to_bytes())

    assert example.to_bytes() == example_serialized.to_bytes()
    assert [s.text for s in example.sents] == [s.text for s in example_serialized.sents]


def test_sbd_empty_string(EN):
    '''Test Issue #309: SBD fails on empty string
    '''
    doc = EN(u' ')
    doc.is_parsed = True
    assert len(doc) == 1
    sents = list(doc.sents)
    assert len(sents) == 1


# TODO:
# @pytest.mark.models
# def test_sbd_serialization_nonprojective(DE):
#     """
#     test that before and after serialization, the sentence boundaries are the same in a non-projective sentence.
#     """
#     example = EN.tokenizer.tokens_from_list(u"Den Mann hat Peter nicht gesehen . Er war zu langsam .".split(' '))
#     EN.tagger(example)
#     apply_transition_sequence(EN, example, ['L-nk','L-oa||oc','R-sb','D','S','L-ng','B-ROOT','L-nsubj','R-neg','D','S','L-advmod','R-acomp','D','R-punct'])
#     print [(t.dep_,t.head.i) for t in example]

#     example_serialized = Doc(EN.vocab).from_bytes(example.to_bytes())

#     assert example.to_bytes() == example_serialized.to_bytes()
#     assert [s.text for s in example.sents] == [s.text for s in example_serialized.sents]
    












