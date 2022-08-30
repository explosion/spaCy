import pytest
from spacy.tokens import Doc
from spacy.util import filter_spans


@pytest.fixture
def nl_sample(nl_vocab):
    # TEXT :
    # Haar vriend lacht luid. We kregen alweer ruzie toen we de supermarkt ingingen.
    # Aan het begin van de supermarkt is al het fruit en de groentes. Uiteindelijk hebben we dan ook
    # geen avondeten gekocht.
    words = [
        "Haar",
        "vriend",
        "lacht",
        "luid",
        ".",
        "We",
        "kregen",
        "alweer",
        "ruzie",
        "toen",
        "we",
        "de",
        "supermarkt",
        "ingingen",
        ".",
        "Aan",
        "het",
        "begin",
        "van",
        "de",
        "supermarkt",
        "is",
        "al",
        "het",
        "fruit",
        "en",
        "de",
        "groentes",
        ".",
        "Uiteindelijk",
        "hebben",
        "we",
        "dan",
        "ook",
        "geen",
        "avondeten",
        "gekocht",
        ".",
    ]
    heads = [
        1,
        2,
        2,
        2,
        2,
        6,
        6,
        6,
        6,
        13,
        13,
        12,
        13,
        6,
        6,
        17,
        17,
        24,
        20,
        20,
        17,
        24,
        24,
        24,
        24,
        27,
        27,
        24,
        24,
        36,
        36,
        36,
        36,
        36,
        35,
        36,
        36,
        36,
    ]
    deps = [
        "nmod:poss",
        "nsubj",
        "ROOT",
        "advmod",
        "punct",
        "nsubj",
        "ROOT",
        "advmod",
        "obj",
        "mark",
        "nsubj",
        "det",
        "obj",
        "advcl",
        "punct",
        "case",
        "det",
        "obl",
        "case",
        "det",
        "nmod",
        "cop",
        "advmod",
        "det",
        "ROOT",
        "cc",
        "det",
        "conj",
        "punct",
        "advmod",
        "aux",
        "nsubj",
        "advmod",
        "advmod",
        "det",
        "obj",
        "ROOT",
        "punct",
    ]
    pos = [
        "PRON",
        "NOUN",
        "VERB",
        "ADJ",
        "PUNCT",
        "PRON",
        "VERB",
        "ADV",
        "NOUN",
        "SCONJ",
        "PRON",
        "DET",
        "NOUN",
        "NOUN",
        "PUNCT",
        "ADP",
        "DET",
        "NOUN",
        "ADP",
        "DET",
        "NOUN",
        "AUX",
        "ADV",
        "DET",
        "NOUN",
        "CCONJ",
        "DET",
        "NOUN",
        "PUNCT",
        "ADJ",
        "AUX",
        "PRON",
        "ADV",
        "ADV",
        "DET",
        "NOUN",
        "VERB",
        "PUNCT",
    ]
    return Doc(nl_vocab, words=words, heads=heads, deps=deps, pos=pos)


@pytest.fixture
def nl_reference_chunking():
    # Using frog https://github.com/LanguageMachines/frog/ we obtain the following NOUN-PHRASES:
    return [
        "haar vriend",
        "we",
        "ruzie",
        "we",
        "de supermarkt",
        "het begin",
        "de supermarkt",
        "het fruit",
        "de groentes",
        "we",
        "geen avondeten",
    ]


def test_need_dep(nl_tokenizer):
    """
    Test that noun_chunks raises Value Error for 'nl' language if Doc is not parsed.
    """
    txt = "Haar vriend lacht luid."
    doc = nl_tokenizer(txt)

    with pytest.raises(ValueError):
        list(doc.noun_chunks)


def test_chunking(nl_sample, nl_reference_chunking):
    """
    Test the noun chunks of a sample text. Uses a sample.
    The sample text simulates a Doc object as would be produced by nl_core_news_md.
    """
    chunks = [s.text.lower() for s in nl_sample.noun_chunks]
    assert chunks == nl_reference_chunking


@pytest.mark.issue(10846)
def test_no_overlapping_chunks(nl_vocab):
    # fmt: off
    doc = Doc(
        nl_vocab,
        words=["Dit", "programma", "wordt", "beschouwd", "als", "'s", "werelds", "eerste", "computerprogramma"],
        deps=["det", "nsubj:pass", "aux:pass", "ROOT", "mark", "det", "fixed", "amod", "xcomp"],
        heads=[1, 3, 3, 3, 8, 8, 5, 8, 3],
        pos=["DET", "NOUN", "AUX", "VERB", "SCONJ", "DET", "NOUN", "ADJ", "NOUN"],
    )
    # fmt: on
    chunks = list(doc.noun_chunks)
    assert filter_spans(chunks) == chunks
