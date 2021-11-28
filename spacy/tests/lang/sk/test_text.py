import pytest


def test_long_text(sk_tokenizer):
    # Excerpt: European Convention on Human Rights
    text = """
majúc na zreteli, že cieľom tejto deklarácie je zabezpečiť všeobecné
a účinné uznávanie a dodržiavanie práv v nej vyhlásených;
majúc na zreteli, že cieľom Rady Európy je dosiahnutie väčšej
jednoty medzi jej členmi, a že jedným zo spôsobov, ktorým sa
má tento cieľ napĺňať, je ochrana a ďalší rozvoj ľudských práv
a základných slobôd;
znovu potvrdzujúc svoju hlbokú vieru v tie základné slobody, ktoré
sú základom spravodlivosti a mieru vo svete, a ktoré sú najlepšie
zachovávané na jednej strane účinnou politickou demokraciou
a na strane druhej spoločným poňatím a dodržiavaním ľudských
práv, od ktorých závisia;
    """
    tokens = sk_tokenizer(text)
    assert len(tokens) == 118


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10,000", True),
        ("10,00", True),
        ("štyri", True),
        ("devätnásť", True),
        ("milión", True),
        ("pes", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(sk_tokenizer, text, match):
    tokens = sk_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match


@pytest.mark.xfail
def test_ordinal_number(sk_tokenizer):
    text = "10. decembra 1948"
    tokens = sk_tokenizer(text)
    assert len(tokens) == 3
