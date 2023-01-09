import pytest
import warnings
import srsly
from mock import Mock

from spacy.lang.en import English
from spacy.matcher import PhraseMatcher, Matcher
from spacy.tokens import Doc, Span
from spacy.vocab import Vocab


from ..util import make_tempdir


@pytest.mark.issue(3248)
def test_issue3248_1():
    """Test that the PhraseMatcher correctly reports its number of rules, not
    total number of patterns."""
    nlp = English()
    matcher = PhraseMatcher(nlp.vocab)
    matcher.add("TEST1", [nlp("a"), nlp("b"), nlp("c")])
    matcher.add("TEST2", [nlp("d")])
    assert len(matcher) == 2


@pytest.mark.issue(3331)
def test_issue3331(en_vocab):
    """Test that duplicate patterns for different rules result in multiple
    matches, one per rule.
    """
    matcher = PhraseMatcher(en_vocab)
    matcher.add("A", [Doc(en_vocab, words=["Barack", "Obama"])])
    matcher.add("B", [Doc(en_vocab, words=["Barack", "Obama"])])
    doc = Doc(en_vocab, words=["Barack", "Obama", "lifts", "America"])
    matches = matcher(doc)
    assert len(matches) == 2
    match_ids = [en_vocab.strings[matches[0][0]], en_vocab.strings[matches[1][0]]]
    assert sorted(match_ids) == ["A", "B"]


@pytest.mark.issue(3972)
def test_issue3972(en_vocab):
    """Test that the PhraseMatcher returns duplicates for duplicate match IDs."""
    matcher = PhraseMatcher(en_vocab)
    matcher.add("A", [Doc(en_vocab, words=["New", "York"])])
    matcher.add("B", [Doc(en_vocab, words=["New", "York"])])
    doc = Doc(en_vocab, words=["I", "live", "in", "New", "York"])
    matches = matcher(doc)

    assert len(matches) == 2

    # We should have a match for each of the two rules
    found_ids = [en_vocab.strings[ent_id] for (ent_id, _, _) in matches]
    assert "A" in found_ids
    assert "B" in found_ids


@pytest.mark.issue(4002)
def test_issue4002(en_vocab):
    """Test that the PhraseMatcher can match on overwritten NORM attributes."""
    matcher = PhraseMatcher(en_vocab, attr="NORM")
    pattern1 = Doc(en_vocab, words=["c", "d"])
    assert [t.norm_ for t in pattern1] == ["c", "d"]
    matcher.add("TEST", [pattern1])
    doc = Doc(en_vocab, words=["a", "b", "c", "d"])
    assert [t.norm_ for t in doc] == ["a", "b", "c", "d"]
    matches = matcher(doc)
    assert len(matches) == 1
    matcher = PhraseMatcher(en_vocab, attr="NORM")
    pattern2 = Doc(en_vocab, words=["1", "2"])
    pattern2[0].norm_ = "c"
    pattern2[1].norm_ = "d"
    assert [t.norm_ for t in pattern2] == ["c", "d"]
    matcher.add("TEST", [pattern2])
    matches = matcher(doc)
    assert len(matches) == 1


@pytest.mark.issue(4373)
def test_issue4373():
    """Test that PhraseMatcher.vocab can be accessed (like Matcher.vocab)."""
    matcher = Matcher(Vocab())
    assert isinstance(matcher.vocab, Vocab)
    matcher = PhraseMatcher(Vocab())
    assert isinstance(matcher.vocab, Vocab)


@pytest.mark.issue(4651)
def test_issue4651_with_phrase_matcher_attr():
    """Test that the EntityRuler PhraseMatcher is deserialized correctly using
    the method from_disk when the EntityRuler argument phrase_matcher_attr is
    specified.
    """
    text = "Spacy is a python library for nlp"
    nlp = English()
    patterns = [{"label": "PYTHON_LIB", "pattern": "spacy", "id": "spaCy"}]
    ruler = nlp.add_pipe("entity_ruler", config={"phrase_matcher_attr": "LOWER"})
    ruler.add_patterns(patterns)
    doc = nlp(text)
    res = [(ent.text, ent.label_, ent.ent_id_) for ent in doc.ents]
    nlp_reloaded = English()
    with make_tempdir() as d:
        file_path = d / "entityruler"
        ruler.to_disk(file_path)
        nlp_reloaded.add_pipe("entity_ruler").from_disk(file_path)
    doc_reloaded = nlp_reloaded(text)
    res_reloaded = [(ent.text, ent.label_, ent.ent_id_) for ent in doc_reloaded.ents]
    assert res == res_reloaded


