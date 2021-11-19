import pytest

KN_BASIC_TOKENIZATION_TESTS = [
    (
        "ಕಾಲುದಾರಿ ವಿತರಣಾ ರೋಬೋಟ್‌ಗಳನ್ನು ನಿಷೇಧಿಸುವುದನ್ನು ಸ್ಯಾನ್ ಫ್ರಾನ್ಸಿಸ್ಕೊ ಪರಿಗಣಿಸುತ್ತದೆ.",
        ['ಕಾಲುದಾರಿ', 'ವಿತರಣಾ', 'ರೋಬೋಟ್‌ಗಳನ್ನು', 'ನಿಷೇಧಿಸುವುದನ್ನು', 'ಸ್ಯಾನ್', 'ಫ್ರಾನ್ಸಿಸ್ಕೊ',
            'ಪರಿಗಣಿಸುತ್ತದೆ', '.'],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", KN_BASIC_TOKENIZATION_TESTS)
def test_kn_tokenizer_basic(kn_tokenizer, text, expected_tokens):
    tokens = kn_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    print(token_list)
    assert expected_tokens == token_list

