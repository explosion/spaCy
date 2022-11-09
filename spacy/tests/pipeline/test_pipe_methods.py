import gc

import numpy
import pytest
from thinc.api import get_current_ops

import spacy
from spacy.lang.en import English
from spacy.lang.en.syntax_iterators import noun_chunks
from spacy.language import Language
from spacy.pipeline import TrainablePipe
from spacy.tokens import Doc
from spacy.training import Example
from spacy.util import SimpleFrozenList, get_arg_names, make_tempdir
from spacy.vocab import Vocab


@pytest.fixture
def nlp():
    return Language()


@Language.component("new_pipe")
def new_pipe(doc):
    return doc


@Language.component("other_pipe")
def other_pipe(doc):
    return doc


@pytest.mark.issue(1506)
def test_issue1506():
    def string_generator():
        for _ in range(10001):
            yield "It's sentence produced by that bug."
        for _ in range(10001):
            yield "I erase some hbdsaj lemmas."
        for _ in range(10001):
            yield "I erase lemmas."
        for _ in range(10001):
            yield "It's sentence produced by that bug."
        for _ in range(10001):
            yield "It's sentence produced by that bug."

    nlp = English()
    for i, d in enumerate(nlp.pipe(string_generator())):
        # We should run cleanup more than one time to actually cleanup data.
        # In first run — clean up only mark strings as «not hitted».
        if i == 10000 or i == 20000 or i == 30000:
            gc.collect()
        for t in d:
            str(t.lemma_)


@pytest.mark.issue(1654)
def test_issue1654():
    nlp = Language(Vocab())
    assert not nlp.pipeline

    @Language.component("component")
    def component(doc):
        return doc

    nlp.add_pipe("component", name="1")
    nlp.add_pipe("component", name="2", after="1")
    nlp.add_pipe("component", name="3", after="2")
    assert nlp.pipe_names == ["1", "2", "3"]
    nlp2 = Language(Vocab())
    assert not nlp2.pipeline
    nlp2.add_pipe("component", name="3")
    nlp2.add_pipe("component", name="2", before="3")
    nlp2.add_pipe("component", name="1", before="2")
    assert nlp2.pipe_names == ["1", "2", "3"]


@pytest.mark.issue(3880)
def test_issue3880():
    """Test that `nlp.pipe()` works when an empty string ends the batch.

    Fixed in v7.0.5 of Thinc.
    """
    texts = ["hello", "world", "", ""]
    nlp = English()
    nlp.add_pipe("parser").add_label("dep")
    nlp.add_pipe("ner").add_label("PERSON")
    nlp.add_pipe("tagger").add_label("NN")
    nlp.initialize()
    for doc in nlp.pipe(texts):
        pass


@pytest.mark.issue(5082)
def test_issue5082():
    # Ensure the 'merge_entities' pipeline does something sensible for the vectors of the merged tokens
    nlp = English()
    vocab = nlp.vocab
    array1 = numpy.asarray([0.1, 0.5, 0.8], dtype=numpy.float32)
    array2 = numpy.asarray([-0.2, -0.6, -0.9], dtype=numpy.float32)
    array3 = numpy.asarray([0.3, -0.1, 0.7], dtype=numpy.float32)
    array4 = numpy.asarray([0.5, 0, 0.3], dtype=numpy.float32)
    array34 = numpy.asarray([0.4, -0.05, 0.5], dtype=numpy.float32)
    vocab.set_vector("I", array1)
    vocab.set_vector("like", array2)
    vocab.set_vector("David", array3)
    vocab.set_vector("Bowie", array4)
    text = "I like David Bowie"
    patterns = [
        {"label": "PERSON", "pattern": [{"LOWER": "david"}, {"LOWER": "bowie"}]}
    ]
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(patterns)
    parsed_vectors_1 = [t.vector for t in nlp(text)]
    assert len(parsed_vectors_1) == 4
    ops = get_current_ops()
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_1[0]), array1)
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_1[1]), array2)
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_1[2]), array3)
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_1[3]), array4)
    nlp.add_pipe("merge_entities")
    parsed_vectors_2 = [t.vector for t in nlp(text)]
    assert len(parsed_vectors_2) == 3
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_2[0]), array1)
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_2[1]), array2)
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_2[2]), array34)


