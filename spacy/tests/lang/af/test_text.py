import pytest


def test_long_text(af_tokenizer):
    # Excerpt: Universal Declaration of Human Rights; “'n” changed to “die” in first sentence
    text = """
Hierdie Universele Verklaring van Menseregte as die algemene standaard vir die verwesenliking deur alle mense en nasies, 
om te verseker dat elke individu en elke deel van die gemeenskap hierdie Verklaring in ag sal neem en deur opvoeding, 
respek vir hierdie regte en vryhede te bevorder, op nasionale en internasionale vlak, daarna sal strewe om die universele 
en effektiewe erkenning en agting van hierdie regte te verseker, nie net vir die mense van die Lidstate nie, maar ook vir 
die mense in die gebiede onder hul jurisdiksie.

"""
    tokens = af_tokenizer(text)
    assert len(tokens) == 100


@pytest.mark.xfail
def test_indefinite_article(af_tokenizer):
    text = "as 'n algemene standaard"
    tokens = af_tokenizer(text)
    assert len(tokens) == 4
