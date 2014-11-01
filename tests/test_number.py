from spacy.orth import is_number


def test_digits():
    assert is_number('10')
    assert is_number('1')


def test_comma():
    assert is_number('10,000')
    assert is_number('10,00')
    assert is_number(',10')


def test_period():
    assert is_number('999.0')
    assert is_number('.99')


def test_fraction():
    assert is_number('1/2')
    assert not is_number('1/2/3')


def test_word():
    assert is_number('one')
    assert is_number('two')
    assert is_number('billion')


def test_not_number():
    assert not is_number('dog')
    assert not is_number(',')

