import pytest


@pytest.mark.parametrize(
    "text,norms",
    [
        ("о.г.", ["ove godine"]),
        ("чет.", ["četvrtak"]),
        ("гђа", ["gospođa"]),
        ("ил'", ["ili"]),
    ],
)
def test_sr_tokenizer_abbrev_exceptions(sr_tokenizer, text, norms):
    tokens = sr_tokenizer(text)
    assert len(tokens) == 1
    assert [token.norm_ for token in tokens] == norms
