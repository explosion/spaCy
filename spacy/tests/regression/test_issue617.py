from ...vocab import Vocab


def test_load_vocab_with_string():
    vocab = Vocab.load('/tmp/vocab')
