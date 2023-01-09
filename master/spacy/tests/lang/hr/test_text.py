import pytest


def test_long_text(hr_tokenizer):
    # Excerpt: European Convention on Human Rights
    text = """
uzimajući u obzir da ta deklaracija nastoji osigurati opće i djelotvorno
priznanje i poštovanje u njoj proglašenih prava;
uzimajući u obzir da je cilj Vijeća Europe postizanje većeg jedinstva
njegovih članica, i da je jedan od načina postizanja toga cilja
očuvanje i daljnje ostvarivanje ljudskih prava i temeljnih sloboda;
potvrđujući svoju duboku privrženost tim temeljnim slobodama
koje su osnova pravde i mira u svijetu i koje su najbolje zaštićene
istinskom političkom demokracijom s jedne strane te zajedničkim
razumijevanjem i poštovanjem ljudskih prava o kojima te slobode
ovise s druge strane;
"""
    tokens = hr_tokenizer(text)
    assert len(tokens) == 105


@pytest.mark.xfail
def test_ordinal_number(hr_tokenizer):
    text = "10. prosinca 1948"
    tokens = hr_tokenizer(text)
    assert len(tokens) == 3
