from __future__ import unicode_literals

import pytest


def test_tokenizer_handles_emoticons(en_tokenizer):
    # Tweebo challenge (CMU)
    text = u""":o :/ :'( >:o (: :) >.< XD -__- o.O ;D :-) @_@ :P 8D :1 >:( :D =| ") :> ...."""
    tokens = en_tokenizer(text)
    assert tokens[0].orth_ == ":o"
    assert tokens[1].orth_ == ":/"
    assert tokens[2].orth_ == ":'("
    assert tokens[3].orth_ == ">:o"
    assert tokens[4].orth_ == "(:"
    assert tokens[5].orth_ == ":)"
    assert tokens[6].orth_ == ">.<"
    assert tokens[7].orth_ == "XD"
    assert tokens[8].orth_ == "-__-"
    assert tokens[9].orth_ == "o.O"
    assert tokens[10].orth_ == ";D"
    assert tokens[11].orth_ == ":-)"
    assert tokens[12].orth_ == "@_@"
    assert tokens[13].orth_ == ":P"
    assert tokens[14].orth_ == "8D"
    assert tokens[15].orth_ == ":1"
    assert tokens[16].orth_ == ">:("
    assert tokens[17].orth_ == ":D"
    assert tokens[18].orth_ == "=|"
    assert tokens[19].orth_ == '")'
    assert tokens[20].orth_ == ':>'
    assert tokens[21].orth_ == '....'


@pytest.mark.parametrize('text,length', [("example:)", 3), ("108)", 2), ("XDN", 1)])
def test_tokenizer_excludes_false_pos_emoticons(en_tokenizer, text, length):
    tokens = en_tokenizer(text)
    assert len(tokens) == length
