import py.test
from spacy.pos_util import realign_tagged
from spacy.pos_util import _parse_line

def test_realign():
    rules = ["<SEP>,", "ca<SEP>n't", "``<SEP>"]
    tagged = "``/`` I/PRP ca/MD n't/RB"
    assert realign_tagged(rules, tagged) == "``<SEP>I/``_PRP ca<SEP>n't/MD_RB"


def test_parse_line():
    line = "Pierre/NNP Vinken,/NNP_, isn't/VBZ_RB 61/CD years/NNS old./RB_.\n"
    tokens, tags = _parse_line(line, '/')
    assert len(tokens) == len(tags)
    assert len(tokens) == 9
