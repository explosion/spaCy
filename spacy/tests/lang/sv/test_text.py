# coding: utf-8
from __future__ import unicode_literals


def test_sv_tokenizer_handles_long_text(sv_tokenizer):
    text = """Det var så härligt ute på landet. Det var sommar, majsen var gul, havren grön,
höet var uppställt i stackar nere vid den gröna ängen, och där gick storken på sina långa,
röda ben och snackade engelska, för det språket hade han lärt sig av sin mor.

Runt om åkrar och äng låg den stora skogen, och mitt i skogen fanns djupa sjöar; jo, det var verkligen trevligt ute på landet!"""
    tokens = sv_tokenizer(text)
    assert len(tokens) == 86


def test_sv_tokenizer_handles_trailing_dot_for_i_in_sentence(sv_tokenizer):
    text = "Provar att tokenisera en mening med ord i."
    tokens = sv_tokenizer(text)
    assert len(tokens) == 9
