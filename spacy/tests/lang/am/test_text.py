# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.lang.am.lex_attrs import like_num


def test_am_tokenizer_handles_long_text(am_tokenizer):
    text = """ሆሴ ሙጂካ በበጋ ወቅት በኦክስፎርድ ንግግር አንድያቀርቡ ሲጋበዙ ጭንቅላታቸው "ፈነዳ"።

“እጅግ ጥንታዊ” የእንግሊዝኛ ተናጋሪ ዩኒቨርስቲ፣ በአስር ሺዎች የሚቆጠሩ ዩሮዎችን ለተማሪዎች በማስተማር የሚያስከፍለው 

እና ከማርጋሬት ታቸር እስከ ስቲቨን ሆኪንግ በአዳራሾቻቸው ውስጥ ንግግር ያደረጉበት የትምህርት ማዕከል፣ በሞንቴቪዴኦ 

በሚገኘው የመንግስት ትምህርት ቤት የሰለጠኑትን የ81 ዓመቱ አዛውንት አገልግሎት ጠየቁ።"""
    tokens = am_tokenizer(text)
    
    assert len(tokens) == 51


@pytest.mark.parametrize(
    "text,length",
    [
        ("¿Por qué José Mujica?", 6),
        ("“¿Oh no?”", 6),
        ("""¡Sí! "Vámonos", contestó José Arcadio Buendía""", 11),
        ("Corrieron aprox. 10km.", 5),
        ("Y entonces por qué...", 5),
    ],
)
def test_es_tokenizer_handles_cnts(es_tokenizer, text, length):
    tokens = es_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10.000", True),
        ("1000", True),
        ("999,0", True),
        ("uno", True),
        ("dos", True),
        ("billón", True),
        ("veintiséis", True),
        ("perro", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(es_tokenizer, text, match):
    tokens = es_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match


""" @pytest.mark.parametrize("word", ["once"])
def test_am_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper()) """
