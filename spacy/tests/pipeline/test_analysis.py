# coding: utf8
from __future__ import unicode_literals

import spacy.language
from spacy.language import Language, component
from spacy.analysis import print_summary, validate_attrs
from spacy.analysis import get_assigns_for_attr, get_requires_for_attr
from spacy.compat import is_python2
from mock import Mock, ANY
import pytest


def test_component_decorator_function():
    @component(name="test")
    def test_component(doc):
        """docstring"""
        return doc

    assert test_component.name == "test"
    if not is_python2:
        assert test_component.__doc__ == "docstring"
    assert test_component("foo") == "foo"


def test_component_decorator_class():
    @component(name="test")
    class TestComponent(object):
        """docstring1"""

        foo = "bar"

        def __call__(self, doc):
            """docstring2"""
            return doc

        def custom(self, x):
            """docstring3"""
            return x

    assert TestComponent.name == "test"
    assert TestComponent.foo == "bar"
    assert hasattr(TestComponent, "custom")
    test_component = TestComponent()
    assert test_component.foo == "bar"
    assert test_component("foo") == "foo"
    assert hasattr(test_component, "custom")
    assert test_component.custom("bar") == "bar"
    if not is_python2:
        assert TestComponent.__doc__ == "docstring1"
        assert TestComponent.__call__.__doc__ == "docstring2"
        assert TestComponent.custom.__doc__ == "docstring3"
        assert test_component.__doc__ == "docstring1"
        assert test_component.__call__.__doc__ == "docstring2"
        assert test_component.custom.__doc__ == "docstring3"


def test_component_decorator_assigns():
    spacy.language.ENABLE_PIPELINE_ANALYSIS = True

    @component("c1", assigns=["token.tag", "doc.tensor"])
    def test_component1(doc):
        return doc

    @component(
        "c2", requires=["token.tag", "token.pos"], assigns=["token.lemma", "doc.tensor"]
    )
    def test_component2(doc):
        return doc

    @component("c3", requires=["token.lemma"], assigns=["token._.custom_lemma"])
    def test_component3(doc):
        return doc

    assert "c1" in Language.factories
    assert "c2" in Language.factories
    assert "c3" in Language.factories

    nlp = Language()
    nlp.add_pipe(test_component1)
    with pytest.warns(UserWarning):
        nlp.add_pipe(test_component2)
    nlp.add_pipe(test_component3)
    assigns_tensor = get_assigns_for_attr(nlp.pipeline, "doc.tensor")
    assert [name for name, _ in assigns_tensor] == ["c1", "c2"]
    test_component4 = nlp.create_pipe("c1")
    assert test_component4.name == "c1"
    assert test_component4.factory == "c1"
    nlp.add_pipe(test_component4, name="c4")
    assert nlp.pipe_names == ["c1", "c2", "c3", "c4"]
    assert "c4" not in Language.factories
    assert nlp.pipe_factories["c1"] == "c1"
    assert nlp.pipe_factories["c4"] == "c1"
    assigns_tensor = get_assigns_for_attr(nlp.pipeline, "doc.tensor")
    assert [name for name, _ in assigns_tensor] == ["c1", "c2", "c4"]
    requires_pos = get_requires_for_attr(nlp.pipeline, "token.pos")
    assert [name for name, _ in requires_pos] == ["c2"]
    assert print_summary(nlp, no_print=True)
    assert nlp("hello world")


def test_component_factories_from_nlp():
    """Test that class components can implement a from_nlp classmethod that
    gives them access to the nlp object and config via the factory."""

    class TestComponent5(object):
        def __call__(self, doc):
            return doc

    mock = Mock()
    mock.return_value = TestComponent5()
    TestComponent5.from_nlp = classmethod(mock)
    TestComponent5 = component("c5")(TestComponent5)

    assert "c5" in Language.factories
    nlp = Language()
    pipe = nlp.create_pipe("c5", config={"foo": "bar"})
    nlp.add_pipe(pipe)
    assert nlp("hello world")
    # The first argument here is the class itself, so we're accepting any here
    mock.assert_called_once_with(ANY, nlp, foo="bar")


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
    spacy.language.ENABLE_PIPELINE_ANALYSIS = True

    @component("c1", assigns=["token.tag"])
    def c1(doc):
        return doc

    @component("c2", requires=["token.pos"])
    def c2(doc):
        return doc

    nlp = Language()
    nlp.add_pipe(c1)
    with pytest.warns(UserWarning):
        nlp.add_pipe(c2)
    with pytest.warns(None) as record:
        nlp.remove_pipe("c2")
    assert not record.list
