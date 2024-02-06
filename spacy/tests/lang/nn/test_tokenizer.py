import pytest

# examples taken from Omsetjingsminne frå Nynorsk pressekontor 2022 (https://www.nb.no/sprakbanken/en/resource-catalogue/oai-nb-no-sbr-80/)
# fmt: off
NN_TOKEN_EXCEPTION_TESTS = [
    (
        "Målet til direktoratet er at alle skal bli tilbydd jobb i politiet så raskt som mogleg i 2014.",
        [
            "Målet", "til", "direktoratet", "er", "at", "alle", "skal", "bli", "tilbydd", "jobb", "i", "politiet", "så", "raskt", "som", "mogleg", "i", "2014", ".",
        ],
    ),
    (
        "Han ønskjer ikkje at staten skal vere med på å finansiere slik undervisning, men dette er rektor på skulen ueinig i.",
        [
            "Han", "ønskjer", "ikkje", "at", "staten", "skal", "vere", "med", "på", "å", "finansiere", "slik", "undervisning", ",", "men", "dette", "er", "rektor", "på", "skulen", "ueinig", "i", ".",
        ],
    ),
    (
        "Ifølgje China Daily vart det 8.848 meter høge fjellet flytta 3 centimeter sørvestover under jordskjelvet, som vart målt til 7,8.",
        [
            "Ifølgje", "China", "Daily", "vart", "det", "8.848", "meter", "høge", "fjellet", "flytta", "3", "centimeter", "sørvestover", "under", "jordskjelvet", ",", "som", "vart", "målt", "til", "7,8", ".",
        ],
    ),
    (
        "Brukssesongen er frå nov. til mai, med ein topp i mars.",
        [
            "Brukssesongen", "er", "frå", "nov.", "til", "mai", ",", "med", "ein", "topp", "i", "mars", ".",
        ],
    ),
]
# fmt: on


@pytest.mark.parametrize("text,expected_tokens", NN_TOKEN_EXCEPTION_TESTS)
def test_nn_tokenizer_handles_exception_cases(nn_tokenizer, text, expected_tokens):
    tokens = nn_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
