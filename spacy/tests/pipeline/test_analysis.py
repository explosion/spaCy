import spacy.language
from spacy.language import Language
from spacy.pipe_analysis import print_summary, validate_attrs
from spacy.pipe_analysis import get_assigns_for_attr, get_requires_for_attr
from spacy.pipe_analysis import count_pipeline_interdependencies
from mock import Mock
import pytest


@pytest.mark.xfail(reason="TODO: fix warnings")
def test_component_decorator_assigns():
    spacy.language.ENABLE_PIPELINE_ANALYSIS = True

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
    with pytest.warns(UserWarning):
        nlp.add_pipe("c2")
    nlp.add_pipe("c3")
    assigns_tensor = get_assigns_for_attr(nlp.pipeline, "doc.tensor")
    assert [name for name, _ in assigns_tensor] == ["c1", "c2"]
    test_component4 = nlp.create_pipe("c1")
    assert test_component4.name == "c1"
    assert test_component4.factory == "c1"
    nlp.add_pipe("c1", name="c4")
    assert nlp.pipe_names == ["c1", "c2", "c3", "c4"]
    assert not Language.has_factory("c4")
    assert nlp.pipe_factories["c1"] == "c1"
    assert nlp.pipe_factories["c4"] == "c1"
    assigns_tensor = get_assigns_for_attr(nlp.pipeline, "doc.tensor")
    assert [name for name, _ in assigns_tensor] == ["c1", "c2", "c4"]
    requires_pos = get_requires_for_attr(nlp.pipeline, "token.pos")
    assert [name for name, _ in requires_pos] == ["c2"]
    assert print_summary(nlp, no_print=True)
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


@pytest.mark.xfail(reason="TODO: fix warnings")
def test_analysis_validate_attrs_remove_pipe():
    """Test that attributes are validated correctly on remove."""
    spacy.language.ENABLE_PIPELINE_ANALYSIS = True

    @Language.component("c6", assigns=["token.tag"])
    def c1(doc):
        return doc

    @Language.component("c7", requires=["token.pos"])
    def c2(doc):
        return doc

    nlp = Language()
    nlp.add_pipe("c6")
    with pytest.warns(UserWarning):
        nlp.add_pipe("c7")
    with pytest.warns(None) as record:
        nlp.remove_pipe("c6")
    assert not record.list


def test_pipe_interdependencies():
    class Fancifier:
        name = "fancifier"
        assigns = ("doc._.fancy",)
        requires = tuple()

    class FancyNeeder:
        name = "needer"
        assigns = tuple()
        requires = ("doc._.fancy",)

    pipeline = [("fancifier", Fancifier()), ("needer", FancyNeeder())]
    counts = count_pipeline_interdependencies(pipeline)
    assert counts == [1, 0]
