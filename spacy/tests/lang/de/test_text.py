import pytest


def test_de_tokenizer_handles_long_text(de_tokenizer):
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


@pytest.mark.parametrize(
    "text",
    [
        "Donaudampfschifffahrtsgesellschaftskapitänsanwärterposten",
        "Rindfleischetikettierungsüberwachungsaufgabenübertragungsgesetz",
        "Kraftfahrzeug-Haftpflichtversicherung",
        "Vakuum-Mittelfrequenz-Induktionsofen",
    ],
)
def test_de_tokenizer_handles_long_words(de_tokenizer, text):
    tokens = de_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize(
    "text,length",
    [
        ("»Was ist mit mir geschehen?«, dachte er.", 12),
        ("“Dies frühzeitige Aufstehen”, dachte er, “macht einen ganz blödsinnig. ", 15),
    ],
)
def test_de_tokenizer_handles_examples(de_tokenizer, text, length):
    tokens = de_tokenizer(text)
    assert len(tokens) == length
