import pytest
from spacy.language import Language, BaseDefaults
from spacy.lang.punctuation import TOKENIZER_INFIXES
from spacy.lang.char_classes import ALPHA


@pytest.mark.issue(768)
@pytest.mark.parametrize(
    "text,expected_tokens", [("l'avion", ["l'", "avion"]), ("j'ai", ["j'", "ai"])]
)
def test_issue768(text, expected_tokens):
    """Allow zero-width 'infix' token during the tokenization process."""
    SPLIT_INFIX = r"(?<=[{a}]\')(?=[{a}])".format(a=ALPHA)

    class FrenchTest(Language):
        class Defaults(BaseDefaults):
            infixes = TOKENIZER_INFIXES + [SPLIT_INFIX]

    fr_tokenizer_w_infix = FrenchTest().tokenizer
    tokens = fr_tokenizer_w_infix(text)
    assert len(tokens) == 2
    assert [t.text for t in tokens] == expected_tokens
