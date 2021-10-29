import pytest
from spacy.language import Language
from spacy.pipeline import TrainablePipe
from spacy.training import Example
from spacy.util import SimpleFrozenList, get_arg_names
from spacy.lang.en import English


@pytest.fixture
def nlp():
    return Language()


@Language.component("new_pipe")
def new_pipe(doc):
    return doc


@Language.component("other_pipe")
def other_pipe(doc):
    return doc


def test_add_pipe_no_name(nlp):
    nlp.add_pipe("new_pipe")
    assert "new_pipe" in nlp.pipe_names


def test_add_pipe_duplicate_name(nlp):
    nlp.add_pipe("new_pipe", name="duplicate_name")
    with pytest.raises(ValueError):
        nlp.add_pipe("new_pipe", name="duplicate_name")


@pytest.mark.parametrize("name", ["parser"])
def test_add_pipe_first(nlp, name):
    nlp.add_pipe("new_pipe", name=name, first=True)
    assert nlp.pipeline[0][0] == name


@pytest.mark.parametrize("name1,name2", [("parser", "lambda_pipe")])
def test_add_pipe_last(nlp, name1, name2):
    Language.component("new_pipe2", func=lambda doc: doc)
    nlp.add_pipe("new_pipe2", name=name2)
    nlp.add_pipe("new_pipe", name=name1, last=True)
    assert nlp.pipeline[0][0] != name1
    assert nlp.pipeline[-1][0] == name1


def test_cant_add_pipe_first_and_last(nlp):
    with pytest.raises(ValueError):
        nlp.add_pipe("new_pipe", first=True, last=True)


@pytest.mark.parametrize("name", ["test_get_pipe"])
def test_get_pipe(nlp, name):
    with pytest.raises(KeyError):
        nlp.get_pipe(name)
    nlp.add_pipe("new_pipe", name=name)
    assert nlp.get_pipe(name) == new_pipe


@pytest.mark.parametrize(
    "name,replacement,invalid_replacement",
    [("test_replace_pipe", "other_pipe", lambda doc: doc)],
)
def test_replace_pipe(nlp, name, replacement, invalid_replacement):
    with pytest.raises(ValueError):
        nlp.replace_pipe(name, new_pipe)
    nlp.add_pipe("new_pipe", name=name)
    with pytest.raises(ValueError):
        nlp.replace_pipe(name, invalid_replacement)
    nlp.replace_pipe(name, replacement)
    assert nlp.get_pipe(name) == nlp.create_pipe(replacement)


def test_replace_last_pipe(nlp):
    nlp.add_pipe("sentencizer")
    nlp.add_pipe("ner")
    assert nlp.pipe_names == ["sentencizer", "ner"]
    nlp.replace_pipe("ner", "ner")
    assert nlp.pipe_names == ["sentencizer", "ner"]


def test_replace_pipe_config(nlp):
    nlp.add_pipe("entity_linker")
    nlp.add_pipe("sentencizer")
    assert nlp.get_pipe("entity_linker").incl_prior is True
    nlp.replace_pipe("entity_linker", "entity_linker", config={"incl_prior": False})
    assert nlp.get_pipe("entity_linker").incl_prior is False


@pytest.mark.parametrize("old_name,new_name", [("old_pipe", "new_pipe")])
def test_rename_pipe(nlp, old_name, new_name):
    with pytest.raises(ValueError):
        nlp.rename_pipe(old_name, new_name)
    nlp.add_pipe("new_pipe", name=old_name)
    nlp.rename_pipe(old_name, new_name)
    assert nlp.pipeline[0][0] == new_name


@pytest.mark.parametrize("name", ["my_component"])
def test_remove_pipe(nlp, name):
    with pytest.raises(ValueError):
        nlp.remove_pipe(name)
    nlp.add_pipe("new_pipe", name=name)
    assert len(nlp.pipeline) == 1
    removed_name, removed_component = nlp.remove_pipe(name)
    assert not len(nlp.pipeline)
    assert removed_name == name
    assert removed_component == new_pipe


@pytest.mark.parametrize("name", ["my_component"])
def test_disable_pipes_method(nlp, name):
    nlp.add_pipe("new_pipe", name=name)
    assert nlp.has_pipe(name)
    disabled = nlp.select_pipes(disable=name)
    assert not nlp.has_pipe(name)
    disabled.restore()


