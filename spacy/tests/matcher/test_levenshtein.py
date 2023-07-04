import pytest

from spacy.matcher import levenshtein
from spacy.matcher.levenshtein import levenshtein_compare


# empty string plus 10 random ASCII, 10 random unicode, and 2 random long tests
# from polyleven
@pytest.mark.parametrize(
    "dist,a,b",
    [
        (0, "", ""),
        (4, "bbcb", "caba"),
        (3, "abcb", "cacc"),
        (3, "aa", "ccc"),
        (1, "cca", "ccac"),
        (1, "aba", "aa"),
        (4, "bcbb", "abac"),
        (3, "acbc", "bba"),
        (3, "cbba", "a"),
        (2, "bcc", "ba"),
        (4, "aaa", "ccbb"),
        (3, "うあい", "いいうい"),
        (2, "あううい", "うあい"),
        (3, "いういい", "うううあ"),
        (2, "うい", "あいあ"),
        (2, "いあい", "いう"),
        (1, "いい", "あいい"),
        (3, "あうあ", "いいああ"),
        (4, "いあうう", "ううああ"),
        (3, "いあいい", "ういああ"),
        (3, "いいああ", "ううあう"),
        (
            166,
            "TCTGGGCACGGATTCGTCAGATTCCATGTCCATATTTGAGGCTCTTGCAGGCAAAATTTGGGCATGTGAACTCCTTATAGTCCCCGTGC",
            "ATATGGATTGGGGGCATTCAAAGATACGGTTTCCCTTTCTTCAGTTTCGCGCGGCGCACGTCCGGGTGCGAGCCAGTTCGTCTTACTCACATTGTCGACTTCACGAATCGCGCATGATGTGCTTAGCCTGTACTTACGAACGAACTTTCGGTCCAAATACATTCTATCAACACCGAGGTATCCGTGCCACACGCCGAAGCTCGACCGTGTTCGTTGAGAGGTGGAAATGGTAAAAGATGAACATAGTC",
        ),
        (
            111,
            "GGTTCGGCCGAATTCATAGAGCGTGGTAGTCGACGGTATCCCGCCTGGTAGGGGCCCCTTCTACCTAGCGGAAGTTTGTCAGTACTCTATAACACGAGGGCCTCTCACACCCTAGATCGTCCAGCCACTCGAAGATCGCAGCACCCTTACAGAAAGGCATTAATGTTTCTCCTAGCACTTGTGCAATGGTGAAGGAGTGATG",
            "CGTAACACTTCGCGCTACTGGGCTGCAACGTCTTGGGCATACATGCAAGATTATCTAATGCAAGCTTGAGCCCCGCTTGCGGAATTTCCCTAATCGGGGTCCCTTCCTGTTACGATAAGGACGCGTGCACT",
        ),
    ],
)
def test_levenshtein(dist, a, b):
    assert levenshtein(a, b) == dist


@pytest.mark.parametrize(
    "a,b,fuzzy,expected",
    [
        ("a", "a", 1, True),
        ("a", "a", 0, True),
        ("a", "a", -1, True),
        ("a", "ab", 1, True),
        ("a", "ab", 0, False),
        ("a", "ab", -1, True),
        ("ab", "ac", 1, True),
        ("ab", "ac", -1, True),
        ("abc", "cde", 4, True),
        ("abc", "cde", -1, False),
        ("abcdef", "cdefgh", 4, True),
        ("abcdef", "cdefgh", 3, False),
        ("abcdef", "cdefgh", -1, False),  # default (2 for length 6)
        ("abcdefgh", "cdefghijk", 5, True),
        ("abcdefgh", "cdefghijk", 4, False),
        ("abcdefgh", "cdefghijk", -1, False),  # default (2)
        ("abcdefgh", "cdefghijkl", 6, True),
        ("abcdefgh", "cdefghijkl", 5, False),
        ("abcdefgh", "cdefghijkl", -1, False),  # default (2)
    ],
)
def test_levenshtein_compare(a, b, fuzzy, expected):
    assert levenshtein_compare(a, b, fuzzy) == expected
