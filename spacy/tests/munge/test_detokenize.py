from spacy.deprecated import detokenize

def test_punct():
    tokens = 'Pierre Vinken , 61 years old .'.split()
    detoks = [(0,), (1, 2), (3,), (4,), (5, 6)]
    token_rules = ('<SEP>,', '<SEP>.')
    assert detokenize(token_rules, tokens) == detoks


def test_contractions():
    tokens = "I ca n't even".split()
    detoks = [(0,), (1, 2), (3,)]
    token_rules = ("ca<SEP>n't",)
    assert detokenize(token_rules, tokens) == detoks


def test_contractions_punct():
    tokens = "I ca n't !".split()
    detoks = [(0,), (1, 2, 3)]
    token_rules = ("ca<SEP>n't", '<SEP>!')
    assert detokenize(token_rules, tokens) == detoks
