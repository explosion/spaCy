import pytest

from spacy import registry
from spacy.language import Language
from spacy.lang.en import English
from spacy.pipeline import SpanRuler
from spacy.errors import MatchPatternError
from spacy.tests.util import make_tempdir

from thinc.api import NumpyOps, get_current_ops


@pytest.fixture
def nlp():
    return Language()


@pytest.fixture
@registry.misc("span_ruler_patterns")
def patterns():
    return [
        {"label": "HELLO", "pattern": "hello world"},
        {"label": "BYE", "pattern": [{"LOWER": "bye"}, {"LOWER": "bye"}]},
        {"label": "HELLO", "pattern": [{"ORTH": "HELLO"}]},
        {"label": "COMPLEX", "pattern": [{"ORTH": "foo", "OP": "*"}]},
        {"label": "TECH_ORG", "pattern": "Apple"},
        {"label": "TECH_ORG", "pattern": "Microsoft"},
    ]


def test_span_ruler_add_empty(nlp, patterns):
    """Test that patterns don't get added excessively."""
    ruler = nlp.add_pipe("span_ruler", config={"validate": True})
    ruler.add_patterns(patterns)
    pattern_count = sum(len(mm) for mm in ruler.matcher._patterns.values())
    assert pattern_count > 0
    ruler.add_patterns([])
    after_count = sum(len(mm) for mm in ruler.matcher._patterns.values())
    assert after_count == pattern_count


def test_span_ruler_init(nlp, patterns):
    ruler = SpanRuler(nlp)
    ruler.add_patterns(patterns)
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    assert "HELLO" in ruler
    assert "BYE" in ruler
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(patterns)
    doc = nlp("hello world bye bye")
    assert len(doc.spans["ruler"]) == 2
    assert doc.spans["ruler"][0].label_ == "HELLO"
    assert doc.spans["ruler"][1].label_ == "BYE"


def test_span_ruler_no_patterns_warns(nlp):
    ruler = SpanRuler(nlp)
    assert len(ruler) == 0
    assert len(ruler.labels) == 0
    nlp.add_pipe("span_ruler")
    assert nlp.pipe_names == ["span_ruler"]
    with pytest.warns(UserWarning):
        doc = nlp("hello world bye bye")
    assert len(doc.spans["ruler"]) == 0


def test_span_ruler_init_patterns(nlp, patterns):
    # initialize with patterns
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


def test_span_ruler_init_clear(nlp, patterns):
    """Test that initialization clears patterns."""
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(patterns)
    assert len(ruler.labels) == 4
    ruler.initialize(lambda: [])
    assert len(ruler.labels) == 0


def test_span_ruler_clear(nlp, patterns):
    """Test that initialization clears patterns."""
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


def test_span_ruler_existing(nlp, patterns):
    ruler = nlp.add_pipe("span_ruler", config={"overwrite": False})
    ruler.add_patterns(patterns)
    doc = nlp.make_doc("OH HELLO WORLD bye bye")
    doc.spans["ruler"] = [doc[0:2]]
    doc = nlp(doc)
    assert len(doc.spans["ruler"]) == 3
    assert doc.spans["ruler"][0] == doc[0:2]
    assert doc.spans["ruler"][1].label_ == "HELLO"
    assert doc.spans["ruler"][2].label_ == "BYE"


def test_span_ruler_existing_overwrite(nlp, patterns):
    ruler = nlp.add_pipe("span_ruler", config={"overwrite": True})
    ruler.add_patterns(patterns)
    doc = nlp.make_doc("OH HELLO WORLD bye bye")
    doc.spans["ruler"] = [doc[0:2]]
    doc = nlp(doc)
    assert len(doc.spans["ruler"]) == 2
    assert doc.spans["ruler"][0].label_ == "HELLO"
    assert doc.spans["ruler"][0].text == "HELLO"
    assert doc.spans["ruler"][1].label_ == "BYE"


