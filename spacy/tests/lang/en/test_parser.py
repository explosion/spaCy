from spacy.tokens import Doc


def test_en_parser_noun_chunks_standard(en_vocab):
    words = ["A", "base", "phrase", "should", "be", "recognized", "."]
    heads = [2, 2, 5, 5, 5, 5, 5]
    pos = ["DET", "ADJ", "NOUN", "AUX", "VERB", "VERB", "PUNCT"]
    deps = ["det", "amod", "nsubjpass", "aux", "auxpass", "ROOT", "punct"]
    doc = Doc(en_vocab, words=words, pos=pos, deps=deps, heads=heads)
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "A base phrase "


def test_en_parser_noun_chunks_coordinated(en_vocab):
    # fmt: off
    words = ["A", "base", "phrase", "and", "a", "good", "phrase", "are", "often", "the", "same", "."]
    heads = [2, 2, 7, 2, 6, 6, 2, 7, 7, 10, 7, 7]
    pos = ["DET", "NOUN", "NOUN", "CCONJ", "DET", "ADJ", "NOUN", "VERB", "ADV", "DET", "ADJ", "PUNCT"]
    deps = ["det", "compound", "nsubj", "cc", "det", "amod", "conj", "ROOT", "advmod", "det", "attr", "punct"]
    # fmt: on
    doc = Doc(en_vocab, words=words, pos=pos, deps=deps, heads=heads)
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 2
    assert chunks[0].text_with_ws == "A base phrase "
    assert chunks[1].text_with_ws == "a good phrase "


def test_en_parser_noun_chunks_pp_chunks(en_vocab):
    words = ["A", "phrase", "with", "another", "phrase", "occurs", "."]
    heads = [1, 5, 1, 4, 2, 5, 5]
    pos = ["DET", "NOUN", "ADP", "DET", "NOUN", "VERB", "PUNCT"]
    deps = ["det", "nsubj", "prep", "det", "pobj", "ROOT", "punct"]
    doc = Doc(en_vocab, words=words, pos=pos, deps=deps, heads=heads)
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 2
    assert chunks[0].text_with_ws == "A phrase "
    assert chunks[1].text_with_ws == "another phrase "


def test_en_parser_noun_chunks_appositional_modifiers(en_vocab):
    # fmt: off
    words = ["Sam", ",", "my", "brother", ",", "arrived", "to", "the", "house", "."]
    heads = [5, 0, 3, 0, 0, 5, 5, 8, 6, 5]
    pos = ["PROPN", "PUNCT", "DET", "NOUN", "PUNCT", "VERB", "ADP", "DET", "NOUN", "PUNCT"]
    deps = ["nsubj", "punct", "poss", "appos", "punct", "ROOT", "prep", "det", "pobj", "punct"]
    # fmt: on
    doc = Doc(en_vocab, words=words, pos=pos, deps=deps, heads=heads)
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 3
    assert chunks[0].text_with_ws == "Sam "
    assert chunks[1].text_with_ws == "my brother "
    assert chunks[2].text_with_ws == "the house "


def test_en_parser_noun_chunks_dative(en_vocab):
    words = ["She", "gave", "Bob", "a", "raise", "."]
    heads = [1, 1, 1, 4, 1, 1]
    pos = ["PRON", "VERB", "PROPN", "DET", "NOUN", "PUNCT"]
    deps = ["nsubj", "ROOT", "dative", "det", "dobj", "punct"]
    doc = Doc(en_vocab, words=words, pos=pos, deps=deps, heads=heads)
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 3
    assert chunks[0].text_with_ws == "She "
    assert chunks[1].text_with_ws == "Bob "
    assert chunks[2].text_with_ws == "a raise "
