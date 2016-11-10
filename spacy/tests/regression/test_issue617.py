from ...vocab import Vocab


def test_load_vocab_with_string():
    try:
        vocab = Vocab.load('/tmp/vocab')
    except IOError:
        pass
