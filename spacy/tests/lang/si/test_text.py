import pytest

from spacy.lang.si.lex_attrs import like_num

# note: this text taken from https://www.bbc.com/sinhala/articles/cgmpy0kpljno
def test_si_tokenizer_handles_long_text(si_tokenizer):
    text = """දිනය 2025 නොවැම්බර් 27 වන දා යි.

එදින මහනුවර සිට නාවලපිටිය බලා ධාවනය වන මගී දුම්රිය පස්වරු 2.06ට පමණ මහනුවර දුම්රිය ස්ථානයෙන් තම දුම්රිය ගමන ආරම්භ කර තිබුණේ, 
දැඩි වර්ෂාව මධ්‍යයේ ය.මැදිරි හතරකින් සමන්විත මෙම දුම්රිය කෙටිදුර ධාවනයේ නිරත වන මන්දගාමී දුම්රියකි.
එදින මෙම දුම්රිය ගමනාන්තය කරා ගෙන යාමේ කාර්යය භාර වී තිබුණේ, විශේෂ පන්ති දුම්රිය රියැදුරෙකු වු ජයම්පති මඩිගසේකරට ය.

1982 වසරේ දුම්රිය සේවයට එක්වූ ජයම්පති මඩිගසේකර දැනට විශ්‍රාම ගොස් වසර 6කි."""
    tokens = si_tokenizer(text)
    assert len(tokens) == 83


@pytest.mark.parametrize(
    "text,length",
    [
        ("""හැන්දෑවේ 4 - 5ට විතර හොඳට ම වැස්සා මගේ ජීවිතේට ම දැකල නැති වැස්සක්.""", 15),
        ("ඩොලරයේ අගය ඉහළ ගියේ ඇයි ?", 6),
        ("මහනුවර සිට නාවලපිටිය", 3),
        ("ශ්‍රී ලාංකිකයන් බොහෝ දෙනෙකු සිංහල අලුත් අවුරුද්ද සැමරීමට සූදානම්.", 10),
        ("සිසුන් 110,000කට පමණ වෘත්තීය අධ්‍යාපනය ලබා දීම", 7),
        ("එහෙමද? මම එහෙම කීවේ නැ!", 7),
        ("එහි අරමුණු කිහිපයකි. ඒවා අතර;", 7),
    ],
)
def test_si_tokenizer_handles_cnts(si_tokenizer, text, length):
    tokens = si_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10,000", True),
        ("1,000", True),
        ("999.0", True),
        ("එක", True),
        ("දෙක", True),
        ("බිලියනය", True),
        ("බල්ලා", False),
        (",", False),
        ("1/2", True),
        ("අශේන්", False),
        ("වැලිගල්ල", False),
    ],
)
def test_lex_attrs_like_number(si_tokenizer, text, match):
    tokens = si_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match


@pytest.mark.parametrize(
    "word", ["තෙවන", "මිලියනවන", "100වන", "සියවන", "23වෙනි", "52වෙනි"]
)
def test_si_lex_attrs_like_number_for_ordinal(word):
    assert like_num(word)


@pytest.mark.parametrize("word", ["එකොළොස්වන"])
def test_si_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
