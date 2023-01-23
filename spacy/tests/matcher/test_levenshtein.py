import pytest
from spacy.matcher import levenshtein


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
