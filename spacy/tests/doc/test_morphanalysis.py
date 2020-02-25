import pytest


@pytest.fixture
def i_has(en_tokenizer):
    doc = en_tokenizer("I has")
    doc[0].tag_ = "PRP"
    doc[1].tag_ = "VBZ"
    return doc


def test_token_morph_eq(i_has):
    assert i_has[0].morph is not i_has[0].morph
    assert i_has[0].morph == i_has[0].morph
    assert i_has[0].morph != i_has[1].morph


def test_token_morph_key(i_has):
    assert i_has[0].morph.key != 0
    assert i_has[1].morph.key != 0
    assert i_has[0].morph.key == i_has[0].morph.key
    assert i_has[0].morph.key != i_has[1].morph.key


def test_morph_props(i_has):
    assert i_has[0].morph.get("PronType") == ["PronType=prs"]
    assert i_has[1].morph.get("PronType") == []


def test_morph_iter(i_has):
    assert set(i_has[0].morph) == set(["PronType=prs"])
    assert set(i_has[1].morph) == set(
        ["Number=sing", "Person=three", "Tense=pres", "VerbForm=fin"]
    )


def test_morph_get(i_has):
    assert i_has[0].morph.get("PronType") == ["PronType=prs"]


def test_morph_set(i_has):
    assert i_has[0].morph.get("PronType") == ["PronType=prs"]
    # set by string
    i_has[0].morph_ = "PronType=unk"
    assert i_has[0].morph.get("PronType") == ["PronType=unk"]
    # set by string, fields are alphabetized
    i_has[0].morph_ = "PronType=123|NounType=unk"
    assert i_has[0].morph_ == "NounType=unk|PronType=123"
    # set by dict
    i_has[0].morph_ = {"AType": "123", "BType": "unk", "POS": "ADJ"}
    assert i_has[0].morph_ == "AType=123|BType=unk|POS=ADJ"
    # set by string with multiple values, fields and values are alphabetized
    i_has[0].morph_ = "BType=c|AType=b,a"
    assert i_has[0].morph_ == "AType=a,b|BType=c"
    # set by dict with multiple values, fields and values are alphabetized
    i_has[0].morph_ = {"AType": "b,a", "BType": "c"}
    assert i_has[0].morph_ == "AType=a,b|BType=c"


def test_morph_str(i_has):
    assert str(i_has[0].morph) == "PronType=prs"
    assert str(i_has[1].morph) == "Number=sing|Person=three|Tense=pres|VerbForm=fin"