def test_span_ruler_serialize_bytes(nlp, patterns):
    ruler = SpanRuler(nlp)
    ruler.add_patterns(patterns)
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    ruler_bytes = ruler.to_bytes()
    new_ruler = SpanRuler(nlp)
    assert len(new_ruler) == 0
    assert len(new_ruler.labels) == 0
    new_ruler = new_ruler.from_bytes(ruler_bytes)
    assert len(new_ruler) == len(patterns)
    assert len(new_ruler.labels) == 4
    assert len(new_ruler.patterns) == len(ruler.patterns)
    for pattern in ruler.patterns:
        assert pattern in new_ruler.patterns
    assert sorted(new_ruler.labels) == sorted(ruler.labels)


def test_span_ruler_serialize_phrase_matcher_attr_bytes(nlp, patterns):
    ruler = SpanRuler(nlp, phrase_matcher_attr="LOWER")
    ruler.add_patterns(patterns)
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    ruler_bytes = ruler.to_bytes()
    new_ruler = SpanRuler(nlp)
    assert len(new_ruler) == 0
    assert len(new_ruler.labels) == 0
    assert new_ruler.cfg["phrase_matcher_attr"] is None
    new_ruler = new_ruler.from_bytes(ruler_bytes)
    assert len(new_ruler) == len(patterns)
    assert len(new_ruler.labels) == 4
    assert new_ruler.cfg["phrase_matcher_attr"] == "LOWER"


def test_span_ruler_validate(nlp):
    ruler = SpanRuler(nlp)
    validated_ruler = SpanRuler(nlp, validate=True)

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


def test_span_ruler_properties(nlp, patterns):
    ruler = SpanRuler(nlp, overwrite=True)
    ruler.add_patterns(patterns)
    assert sorted(ruler.labels) == sorted(["HELLO", "BYE", "COMPLEX", "TECH_ORG"])


def test_span_ruler_overlapping_spans(nlp):
    ruler = SpanRuler(nlp)
    patterns = [
        {"label": "FOOBAR", "pattern": "foo bar"},
        {"label": "BARBAZ", "pattern": "bar baz"},
    ]
    ruler.add_patterns(patterns)
    doc = ruler(nlp.make_doc("foo bar baz"))
    assert len(doc.spans["ruler"]) == 2
    assert doc.spans["ruler"][0].label_ == "FOOBAR"
    assert doc.spans["ruler"][1].label_ == "BARBAZ"


@pytest.mark.parametrize("n_process", [1, 2])
def test_span_ruler_multiprocessing(nlp, n_process):
    if isinstance(get_current_ops, NumpyOps) or n_process < 2:
        texts = ["I enjoy eating Pizza Hut pizza."]

        patterns = [{"label": "FASTFOOD", "pattern": "Pizza Hut"}]

        ruler = nlp.add_pipe("span_ruler")
        ruler.add_patterns(patterns)

        for doc in nlp.pipe(texts, n_process=2):
            for ent in doc.spans["ruler"]:
                assert ent.label_ == "FASTFOOD"


def test_span_ruler_serialize_dir(nlp, patterns):
    ruler = nlp.add_pipe("span_ruler")
    ruler.add_patterns(patterns)
    with make_tempdir() as d:
        ruler.to_disk(d / "test_ruler")
        ruler.from_disk(d / "test_ruler")  # read from an existing directory
        with pytest.raises(ValueError):
            ruler.from_disk(d / "non_existing_dir")  # read from a bad directory


def test_span_ruler_remove_basic(nlp):
    ruler = SpanRuler(nlp)
    patterns = [
        {"label": "PERSON", "pattern": "Duygu"},
        {"label": "ORG", "pattern": "ACME"},
        {"label": "ORG", "pattern": "ACM"},
    ]
    ruler.add_patterns(patterns)
    doc = ruler(nlp.make_doc("Duygu went to school"))
    assert len(ruler.patterns) == 3
    assert len(doc.spans["ruler"]) == 1
    assert doc.spans["ruler"][0].label_ == "PERSON"
    assert doc.spans["ruler"][0].text == "Duygu"
    assert "PERSON" in ruler.phrase_matcher
    ruler.remove("PERSON")
    doc = ruler(nlp.make_doc("Duygu went to school"))
    assert len(doc.spans["ruler"]) == 0
    assert "PERSON" not in ruler.phrase_matcher
    assert len(ruler.patterns) == 2