@pytest.mark.issue(5458)
def test_issue5458():
    # Test that the noun chuncker does not generate overlapping spans
    # fmt: off
    words = ["In", "an", "era", "where", "markets", "have", "brought", "prosperity", "and", "empowerment", "."]
    vocab = Vocab(strings=words)
    deps = ["ROOT", "det", "pobj", "advmod", "nsubj", "aux", "relcl", "dobj", "cc", "conj", "punct"]
    pos = ["ADP", "DET", "NOUN", "ADV", "NOUN", "AUX", "VERB", "NOUN", "CCONJ", "NOUN", "PUNCT"]
    heads = [0, 2, 0, 9, 6, 6, 2, 6, 7, 7, 0]
    # fmt: on
    en_doc = Doc(vocab, words=words, pos=pos, heads=heads, deps=deps)
    en_doc.noun_chunks_iterator = noun_chunks

    # if there are overlapping spans, this will fail with an E102 error "Can't merge non-disjoint spans"
    nlp = English()
    merge_nps = nlp.create_pipe("merge_noun_chunks")
    merge_nps(en_doc)


def test_multiple_predictions():
    class DummyPipe(TrainablePipe):
        def __init__(self):
            self.model = "dummy_model"

        def predict(self, docs):
            return ([1, 2, 3], [4, 5, 6])

        def set_annotations(self, docs, scores):
            return docs

    nlp = Language()
    doc = nlp.make_doc("foo")
    dummy_pipe = DummyPipe()
    dummy_pipe(doc)


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


@pytest.mark.issue(11443)
def test_enable_disable_conflict_with_config():
    """Test conflict between enable/disable w.r.t. `nlp.disabled` set in the config."""
    nlp = English()
    nlp.add_pipe("tagger")
    nlp.add_pipe("senter")
    nlp.add_pipe("sentencizer")

    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        # Expected to succeed, as config and arguments do not conflict.
        assert spacy.load(
            tmp_dir, enable=["tagger"], config={"nlp": {"disabled": ["senter"]}}
        ).disabled == ["senter", "sentencizer"]
        # Expected to succeed without warning due to the lack of a conflicting config option.
        spacy.load(tmp_dir, enable=["tagger"])
        # Expected to fail due to conflict between enable and disabled.
        with pytest.raises(ValueError):
            spacy.load(
                tmp_dir,
                enable=["senter"],
                config={"nlp": {"disabled": ["senter", "tagger"]}},
            )


def test_load_disable_enable():
    """Tests spacy.load() with dis-/enabling components."""

    base_nlp = English()
    for pipe in ("sentencizer", "tagger", "parser"):
        base_nlp.add_pipe(pipe)

    with make_tempdir() as tmp_dir:
        base_nlp.to_disk(tmp_dir)
        to_disable = ["parser", "tagger"]
        to_enable = ["tagger", "parser"]
        single_str = "tagger"

        # Setting only `disable`.
        nlp = spacy.load(tmp_dir, disable=to_disable)
        assert all([comp_name in nlp.disabled for comp_name in to_disable])

        # Setting only `enable`.
        nlp = spacy.load(tmp_dir, enable=to_enable)
        assert all(
            [
                (comp_name in nlp.disabled) is (comp_name not in to_enable)
                for comp_name in nlp.component_names
            ]
        )

        # Loading with a string representing one component
        nlp = spacy.load(tmp_dir, exclude=single_str)
        assert single_str not in nlp.component_names

        nlp = spacy.load(tmp_dir, disable=single_str)
        assert single_str in nlp.component_names
        assert single_str not in nlp.pipe_names
        assert nlp._disabled == {single_str}
        assert nlp.disabled == [single_str]

        # Testing consistent enable/disable combination.
        nlp = spacy.load(
            tmp_dir,
            enable=to_enable,
            disable=[
                comp_name
                for comp_name in nlp.component_names
                if comp_name not in to_enable
            ],
        )
        assert all(
            [
                (comp_name in nlp.disabled) is (comp_name not in to_enable)
                for comp_name in nlp.component_names
            ]
        )

        # Inconsistent enable/disable combination.
        with pytest.raises(ValueError):
            spacy.load(tmp_dir, enable=to_enable, disable=["parser"])
