from spacy.munge.read_ner import _get_text, _get_tag


def test_get_text():
    assert _get_text('asbestos') == 'asbestos'
    assert _get_text('<ENAMEX TYPE="ORG">Lorillard</ENAMEX>') == 'Lorillard'
    assert _get_text('<ENAMEX TYPE="DATE">more') == 'more'
    assert _get_text('ago</ENAMEX>') == 'ago'


def test_get_tag():
    assert _get_tag('asbestos', None) == ('O', None)
    assert _get_tag('asbestos', 'PER') == ('I-PER', 'PER')
    assert _get_tag('<ENAMEX TYPE="ORG">Lorillard</ENAMEX>', None) == ('U-ORG', None)
    assert _get_tag('<ENAMEX TYPE="DATE">more', None) == ('B-DATE', 'DATE')
    assert _get_tag('ago</ENAMEX>', 'DATE') == ('L-DATE', None)