@pytest.mark.issue(6839)
def test_issue6839(en_vocab):
    """Ensure that PhraseMatcher accepts Span as input"""
    # fmt: off
    words = ["I", "like", "Spans", "and", "Docs", "in", "my", "input", ",", "and", "nothing", "else", "."]
    # fmt: on
    doc = Doc(en_vocab, words=words)
    span = doc[:8]
    pattern = Doc(en_vocab, words=["Spans", "and", "Docs"])
    matcher = PhraseMatcher(en_vocab)
    matcher.add("SPACY", [pattern])
    matches = matcher(span)
    assert matches


@pytest.mark.issue(10643)
def test_issue10643(en_vocab):
    """Ensure overlapping terms can be removed from PhraseMatcher"""

    # fmt: off
    words = ["Only", "save", "out", "the", "binary", "data", "for", "the", "individual", "components", "."]
    # fmt: on
    doc = Doc(en_vocab, words=words)
    terms = {
        "0": Doc(en_vocab, words=["binary"]),
        "1": Doc(en_vocab, words=["binary", "data"]),
    }
    matcher = PhraseMatcher(en_vocab)
    for match_id, term in terms.items():
        matcher.add(match_id, [term])

    matches = matcher(doc)
    assert matches == [(en_vocab.strings["0"], 4, 5), (en_vocab.strings["1"], 4, 6)]

    matcher.remove("0")
    assert len(matcher) == 1
    new_matches = matcher(doc)
    assert new_matches == [(en_vocab.strings["1"], 4, 6)]

    matcher.remove("1")
    assert len(matcher) == 0
    no_matches = matcher(doc)
    assert not no_matches


def test_matcher_phrase_matcher(en_vocab):
    doc = Doc(en_vocab, words=["I", "like", "Google", "Now", "best"])
    # intermediate phrase
    pattern = Doc(en_vocab, words=["Google", "Now"])
    matcher = PhraseMatcher(en_vocab)
    matcher.add("COMPANY", [pattern])
    assert len(matcher(doc)) == 1
    # initial token
    pattern = Doc(en_vocab, words=["I"])
    matcher = PhraseMatcher(en_vocab)
    matcher.add("I", [pattern])
    assert len(matcher(doc)) == 1
    # initial phrase
    pattern = Doc(en_vocab, words=["I", "like"])
    matcher = PhraseMatcher(en_vocab)
    matcher.add("ILIKE", [pattern])
    assert len(matcher(doc)) == 1
    # final token
    pattern = Doc(en_vocab, words=["best"])
    matcher = PhraseMatcher(en_vocab)
    matcher.add("BEST", [pattern])
    assert len(matcher(doc)) == 1
    # final phrase
    pattern = Doc(en_vocab, words=["Now", "best"])
    matcher = PhraseMatcher(en_vocab)
    matcher.add("NOWBEST", [pattern])
    assert len(matcher(doc)) == 1


