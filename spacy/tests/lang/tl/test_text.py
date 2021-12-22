import pytest
from spacy.lang.tl.lex_attrs import like_num

# https://github.com/explosion/spaCy/blob/master/spacy/tests/lang/en/test_text.py


def test_tl_tokenizer_handles_long_text(tl_tokenizer):
    # Excerpt: "Sapagkat ang Pilosopiya ay Ginagawa" by Padre Roque Ferriols
    text = """
    Tingin tayo nang tingin. Kailangan lamang nating dumilat at
    marami tayong makikita. At ang pagtingin ay isang gawain na ako lamang ang
    makagagawa, kung ako nga ang makakita. Kahit na napanood na ng aking
    matalik na kaibigan ang isang sine, kailangan ko pa ring panoorin, kung
    ako nga ang may gustong makakita. Kahit na gaano kadikit ang aming
    pagkabuklod, hindi siya maaaring tumingin sa isang paraan na ako ang
    nakakakita. Kung ako ang makakita, ako lamang ang makatitingin.
    """
    tokens = tl_tokenizer(text)
    assert len(tokens) == 97


@pytest.mark.parametrize(
    "text,length",
    [
        ("Huwag mo nang itanong sa akin.", 7),
        ("Nasubukan mo na bang hulihin ang hangin?", 8),
        ("Hindi ba?", 3),
        ("Nagbukas ang DFA ng 1,000 appointment slots para sa pasaporte.", 11),
        ("'Wala raw pasok bukas kasi may bagyo!' sabi ni Micah.", 14),
        ("'Ingat,' aniya. 'Maingay sila pag malayo at tahimik kung malapit.'", 17),
    ],
)
def test_tl_tokenizer_handles_cnts(tl_tokenizer, text, length):
    tokens = tl_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("isa", True),
        ("dalawa", True),
        ("tatlumpu", True),
        pytest.param(
            "isang daan",
            True,
            marks=pytest.mark.xfail(reason="Not yet implemented (means 100)"),
        ),
        pytest.param(
            "kalahati",
            True,
            marks=pytest.mark.xfail(reason="Not yet implemented (means 1/2)"),
        ),
        pytest.param(
            "isa't kalahati",
            True,
            marks=pytest.mark.xfail(
                reason="Not yet implemented (means one-and-a-half)"
            ),
        ),
    ],
)
def test_lex_attrs_like_number(tl_tokenizer, text, match):
    tokens = tl_tokenizer(text)
    assert all([token.like_num for token in tokens]) == match


@pytest.mark.xfail(reason="Not yet implemented, fails when capitalized.")
@pytest.mark.parametrize("word", ["isa", "dalawa", "tatlo"])
def test_tl_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
