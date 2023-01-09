import pytest


def test_ml_tokenizer_handles_long_text(ml_tokenizer):
    text = """അനാവശ്യമായി കണ്ണിലും മൂക്കിലും വായിലും സ്പർശിക്കാതിരിക്കുക"""
    tokens = ml_tokenizer(text)
    assert len(tokens) == 5


@pytest.mark.parametrize(
    "text,length",
    [
        (
            "എന്നാൽ അച്ചടിയുടെ ആവിർഭാവം ലിപിയിൽ കാര്യമായ മാറ്റങ്ങൾ വരുത്തിയത് കൂട്ടക്ഷരങ്ങളെ അണുഅക്ഷരങ്ങളായി പിരിച്ചുകൊണ്ടായിരുന്നു",
            10,
        ),
        ("പരമ്പരാഗതമായി മലയാളം ഇടത്തുനിന്ന് വലത്തോട്ടാണ് എഴുതുന്നത്", 5),
    ],
)
def test_ml_tokenizer_handles_cnts(ml_tokenizer, text, length):
    tokens = ml_tokenizer(text)
    assert len(tokens) == length
