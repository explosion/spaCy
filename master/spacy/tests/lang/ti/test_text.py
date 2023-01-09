import pytest


def test_ti_tokenizer_handles_long_text(ti_tokenizer):
    text = """ቻንስለር ጀርመን ኣንገላ መርከል ኣብታ ሃገር ቁጽሪ መትሓዝቲ ኮቪድ መዓልታዊ ክብረ መዝገብ ድሕሪ ምህራሙ- ጽኑዕ እገዳ ክግበር ጸዊዓ።

መርከል ሎሚ ንታሕታዋይ ባይቶ ሃገራ ክትገልጽ ከላ፡ ኣብ ወሳኒ ምዕራፍ ቃልሲ ኢና ዘለና-ዳሕራዋይ ማዕበል ካብቲ ቀዳማይ ክገድድ ይኽእል`ዩ ኢላ።

ትካል ምክልኻል ተላገብቲ ሕማማት ጀርመን፡ ኣብ ዝሓለፈ 24 ሰዓታት ኣብ ምልእቲ ጀርመር 590 ሰባት ብኮቪድ19 ምሟቶም ኣፍሊጡ`ሎ።

ቻንስለር ኣንጀላ መርከል ኣብ እዋን በዓላት ልደት ስድራቤታት ክተኣኻኸባ ዝፍቀደለን`ኳ እንተኾነ ድሕሪኡ ኣብ ዘሎ ግዜ ግን እቲ እገዳታት ክትግበር ትደሊ።"""
    tokens = ti_tokenizer(text)

    assert len(tokens) == 85


@pytest.mark.parametrize(
    "text,length",
    [
        ("ቻንስለር ጀርመን ኣንገላ መርከል፧", 5),
        ("“ስድራቤታት፧”", 4),
        ("""ኣብ እዋን በዓላት ልደት ስድራቤታት ክተኣኻኸባ ዝፍቀደለን`ኳ እንተኾነ።""", 9),
        ("ብግምት 10ኪ.ሜ. ጎይዩ።", 6),
        ("ኣብ ዝሓለፈ 24 ሰዓታት...", 5),
    ],
)
def test_ti_tokenizer_handles_cnts(ti_tokenizer, text, length):
    tokens = ti_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10.000", True),
        ("1000", True),
        ("999,0", True),
        ("ሓደ", True),
        ("ክልተ", True),
        ("ትሪልዮን", True),
        ("ከልቢ", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(ti_tokenizer, text, match):
    tokens = ti_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
