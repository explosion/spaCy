import pytest


@pytest.mark.parametrize("text", ["(under)"])
def test_da_tokenizer_splits_no_special(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["ta'r", "Søren's", "Lars'"])
def test_da_tokenizer_handles_no_punct(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["(ta'r"])
def test_da_tokenizer_splits_prefix_punct(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 2
    assert tokens[0].text == "("
    assert tokens[1].text == "ta'r"


@pytest.mark.parametrize("text", ["ta'r)"])
def test_da_tokenizer_splits_suffix_punct(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 2
    assert tokens[0].text == "ta'r"
    assert tokens[1].text == ")"


@pytest.mark.parametrize(
    "text,expected", [("(ta'r)", ["(", "ta'r", ")"]), ("'ta'r'", ["'", "ta'r", "'"])]
)
def test_da_tokenizer_splits_even_wrap(da_tokenizer, text, expected):
    tokens = da_tokenizer(text)
    assert len(tokens) == len(expected)
    assert [t.text for t in tokens] == expected


@pytest.mark.parametrize("text", ["(ta'r?)"])
def test_da_tokenizer_splits_uneven_wrap(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 4
    assert tokens[0].text == "("
    assert tokens[1].text == "ta'r"
    assert tokens[2].text == "?"
    assert tokens[3].text == ")"


@pytest.mark.parametrize(
    "text,expected",
    [("f.eks.", ["f.eks."]), ("fe.", ["fe", "."]), ("(f.eks.", ["(", "f.eks."])],
)
def test_da_tokenizer_splits_prefix_interact(da_tokenizer, text, expected):
    tokens = da_tokenizer(text)
    assert len(tokens) == len(expected)
    assert [t.text for t in tokens] == expected


@pytest.mark.parametrize("text", ["f.eks.)"])
def test_da_tokenizer_splits_suffix_interact(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 2
    assert tokens[0].text == "f.eks."
    assert tokens[1].text == ")"


@pytest.mark.parametrize("text", ["(f.eks.)"])
def test_da_tokenizer_splits_even_wrap_interact(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[0].text == "("
    assert tokens[1].text == "f.eks."
    assert tokens[2].text == ")"


@pytest.mark.parametrize("text", ["(f.eks.?)"])
def test_da_tokenizer_splits_uneven_wrap_interact(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 4
    assert tokens[0].text == "("
    assert tokens[1].text == "f.eks."
    assert tokens[2].text == "?"
    assert tokens[3].text == ")"


@pytest.mark.parametrize("text", ["0,1-13,5", "0,0-0,1", "103,27-300", "1/2-3/4"])
def test_da_tokenizer_handles_numeric_range(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["sort.Gul", "Hej.Verden"])
def test_da_tokenizer_splits_period_infix(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["Hej,Verden", "en,to"])
def test_da_tokenizer_splits_comma_infix(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[0].text == text.split(",")[0]
    assert tokens[1].text == ","
    assert tokens[2].text == text.split(",")[1]


@pytest.mark.parametrize("text", ["sort...Gul", "sort...gul"])
def test_da_tokenizer_splits_ellipsis_infix(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize(
    "text",
    ["gå-på-mod", "4-hjulstræk", "100-Pfennig-frimærke", "TV-2-spots", "trofæ-vaeggen"],
)
def test_da_tokenizer_keeps_hyphens(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 1


def test_da_tokenizer_splits_double_hyphen_infix(da_tokenizer):
    tokens = da_tokenizer(
        "Mange regler--eksempelvis bindestregs-reglerne--er komplicerede."
    )
    assert len(tokens) == 9
    assert tokens[0].text == "Mange"
    assert tokens[1].text == "regler"
    assert tokens[2].text == "--"
    assert tokens[3].text == "eksempelvis"
    assert tokens[4].text == "bindestregs-reglerne"
    assert tokens[5].text == "--"
    assert tokens[6].text == "er"
    assert tokens[7].text == "komplicerede"


def test_da_tokenizer_handles_posessives_and_contractions(da_tokenizer):
    tokens = da_tokenizer(
        "'DBA's, Lars' og Liz' bil sku' sgu' ik' ha' en bule, det ka' han ik' li' mere', sagde hun."
    )
    assert len(tokens) == 25
    assert tokens[0].text == "'"
    assert tokens[1].text == "DBA's"
    assert tokens[2].text == ","
    assert tokens[3].text == "Lars'"
    assert tokens[4].text == "og"
    assert tokens[5].text == "Liz'"
    assert tokens[6].text == "bil"
    assert tokens[7].text == "sku'"
    assert tokens[8].text == "sgu'"
    assert tokens[9].text == "ik'"
    assert tokens[10].text == "ha'"
    assert tokens[11].text == "en"
    assert tokens[12].text == "bule"
    assert tokens[13].text == ","
    assert tokens[14].text == "det"
    assert tokens[15].text == "ka'"
    assert tokens[16].text == "han"
    assert tokens[17].text == "ik'"
    assert tokens[18].text == "li'"
    assert tokens[19].text == "mere"
    assert tokens[20].text == "'"
    assert tokens[21].text == ","
    assert tokens[22].text == "sagde"
    assert tokens[23].text == "hun"
    assert tokens[24].text == "."
