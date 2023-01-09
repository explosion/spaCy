import pytest


def test_long_text(is_tokenizer):
    # Excerpt: European Convention on Human Rights
    text = """
hafa í huga, að yfirlýsing þessi hefur það markmið að tryggja
almenna og raunhæfa viðurkenningu og vernd þeirra réttinda,
sem þar er lýst;
hafa í huga, að markmið Evrópuráðs er að koma á nánari einingu
aðildarríkjanna og að ein af leiðunum að því marki er sú, að
mannréttindi og mannfrelsi séu í heiðri höfð og efld;
lýsa á ný eindreginni trú sinni á það mannfrelsi, sem er undirstaða
réttlætis og friðar í heiminum og best er tryggt, annars vegar með
virku, lýðræðislegu stjórnarfari og, hins vegar, almennum skilningi
og varðveislu þeirra mannréttinda, sem eru grundvöllur frelsisins;
"""
    tokens = is_tokenizer(text)
    assert len(tokens) == 120


@pytest.mark.xfail
def test_ordinal_number(is_tokenizer):
    text = "10. desember 1948"
    tokens = is_tokenizer(text)
    assert len(tokens) == 3
