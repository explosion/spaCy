# coding: utf-8
from __future__ import unicode_literals

import pytest


def test_lb_tokenizer_handles_long_text(lb_tokenizer):
    text = """Den Nordwand an d'Sonn An der Zäit hunn sech den Nordwand an d'Sonn gestridden, wie vun hinnen zwee wuel méi staark wier, wéi e Wanderer, deen an ee waarme Mantel agepak war, iwwert de Wee koum. Si goufen sech eens, dass deejéinege fir de Stäerkste gëlle sollt, deen de Wanderer forcéiere géif, säi Mantel auszedoen. Den Nordwand huet mat aller Force geblosen, awer wat e méi geblosen huet, wat de Wanderer sech méi a säi Mantel agewéckelt huet. Um Enn huet den Nordwand säi Kampf opginn. Dunn huet d'Sonn d'Loft mat hire frëndleche Strale gewiermt, a schonn no kuerzer Zäit huet de Wanderer säi Mantel ausgedoen. Do huet den Nordwand missen zouginn, dass d'Sonn vun hinnen zwee de Stäerkste wier."""

    tokens = lb_tokenizer(text)
    assert len(tokens) == 142


@pytest.mark.parametrize(
    "text,length",
    [
        ("»Wat ass mat mir geschitt?«, huet hie geduecht.", 13),
        ("“Dëst fréi Opstoen”, denkt hien, “mécht ee ganz duercherneen. ", 15),
        ("Am Grand-Duché ass d'Liewen schéin, mee 't gëtt ze vill Autoen.", 14),
    ],
)
def test_lb_tokenizer_handles_examples(lb_tokenizer, text, length):
    tokens = lb_tokenizer(text)
    assert len(tokens) == length
