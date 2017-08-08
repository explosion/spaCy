from ...vocab import Vocab

def test_lexeme_text():
    vocab = Vocab()
    lex = vocab[u'the']
    assert lex.text == u'the'


def test_lexeme_lex_id():
    vocab = Vocab()
    lex1 = vocab[u'the']
    lex2 = vocab[u'be']
    assert lex1.lex_id != lex2.lex_id