@pytest.mark.parametrize("name", ["my_component"])
def test_enable_pipes_method(nlp, name):
    nlp.add_pipe("new_pipe", name=name)
    assert nlp.has_pipe(name)
    disabled = nlp.select_pipes(enable=[])
    assert not nlp.has_pipe(name)
    disabled.restore()


@pytest.mark.parametrize("name", ["my_component"])
def test_disable_pipes_context(nlp, name):
    """Test that an enabled component stays enabled after running the context manager."""
    nlp.add_pipe("new_pipe", name=name)
    assert nlp.has_pipe(name)
    with nlp.select_pipes(disable=name):
        assert not nlp.has_pipe(name)
    assert nlp.has_pipe(name)


@pytest.mark.parametrize("name", ["my_component"])
def test_disable_pipes_context_restore(nlp, name):
    """Test that a disabled component stays disabled after running the context manager."""
    nlp.add_pipe("new_pipe", name=name)
    assert nlp.has_pipe(name)
    nlp.disable_pipe(name)
    assert not nlp.has_pipe(name)
    with nlp.select_pipes(disable=name):
        assert not nlp.has_pipe(name)
    assert not nlp.has_pipe(name)


def test_select_pipes_list_arg(nlp):
    for name in ["c1", "c2", "c3"]:
        nlp.add_pipe("new_pipe", name=name)
        assert nlp.has_pipe(name)
    with nlp.select_pipes(disable=["c1", "c2"]):
        assert not nlp.has_pipe("c1")
        assert not nlp.has_pipe("c2")
        assert nlp.has_pipe("c3")
    with nlp.select_pipes(enable="c3"):
        assert not nlp.has_pipe("c1")
        assert not nlp.has_pipe("c2")
        assert nlp.has_pipe("c3")
    with nlp.select_pipes(enable=["c1", "c2"], disable="c3"):
        assert nlp.has_pipe("c1")
        assert nlp.has_pipe("c2")
        assert not nlp.has_pipe("c3")
    with nlp.select_pipes(enable=[]):
        assert not nlp.has_pipe("c1")
        assert not nlp.has_pipe("c2")
        assert not nlp.has_pipe("c3")
    with nlp.select_pipes(enable=["c1", "c2", "c3"], disable=[]):
        assert nlp.has_pipe("c1")
        assert nlp.has_pipe("c2")
        assert nlp.has_pipe("c3")
    with nlp.select_pipes(disable=["c1", "c2", "c3"], enable=[]):
        assert not nlp.has_pipe("c1")
        assert not nlp.has_pipe("c2")
        assert not nlp.has_pipe("c3")


def test_select_pipes_errors(nlp):
    for name in ["c1", "c2", "c3"]:
        nlp.add_pipe("new_pipe", name=name)
        assert nlp.has_pipe(name)

    with pytest.raises(ValueError):
        nlp.select_pipes()

    with pytest.raises(ValueError):
        nlp.select_pipes(enable=["c1", "c2"], disable=["c1"])

    with pytest.raises(ValueError):
        nlp.select_pipes(enable=["c1", "c2"], disable=[])

    with pytest.raises(ValueError):
        nlp.select_pipes(enable=[], disable=["c3"])

    disabled = nlp.select_pipes(disable=["c2"])
    nlp.remove_pipe("c2")
    with pytest.raises(ValueError):
        disabled.restore()


@pytest.mark.parametrize("n_pipes", [100])
def test_add_lots_of_pipes(nlp, n_pipes):
    Language.component("n_pipes", func=lambda doc: doc)
    for i in range(n_pipes):
        nlp.add_pipe("n_pipes", name=f"pipe_{i}")
    assert len(nlp.pipe_names) == n_pipes


@pytest.mark.parametrize("component", [lambda doc: doc, {"hello": "world"}])
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


def test_pipe_labels(nlp):
    input_labels = {
        "ner": ["PERSON", "ORG", "GPE"],
        "textcat": ["POSITIVE", "NEGATIVE"],
    }
    for name, labels in input_labels.items():
        nlp.add_pipe(name)
        pipe = nlp.get_pipe(name)
        for label in labels:
            pipe.add_label(label)
        assert len(pipe.labels) == len(labels)

    assert len(nlp.pipe_labels) == len(input_labels)
    for name, labels in nlp.pipe_labels.items():
        assert sorted(input_labels[name]) == sorted(labels)


