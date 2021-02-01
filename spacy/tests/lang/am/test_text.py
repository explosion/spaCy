import pytest


def test_am_tokenizer_handles_long_text(am_tokenizer):
    text = """ሆሴ ሙጂካ በበጋ ወቅት በኦክስፎርድ ንግግር አንድያቀርቡ ሲጋበዙ ጭንቅላታቸው "ፈነዳ"።

“እጅግ ጥንታዊ” የእንግሊዝኛ ተናጋሪ ዩኒቨርስቲ፣ በአስር ሺዎች የሚቆጠሩ ዩሮዎችን ለተማሪዎች በማስተማር የሚያስከፍለው

እና ከማርጋሬት ታቸር እስከ ስቲቨን ሆኪንግ በአዳራሾቻቸው ውስጥ ንግግር ያደረጉበት የትምህርት ማዕከል፣ በሞንቴቪዴኦ

በሚገኘው የመንግስት ትምህርት ቤት የሰለጠኑትን የ81 ዓመቱ አዛውንት አገልግሎት ጠየቁ።"""
    tokens = am_tokenizer(text)

    assert len(tokens) == 56


@pytest.mark.parametrize(
    "text,length",
    [
        ("ሆሴ ሙጂካ ለምን ተመረጠ?", 5),
        ("“በፍፁም?”", 4),
        ("""አዎ! ሆዜ አርካዲዮ ቡንዲያ “እንሂድ” ሲል መለሰ።""", 11),
        ("እነሱ በግምት 10ኪ.ሜ. ሮጡ።", 7),
        ("እና ከዚያ ለምን...", 4),
    ],
)
def test_am_tokenizer_handles_cnts(am_tokenizer, text, length):
    tokens = am_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10.000", True),
        ("1000", True),
        ("999,0", True),
        ("አንድ", True),
        ("ሁለት", True),
        ("ትሪሊዮን", True),
        ("ውሻ", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(am_tokenizer, text, match):
    tokens = am_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
