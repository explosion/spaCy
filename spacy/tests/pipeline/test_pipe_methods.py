# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.language import Language


@pytest.fixture
def nlp():
    return Language()


def new_pipe(doc):
    return doc


def test_add_pipe_no_name(nlp):
    nlp.add_pipe(new_pipe)
    assert "new_pipe" in nlp.pipe_names


def test_add_pipe_duplicate_name(nlp):
    nlp.add_pipe(new_pipe, name="duplicate_name")
    with pytest.raises(ValueError):
        nlp.add_pipe(new_pipe, name="duplicate_name")


@pytest.mark.parametrize("name", ["parser"])
def test_add_pipe_first(nlp, name):
    nlp.add_pipe(new_pipe, name=name, first=True)
    assert nlp.pipeline[0][0] == name


@pytest.mark.parametrize("name1,name2", [("parser", "lambda_pipe")])
def test_add_pipe_last(nlp, name1, name2):
    nlp.add_pipe(lambda doc: doc, name=name2)
    nlp.add_pipe(new_pipe, name=name1, last=True)
    assert nlp.pipeline[0][0] != name1
    assert nlp.pipeline[-1][0] == name1


def test_cant_add_pipe_first_and_last(nlp):
    with pytest.raises(ValueError):
        nlp.add_pipe(new_pipe, first=True, last=True)


@pytest.mark.parametrize("name", ["my_component"])
def test_get_pipe(nlp, name):
    with pytest.raises(KeyError):
        nlp.get_pipe(name)
    nlp.add_pipe(new_pipe, name=name)
    assert nlp.get_pipe(name) == new_pipe


@pytest.mark.parametrize("name,replacement,not_callable", [("my_component", lambda doc: doc, {})])
def test_replace_pipe(nlp, name, replacement, not_callable):
    with pytest.raises(ValueError):
        nlp.replace_pipe(name, new_pipe)
    nlp.add_pipe(new_pipe, name=name)
    with pytest.raises(ValueError):
        nlp.replace_pipe(name, not_callable)
    nlp.replace_pipe(name, replacement)
    assert nlp.get_pipe(name) != new_pipe
    assert nlp.get_pipe(name) == replacement


@pytest.mark.parametrize("old_name,new_name", [("old_pipe", "new_pipe")])
def test_rename_pipe(nlp, old_name, new_name):
    with pytest.raises(ValueError):
        nlp.rename_pipe(old_name, new_name)
    nlp.add_pipe(new_pipe, name=old_name)
    nlp.rename_pipe(old_name, new_name)
    assert nlp.pipeline[0][0] == new_name


@pytest.mark.parametrize("name", ["my_component"])
def test_remove_pipe(nlp, name):
    with pytest.raises(ValueError):
        nlp.remove_pipe(name)
    nlp.add_pipe(new_pipe, name=name)
    assert len(nlp.pipeline) == 1
    removed_name, removed_component = nlp.remove_pipe(name)
    assert not len(nlp.pipeline)
    assert removed_name == name
    assert removed_component == new_pipe


@pytest.mark.parametrize("name", ["my_component"])
def test_disable_pipes_method(nlp, name):
    nlp.add_pipe(new_pipe, name=name)
    assert nlp.has_pipe(name)
    disabled = nlp.disable_pipes(name)
    assert not nlp.has_pipe(name)
    disabled.restore()


@pytest.mark.parametrize("name", ["my_component"])
def test_disable_pipes_context(nlp, name):
    nlp.add_pipe(new_pipe, name=name)
    assert nlp.has_pipe(name)
    with nlp.disable_pipes(name):
        assert not nlp.has_pipe(name)
    assert nlp.has_pipe(name)


@pytest.mark.parametrize("n_pipes", [100])
def test_add_lots_of_pipes(nlp, n_pipes):
    for i in range(n_pipes):
        nlp.add_pipe(lambda doc: doc, name="pipe_%d" % i)
    assert len(nlp.pipe_names) == n_pipes


@pytest.mark.parametrize("component", ["ner", {"hello": "world"}])
def test_raise_for_invalid_components(nlp, component):
    with pytest.raises(ValueError):
        nlp.add_pipe(component)


@pytest.mark.parametrize("component", ["ner", "tagger", "parser", "textcat"])
def test_pipe_base_class_add_label(nlp, component):
    label = "TEST"
    pipe = nlp.create_pipe(component)
    pipe.add_label(label)
    if component == "tagger":
        # Tagger always has the default coarse-grained label scheme
        assert label in pipe.labels
    else:
        assert pipe.labels == (label,)
