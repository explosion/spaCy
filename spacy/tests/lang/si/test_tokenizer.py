import pytest

SI_TOKEN_EXCEPTION_TESTS = [
    (
        "ශ්‍රී ලංකා හමුදාව නිර්භීතව ත්‍රස්තවාදීන් පරාජය කලහ.",
        ["ශ්‍රී", "ලංකා", "හමුදාව", "නිර්භීතව", "ත්‍රස්තවාදීන්", "පරාජය", "කලහ","."],
    ),
    (
        "සමන්, කරුණාකරලා 10වෙනි පිටුව පෙරලලා කියවන්න.",
        ["සමන්",",", "කරුණාකරලා", "10වෙනි", "පිටුව", "පෙරලලා", "කියවන්න", "."],
    ),
    (
        "දෙවන විමලධර්මසූරිය රජුගේ කාලයේ බුද්ධාගම ප්‍රචලිත කලේය.",
        ["දෙවන", "විමලධර්මසූරිය", "රජුගේ", "කාලයේ", "බුද්ධාගම", "ප්‍රචලිත", "කලේය","."],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", SI_TOKEN_EXCEPTION_TESTS)
def test_si_tokenizer_handles_exception_cases(si_tokenizer, text, expected_tokens):
    tokens = si_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert token_list == expected_tokens
