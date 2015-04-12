# encoding: utf-8
# SBD tests from "Pragmatic Segmenter"
from __future__ import unicode_literals

from spacy.en import English

EN = English()


def get_sent_strings(text):
    tokens = EN(text)
    sents = []
    for sent in tokens.sents:
        sents.append(''.join(tokens[i].string
                     for i in range(sent.start, sent.end)).strip())
    return sents


def test_gr1():
    sents = get_sent_strings("Hello World. My name is Jonas.")
    assert sents == ["Hello World.", "My name is Jonas."]


def test_gr2():
    sents = get_sent_strings("What is your name? My name is Jonas.")
    assert sents == ["What is your name?", "My name is Jonas."]


def test_gr3():
    sents = get_sent_strings("There it is! I found it.")
    assert sents == ["There it is!", "I found it."]


def test_gr4():
    sents = get_sent_strings("My name is Jonas E. Smith.")
    assert sents == ["My name is Jonas E. Smith."]


def test_gr5():
    sents = get_sent_strings("Please turn to p. 55.")
    assert sents == ["Please turn to p. 55."]


def test_gr6():
    sents = get_sent_strings("Were Jane and co. at the party?")
    assert sents == ["Were Jane and co. at the party?"]


def test_gr7():
    sents = get_sent_strings("They closed the deal with Pitt, Briggs & Co. at noon.")
    assert sents == ["They closed the deal with Pitt, Briggs & Co. at noon."]


def test_gr8():
    sents = get_sent_strings("Let's ask Jane and co. They should know.")
    assert sents == ["Let's ask Jane and co.", "They should know."]


def test_gr9():
    sents = get_sent_strings("They closed the deal with Pitt, Briggs & Co. It closed yesterday.")
    assert sents == ["They closed the deal with Pitt, Briggs & Co.", "It closed yesterday."]


def test_gr10():
    sents = get_sent_strings("I can see Mt. Fuji from here.")
    assert sents == ["I can see Mt. Fuji from here."]


def test_gr11():
    sents = get_sent_strings("St. Michael's Church is on 5th st. near the light.")
    assert sents == ["St. Michael's Church is on 5th st. near the light."]


def test_gr12():
    sents = get_sent_strings("That is JFK Jr.'s book.")
    assert sents == ["That is JFK Jr.'s book."]


def test_gr13():
    sents = get_sent_strings("I visited the U.S.A. last year.")
    assert sents == ["I visited the U.S.A. last year."]


def test_gr14():
    sents = get_sent_strings("I live in the E.U. How about you?")
    assert sents == ["I live in the E.U.", "How about you?"]


def test_gr15():
    sents = get_sent_strings("I live in the U.S. How about you?")
    assert sents == ["I live in the U.S.", "How about you?"]


def test_gr16():
    sents = get_sent_strings("I work for the U.S. Government in Virginia.")
    assert sents == ["I work for the U.S. Government in Virginia."]


def test_gr17():
    sents = get_sent_strings("I have lived in the U.S. for 20 years.")
    assert sents == ["I have lived in the U.S. for 20 years."]


def test_gr18():
    sents = get_sent_strings("At 5 a.m. Mr. Smith went to the bank. He left the bank at 6 P.M. Mr. Smith then went to the store.")
    assert sents == ["At 5 a.m. Mr. Smith went to the bank.", "He left the bank at 6 P.M.", "Mr. Smith then went to the store."]


def test_gr19():
    sents = get_sent_strings("She has $100.00 in her bag.")
    assert sents == ["She has $100.00 in her bag."]


def test_gr20():
    sents = get_sent_strings("She has $100.00. It is in her bag.")
    assert sents == ["She has $100.00.", "It is in her bag."]


def test_gr21():
    sents = get_sent_strings("He teaches science (He previously worked for 5 years as an engineer.) at the local University.")
    assert sents == ["He teaches science (He previously worked for 5 years as an engineer.) at the local University."]