def test_add_pipe_before_after():
    """Test that before/after works with strings and ints."""
    nlp = Language()
    nlp.add_pipe("ner")
    with pytest.raises(ValueError):
        nlp.add_pipe("textcat", before="parser")
    nlp.add_pipe("textcat", before="ner")
    assert nlp.pipe_names == ["textcat", "ner"]
    with pytest.raises(ValueError):
        nlp.add_pipe("parser", before=3)
    with pytest.raises(ValueError):
        nlp.add_pipe("parser", after=3)
    nlp.add_pipe("parser", after=0)
    assert nlp.pipe_names == ["textcat", "parser", "ner"]
    nlp.add_pipe("tagger", before=2)
    assert nlp.pipe_names == ["textcat", "parser", "tagger", "ner"]
    with pytest.raises(ValueError):
        nlp.add_pipe("entity_ruler", after=1, first=True)
    with pytest.raises(ValueError):
        nlp.add_pipe("entity_ruler", before="ner", after=2)
    with pytest.raises(ValueError):
        nlp.add_pipe("entity_ruler", before=True)
    with pytest.raises(ValueError):
        nlp.add_pipe("entity_ruler", first=False)


def test_disable_enable_pipes():
    name = "test_disable_enable_pipes"
    results = {}

    def make_component(name):
        results[name] = ""

        def component(doc):
            nonlocal results
            results[name] = doc.text
            return doc

        return component

    c1 = Language.component(f"{name}1", func=make_component(f"{name}1"))
    c2 = Language.component(f"{name}2", func=make_component(f"{name}2"))

    nlp = Language()
    nlp.add_pipe(f"{name}1")
    nlp.add_pipe(f"{name}2")
    assert results[f"{name}1"] == ""
    assert results[f"{name}2"] == ""
    assert nlp.pipeline == [(f"{name}1", c1), (f"{name}2", c2)]
    assert nlp.pipe_names == [f"{name}1", f"{name}2"]
    nlp.disable_pipe(f"{name}1")
    assert nlp.disabled == [f"{name}1"]
    assert nlp.component_names == [f"{name}1", f"{name}2"]
    assert nlp.pipe_names == [f"{name}2"]
    assert nlp.config["nlp"]["disabled"] == [f"{name}1"]
    nlp("hello")
    assert results[f"{name}1"] == ""  # didn't run
    assert results[f"{name}2"] == "hello"  # ran
    nlp.enable_pipe(f"{name}1")
    assert nlp.disabled == []
    assert nlp.pipe_names == [f"{name}1", f"{name}2"]
    assert nlp.config["nlp"]["disabled"] == []
    nlp("world")
    assert results[f"{name}1"] == "world"
    assert results[f"{name}2"] == "world"
    nlp.disable_pipe(f"{name}2")
    nlp.remove_pipe(f"{name}2")
    assert nlp.components == [(f"{name}1", c1)]
    assert nlp.pipeline == [(f"{name}1", c1)]
    assert nlp.component_names == [f"{name}1"]
    assert nlp.pipe_names == [f"{name}1"]
    assert nlp.disabled == []
    assert nlp.config["nlp"]["disabled"] == []
    nlp.rename_pipe(f"{name}1", name)
    assert nlp.components == [(name, c1)]
    assert nlp.component_names == [name]
    nlp("!")
    assert results[f"{name}1"] == "!"
    assert results[f"{name}2"] == "world"
    with pytest.raises(ValueError):
        nlp.disable_pipe(f"{name}2")
    nlp.disable_pipe(name)
    assert nlp.component_names == [name]
    assert nlp.pipe_names == []
    assert nlp.config["nlp"]["disabled"] == [name]
    nlp("?")
    assert results[f"{name}1"] == "!"


