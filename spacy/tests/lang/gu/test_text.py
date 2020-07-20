import pytest


def test_gu_tokenizer_handlers_long_text(gu_tokenizer):
    text = """પશ્ચિમ ભારતમાં આવેલું ગુજરાત રાજ્ય જે વ્યક્તિઓની માતૃભૂમિ છે"""
    tokens = gu_tokenizer(text)
    assert len(tokens) == 9


@pytest.mark.parametrize(
    "text,length",
    [("ગુજરાતીઓ ખાવાના શોખીન માનવામાં આવે છે", 6), ("ખેતરની ખેડ કરવામાં આવે છે.", 5)],
)
def test_gu_tokenizer_handles_cnts(gu_tokenizer, text, length):
    tokens = gu_tokenizer(text)
    assert len(tokens) == length
