# coding: utf-8
from __future__ import unicode_literals

from ....tokens import Doc
from ...util import get_doc, apply_transition_sequence

import pytest


@pytest.mark.parametrize('text', ["A test sentence"])
@pytest.mark.parametrize('punct', ['.', '!', '?', ''])
def test_en_sbd_single_punct(en_tokenizer, text, punct):
    heads = [2, 1, 0, -1] if punct else [2, 1, 0]
    tokens = en_tokenizer(text + punct)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads)
    assert len(doc) == 4 if punct else 3
    assert len(list(doc.sents)) == 1
    assert sum(len(sent) for sent in doc.sents) == len(doc)


@pytest.mark.xfail
def test_en_sentence_breaks(en_tokenizer, en_parser):
    text = "This is a sentence . This is another one ."
    heads = [1, 0, 1, -2, -3, 1, 0, 1, -2, -3]
    deps = ['nsubj', 'ROOT', 'det', 'attr', 'punct', 'nsubj', 'ROOT', 'det',
            'attr', 'punct']
    transition = ['L-nsubj', 'S', 'L-det', 'R-attr', 'D', 'R-punct', 'B-ROOT',
                  'L-nsubj', 'S', 'L-attr', 'R-attr', 'D', 'R-punct']

    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads, deps=deps)
    apply_transition_sequence(en_parser, doc, transition)

    assert len(list(doc.sents)) == 2
    for token in doc:
        assert token.dep != 0 or token.is_space
    assert [token.head.i for token in doc ] == [1, 1, 3, 1, 1, 6, 6, 8, 6, 6]


# Currently, there's no way of setting the serializer data for the parser
# without loading the models, so we can't remove the model dependency here yet.

@pytest.mark.xfail
@pytest.mark.models('en')
def test_en_sbd_serialization_projective(EN):
    """Test that before and after serialization, the sentence boundaries are
    the same."""

    text = "I bought a couch from IKEA It wasn't very comfortable."
    transition = ['L-nsubj', 'S', 'L-det', 'R-dobj', 'D', 'R-prep', 'R-pobj',
                  'B-ROOT', 'L-nsubj', 'R-neg', 'D', 'S', 'L-advmod',
                  'R-acomp', 'D', 'R-punct']

    doc = EN.tokenizer(text)
    apply_transition_sequence(EN.parser, doc, transition)
    doc_serialized = Doc(EN.vocab).from_bytes(doc.to_bytes())
    assert doc.is_parsed == True
    assert doc_serialized.is_parsed == True
    assert doc.to_bytes() == doc_serialized.to_bytes()
    assert [s.text for s in doc.sents] == [s.text for s in doc_serialized.sents]


