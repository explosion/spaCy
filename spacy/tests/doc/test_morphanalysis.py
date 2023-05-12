import pytest


@pytest.fixture
def i_has(en_tokenizer):
    doc = en_tokenizer("I has")
    doc[0].set_morph({"PronType": "prs"})
    doc[1].set_morph(
        {
            "VerbForm": "fin",
            "Tense": "pres",
            "Number": "sing",
            "Person": "three",
        }
    )

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
    assert i_has[0].morph.get("PronType") == ["prs"]
    assert i_has[1].morph.get("PronType") == []
    assert i_has[1].morph.get("AsdfType", ["asdf"]) == ["asdf"]
    assert i_has[1].morph.get("AsdfType", default=["asdf", "qwer"]) == ["asdf", "qwer"]


def test_morph_iter(i_has):
    assert set(i_has[0].morph) == set(["PronType=prs"])
    assert set(i_has[1].morph) == set(
        ["Number=sing", "Person=three", "Tense=pres", "VerbForm=fin"]
    )


def test_morph_get(i_has):
    assert i_has[0].morph.get("PronType") == ["prs"]


def test_morph_set(i_has):
    assert i_has[0].morph.get("PronType") == ["prs"]
    # set by string
    i_has[0].set_morph("PronType=unk")
    assert i_has[0].morph.get("PronType") == ["unk"]
    # set by string, fields are alphabetized
    i_has[0].set_morph("PronType=123|NounType=unk")
    assert str(i_has[0].morph) == "NounType=unk|PronType=123"
    # set by dict
    i_has[0].set_morph({"AType": "123", "BType": "unk"})
    assert str(i_has[0].morph) == "AType=123|BType=unk"
    # set by string with multiple values, fields and values are alphabetized
    i_has[0].set_morph("BType=c|AType=b,a")
    assert str(i_has[0].morph) == "AType=a,b|BType=c"
    # set by dict with multiple values, fields and values are alphabetized
    i_has[0].set_morph({"AType": "b,a", "BType": "c"})
    assert str(i_has[0].morph) == "AType=a,b|BType=c"


def test_morph_str(i_has):
    assert str(i_has[0].morph) == "PronType=prs"
    assert str(i_has[1].morph) == "Number=sing|Person=three|Tense=pres|VerbForm=fin"


def test_morph_property(tokenizer):
    doc = tokenizer("a dog")

    # set through token.morph_
    doc[0].set_morph("PronType=prs")
    assert str(doc[0].morph) == "PronType=prs"
    assert doc.to_array(["MORPH"])[0] != 0

    # unset with token.morph
    doc[0].set_morph(None)
    assert doc.to_array(["MORPH"])[0] == 0

    # empty morph is equivalent to "_"
    doc[0].set_morph("")
    assert str(doc[0].morph) == ""
    assert doc.to_array(["MORPH"])[0] == tokenizer.vocab.strings["_"]

    # "_" morph is also equivalent to empty morph
    doc[0].set_morph("_")
    assert str(doc[0].morph) == ""
    assert doc.to_array(["MORPH"])[0] == tokenizer.vocab.strings["_"]

    # set through existing hash with token.morph
    tokenizer.vocab.strings.add("Feat=Val")
    doc[0].set_morph(tokenizer.vocab.strings.add("Feat=Val"))
    assert str(doc[0].morph) == "Feat=Val"