def test_phrase_matcher_length(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    assert len(matcher) == 0
    matcher.add("TEST", [Doc(en_vocab, words=["test"])])
    assert len(matcher) == 1
    matcher.add("TEST2", [Doc(en_vocab, words=["test2"])])
    assert len(matcher) == 2


def test_phrase_matcher_contains(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    matcher.add("TEST", [Doc(en_vocab, words=["test"])])
    assert "TEST" in matcher
    assert "TEST2" not in matcher


def test_phrase_matcher_add_new_api(en_vocab):
    doc = Doc(en_vocab, words=["a", "b"])
    patterns = [Doc(en_vocab, words=["a"]), Doc(en_vocab, words=["a", "b"])]
    matcher = PhraseMatcher(en_vocab)
    matcher.add("OLD_API", None, *patterns)
    assert len(matcher(doc)) == 2
    matcher = PhraseMatcher(en_vocab)
    on_match = Mock()
    matcher.add("OLD_API_CALLBACK", on_match, *patterns)
    assert len(matcher(doc)) == 2
    assert on_match.call_count == 2
    # New API: add(key: str, patterns: List[List[dict]], on_match: Callable)
    matcher = PhraseMatcher(en_vocab)
    matcher.add("NEW_API", patterns)
    assert len(matcher(doc)) == 2
    matcher = PhraseMatcher(en_vocab)
    on_match = Mock()
    matcher.add("NEW_API_CALLBACK", patterns, on_match=on_match)
    assert len(matcher(doc)) == 2
    assert on_match.call_count == 2


def test_phrase_matcher_repeated_add(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    # match ID only gets added once
    matcher.add("TEST", [Doc(en_vocab, words=["like"])])
    matcher.add("TEST", [Doc(en_vocab, words=["like"])])
    matcher.add("TEST", [Doc(en_vocab, words=["like"])])
    matcher.add("TEST", [Doc(en_vocab, words=["like"])])
    doc = Doc(en_vocab, words=["I", "like", "Google", "Now", "best"])
    assert "TEST" in matcher
    assert "TEST2" not in matcher
    assert len(matcher(doc)) == 1


def test_phrase_matcher_remove(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    matcher.add("TEST1", [Doc(en_vocab, words=["like"])])
    matcher.add("TEST2", [Doc(en_vocab, words=["best"])])
    doc = Doc(en_vocab, words=["I", "like", "Google", "Now", "best"])
    assert "TEST1" in matcher
    assert "TEST2" in matcher
    assert "TEST3" not in matcher
    assert len(matcher(doc)) == 2
    matcher.remove("TEST1")
    assert "TEST1" not in matcher
    assert "TEST2" in matcher
    assert "TEST3" not in matcher
    assert len(matcher(doc)) == 1
    matcher.remove("TEST2")
    assert "TEST1" not in matcher
    assert "TEST2" not in matcher
    assert "TEST3" not in matcher
    assert len(matcher(doc)) == 0
    with pytest.raises(KeyError):
        matcher.remove("TEST3")
    assert "TEST1" not in matcher
    assert "TEST2" not in matcher
    assert "TEST3" not in matcher
    assert len(matcher(doc)) == 0


def test_phrase_matcher_overlapping_with_remove(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    matcher.add("TEST", [Doc(en_vocab, words=["like"])])
    # TEST2 is added alongside TEST
    matcher.add("TEST2", [Doc(en_vocab, words=["like"])])
    doc = Doc(en_vocab, words=["I", "like", "Google", "Now", "best"])
    assert "TEST" in matcher
    assert len(matcher) == 2
    assert len(matcher(doc)) == 2
    # removing TEST does not remove the entry for TEST2
    matcher.remove("TEST")
    assert "TEST" not in matcher
    assert len(matcher) == 1
    assert len(matcher(doc)) == 1
    assert matcher(doc)[0][0] == en_vocab.strings["TEST2"]
    # removing TEST2 removes all
    matcher.remove("TEST2")
    assert "TEST2" not in matcher
    assert len(matcher) == 0
    assert len(matcher(doc)) == 0


def test_phrase_matcher_string_attrs(en_vocab):
    words1 = ["I", "like", "cats"]
    pos1 = ["PRON", "VERB", "NOUN"]
    words2 = ["Yes", ",", "you", "hate", "dogs", "very", "much"]
    pos2 = ["INTJ", "PUNCT", "PRON", "VERB", "NOUN", "ADV", "ADV"]
    pattern = Doc(en_vocab, words=words1, pos=pos1)
    matcher = PhraseMatcher(en_vocab, attr="POS")
    matcher.add("TEST", [pattern])
    doc = Doc(en_vocab, words=words2, pos=pos2)
    matches = matcher(doc)
    assert len(matches) == 1
    match_id, start, end = matches[0]
    assert match_id == en_vocab.strings["TEST"]
    assert start == 2
    assert end == 5


def test_phrase_matcher_string_attrs_negative(en_vocab):
    """Test that token with the control codes as ORTH are *not* matched."""
    words1 = ["I", "like", "cats"]
    pos1 = ["PRON", "VERB", "NOUN"]
    words2 = ["matcher:POS-PRON", "matcher:POS-VERB", "matcher:POS-NOUN"]
    pos2 = ["X", "X", "X"]
    pattern = Doc(en_vocab, words=words1, pos=pos1)
    matcher = PhraseMatcher(en_vocab, attr="POS")
    matcher.add("TEST", [pattern])
    doc = Doc(en_vocab, words=words2, pos=pos2)
    matches = matcher(doc)
    assert len(matches) == 0


def test_phrase_matcher_bool_attrs(en_vocab):
    words1 = ["Hello", "world", "!"]
    words2 = ["No", "problem", ",", "he", "said", "."]
    pattern = Doc(en_vocab, words=words1)
    matcher = PhraseMatcher(en_vocab, attr="IS_PUNCT")
    matcher.add("TEST", [pattern])
    doc = Doc(en_vocab, words=words2)
    matches = matcher(doc)
    assert len(matches) == 2
    match_id1, start1, end1 = matches[0]
    match_id2, start2, end2 = matches[1]
    assert match_id1 == en_vocab.strings["TEST"]
    assert match_id2 == en_vocab.strings["TEST"]
    assert start1 == 0
    assert end1 == 3
    assert start2 == 3
    assert end2 == 6


def test_phrase_matcher_validation(en_vocab):
    doc1 = Doc(en_vocab, words=["Test"])
    doc1[0].dep_ = "ROOT"
    doc2 = Doc(en_vocab, words=["Test"])
    doc2[0].tag_ = "TAG"
    doc2[0].pos_ = "X"
    doc2[0].set_morph("Feat=Val")
    doc3 = Doc(en_vocab, words=["Test"])
    matcher = PhraseMatcher(en_vocab, validate=True)
    with pytest.warns(UserWarning):
        matcher.add("TEST1", [doc1])
    with pytest.warns(UserWarning):
        matcher.add("TEST2", [doc2])
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        matcher.add("TEST3", [doc3])
    matcher = PhraseMatcher(en_vocab, attr="POS", validate=True)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        matcher.add("TEST4", [doc2])


def test_attr_validation(en_vocab):
    with pytest.raises(ValueError):
        PhraseMatcher(en_vocab, attr="UNSUPPORTED")


def test_attr_pipeline_checks(en_vocab):
    doc1 = Doc(en_vocab, words=["Test"])
    doc1[0].dep_ = "ROOT"
    doc2 = Doc(en_vocab, words=["Test"])
    doc2[0].tag_ = "TAG"
    doc2[0].pos_ = "X"
    doc2[0].set_morph("Feat=Val")
    doc2[0].lemma_ = "LEMMA"
    doc3 = Doc(en_vocab, words=["Test"])
    # DEP requires DEP
    matcher = PhraseMatcher(en_vocab, attr="DEP")
    matcher.add("TEST1", [doc1])
    with pytest.raises(ValueError):
        matcher.add("TEST2", [doc2])
    with pytest.raises(ValueError):
        matcher.add("TEST3", [doc3])
    # TAG, POS, LEMMA require those values
    for attr in ("TAG", "POS", "LEMMA"):
        matcher = PhraseMatcher(en_vocab, attr=attr)
        matcher.add("TEST2", [doc2])
        with pytest.raises(ValueError):
            matcher.add("TEST1", [doc1])
        with pytest.raises(ValueError):
            matcher.add("TEST3", [doc3])
    # TEXT/ORTH only require tokens
    matcher = PhraseMatcher(en_vocab, attr="ORTH")
    matcher.add("TEST3", [doc3])
    matcher = PhraseMatcher(en_vocab, attr="TEXT")
    matcher.add("TEST3", [doc3])


def test_phrase_matcher_callback(en_vocab):
    mock = Mock()
    doc = Doc(en_vocab, words=["I", "like", "Google", "Now", "best"])
    pattern = Doc(en_vocab, words=["Google", "Now"])
    matcher = PhraseMatcher(en_vocab)
    matcher.add("COMPANY", [pattern], on_match=mock)
    matches = matcher(doc)
    mock.assert_called_once_with(matcher, doc, 0, matches)


def test_phrase_matcher_remove_overlapping_patterns(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    pattern1 = Doc(en_vocab, words=["this"])
    pattern2 = Doc(en_vocab, words=["this", "is"])
    pattern3 = Doc(en_vocab, words=["this", "is", "a"])
    pattern4 = Doc(en_vocab, words=["this", "is", "a", "word"])
    matcher.add("THIS", [pattern1, pattern2, pattern3, pattern4])
    matcher.remove("THIS")


def test_phrase_matcher_basic_check(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    # Potential mistake: pass in pattern instead of list of patterns
    pattern = Doc(en_vocab, words=["hello", "world"])
    with pytest.raises(ValueError):
        matcher.add("TEST", pattern)


def test_phrase_matcher_pickle(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    mock = Mock()
    matcher.add("TEST", [Doc(en_vocab, words=["test"])])
    matcher.add("TEST2", [Doc(en_vocab, words=["test2"])], on_match=mock)
    doc = Doc(en_vocab, words=["these", "are", "tests", ":", "test", "test2"])
    assert len(matcher) == 2

    b = srsly.pickle_dumps(matcher)
    matcher_unpickled = srsly.pickle_loads(b)

    # call after pickling to avoid recursion error related to mock
    matches = matcher(doc)
    matches_unpickled = matcher_unpickled(doc)

    assert len(matcher) == len(matcher_unpickled)
    assert matches == matches_unpickled

    # clunky way to vaguely check that callback is unpickled
    (vocab, docs, callbacks, attr) = matcher_unpickled.__reduce__()[1]
    assert isinstance(callbacks.get("TEST2"), Mock)


def test_phrase_matcher_as_spans(en_vocab):
    """Test the new as_spans=True API."""
    matcher = PhraseMatcher(en_vocab)
    matcher.add("A", [Doc(en_vocab, words=["hello", "world"])])
    matcher.add("B", [Doc(en_vocab, words=["test"])])
    doc = Doc(en_vocab, words=["...", "hello", "world", "this", "is", "a", "test"])
    matches = matcher(doc, as_spans=True)
    assert len(matches) == 2
    assert isinstance(matches[0], Span)
    assert matches[0].text == "hello world"
    assert matches[0].label_ == "A"
    assert isinstance(matches[1], Span)
    assert matches[1].text == "test"
    assert matches[1].label_ == "B"


def test_phrase_matcher_deprecated(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    matcher.add("TEST", [Doc(en_vocab, words=["helllo"])])
    doc = Doc(en_vocab, words=["hello", "world"])
    with pytest.warns(DeprecationWarning) as record:
        for _ in matcher.pipe([doc]):
            pass
        assert record.list
        assert "spaCy v3.0" in str(record.list[0].message)


@pytest.mark.parametrize("attr", ["SENT_START", "IS_SENT_START"])
def test_phrase_matcher_sent_start(en_vocab, attr):
    _ = PhraseMatcher(en_vocab, attr=attr)  # noqa: F841


def test_span_in_phrasematcher(en_vocab):
    """Ensure that PhraseMatcher accepts Span and Doc as input"""
    # fmt: off
    words = ["I", "like", "Spans", "and", "Docs", "in", "my", "input", ",", "and", "nothing", "else", "."]
    # fmt: on
    doc = Doc(en_vocab, words=words)
    span = doc[:8]
    pattern = Doc(en_vocab, words=["Spans", "and", "Docs"])
    matcher = PhraseMatcher(en_vocab)
    matcher.add("SPACY", [pattern])
    matches_doc = matcher(doc)
    matches_span = matcher(span)
    assert len(matches_doc) == 1
    assert len(matches_span) == 1


def test_span_v_doc_in_phrasematcher(en_vocab):
    """Ensure that PhraseMatcher only returns matches in input Span and not in entire Doc"""
    # fmt: off
    words = [
        "I", "like", "Spans", "and", "Docs", "in", "my", "input", ",", "Spans",
        "and", "Docs", "in", "my", "matchers", "," "and", "Spans", "and", "Docs",
        "everywhere", "."
    ]
    # fmt: on
    doc = Doc(en_vocab, words=words)
    span = doc[9:15]  # second clause
    pattern = Doc(en_vocab, words=["Spans", "and", "Docs"])
    matcher = PhraseMatcher(en_vocab)
    matcher.add("SPACY", [pattern])
    matches_doc = matcher(doc)
    matches_span = matcher(span)
    assert len(matches_doc) == 3
    assert len(matches_span) == 1
