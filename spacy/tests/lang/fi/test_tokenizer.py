import pytest

ABBREVIATION_TESTS = [
    (
        "Hyvää uutta vuotta t. siht. Niemelä!",
        ["Hyvää", "uutta", "vuotta", "t.", "siht.", "Niemelä", "!"],
    ),
    ("Paino on n. 2.2 kg", ["Paino", "on", "n.", "2.2", "kg"]),
    (
        "Vuonna 1 eaa. tapahtui kauheita.",
        ["Vuonna", "1", "eaa.", "tapahtui", "kauheita", "."],
    ),
]

HYPHENATED_TESTS = [
    (
        "1700-luvulle sijoittuva taide-elokuva Wikimedia-säätiön Varsinais-Suomen",
        [
            "1700-luvulle",
            "sijoittuva",
            "taide-elokuva",
            "Wikimedia-säätiön",
            "Varsinais-Suomen",
        ],
    )
]

ABBREVIATION_INFLECTION_TESTS = [
    (
        "VTT:ssa ennen v:ta 2010 suoritetut mittaukset",
        ["VTT:ssa", "ennen", "v:ta", "2010", "suoritetut", "mittaukset"],
    ),
    ("ALV:n osuus on 24 %.", ["ALV:n", "osuus", "on", "24", "%", "."]),
    ("Hiihtäjä oli kilpailun 14:s.", ["Hiihtäjä", "oli", "kilpailun", "14:s", "."]),
    ("EU:n toimesta tehtiin jotain.", ["EU:n", "toimesta", "tehtiin", "jotain", "."]),
]

CONTRACTION_TESTS = [
    (
        "Päätimme ettemme tule.",
        ["Päätimme", "ett", "emme", "tule", "."],
        ["päätimme", "että", "emme", "tule", "."],
    ),
    (
        "Miksei puhuttaisi?",
        ["Miks", "ei", "puhuttaisi", "?"],
        ["miksi", "ei", "puhuttaisi", "?"],
    ),
    (
        "He tottelivat vaikkeivat halunneet",
        ["He", "tottelivat", "vaikk", "eivat", "halunneet"],
        ["he", "tottelivat", "vaikka", "eivät", "halunneet"],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", ABBREVIATION_TESTS)
def test_fi_tokenizer_abbreviations(fi_tokenizer, text, expected_tokens):
    tokens = fi_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list


@pytest.mark.parametrize("text,expected_tokens", HYPHENATED_TESTS)
def test_fi_tokenizer_hyphenated_words(fi_tokenizer, text, expected_tokens):
    tokens = fi_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list


@pytest.mark.parametrize("text,expected_tokens", ABBREVIATION_INFLECTION_TESTS)
def test_fi_tokenizer_abbreviation_inflections(fi_tokenizer, text, expected_tokens):
    tokens = fi_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list


@pytest.mark.parametrize("text,expected_tokens,expected_norms", CONTRACTION_TESTS)
def test_fi_tokenizer_contractions(fi_tokenizer, text, expected_tokens, expected_norms):
    tokens = fi_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    norm_list = [token.norm_ for token in tokens if not token.is_space]
    assert expected_tokens == token_list
    assert expected_norms == norm_list
