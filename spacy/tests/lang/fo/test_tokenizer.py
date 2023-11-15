import pytest

# examples taken from Basic LAnguage Resource Kit 1.0 for Faroese (https://maltokni.fo/en/resources) licensed with CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
# fmt: off
FO_TOKEN_EXCEPTION_TESTS = [
    (
        "Eftir løgtingslóg um samsýning og eftirløn landsstýrismanna v.m., skulu løgmaður og landsstýrismenn vanliga siga frá sær størv í almennari tænastu ella privatum virkjum, samtøkum ella stovnum. ",
        [
            "Eftir", "løgtingslóg", "um", "samsýning", "og", "eftirløn", "landsstýrismanna", "v.m.", ",", "skulu", "løgmaður", "og", "landsstýrismenn", "vanliga", "siga", "frá", "sær", "størv", "í", "almennari", "tænastu", "ella", "privatum", "virkjum", ",", "samtøkum", "ella", "stovnum", ".",
        ],
    ),
    (
        "Sambandsflokkurin gongur aftur við 2,7 prosentum í mun til valið í 1994, tá flokkurin fekk undirtøku frá 23,4 prosent av veljarunum.",
        [
            "Sambandsflokkurin", "gongur", "aftur", "við", "2,7", "prosentum", "í", "mun", "til", "valið", "í", "1994", ",", "tá", "flokkurin", "fekk", "undirtøku", "frá", "23,4", "prosent", "av", "veljarunum", ".",
        ],
    ),
]
# fmt: on


@pytest.mark.parametrize("text,expected_tokens", FO_TOKEN_EXCEPTION_TESTS)
def test_fo_tokenizer_handles_exception_cases(fo_tokenizer, text, expected_tokens):
    tokens = fo_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