def test_span_ruler_remove_nonexisting_pattern(nlp):
    ruler = SpanRuler(nlp)
    patterns = [
        {"label": "PERSON", "pattern": "Duygu"},
        {"label": "ORG", "pattern": "ACME"},
        {"label": "ORG", "pattern": "ACM"},
    ]
    ruler.add_patterns(patterns)
    assert len(ruler.patterns) == 3
    with pytest.raises(ValueError):
        ruler.remove("NE")
        assert len(ruler.patterns) == 3


def test_span_ruler_remove_several_patterns(nlp):
    ruler = SpanRuler(nlp)
    patterns = [
        {"label": "PERSON", "pattern": "Duygu"},
        {"label": "ORG", "pattern": "ACME"},
        {"label": "ORG", "pattern": "ACM"},
    ]
    ruler.add_patterns(patterns)
    doc = ruler(nlp.make_doc("Duygu founded her company ACME."))
    assert len(ruler.patterns) == 3
    assert len(doc.spans["ruler"]) == 2
    assert doc.spans["ruler"][0].label_ == "PERSON"
    assert doc.spans["ruler"][0].text == "Duygu"
    assert doc.spans["ruler"][1].label_ == "ORG"
    assert doc.spans["ruler"][1].text == "ACME"
    ruler.remove("PERSON")
    doc = ruler(nlp.make_doc("Duygu founded her company ACME"))
    assert len(ruler.patterns) == 2
    assert len(doc.spans["ruler"]) == 1
    assert doc.spans["ruler"][0].label_ == "ORG"
    assert doc.spans["ruler"][0].text == "ACME"
    ruler.remove("ORG")
    with pytest.warns(UserWarning):
        doc = ruler(nlp.make_doc("Duygu founded her company ACME"))
        assert len(ruler.patterns) == 0
        assert len(doc.spans["ruler"]) == 0


def test_span_ruler_remove_patterns_in_a_row(nlp):
    ruler = SpanRuler(nlp)
    patterns = [
        {"label": "PERSON", "pattern": "Duygu"},
        {"label": "ORG", "pattern": "ACME"},
        {"label": "DATE", "pattern": "her birthday"},
        {"label": "ORG", "pattern": "ACM"},
    ]
    ruler.add_patterns(patterns)
    doc = ruler(nlp.make_doc("Duygu founded her company ACME on her birthday"))
    assert len(doc.spans["ruler"]) == 3
    assert doc.spans["ruler"][0].label_ == "PERSON"
    assert doc.spans["ruler"][0].text == "Duygu"
    assert doc.spans["ruler"][1].label_ == "ORG"
    assert doc.spans["ruler"][1].text == "ACME"
    assert doc.spans["ruler"][2].label_ == "DATE"
    assert doc.spans["ruler"][2].text == "her birthday"
    ruler.remove("ORG")
    ruler.remove("DATE")
    doc = ruler(nlp.make_doc("Duygu went to school"))
    assert len(doc.spans["ruler"]) == 1


def test_span_ruler_remove_all_patterns(nlp):
    ruler = SpanRuler(nlp)
    patterns = [
        {"label": "PERSON", "pattern": "Duygu"},
        {"label": "ORG", "pattern": "ACME"},
        {"label": "DATE", "pattern": "her birthday"},
    ]
    ruler.add_patterns(patterns)
    assert len(ruler.patterns) == 3
    ruler.remove("PERSON")
    assert len(ruler.patterns) == 2
    ruler.remove("ORG")
    assert len(ruler.patterns) == 1
    ruler.remove("DATE")
    assert len(ruler.patterns) == 0
    with pytest.warns(UserWarning):
        doc = ruler(nlp.make_doc("Duygu founded her company ACME on her birthday"))
        assert len(doc.spans["ruler"]) == 0


def test_span_ruler_remove_and_add(nlp):
    ruler = SpanRuler(nlp)
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
