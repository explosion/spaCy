"""Test that longer and mixed texts are tokenized correctly."""
import pytest


def test_ca_tokenizer_handles_long_text(ca_tokenizer):
    text = """Una taula amb grans gerres de begudes i palles de coloraines com a reclam. Una carta
    cridanera amb ofertes de tapes, paelles i sangria. Un cambrer amb un somriure que convida a
    seure. La ubicació perfecta: el bell mig de la Rambla. Però és la una del migdia d’un dimecres
    de tardor i no hi ha ningú assegut a la terrassa del local. El dia és rúfol, però no fa fred i
    a la majoria de terrasses de la Rambla hi ha poca gent. La immensa majoria dels clients -tret
    d’alguna excepció com al restaurant Núria- són turistes. I la immensa majoria tenen entre mans
    una gerra de cervesa. Ens asseiem -fotògraf i periodista- en una terrassa buida."""

    tokens = ca_tokenizer(text)
    assert len(tokens) == 146


@pytest.mark.parametrize(
    "text,length",
    [
        ("Perquè va anar-hi?", 5),
        ("El cotxe dels veins.", 6),
        ("“Ah no?”", 5),
        ("""Sí! "Anem", va contestar el Joan Carles""", 11),
        ("Van córrer aprox. 10km", 5),
        ("Llavors perqué...", 3),
        ("Vull parlar-te'n demà al matí", 8),
        ("Vull explicar-t'ho demà al matí", 8),
    ],
)
def test_ca_tokenizer_handles_cnts(ca_tokenizer, text, length):
    tokens = ca_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10,000", True),
        ("10,00", True),
        ("999.0", True),
        ("un", True),
        ("dos", True),
        ("bilió", True),
        ("gos", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_ca_lex_attrs_like_number(ca_tokenizer, text, match):
    tokens = ca_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