def test_gr22():
    sents = get_sent_strings("Her email is Jane.Doe@example.com. I sent her an email.")
    assert sents == ["Her email is Jane.Doe@example.com.", "I sent her an email."]


def test_gr23():
    sents = get_sent_strings("The site is: https://www.example.50.com/new-site/awesome_content.html. Please check it out.")
    assert sents == ["The site is: https://www.example.50.com/new-site/awesome_content.html.", "Please check it out."]

"""
"She turned to him, 'This is great.' she said."
["She turned to him, 'This is great.' she said."]

'She turned to him, "This is great." she said.'
['She turned to him, "This is great." she said.']

'She turned to him, "This is great." She held the book out to show him.'
['She turned to him, "This is great."', "She held the book out to show him."]

"Hello!! Long time no see."
["Hello!!", "Long time no see."]

"Hello?? Who is there?"
["Hello??", "Who is there?"]

"Hello!? Is that you?"
["Hello!?", "Is that you?"]

"Hello?! Is that you?"
["Hello?!", "Is that you?"]

"1.) The first item 2.) The second item"
["1.) The first item", "2.) The second item"]

"1.) The first item. 2.) The second item."
["1.) The first item.", "2.) The second item."]

"1) The first item 2) The second item"
["1) The first item", "2) The second item"]

"1) The first item. 2) The second item."
["1) The first item.", "2) The second item."]

"1. The first item 2. The second item"
["1. The first item", "2. The second item"]

"1. The first item. 2. The second item."
["1. The first item.", "2. The second item."]

"• 9. The first item • 10. The second item"
["• 9. The first item", "• 10. The second item"]

"⁃9. The first item ⁃10. The second item"
["⁃9. The first item", "⁃10. The second item"]

"a. The first item b. The second item c. The third list item"
["a. The first item", "b. The second item", "c. The third list item"]

"This is a sentence\ncut off in the middle because pdf."
["This is a sentence cut off in the middle because pdf."]

"It was a cold \nnight in the city."
["It was a cold night in the city."]

"features\ncontact manager\nevents, activities\n"
["features", "contact manager", "events, activities"]

"You can find it at N°. 1026.253.553. That is where the treasure is."
["You can find it at N°. 1026.253.553.", "That is where the treasure is."]

"She works at Yahoo! in the accounting department."
["She works at Yahoo! in the accounting department."]

"We make a good team, you and I. Did you see Albert I. Jones yesterday?"
["We make a good team, you and I.", "Did you see Albert I. Jones yesterday?"]

"Thoreau argues that by simplifying one’s life, “the laws of the universe will appear less complex. . . .”"
    end
"Ellipsis with square brackets #047"
['"Bohr [...] used the analogy of parallel stairways [...]" (Smith 55).'

"If words are left off at the end of a sentence, and that is all that is omitted, indicate the omission with ellipsis marks (preceded and followed by a space) and then indicate the end of the sentence with a period . . . . Next sentence."
["If words are left off at the end of a sentence, and that is all that is omitted, indicate the omission with ellipsis marks (preceded and followed by a space) and then indicate the end of the sentence with a period . . . .", "Next sentence."]

"I never meant that.... She left the store."
["I never meant that....", "She left the store."]

"I wasn’t really ... well, what I mean...see . . . what I'm saying, the thing is . . . I didn’t mean it."
["I wasn’t really ... well, what I mean...see . . . what I'm saying, the thing is . . . I didn’t mean it."]

"One further habit which was somewhat weakened . . . was that of combining words into self-interpreting compounds. . . . The practice was not abandoned. . . ."
["One further habit which was somewhat weakened . . . was that of combining words into self-interpreting compounds.", ". . . The practice was not abandoned. . . ."]

"Hello world.Today is Tuesday.Mr. Smith went to the store and bought 1,000.That is a lot.",
["Hello world.", "Today is Tuesday.", "Mr. Smith went to the store and bought 1,000.", "That is a lot."]
"""
