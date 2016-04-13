from __future__ import unicode_literals

import pytest



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
    doc = EN.tokenizer.tokens_from_list('This is a sentence . This is another one .'.split(' '))
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
    doc = EN.tokenizer.tokens_from_list('\t This is \n a sentence \n \n . \n \t \n This is another \t one .'.split(' '))
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
