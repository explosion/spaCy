import pytest

from spacy.lang.ht.lex_attrs import like_num, norm_custom


def test_ht_tokenizer_handles_long_text(ht_tokenizer):
    text = """Onè ap fèt pou ansyen lidè Pati Travayè Britanik

Moun atravè lemond ap voye onè pou ansyen lidè
Pati Travayè a, John Smith, ki mouri pi bonè jodi a apre li te fè yon gwo kriz kadyak a laj 55 an.

Nan Washington, Depatman Deta Etazini pibliye yon deklarasyon ki eksprime "regre lanmò twò bonè" avoka ak palmantè eskoze a.

"Misye Smith, pandan tout karyè li ki te make ak distenksyon"""
    tokens = ht_tokenizer(text)
    assert len(tokens) == 84


@pytest.mark.parametrize(
    "text,length",
    [
        ("Map manje gato a pandan map gade televizyon lem lakay mwen.", 15),
        ("M'ap vini, eske wap la avek lajan'm? Si oui, di'l non pou fre'w.", 22),
        ("M ap teste sa (pou kounye a).", 10),
    ],
)
def test_ht_tokenizer_handles_cnts(ht_tokenizer, text, length):
    tokens = ht_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10,000", True),
        ("10,00", True),
        ("999.0", True),
        ("en", True),
        ("de", True),
        ("milya", True),
        ("dog", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(ht_tokenizer, text, match):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match


@pytest.mark.parametrize(
    "word", ["ventyèm", "Milyonnyèm", "3yèm", "Santyèm", "25yèm", "52yèm"]
)
def test_ht_lex_attrs_like_number_for_ordinal(word):
    assert like_num(word)


@pytest.mark.parametrize("word", ["onz"])
def test_ht_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())


@pytest.mark.parametrize(
    "word, expected",
    [
        ("'m", "mwen"),
        ("'n", "nou"),
        ("'l", "li"),
        ("'y", "yo"),
        ("'w", "ou"),
    ],
)
def test_ht_lex_attrs_norm_custom(word, expected):
    assert norm_custom(word) == expected