def test_pipe_methods_frozen():
    """Test that spaCy raises custom error messages if "frozen" properties are
    accessed. We still want to use a list here to not break backwards
    compatibility, but users should see an error if they're trying to append
    to nlp.pipeline etc."""
    nlp = Language()
    ner = nlp.add_pipe("ner")
    assert nlp.pipe_names == ["ner"]
    for prop in [
        nlp.pipeline,
        nlp.pipe_names,
        nlp.components,
        nlp.component_names,
        nlp.disabled,
        nlp.factory_names,
    ]:
        assert isinstance(prop, list)
        assert isinstance(prop, SimpleFrozenList)
    with pytest.raises(NotImplementedError):
        nlp.pipeline.append(("ner2", ner))
    with pytest.raises(NotImplementedError):
        nlp.pipe_names.pop()
    with pytest.raises(NotImplementedError):
        nlp.components.sort()
    with pytest.raises(NotImplementedError):
        nlp.component_names.clear()


@pytest.mark.parametrize(
    "pipe", ["tagger", "parser", "ner", "textcat", "morphologizer"]
)
def test_pipe_label_data_exports_labels(pipe):
    nlp = Language()
    pipe = nlp.add_pipe(pipe)
    # Make sure pipe has pipe labels
    assert getattr(pipe, "label_data", None) is not None
    # Make sure pipe can be initialized with labels
    initialize = getattr(pipe, "initialize", None)
    assert initialize is not None
    assert "labels" in get_arg_names(initialize)


@pytest.mark.parametrize("pipe", ["senter", "entity_linker"])
def test_pipe_label_data_no_labels(pipe):
    nlp = Language()
    pipe = nlp.add_pipe(pipe)
    assert getattr(pipe, "label_data", None) is None
    initialize = getattr(pipe, "initialize", None)
    if initialize is not None:
        assert "labels" not in get_arg_names(initialize)


def test_warning_pipe_begin_training():
    with pytest.warns(UserWarning, match="begin_training"):

        class IncompatPipe(TrainablePipe):
            def __init__(self):
                ...

            def begin_training(*args, **kwargs):
                ...


def test_pipe_methods_initialize():
    """Test that the [initialize] config reflects the components correctly."""
    nlp = Language()
    nlp.add_pipe("tagger")
    assert "tagger" not in nlp.config["initialize"]["components"]
    nlp.config["initialize"]["components"]["tagger"] = {"labels": ["hello"]}
    assert nlp.config["initialize"]["components"]["tagger"] == {"labels": ["hello"]}
    nlp.remove_pipe("tagger")
    assert "tagger" not in nlp.config["initialize"]["components"]
    nlp.add_pipe("tagger")
    assert "tagger" not in nlp.config["initialize"]["components"]
    nlp.config["initialize"]["components"]["tagger"] = {"labels": ["hello"]}
    nlp.rename_pipe("tagger", "my_tagger")
    assert "tagger" not in nlp.config["initialize"]["components"]
    assert nlp.config["initialize"]["components"]["my_tagger"] == {"labels": ["hello"]}
    nlp.config["initialize"]["components"]["test"] = {"foo": "bar"}
    nlp.add_pipe("ner", name="test")
    assert "test" in nlp.config["initialize"]["components"]
    nlp.remove_pipe("test")
    assert "test" not in nlp.config["initialize"]["components"]


def test_update_with_annotates():
    name = "test_with_annotates"
    results = {}

    def make_component(name):
        results[name] = ""

        def component(doc):
            nonlocal results
            results[name] += doc.text
            return doc

        return component

    Language.component(f"{name}1", func=make_component(f"{name}1"))
    Language.component(f"{name}2", func=make_component(f"{name}2"))

    components = set([f"{name}1", f"{name}2"])

    nlp = English()
    texts = ["a", "bb", "ccc"]
    examples = []
    for text in texts:
        examples.append(Example(nlp.make_doc(text), nlp.make_doc(text)))

    for components_to_annotate in [
        [],
        [f"{name}1"],
        [f"{name}1", f"{name}2"],
        [f"{name}2", f"{name}1"],
    ]:
        for key in results:
            results[key] = ""
        nlp = English(vocab=nlp.vocab)
        nlp.add_pipe(f"{name}1")
        nlp.add_pipe(f"{name}2")
        nlp.update(examples, annotates=components_to_annotate)
        for component in components_to_annotate:
            assert results[component] == "".join(eg.predicted.text for eg in examples)
        for component in components - set(components_to_annotate):
            assert results[component] == ""
