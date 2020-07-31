from spacy.language import Language
from spacy.pipe_analysis import get_assigns_for_attr, get_requires_for_attr
from spacy.pipe_analysis import validate_attrs, count_pipeline_interdependencies
from mock import Mock
import pytest


def test_component_decorator_assigns():
    @Language.component("c1", assigns=["token.tag", "doc.tensor"])
    def test_component1(doc):
        return doc

    @Language.component(
        "c2", requires=["token.tag", "token.pos"], assigns=["token.lemma", "doc.tensor"]
    )
    def test_component2(doc):
        return doc

    @Language.component(
        "c3", requires=["token.lemma"], assigns=["token._.custom_lemma"]
    )
    def test_component3(doc):
        return doc

    assert Language.has_factory("c1")
    assert Language.has_factory("c2")
    assert Language.has_factory("c3")

    nlp = Language()
    nlp.add_pipe("c1")
    nlp.add_pipe("c2")
    problems = nlp.analyze_pipes(no_print=True)["problems"]
    assert problems["c2"] == ["token.pos"]
    nlp.add_pipe("c3")
    assert get_assigns_for_attr(nlp, "doc.tensor") == ["c1", "c2"]
    nlp.add_pipe("c1", name="c4")
    test_component4_meta = nlp.get_pipe_meta("c1")
    assert test_component4_meta.factory == "c1"
    assert nlp.pipe_names == ["c1", "c2", "c3", "c4"]
    assert not Language.has_factory("c4")
    assert nlp.pipe_factories["c1"] == "c1"
    assert nlp.pipe_factories["c4"] == "c1"
    assert get_assigns_for_attr(nlp, "doc.tensor") == ["c1", "c2", "c4"]
    assert get_requires_for_attr(nlp, "token.pos") == ["c2"]
    assert nlp("hello world")


def test_component_factories_class_func():
    """Test that class components can implement a from_nlp classmethod that
    gives them access to the nlp object and config via the factory."""

    class TestComponent5:
        def __call__(self, doc):
            return doc

    mock = Mock()
    mock.return_value = TestComponent5()

    def test_componen5_factory(nlp, foo: str = "bar", name="c5"):
        return mock(nlp, foo=foo)

    Language.factory("c5", func=test_componen5_factory)
    assert Language.has_factory("c5")
    nlp = Language()
    nlp.add_pipe("c5", config={"foo": "bar"})
    assert nlp("hello world")
    mock.assert_called_once_with(nlp, foo="bar")


def test_analysis_validate_attrs_valid():
    attrs = ["doc.sents", "doc.ents", "token.tag", "token._.xyz", "span._.xyz"]
    assert validate_attrs(attrs)
    for attr in attrs:
        assert validate_attrs([attr])
    with pytest.raises(ValueError):
        validate_attrs(["doc.sents", "doc.xyz"])


@pytest.mark.parametrize(
    "attr",
    [
        "doc",
        "doc_ents",
        "doc.xyz",
        "token.xyz",
        "token.tag_",
        "token.tag.xyz",
        "token._.xyz.abc",
        "span.label",
    ],
)
def test_analysis_validate_attrs_invalid(attr):
    with pytest.raises(ValueError):
        validate_attrs([attr])


def test_analysis_validate_attrs_remove_pipe():
    """Test that attributes are validated correctly on remove."""

    @Language.component("pipe_analysis_c6", assigns=["token.tag"])
    def c1(doc):
        return doc

    @Language.component("pipe_analysis_c7", requires=["token.pos"])
    def c2(doc):
        return doc

    nlp = Language()
    nlp.add_pipe("pipe_analysis_c6")
    nlp.add_pipe("pipe_analysis_c7")
    problems = nlp.analyze_pipes(no_print=True)["problems"]
    assert problems["pipe_analysis_c7"] == ["token.pos"]
    nlp.remove_pipe("pipe_analysis_c7")
    problems = nlp.analyze_pipes(no_print=True)["problems"]
    assert all(p == [] for p in problems.values())


def test_pipe_interdependencies():
    prefix = "test_pipe_interdependencies"

    @Language.component(f"{prefix}.fancifier", assigns=("doc._.fancy",))
    def fancifier(doc):
        return doc

    @Language.component(f"{prefix}.needer", requires=("doc._.fancy",))
    def needer(doc):
        return doc

    nlp = Language()
    nlp.add_pipe(f"{prefix}.fancifier")
    nlp.add_pipe(f"{prefix}.needer")
    counts = count_pipeline_interdependencies(nlp)
    assert counts == [1, 0]
