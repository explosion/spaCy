import pytest
from spacy.tokens import Doc


@pytest.fixture
def words():
    # fmt: off
    return [
        "\n", "It", "was", "a", "bright", "cold", "day", "in", "April", ",",
        "and", "the", "clocks", "were", "striking", "thirteen", ".", "\n",
        "Winston", "Smith", ",", "his", "chin", "nuzzled", "into", "his",
        "breast", "in", "an", "effort", "to", "escape", "the", "\n", "vile",
        "wind", ",", "slipped", "quickly", "through", "the", "glass", "doors",
        "of", "Victory", "Mansions", ",", "\n", "though", "not", "quickly",
        "enough", "to", "prevent", "a", "swirl", "of", "gritty", "dust",
        "from", "entering", "\n", "along", "with", "him", ".", "\n\n", "The",
        "hallway", "smelt", "of", "boiled", "cabbage", "and", "old", "rag",
        "mats", ".", "At", "one", "end", "of", "it", "a", "\n", "coloured",
        "poster", ",", "too", "large", "for", "indoor", "display", ",", "had",
        "been", "tacked", "to", "the", "wall", ".", "\n", "It", "depicted",
        "simply", "an", "enormous", "face", ",", "more", "than", "a", "metre",
        "wide", ":", "the", "face", "of", "a", "\n", "man", "of", "about",
        "forty", "-", "five", ",", "with", "a", "heavy", "black", "moustache",
        "and", "ruggedly", "handsome", "\n", "features", ".", "Winston", "made",
        "for", "the", "stairs", ".", "It", "was", "no", "use", "trying", "the",
        "lift", ".", "Even", "at", "\n", "the", "best", "of", "times", "it",
        "was", "seldom", "working", ",", "and", "at", "present", "the",
        "electric", "current", "\n", "was", "cut", "off", "during", "daylight",
        "hours", ".", "It", "was", "part", "of", "the", "economy", "drive",
        "in", "\n", "preparation", "for", "Hate", "Week", ".", "The", "flat",
        "was", "seven", "flights", "up", ",", "and", "Winston", ",", "who",
        "\n", "was", "thirty", "-", "nine", "and", "had", "a", "varicose",
        "ulcer", "above", "his", "right", "ankle", ",", "went", "slowly", ",",
        "\n", "resting", "several", "times", "on", "the", "way", ".", "On",
        "each", "landing", ",", "opposite", "the", "lift", "-", "shaft", ",",
        "\n", "the", "poster", "with", "the", "enormous", "face", "gazed",
        "from", "the", "wall", ".", "It", "was", "one", "of", "those", "\n",
        "pictures", "which", "are", "so", "contrived", "that", "the", "eyes",
        "follow", "you", "about", "when", "you", "move", ".", "\n", "BIG",
        "BROTHER", "IS", "WATCHING", "YOU", ",", "the", "caption", "beneath",
        "it", "ran", ".", "\n", ]
    # fmt: on


@pytest.fixture
def heads():
    # fmt: off
    return [
        1, 2, 2, 6, 6, 6, 2, 6, 7, 2, 2, 12, 14, 14, 2, 14, 14, 16, 19, 23, 23,
        22, 23, 23, 23, 26, 24, 23, 29, 27, 31, 29, 35, 32, 35, 31, 23, 23, 37,
        37, 42, 42, 39, 42, 45, 43, 37, 46, 37, 50, 51, 37, 53, 51, 55, 53, 55,
        58, 56, 53, 59, 60, 60, 62, 63, 23, 65, 68, 69, 69, 69, 72, 70, 72, 76,
        76, 72, 69, 96, 80, 78, 80, 81, 86, 83, 86, 96, 96, 89, 96, 89, 92, 90,
        96, 96, 96, 96, 96, 99, 97, 96, 100, 103, 103, 103, 107, 107, 103, 107,
        111, 111, 112, 113, 107, 103, 116, 136, 116, 120, 118, 117, 120, 125,
        125, 125, 121, 116, 116, 131, 131, 131, 127, 131, 134, 131, 134, 136,
        136, 139, 139, 139, 142, 140, 139, 145, 145, 147, 145, 147, 150, 148,
        145, 153, 162, 153, 156, 162, 156, 157, 162, 162, 162, 162, 162, 162,
        172, 165, 169, 169, 172, 169, 172, 162, 172, 172, 176, 174, 172, 179,
        179, 179, 180, 183, 181, 179, 184, 185, 185, 187, 190, 188, 179, 193,
        194, 194, 196, 194, 196, 194, 194, 218, 200, 204, 202, 200, 207, 207,
        204, 204, 204, 212, 212, 209, 212, 216, 216, 213, 200, 194, 218, 218,
        220, 218, 224, 222, 222, 227, 225, 218, 246, 231, 229, 246, 246, 237,
        237, 237, 233, 246, 238, 241, 246, 241, 245, 245, 242, 246, 246, 249,
        247, 246, 252, 252, 252, 253, 257, 255, 254, 259, 257, 261, 259, 265,
        264, 265, 261, 265, 265, 270, 270, 267, 252, 271, 274, 275, 275, 276,
        283, 283, 280, 283, 280, 281, 283, 283, 284]
    # fmt: on


def test_parser_parse_navigate_consistency(en_vocab, words, heads):
    doc = Doc(en_vocab, words=words, heads=heads)
    for head in doc:
        for child in head.lefts:
            assert child.head == head
        for child in head.rights:
            assert child.head == head


def test_parser_parse_navigate_child_consistency(en_vocab, words, heads):
    doc = Doc(en_vocab, words=words, heads=heads, deps=["dep"] * len(heads))
    lefts = {}
    rights = {}
    for head in doc:
        assert head.i not in lefts
        lefts[head.i] = set()
        for left in head.lefts:
            lefts[head.i].add(left.i)
        assert head.i not in rights
        rights[head.i] = set()
        for right in head.rights:
            rights[head.i].add(right.i)
    for head in doc:
        assert head.n_rights == len(rights[head.i])
        assert head.n_lefts == len(lefts[head.i])
    for child in doc:
        if child.i < child.head.i:
            assert child.i in lefts[child.head.i]
            assert child.i not in rights[child.head.i]
            lefts[child.head.i].remove(child.i)
        elif child.i > child.head.i:
            assert child.i in rights[child.head.i]
            assert child.i not in lefts[child.head.i]
            rights[child.head.i].remove(child.i)
    for head_index, children in lefts.items():
        assert not children
    for head_index, children in rights.items():
        assert not children


def test_parser_parse_navigate_edges(en_vocab, words, heads):
    doc = Doc(en_vocab, words=words, heads=heads)
    for token in doc:
        subtree = list(token.subtree)
        debug = "\t".join((token.text, token.left_edge.text, subtree[0].text))
        assert token.left_edge == subtree[0], debug
        debug = "\t".join(
            (
                token.text,
                token.right_edge.text,
                subtree[-1].text,
                token.right_edge.head.text,
            )
        )
        assert token.right_edge == subtree[-1], debug
