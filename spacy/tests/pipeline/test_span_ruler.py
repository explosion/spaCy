import pytest

import spacy
from spacy import registry
from spacy.errors import MatchPatternError
from spacy.tokens import Span
from spacy.training import Example
from spacy.tests.util import make_tempdir

from thinc.api import NumpyOps, get_current_ops


@pytest.fixture
@registry.misc("span_ruler_patterns")
def patterns():
    return [
        {"label": "HELLO", "pattern": "hello world", "id": "hello1"},
        {"label": "BYE", "pattern": [{"LOWER": "bye"}, {"LOWER": "bye"}]},
        {"label": "HELLO", "pattern": [{"ORTH": "HELLO"}], "id": "hello2"},
        {"label": "COMPLEX", "pattern": [{"ORTH": "foo", "OP": "*"}]},
        {"label": "TECH_ORG", "pattern": "Apple"},
        {"label": "TECH_ORG", "pattern": "Microsoft"},
    ]


@pytest.fixture
def overlapping_patterns():
    return [
        {"label": "FOOBAR", "pattern": "foo bar"},
        {"label": "BARBAZ", "pattern": "bar baz"},
    ]


@pytest.fixture
def person_org_patterns():
    return [
        {"label": "PERSON", "pattern": "Dina"},
        {"label": "ORG", "pattern": "ACME"},
        {"label": "ORG", "pattern": "ACM"},
    ]


@pytest.fixture
def person_org_date_patterns(person_org_patterns):
    return person_org_patterns + [{"label": "DATE", "pattern": "June 14th"}]


def test_span_ruler_add_empty(patterns):
    """Test that patterns don't get added excessively."""
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler", config={"validate": True})
    ruler.add_patterns(patterns)
    pattern_count = sum(len(mm) for mm in ruler.matcher._patterns.values())
    assert pattern_count > 0
    ruler.add_patterns([])
    after_count = sum(len(mm) for mm in ruler.matcher._patterns.values())
    assert after_count == pattern_count


