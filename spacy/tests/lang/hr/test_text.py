"""Words like numbers are recognized correctly."""
import pytest

def test_long_text(hr_tokenizer):
    # Excerpt: European Convention on Human Rights
    text = """
Vlade potpisnice, članice Vijeća Europe,
uzimajući u obzir Opću deklaraciju o pravima čovjeka koju je Opća
skupština Ujedinjenih naroda proglasila 10. prosinca 1948.;
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
    assert len(tokens) == 136