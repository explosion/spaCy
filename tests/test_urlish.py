from spacy.orth import is_urlish

def test_basic_url():
    assert is_urlish('www.google.com')
    assert is_urlish('google.com')
    assert is_urlish('sydney.com')
    assert is_urlish('Sydney.edu')
    assert is_urlish('2girls1cup.org')


def test_close_enough():
    assert is_urlish('http://stupid')
    assert is_urlish('www.hi')


def test_non_match():
    assert not is_urlish('dog')
    assert not is_urlish('1.2')
    assert not is_urlish('1.a')
    assert not is_urlish('hello.There')
