from spacy.tokens import Doc
from spacy.matcher import PhraseMatcher


def test_span_in_phrasematcher(en_vocab):
    """Ensure that PhraseMatcher accepts Span as input"""
    doc = Doc(en_vocab,
              words=["I", "like", "Spans", "and", "Docs", "in", "my", "input", ",", "and", "nothing", "else", "."])
    span = doc[:8]
    pattern = Doc(en_vocab, words=["Spans", "and", "Docs"])
    matcher = PhraseMatcher(en_vocab)
    matcher.add("SPACY", [pattern])
    matches = matcher(span)
    assert matches

