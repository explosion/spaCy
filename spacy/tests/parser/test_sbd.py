from __future__ import unicode_literals

import pytest
from spacy.tokens import Doc


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
    words = EN(string, tag=False, parse=False)
    assert len(words) == 4
    assert len(list(words.sents)) == 1
    assert sum(len(sent) for sent in words.sents) == len(words)


@pytest.mark.models
def test_sentence_breaks_no_space(EN):
    doc = EN.tokenizer.tokens_from_list(u'This is a sentence . This is another one .'.split(' '))
    EN.tagger(doc)
    with EN.parser.step_through(doc) as stepwise:
        # stack empty, automatic Shift (This)
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('L-nsubj') # attach This
        # stack empty, automatic Shift (is)
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('S') # shift a
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('L-det') # attach a
        assert not EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('R-attr') # attach sentence
        stepwise.transition('D') # remove sentence
        assert not EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('R-punct') # attach .
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('B-ROOT') # set sentence start on This
        # automatic reduction of the stack, automatic Shift to start second sentence
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('L-nsubj') # attach This
        # stack empty, automatic Shift (is)
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('S') # shift another
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('L-attr') # attach another
        assert not EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('R-attr') # attach one
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('D') # remove one
        assert not EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('R-punct') # attach .
        # buffer empty, automatic cleanup
    assert len(list(doc.sents)) == 2
    for tok in doc:
        assert tok.dep != 0 or tok.is_space
    assert [ tok.head.i for tok in doc ] == [1,1,3,1,1,6,6,8,6,6]


@pytest.mark.models
def test_sentence_breaks_with_space(EN):
    doc = EN.tokenizer.tokens_from_list(u'\t This is \n a sentence \n \n . \n \t \n This is another \t one .'.split(' '))
    EN.tagger(doc)
    with EN.parser.step_through(doc) as stepwise:
        # stack empty, automatic Shift (This)
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('L-nsubj') # attach This
        # stack empty, automatic Shift (is)
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('S') # shift a
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('L-det') # attach a
        assert not EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('R-attr') # attach sentence
        stepwise.transition('D') # remove sentence
        assert not EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('R-punct') # attach .
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('B-ROOT') # set sentence start on This
        # automatic reduction of the stack, automatic Shift to start second sentence
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('L-nsubj') # attach This
        # stack empty, automatic Shift (is)
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('S') # shift another
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('L-attr') # attach another
        assert not EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('R-attr') # attach one
        assert EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('D') # remove one
        assert not EN.parser.moves.is_valid(stepwise.stcls,'B-ROOT')
        stepwise.transition('R-punct') # attach .
        # buffer empty, automatic cleanup
    assert len(list(doc.sents)) == 2
    for tok in doc:
        assert tok.dep != 0 or tok.is_space
    assert [ tok.head.i for tok in doc ] == [1,2,2,2,5,2,5,5,2,8,8,8,13,13,16,14,13,13]



def apply_transition_sequence(model, doc, sequence):
    with model.parser.step_through(doc) as stepwise:
        for transition in sequence:
            stepwise.transition(transition)


@pytest.mark.models
def test_sbd_for_root_label_dependents(EN):
    """
    make sure that the parser properly introduces a sentence boundary without
    the break transition by checking for dependents with the root label
    """
    example = EN.tokenizer.tokens_from_list(u"I saw a firefly It glowed".split(' '))
    EN.tagger(example)
    apply_transition_sequence(EN, example, ['L-nsubj','S','L-det','R-dobj','D','S','L-nsubj','R-ROOT'])

    assert example[1].head.i == 1
    assert example[5].head.i == 5

    sents = list(example.sents)
    assert len(sents) == 2
    assert sents[1][0].orth_ == u'It'



@pytest.mark.models
def test_sbd_serialization(EN):
    """
    test that before and after serialization, the sentence boundaries are the same even
    if the parser predicted two roots for the sentence that were made into two sentences
    after parsing by arc_eager.finalize()

    This is actually an interaction between the sentence boundary prediction and doc.from_array
    The process is the following: if the parser doesn't predict a sentence boundary but attaches
    a word with the ROOT label, the second root node is made root of its own sentence after parsing.
    During serialization, sentence boundary information is lost and reintroduced when the code
    is deserialized by introducing sentence starts at every left-edge of every root node.

    BUG that is tested here: So far, the parser wasn't introducing a sentence start when 
    it introduced the second root node.
    """

    example = EN.tokenizer.tokens_from_list(u"I bought a couch from IKEA. It was n't very comfortable .".split(' '))
    EN.tagger(example)
    apply_transition_sequence(EN, example, ['L-nsubj','S','L-det','R-dobj','D','R-prep','R-pobj','D','D','S','L-nsubj','R-ROOT','R-neg','D','S','L-advmod','R-acomp','D','R-punct'])

    example_serialized = Doc(EN.vocab).from_bytes(example.to_bytes())

    assert example.to_bytes() == example_serialized.to_bytes()
    assert [s.text for s in example.sents] == [s.text for s in example_serialized.sents]
