# coding: utf8
from __future__ import unicode_literals

from spacy.language import Language
from spacy.pipeline.analysis import component, print_summary


def test_decorator_function():
    @component(name="test")
    def test_component(doc):
        """docstring"""
        return doc

    assert test_component.name == "test"
    assert test_component.__doc__ == "docstring"
    assert test_component("foo") == "foo"


def test_decorator_class():
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
    assert TestComponent.__doc__ == "docstring1"
    assert TestComponent.__call__.__doc__ == "docstring2"
    assert TestComponent.foo == "bar"
    assert hasattr(TestComponent, "custom")
    assert TestComponent.custom.__doc__ == "docstring3"
    test_component = TestComponent()
    assert test_component.__doc__ == "docstring1"
    assert test_component.__call__.__doc__ == "docstring2"
    assert test_component.foo == "bar"
    assert test_component("foo") == "foo"
    assert hasattr(test_component, "custom")
    assert test_component.custom.__doc__ == "docstring3"
    assert test_component.custom("bar") == "bar"


def test_decorator_assigns():
    @component(assigns=["token.tag"])
    def test_component1(doc):
        return doc

    @component(requires=["token.tag", "token.pos"], assigns=["token.lemma"])
    def test_component2(doc):
        return doc

    @component(requires=["token.lemma"], assigns=["token._.custom_lemma"])
    def test_component3(doc):
        return doc

    nlp = Language()
    nlp.add_pipe(test_component1)
    nlp.add_pipe(test_component2)
    nlp.add_pipe(test_component3)
    print_summary(nlp)
