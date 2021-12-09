import pytest


@pytest.mark.issue(2822)
def test_issue2822(it_tokenizer):
    """Test that the abbreviation of poco is kept as one word."""
    doc = it_tokenizer("Vuoi un po' di zucchero?")
    assert len(doc) == 6
    assert doc[0].text == "Vuoi"
    assert doc[1].text == "un"
    assert doc[2].text == "po'"
    assert doc[3].text == "di"
    assert doc[4].text == "zucchero"
    assert doc[5].text == "?"
