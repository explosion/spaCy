import pytest


@pytest.mark.parametrize(
    "text,norms,lemmas",
    [
        ("о.г.", ["ове године"], ["ова година"]),
        ("чет.", ["четвртак"], ["четвртак"]),
        ("гђа", ["госпођа"], ["госпођа"]),
        ("ил'", ["или"], ["или"]),
    ],
)
def test_sr_tokenizer_abbrev_exceptions(sr_tokenizer, text, norms, lemmas):
    tokens = sr_tokenizer(text)
    assert len(tokens) == 1
    assert [token.norm_ for token in tokens] == norms