TEST_CASES = [
    pytest.mark.xfail(("Hello World. My name is Jonas.", ["Hello World.", "My name is Jonas."])),
    ("What is your name? My name is Jonas.", ["What is your name?", "My name is Jonas."]),
    ("There it is! I found it.", ["There it is!", "I found it."]),
    ("My name is Jonas E. Smith.", ["My name is Jonas E. Smith."]),
    ("Please turn to p. 55.", ["Please turn to p. 55."]),
    ("Were Jane and co. at the party?", ["Were Jane and co. at the party?"]),
    ("They closed the deal with Pitt, Briggs & Co. at noon.", ["They closed the deal with Pitt, Briggs & Co. at noon."]),
    ("Let's ask Jane and co. They should know.", ["Let's ask Jane and co.", "They should know."]),
    ("They closed the deal with Pitt, Briggs & Co. It closed yesterday.", ["They closed the deal with Pitt, Briggs & Co.", "It closed yesterday."]),
    ("I can see Mt. Fuji from here.", ["I can see Mt. Fuji from here."]),
    pytest.mark.xfail(("St. Michael's Church is on 5th st. near the light.", ["St. Michael's Church is on 5th st. near the light."])),
    ("That is JFK Jr.'s book.", ["That is JFK Jr.'s book."]),
    ("I visited the U.S.A. last year.", ["I visited the U.S.A. last year."]),
    ("I live in the E.U. How about you?", ["I live in the E.U.", "How about you?"]),
    ("I live in the U.S. How about you?", ["I live in the U.S.", "How about you?"]),
    ("I work for the U.S. Government in Virginia.", ["I work for the U.S. Government in Virginia."]),
    ("I have lived in the U.S. for 20 years.", ["I have lived in the U.S. for 20 years."]),
    pytest.mark.xfail(("At 5 a.m. Mr. Smith went to the bank. He left the bank at 6 P.M. Mr. Smith then went to the store.", ["At 5 a.m. Mr. Smith went to the bank.", "He left the bank at 6 P.M.", "Mr. Smith then went to the store."])),
    ("She has $100.00 in her bag.", ["She has $100.00 in her bag."]),
    ("She has $100.00. It is in her bag.", ["She has $100.00.", "It is in her bag."]),
    ("He teaches science (He previously worked for 5 years as an engineer.) at the local University.", ["He teaches science (He previously worked for 5 years as an engineer.) at the local University."]),
    ("Her email is Jane.Doe@example.com. I sent her an email.", ["Her email is Jane.Doe@example.com.", "I sent her an email."]),
    ("The site is: https://www.example.50.com/new-site/awesome_content.html. Please check it out.", ["The site is: https://www.example.50.com/new-site/awesome_content.html.", "Please check it out."]),
    pytest.mark.xfail(("She turned to him, 'This is great.' she said.", ["She turned to him, 'This is great.' she said."])),
    pytest.mark.xfail(('She turned to him, "This is great." she said.', ['She turned to him, "This is great." she said.'])),
    ('She turned to him, "This is great." She held the book out to show him.', ['She turned to him, "This is great."', "She held the book out to show him."]),
    ("Hello!! Long time no see.", ["Hello!!", "Long time no see."]),
    ("Hello?? Who is there?", ["Hello??", "Who is there?"]),
    ("Hello!? Is that you?", ["Hello!?", "Is that you?"]),
    ("Hello?! Is that you?", ["Hello?!", "Is that you?"]),
    pytest.mark.xfail(("1.) The first item 2.) The second item", ["1.) The first item", "2.) The second item"])),
    pytest.mark.xfail(("1.) The first item. 2.) The second item.", ["1.) The first item.", "2.) The second item."])),
    pytest.mark.xfail(("1) The first item 2) The second item", ["1) The first item", "2) The second item"])),
    ("1) The first item. 2) The second item.", ["1) The first item.", "2) The second item."]),
    pytest.mark.xfail(("1. The first item 2. The second item", ["1. The first item", "2. The second item"])),
    pytest.mark.xfail(("1. The first item. 2. The second item.", ["1. The first item.", "2. The second item."])),
    pytest.mark.xfail(("• 9. The first item • 10. The second item", ["• 9. The first item", "• 10. The second item"])),
    pytest.mark.xfail(("⁃9. The first item ⁃10. The second item", ["⁃9. The first item", "⁃10. The second item"])),
    pytest.mark.xfail(("a. The first item b. The second item c. The third list item", ["a. The first item", "b. The second item", "c. The third list item"])),
    ("This is a sentence\ncut off in the middle because pdf.", ["This is a sentence\ncut off in the middle because pdf."]),
    ("It was a cold \nnight in the city.", ["It was a cold \nnight in the city."]),
    pytest.mark.xfail(("features\ncontact manager\nevents, activities\n", ["features", "contact manager", "events, activities"])),
    pytest.mark.xfail(("You can find it at N°. 1026.253.553. That is where the treasure is.", ["You can find it at N°. 1026.253.553.", "That is where the treasure is."])),
    ("She works at Yahoo! in the accounting department.", ["She works at Yahoo! in the accounting department."]),
    ("We make a good team, you and I. Did you see Albert I. Jones yesterday?", ["We make a good team, you and I.", "Did you see Albert I. Jones yesterday?"]),
    ("Thoreau argues that by simplifying one’s life, “the laws of the universe will appear less complex. . . .”", ["Thoreau argues that by simplifying one’s life, “the laws of the universe will appear less complex. . . .”"]),
    pytest.mark.xfail((""""Bohr [...] used the analogy of parallel stairways [...]" (Smith 55).""", ['"Bohr [...] used the analogy of parallel stairways [...]" (Smith 55).'])),
    ("If words are left off at the end of a sentence, and that is all that is omitted, indicate the omission with ellipsis marks (preceded and followed by a space) and then indicate the end of the sentence with a period . . . . Next sentence.", ["If words are left off at the end of a sentence, and that is all that is omitted, indicate the omission with ellipsis marks (preceded and followed by a space) and then indicate the end of the sentence with a period . . . .", "Next sentence."]),
    ("I never meant that.... She left the store.", ["I never meant that....", "She left the store."]),
    pytest.mark.xfail(("I wasn’t really ... well, what I mean...see . . . what I'm saying, the thing is . . . I didn’t mean it.", ["I wasn’t really ... well, what I mean...see . . . what I'm saying, the thing is . . . I didn’t mean it."])),
    pytest.mark.xfail(("One further habit which was somewhat weakened . . . was that of combining words into self-interpreting compounds. . . . The practice was not abandoned. . . .", ["One further habit which was somewhat weakened . . . was that of combining words into self-interpreting compounds.", ". . . The practice was not abandoned. . . ."])),
    pytest.mark.xfail(("Hello world.Today is Tuesday.Mr. Smith went to the store and bought 1,000.That is a lot.", ["Hello world.", "Today is Tuesday.", "Mr. Smith went to the store and bought 1,000.", "That is a lot."]))
]

@pytest.mark.skip
@pytest.mark.models('en')
@pytest.mark.parametrize('text,expected_sents', TEST_CASES)
def test_en_sbd_prag(EN, text, expected_sents):
    """SBD tests from Pragmatic Segmenter"""
    doc = EN(text)
    sents = []
    for sent in doc.sents:
        sents.append(''.join(doc[i].string for i in range(sent.start, sent.end)).strip())
    assert sents == expected_sents