def test_span_ruler_init(patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(patterns)
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    assert "HELLO" in ruler
    assert "BYE" in ruler
    doc = nlp("hello world bye bye")
    assert len(doc.spans["ruler"]) == 2
    assert doc.spans["ruler"][0].label_ == "HELLO"
    assert doc.spans["ruler"][0].id_ == "hello1"
    assert doc.spans["ruler"][1].label_ == "BYE"
    assert doc.spans["ruler"][1].id_ == ""


def test_span_ruler_no_patterns_warns():
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    assert len(ruler) == 0
    assert len(ruler.labels) == 0
    assert nlp.pipe_names == ["span_ruler"]
    with pytest.warns(UserWarning):
        doc = nlp("hello world bye bye")
    assert len(doc.spans["ruler"]) == 0


def test_span_ruler_init_patterns(patterns):
    # initialize with patterns
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    assert len(ruler.labels) == 0
    ruler.initialize(lambda: [], patterns=patterns)
    assert len(ruler.labels) == 4
    doc = nlp("hello world bye bye")
    assert doc.spans["ruler"][0].label_ == "HELLO"
    assert doc.spans["ruler"][1].label_ == "BYE"
    nlp.remove_pipe("span_ruler")
    # initialize with patterns from misc registry
    nlp.config["initialize"]["components"]["span_ruler"] = {
        "patterns": {"@misc": "span_ruler_patterns"}
    }
    ruler = nlp.add_pipe("span_ruler")
    assert len(ruler.labels) == 0
    nlp.initialize()
    assert len(ruler.labels) == 4
    doc = nlp("hello world bye bye")
    assert doc.spans["ruler"][0].label_ == "HELLO"
    assert doc.spans["ruler"][1].label_ == "BYE"


def test_span_ruler_init_clear(patterns):
    """Test that initialization clears patterns."""
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(patterns)
    assert len(ruler.labels) == 4
    ruler.initialize(lambda: [])
    assert len(ruler.labels) == 0


def test_span_ruler_clear(patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(patterns)
    assert len(ruler.labels) == 4
    doc = nlp("hello world")
    assert len(doc.spans["ruler"]) == 1
    ruler.clear()
    assert len(ruler.labels) == 0
    with pytest.warns(UserWarning):
        doc = nlp("hello world")
    assert len(doc.spans["ruler"]) == 0


def test_span_ruler_existing(patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler", config={"overwrite": False})
    ruler.add_patterns(patterns)
    doc = nlp.make_doc("OH HELLO WORLD bye bye")
    doc.spans["ruler"] = [doc[0:2]]
    doc = nlp(doc)
    assert len(doc.spans["ruler"]) == 3
    assert doc.spans["ruler"][0] == doc[0:2]
    assert doc.spans["ruler"][1].label_ == "HELLO"
    assert doc.spans["ruler"][1].id_ == "hello2"
    assert doc.spans["ruler"][2].label_ == "BYE"
    assert doc.spans["ruler"][2].id_ == ""


def test_span_ruler_existing_overwrite(patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler", config={"overwrite": True})
    ruler.add_patterns(patterns)
    doc = nlp.make_doc("OH HELLO WORLD bye bye")
    doc.spans["ruler"] = [doc[0:2]]
    doc = nlp(doc)
    assert len(doc.spans["ruler"]) == 2
    assert doc.spans["ruler"][0].label_ == "HELLO"
    assert doc.spans["ruler"][0].text == "HELLO"
    assert doc.spans["ruler"][1].label_ == "BYE"


def test_span_ruler_serialize_bytes(patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(patterns)
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    ruler_bytes = ruler.to_bytes()
    new_nlp = spacy.blank("xx")
    new_ruler = new_nlp.add_pipe("span_ruler")
    assert len(new_ruler) == 0
    assert len(new_ruler.labels) == 0
    new_ruler = new_ruler.from_bytes(ruler_bytes)
    assert len(new_ruler) == len(patterns)
    assert len(new_ruler.labels) == 4
    assert len(new_ruler.patterns) == len(ruler.patterns)
    for pattern in ruler.patterns:
        assert pattern in new_ruler.patterns
    assert sorted(new_ruler.labels) == sorted(ruler.labels)


def test_span_ruler_validate():
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    validated_ruler = nlp.add_pipe(
        "span_ruler", name="validated_span_ruler", config={"validate": True}
    )

    valid_pattern = {"label": "HELLO", "pattern": [{"LOWER": "HELLO"}]}
    invalid_pattern = {"label": "HELLO", "pattern": [{"ASDF": "HELLO"}]}

    # invalid pattern raises error without validate
    with pytest.raises(ValueError):
        ruler.add_patterns([invalid_pattern])

    # valid pattern is added without errors with validate
    validated_ruler.add_patterns([valid_pattern])

    # invalid pattern raises error with validate
    with pytest.raises(MatchPatternError):
        validated_ruler.add_patterns([invalid_pattern])


def test_span_ruler_properties(patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler", config={"overwrite": True})
    ruler.add_patterns(patterns)
    assert sorted(ruler.labels) == sorted(set([p["label"] for p in patterns]))


def test_span_ruler_overlapping_spans(overlapping_patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(overlapping_patterns)
    doc = ruler(nlp.make_doc("foo bar baz"))
    assert len(doc.spans["ruler"]) == 2
    assert doc.spans["ruler"][0].label_ == "FOOBAR"
    assert doc.spans["ruler"][1].label_ == "BARBAZ"


def test_span_ruler_scorer(overlapping_patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(overlapping_patterns)
    text = "foo bar baz"
    pred_doc = ruler(nlp.make_doc(text))
    assert len(pred_doc.spans["ruler"]) == 2
    assert pred_doc.spans["ruler"][0].label_ == "FOOBAR"
    assert pred_doc.spans["ruler"][1].label_ == "BARBAZ"

    ref_doc = nlp.make_doc(text)
    ref_doc.spans["ruler"] = [Span(ref_doc, 0, 2, label="FOOBAR")]
    scores = nlp.evaluate([Example(pred_doc, ref_doc)])
    assert scores["spans_ruler_p"] == 0.5
    assert scores["spans_ruler_r"] == 1.0


@pytest.mark.parametrize("n_process", [1, 2])
def test_span_ruler_multiprocessing(n_process):
    if isinstance(get_current_ops, NumpyOps) or n_process < 2:
        texts = ["I enjoy eating Pizza Hut pizza."]

        patterns = [{"label": "FASTFOOD", "pattern": "Pizza Hut"}]

        nlp = spacy.blank("xx")
        ruler = nlp.add_pipe("span_ruler")
        ruler.add_patterns(patterns)

        for doc in nlp.pipe(texts, n_process=2):
            for ent in doc.spans["ruler"]:
                assert ent.label_ == "FASTFOOD"


def test_span_ruler_serialize_dir(patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(patterns)
    with make_tempdir() as d:
        ruler.to_disk(d / "test_ruler")
        ruler.from_disk(d / "test_ruler")  # read from an existing directory
        with pytest.raises(ValueError):
            ruler.from_disk(d / "non_existing_dir")  # read from a bad directory


def test_span_ruler_remove_basic(person_org_patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(person_org_patterns)
    doc = ruler(nlp.make_doc("Dina went to school"))
    assert len(ruler.patterns) == 3
    assert len(doc.spans["ruler"]) == 1
    assert doc.spans["ruler"][0].label_ == "PERSON"
    assert doc.spans["ruler"][0].text == "Dina"
    ruler.remove("PERSON")
    doc = ruler(nlp.make_doc("Dina went to school"))
    assert len(doc.spans["ruler"]) == 0
    assert len(ruler.patterns) == 2


def test_span_ruler_remove_nonexisting_pattern(person_org_patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(person_org_patterns)
    assert len(ruler.patterns) == 3
    with pytest.raises(ValueError):
        ruler.remove("NE")
    with pytest.raises(ValueError):
        ruler.remove_by_id("NE")


def test_span_ruler_remove_several_patterns(person_org_patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(person_org_patterns)
    doc = ruler(nlp.make_doc("Dina founded the company ACME."))
    assert len(ruler.patterns) == 3
    assert len(doc.spans["ruler"]) == 2
    assert doc.spans["ruler"][0].label_ == "PERSON"
    assert doc.spans["ruler"][0].text == "Dina"
    assert doc.spans["ruler"][1].label_ == "ORG"
    assert doc.spans["ruler"][1].text == "ACME"
    ruler.remove("PERSON")
    doc = ruler(nlp.make_doc("Dina founded the company ACME"))
    assert len(ruler.patterns) == 2
    assert len(doc.spans["ruler"]) == 1
    assert doc.spans["ruler"][0].label_ == "ORG"
    assert doc.spans["ruler"][0].text == "ACME"
    ruler.remove("ORG")
    with pytest.warns(UserWarning):
        doc = ruler(nlp.make_doc("Dina founded the company ACME"))
        assert len(ruler.patterns) == 0
        assert len(doc.spans["ruler"]) == 0


def test_span_ruler_remove_patterns_in_a_row(person_org_date_patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(person_org_date_patterns)
    doc = ruler(nlp.make_doc("Dina founded the company ACME on June 14th"))
    assert len(doc.spans["ruler"]) == 3
    assert doc.spans["ruler"][0].label_ == "PERSON"
    assert doc.spans["ruler"][0].text == "Dina"
    assert doc.spans["ruler"][1].label_ == "ORG"
    assert doc.spans["ruler"][1].text == "ACME"
    assert doc.spans["ruler"][2].label_ == "DATE"
    assert doc.spans["ruler"][2].text == "June 14th"
    ruler.remove("ORG")
    ruler.remove("DATE")
    doc = ruler(nlp.make_doc("Dina went to school"))
    assert len(doc.spans["ruler"]) == 1


def test_span_ruler_remove_all_patterns(person_org_date_patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(person_org_date_patterns)
    assert len(ruler.patterns) == 4
    ruler.remove("PERSON")
    assert len(ruler.patterns) == 3
    ruler.remove("ORG")
    assert len(ruler.patterns) == 1
    ruler.remove("DATE")
    assert len(ruler.patterns) == 0
    with pytest.warns(UserWarning):
        doc = ruler(nlp.make_doc("Dina founded the company ACME on June 14th"))
        assert len(doc.spans["ruler"]) == 0


def test_span_ruler_remove_and_add():
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler")
    patterns1 = [{"label": "DATE1", "pattern": "last time"}]
    ruler.add_patterns(patterns1)
    doc = ruler(
        nlp.make_doc("I saw him last time we met, this time he brought some flowers")
    )
    assert len(ruler.patterns) == 1
    assert len(doc.spans["ruler"]) == 1
    assert doc.spans["ruler"][0].label_ == "DATE1"
    assert doc.spans["ruler"][0].text == "last time"
    patterns2 = [{"label": "DATE2", "pattern": "this time"}]
    ruler.add_patterns(patterns2)
    doc = ruler(
        nlp.make_doc("I saw him last time we met, this time he brought some flowers")
    )
    assert len(ruler.patterns) == 2
    assert len(doc.spans["ruler"]) == 2
    assert doc.spans["ruler"][0].label_ == "DATE1"
    assert doc.spans["ruler"][0].text == "last time"
    assert doc.spans["ruler"][1].label_ == "DATE2"
    assert doc.spans["ruler"][1].text == "this time"
    ruler.remove("DATE1")
    doc = ruler(
        nlp.make_doc("I saw him last time we met, this time he brought some flowers")
    )
    assert len(ruler.patterns) == 1
    assert len(doc.spans["ruler"]) == 1
    assert doc.spans["ruler"][0].label_ == "DATE2"
    assert doc.spans["ruler"][0].text == "this time"
    ruler.add_patterns(patterns1)
    doc = ruler(
        nlp.make_doc("I saw him last time we met, this time he brought some flowers")
    )
    assert len(ruler.patterns) == 2
    assert len(doc.spans["ruler"]) == 2
    patterns3 = [{"label": "DATE3", "pattern": "another time"}]
    ruler.add_patterns(patterns3)
    doc = ruler(
        nlp.make_doc(
            "I saw him last time we met, this time he brought some flowers, another time some chocolate."
        )
    )
    assert len(ruler.patterns) == 3
    assert len(doc.spans["ruler"]) == 3
    ruler.remove("DATE3")
    doc = ruler(
        nlp.make_doc(
            "I saw him last time we met, this time he brought some flowers, another time some chocolate."
        )
    )
    assert len(ruler.patterns) == 2
    assert len(doc.spans["ruler"]) == 2


def test_span_ruler_spans_filter(overlapping_patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe(
        "span_ruler",
        config={"spans_filter": {"@misc": "spacy.first_longest_spans_filter.v1"}},
    )
    ruler.add_patterns(overlapping_patterns)
    doc = ruler(nlp.make_doc("foo bar baz"))
    assert len(doc.spans["ruler"]) == 1
    assert doc.spans["ruler"][0].label_ == "FOOBAR"


def test_span_ruler_ents_default_filter(overlapping_patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe("span_ruler", config={"annotate_ents": True})
    ruler.add_patterns(overlapping_patterns)
    doc = ruler(nlp.make_doc("foo bar baz"))
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "FOOBAR"


def test_span_ruler_ents_overwrite_filter(overlapping_patterns):
    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe(
        "span_ruler",
        config={
            "annotate_ents": True,
            "overwrite": False,
            "ents_filter": {"@misc": "spacy.prioritize_new_ents_filter.v1"},
        },
    )
    ruler.add_patterns(overlapping_patterns)
    # overlapping ents are clobbered, non-overlapping ents are preserved
    doc = nlp.make_doc("foo bar baz a b c")
    doc.ents = [Span(doc, 1, 3, label="BARBAZ"), Span(doc, 3, 6, label="ABC")]
    doc = ruler(doc)
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "FOOBAR"
    assert doc.ents[1].label_ == "ABC"


def test_span_ruler_ents_bad_filter(overlapping_patterns):
    @registry.misc("test_pass_through_filter")
    def make_pass_through_filter():
        def pass_through_filter(spans1, spans2):
            return spans1 + spans2

        return pass_through_filter

    nlp = spacy.blank("xx")
    ruler = nlp.add_pipe(
        "span_ruler",
        config={
            "annotate_ents": True,
            "ents_filter": {"@misc": "test_pass_through_filter"},
        },
    )
    ruler.add_patterns(overlapping_patterns)
    with pytest.raises(ValueError):
        ruler(nlp.make_doc("foo bar baz"))
