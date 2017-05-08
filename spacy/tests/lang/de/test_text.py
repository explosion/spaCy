# coding: utf-8
"""Test that longer and mixed texts are tokenized correctly."""


from __future__ import unicode_literals

import pytest


def test_tokenizer_handles_long_text(de_tokenizer):
    text = """Die Verwandlung

Als Gregor Samsa eines Morgens aus unruhigen Träumen erwachte, fand er sich in
seinem Bett zu einem ungeheueren Ungeziefer verwandelt.

Er lag auf seinem panzerartig harten Rücken und sah, wenn er den Kopf ein wenig
hob, seinen gewölbten, braunen, von bogenförmigen Versteifungen geteilten
Bauch, auf dessen Höhe sich die Bettdecke, zum gänzlichen Niedergleiten bereit,
kaum noch erhalten konnte. Seine vielen, im Vergleich zu seinem sonstigen
Umfang kläglich dünnen Beine flimmerten ihm hilflos vor den Augen.

»Was ist mit mir geschehen?«, dachte er."""

    tokens = de_tokenizer(text)
    assert len(tokens) == 109


@pytest.mark.parametrize('text,length', [
    ("Donaudampfschifffahrtsgesellschaftskapitänsanwärterposten", 1),
    ("Rindfleischetikettierungsüberwachungsaufgabenübertragungsgesetz", 1),
    ("Kraftfahrzeug-Haftpflichtversicherung", 3),
    ("Vakuum-Mittelfrequenz-Induktionsofen", 5)
    ])
def test_tokenizer_handles_long_words(de_tokenizer, text, length):
    tokens = de_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize('text,length', [
    ("»Was ist mit mir geschehen?«, dachte er.", 12),
    ("“Dies frühzeitige Aufstehen”, dachte er, “macht einen ganz blödsinnig. ", 15)
    ])
def test_tokenizer_handles_examples(de_tokenizer, text, length):
    tokens = de_tokenizer(text)
    assert len(tokens) == length
