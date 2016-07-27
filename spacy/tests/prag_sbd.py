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

def test_gr24():
    sents = get_sent_strings("She turned to him, 'This is great.' she said.")
    assert sents == ["She turned to him, 'This is great.' she said."]

def test_gr25():
    sents = get_sent_strings('She turned to him, "This is great." she said.')
    assert sents == ['She turned to him, "This is great." she said.']

def test_gr26():
    sents = get_sent_strings('She turned to him, "This is great." She held the book out to show him.')
    assert sents == ['She turned to him, "This is great."', "She held the book out to show him."]

def test_gr27():
    sents = get_sent_strings("Hello!! Long time no see.")
    assert sents == ["Hello!!", "Long time no see."]

def test_gr28():
    sents = get_sent_strings("Hello?? Who is there?")
    assert sents == ["Hello??", "Who is there?"]

def test_gr29():
    sents = get_sent_strings("Hello!? Is that you?")
    assert sents == ["Hello!?", "Is that you?"]

def test_gr30():
    sents = get_sent_strings("Hello?! Is that you?")
    assert sents == ["Hello?!", "Is that you?"]

def test_gr31():
    sents = get_sent_strings("1.) The first item 2.) The second item")
    assert sents == ["1.) The first item", "2.) The second item"]

def test_gr32():
    sents = get_sent_strings("1.) The first item. 2.) The second item.")
    assert sents == ["1.) The first item.", "2.) The second item."]

def test_gr33():
    sents = get_sent_strings("1) The first item 2) The second item")
    assert sents == ["1) The first item", "2) The second item"]

def test_gr34():
    sents = get_sent_strings("1) The first item. 2) The second item.")
    assert sents == ["1) The first item.", "2) The second item."]

def test_gr35():
    sents = get_sent_strings("1. The first item 2. The second item")
    assert sents == ["1. The first item", "2. The second item"]

def test_gr36():
    sents = get_sent_strings("1. The first item. 2. The second item.")
    assert sents == ["1. The first item.", "2. The second item."]

def test_gr37():
    sents = get_sent_strings("• 9. The first item • 10. The second item")
    assert sents == ["• 9. The first item", "• 10. The second item"]

def test_gr38():
    sents = get_sent_strings("⁃9. The first item ⁃10. The second item")
    assert sents == ["⁃9. The first item", "⁃10. The second item"]

def test_gr39():
    sents = get_sent_strings("a. The first item b. The second item c. The third list item")
    assert sents == ["a. The first item", "b. The second item", "c. The third list item"]

def test_gr40():
    sents = get_sent_strings("This is a sentence\ncut off in the middle because pdf.")
    assert sents == ["This is a sentence\ncut off in the middle because pdf."]

def test_gr41():
    sents = get_sent_strings("It was a cold \nnight in the city.")
    assert sents == ["It was a cold \nnight in the city."]

def test_gr42():
    sents = get_sent_strings("features\ncontact manager\nevents, activities\n")
    assert sents == ["features", "contact manager", "events, activities"]

def test_gr43():
    sents = get_sent_strings("You can find it at N°. 1026.253.553. That is where the treasure is.")
    assert sents == ["You can find it at N°. 1026.253.553.", "That is where the treasure is."]

def test_gr44():
    sents = get_sent_strings("She works at Yahoo! in the accounting department.")
    assert sents == ["She works at Yahoo! in the accounting department."]

def test_gr45():
    sents = get_sent_strings("We make a good team, you and I. Did you see Albert I. Jones yesterday?")
    assert sents == ["We make a good team, you and I.", "Did you see Albert I. Jones yesterday?"]

def test_gr46():
    sents = get_sent_strings("Thoreau argues that by simplifying one’s life, “the laws of the universe will appear less complex. . . .”")
    assert sents == ["Thoreau argues that by simplifying one’s life, “the laws of the universe will appear less complex. . . .”"]

def test_gr47():
    sents = get_sent_strings(""""Bohr [...] used the analogy of parallel stairways [...]" (Smith 55).""")
    assert sents == ['"Bohr [...] used the analogy of parallel stairways [...]" (Smith 55).']

def test_gr48():
    sents = get_sent_strings("If words are left off at the end of a sentence, and that is all that is omitted, indicate the omission with ellipsis marks (preceded and followed by a space) and then indicate the end of the sentence with a period . . . . Next sentence.")
    assert sents == ["If words are left off at the end of a sentence, and that is all that is omitted, indicate the omission with ellipsis marks (preceded and followed by a space) and then indicate the end of the sentence with a period . . . .", "Next sentence."]

def test_gr49():
    sents = get_sent_strings("I never meant that.... She left the store.")
    assert sents == ["I never meant that....", "She left the store."]

def test_gr50():
    sents = get_sent_strings("I wasn’t really ... well, what I mean...see . . . what I'm saying, the thing is . . . I didn’t mean it.")
    assert sents == ["I wasn’t really ... well, what I mean...see . . . what I'm saying, the thing is . . . I didn’t mean it."]

def test_gr51():
    sents = get_sent_strings("One further habit which was somewhat weakened . . . was that of combining words into self-interpreting compounds. . . . The practice was not abandoned. . . .")
    assert sents == ["One further habit which was somewhat weakened . . . was that of combining words into self-interpreting compounds.", ". . . The practice was not abandoned. . . ."]

def test_gr52():
    sents = get_sent_strings("Hello world.Today is Tuesday.Mr. Smith went to the store and bought 1,000.That is a lot.",)
    assert sents == ["Hello world.", "Today is Tuesday.", "Mr. Smith went to the store and bought 1,000.", "That is a lot."]
