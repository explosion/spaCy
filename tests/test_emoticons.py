from __future__ import unicode_literals

from spacy.en import EN

def test_tweebo_challenge():
    text = u""":o :/ :'( >:o (: :) >.< XD -__- o.O ;D :-) @_@ :P 8D :1 >:( :D =| ") :> ...."""
    tokens = EN.tokenize(text)
    assert tokens[0].string == ":o"
    assert tokens[1].string == ":/"
    assert tokens[2].string == ":'("
    assert tokens[3].string == ">:o"
    assert tokens[4].string == "(:"
    assert tokens[5].string == ":)"
    assert tokens[6].string == ">.<"
    assert tokens[7].string == "XD"
    assert tokens[8].string == "-__-"
    assert tokens[9].string == "o.O"
    assert tokens[10].string == ";D"
    assert tokens[11].string == ":-)"
    assert tokens[12].string == "@_@"
    assert tokens[13].string == ":P"
    assert tokens[14].string == "8D"
    assert tokens[15].string == ":1"
    assert tokens[16].string == ">:("
    assert tokens[17].string == ":D"
    assert tokens[18].string == "=|"
    assert tokens[19].string == '")'
    assert tokens[20].string == ':>'
    assert tokens[21].string == '....'


def test_false_positive():
    text = "example:)"
    tokens = EN.tokenize(text)
    assert len(tokens) == 3
