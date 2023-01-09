import pytest


# fmt: off
GRC_TOKEN_EXCEPTION_TESTS = [
    ("τὸ 〈τῆς〉 φιλοσοφίας ἔργον ἔνιοί φασιν ἀπὸ ⟦βαρβάρων⟧ ἄρξαι.", ["τὸ", "〈", "τῆς", "〉", "φιλοσοφίας", "ἔργον", "ἔνιοί", "φασιν", "ἀπὸ", "⟦", "βαρβάρων", "⟧", "ἄρξαι", "."]),
    ("τὴν δὲ τῶν Αἰγυπτίων φιλοσοφίαν εἶναι τοιαύτην περί τε †θεῶν† καὶ ὑπὲρ δικαιοσύνης.", ["τὴν", "δὲ", "τῶν", "Αἰγυπτίων", "φιλοσοφίαν", "εἶναι", "τοιαύτην", "περί", "τε", "†", "θεῶν", "†", "καὶ", "ὑπὲρ", "δικαιοσύνης", "."]),
    ("⸏πόσις δ' Ἐρεχθεύς ἐστί μοι σεσωσμένος⸏", ["⸏", "πόσις", "δ'", "Ἐρεχθεύς", "ἐστί", "μοι", "σεσωσμένος", "⸏"]),
    ("⸏ὔπνον ἴδωμεν⸎", ["⸏", "ὔπνον", "ἴδωμεν", "⸎"]),
]
# fmt: on


@pytest.mark.parametrize("text,expected_tokens", GRC_TOKEN_EXCEPTION_TESTS)
def test_grc_tokenizer(grc_tokenizer, text, expected_tokens):
    tokens = grc_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
