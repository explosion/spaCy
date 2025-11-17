import pytest

try:
    from pydantic.v1 import StrictInt, StrictStr
except ImportError:
    from pydantic import StrictInt, StrictStr  # type: ignore

from thinc.api import ConfigValidationError, Linear, Model

import spacy
from spacy.lang.de import German
from spacy.lang.en import English
from spacy.language import Language
from spacy.pipeline.tok2vec import DEFAULT_TOK2VEC_MODEL
from spacy.tokens import Doc
from spacy.util import SimpleFrozenDict, combine_score_weights, registry

from ..util import make_tempdir


@pytest.mark.issue(5137)
def test_issue5137():
    factory_name = "test_issue5137"
    pipe_name = "my_component"

    @Language.factory(factory_name)
    class MyComponent:
        def __init__(self, nlp, name=pipe_name, categories="all_categories"):
            self.nlp = nlp
            self.categories = categories
            self.name = name

        def __call__(self, doc):
            pass

        def to_disk(self, path, **kwargs):
            pass

        def from_disk(self, path, **cfg):
            pass

    nlp = English()
    my_component = nlp.add_pipe(factory_name, name=pipe_name)
    assert my_component.categories == "all_categories"
    with make_tempdir() as tmpdir:
        nlp.to_disk(tmpdir)
        overrides = {"components": {pipe_name: {"categories": "my_categories"}}}
        nlp2 = spacy.load(tmpdir, config=overrides)
        assert nlp2.get_pipe(pipe_name).categories == "my_categories"


def test_pipe_function_component():
    name = "test_component"

    @Language.component(name)
    def component(doc: Doc) -> Doc:
        return doc

    assert name in registry.factories
    nlp = Language()
    with pytest.raises(ValueError):
        nlp.add_pipe(component)
    nlp.add_pipe(name)
    assert name in nlp.pipe_names
    assert nlp.pipe_factories[name] == name
    assert Language.get_factory_meta(name)
    assert nlp.get_pipe_meta(name)
    pipe = nlp.get_pipe(name)
    assert pipe == component
    pipe = nlp.create_pipe(name)
    assert pipe == component


def test_pipe_class_component_init():
    name1 = "test_class_component1"
    name2 = "test_class_component2"

    @Language.factory(name1)
    class Component1:
        def __init__(self, nlp: Language, name: str):
            self.nlp = nlp

        def __call__(self, doc: Doc) -> Doc:
            return doc

    class Component2:
        def __init__(self, nlp: Language, name: str):
            self.nlp = nlp

        def __call__(self, doc: Doc) -> Doc:
            return doc

    @Language.factory(name2)
    def factory(nlp: Language, name=name2):
        return Component2(nlp, name)

    nlp = Language()
    for name, Component in [(name1, Component1), (name2, Component2)]:
        assert name in registry.factories
        with pytest.raises(ValueError):
            nlp.add_pipe(Component(nlp, name))
        nlp.add_pipe(name)
        assert name in nlp.pipe_names
        assert nlp.pipe_factories[name] == name
        assert Language.get_factory_meta(name)
        assert nlp.get_pipe_meta(name)
        pipe = nlp.get_pipe(name)
        assert isinstance(pipe, Component)
        assert isinstance(pipe.nlp, Language)
        pipe = nlp.create_pipe(name)
        assert isinstance(pipe, Component)
        assert isinstance(pipe.nlp, Language)


def test_pipe_class_component_config():
    name = "test_class_component_config"

    @Language.factory(name)
    class Component:
        def __init__(
            self, nlp: Language, name: str, value1: StrictInt, value2: StrictStr
        ):
            self.nlp = nlp
            self.value1 = value1
            self.value2 = value2
            self.is_base = True
            self.name = name

        def __call__(self, doc: Doc) -> Doc:
            return doc

    @English.factory(name)
    class ComponentEN:
        def __init__(
            self, nlp: Language, name: str, value1: StrictInt, value2: StrictStr
        ):
            self.nlp = nlp
            self.value1 = value1
            self.value2 = value2
            self.is_base = False

        def __call__(self, doc: Doc) -> Doc:
            return doc

    nlp = Language()
    with pytest.raises(ConfigValidationError):  # no config provided
        nlp.add_pipe(name)
    with pytest.raises(ConfigValidationError):  # invalid config
        nlp.add_pipe(name, config={"value1": "10", "value2": "hello"})
    with pytest.warns(UserWarning):
        nlp.add_pipe(
            name, config={"value1": 10, "value2": "hello", "name": "wrong_name"}
        )
    pipe = nlp.get_pipe(name)
    assert isinstance(pipe.nlp, Language)
    assert pipe.value1 == 10
    assert pipe.value2 == "hello"
    assert pipe.is_base is True
    assert pipe.name == name

    nlp_en = English()
    with pytest.raises(ConfigValidationError):  # invalid config
        nlp_en.add_pipe(name, config={"value1": "10", "value2": "hello"})
    nlp_en.add_pipe(name, config={"value1": 10, "value2": "hello"})
    pipe = nlp_en.get_pipe(name)
    assert isinstance(pipe.nlp, English)
    assert pipe.value1 == 10
    assert pipe.value2 == "hello"
    assert pipe.is_base is False


def test_pipe_class_component_defaults():
    name = "test_class_component_defaults"

    @Language.factory(name)
    class Component:
        def __init__(
            self,
            nlp: Language,
            name: str,
            value1: StrictInt = StrictInt(10),
            value2: StrictStr = StrictStr("hello"),
        ):
            self.nlp = nlp
            self.value1 = value1
            self.value2 = value2

        def __call__(self, doc: Doc) -> Doc:
            return doc

    nlp = Language()
    nlp.add_pipe(name)
    pipe = nlp.get_pipe(name)
    assert isinstance(pipe.nlp, Language)
    assert pipe.value1 == 10
    assert pipe.value2 == "hello"


def test_pipe_class_component_model():
    name = "test_class_component_model"
    default_config = {
        "model": {
            "@architectures": "spacy.TextCatEnsemble.v2",
            "tok2vec": DEFAULT_TOK2VEC_MODEL,
            "linear_model": {
                "@architectures": "spacy.TextCatBOW.v3",
                "exclusive_classes": False,
                "ngram_size": 1,
                "no_output_layer": False,
            },
        },
        "value1": 10,
    }

    @Language.factory(name, default_config=default_config)
    class Component:
        def __init__(self, nlp: Language, model: Model, name: str, value1: StrictInt):
            self.nlp = nlp
            self.model = model
            self.value1 = value1
            self.name = name

        def __call__(self, doc: Doc) -> Doc:
            return doc

    nlp = Language()
    nlp.add_pipe(name)
    pipe = nlp.get_pipe(name)
    assert isinstance(pipe.nlp, Language)
    assert pipe.value1 == 10
    assert isinstance(pipe.model, Model)


def test_pipe_class_component_model_custom():
    name = "test_class_component_model_custom"
    arch = f"{name}.arch"
    default_config = {"value1": 1, "model": {"@architectures": arch, "nO": 0, "nI": 0}}

    @Language.factory(name, default_config=default_config)
    class Component:
        def __init__(
            self,
            nlp: Language,
            model: Model,
            name: str,
            value1: StrictInt = StrictInt(10),
        ):
            self.nlp = nlp
            self.model = model
            self.value1 = value1
            self.name = name

        def __call__(self, doc: Doc) -> Doc:
            return doc

    @registry.architectures(arch)
    def make_custom_arch(nO: StrictInt, nI: StrictInt):
        return Linear(nO, nI)

    nlp = Language()
    config = {"value1": 20, "model": {"@architectures": arch, "nO": 1, "nI": 2}}
    nlp.add_pipe(name, config=config)
    pipe = nlp.get_pipe(name)
    assert isinstance(pipe.nlp, Language)
    assert pipe.value1 == 20
    assert isinstance(pipe.model, Model)
    assert pipe.model.name == "linear"

    nlp = Language()
    with pytest.raises(ConfigValidationError):
        config = {"value1": "20", "model": {"@architectures": arch, "nO": 1, "nI": 2}}
        nlp.add_pipe(name, config=config)
    with pytest.raises(ConfigValidationError):
        config = {"value1": 20, "model": {"@architectures": arch, "nO": 1.0, "nI": 2.0}}
        nlp.add_pipe(name, config=config)


def test_pipe_factories_wrong_formats():
    with pytest.raises(ValueError):
        # Decorator is not called
        @Language.component
        def component(foo: int, bar: str): ...

    with pytest.raises(ValueError):
        # Decorator is not called
        @Language.factory
        def factory1(foo: int, bar: str): ...

    with pytest.raises(ValueError):
        # Factory function is missing "nlp" and "name" arguments
        @Language.factory("test_pipe_factories_missing_args")
        def factory2(foo: int, bar: str): ...


def test_pipe_factory_meta_config_cleanup():
    """Test that component-specific meta and config entries are represented
    correctly and cleaned up when pipes are removed, replaced or renamed."""
    nlp = Language()
    nlp.add_pipe("ner", name="ner_component")
    nlp.add_pipe("textcat")
    assert nlp.get_factory_meta("ner")
    assert nlp.get_pipe_meta("ner_component")
    assert nlp.get_pipe_config("ner_component")
    assert nlp.get_factory_meta("textcat")
    assert nlp.get_pipe_meta("textcat")
    assert nlp.get_pipe_config("textcat")
    nlp.rename_pipe("textcat", "tc")
    assert nlp.get_pipe_meta("tc")
    assert nlp.get_pipe_config("tc")
    with pytest.raises(ValueError):
        nlp.remove_pipe("ner")
    nlp.remove_pipe("ner_component")
    assert "ner_component" not in nlp._pipe_meta
    assert "ner_component" not in nlp._pipe_configs
    with pytest.raises(ValueError):
        nlp.replace_pipe("textcat", "parser")
    nlp.replace_pipe("tc", "parser")
    assert nlp.get_factory_meta("parser")
    assert nlp.get_pipe_meta("tc").factory == "parser"


def test_pipe_factories_empty_dict_default():
    """Test that default config values can be empty dicts and that no config
    validation error is raised."""
    # TODO: fix this
    name = "test_pipe_factories_empty_dict_default"

    @Language.factory(name, default_config={"foo": {}})
    def factory(nlp: Language, name: str, foo: dict): ...

    nlp = Language()
    nlp.create_pipe(name)


def test_pipe_factories_language_specific():
    """Test that language sub-classes can have their own factories, with
    fallbacks to the base factories."""
    name1 = "specific_component1"
    name2 = "specific_component2"
    Language.component(name1, func=lambda: "base")
    English.component(name1, func=lambda: "en")
    German.component(name2, func=lambda: "de")

    assert Language.has_factory(name1)
    assert not Language.has_factory(name2)
    assert English.has_factory(name1)
    assert not English.has_factory(name2)
    assert German.has_factory(name1)
    assert German.has_factory(name2)

    nlp = Language()
    assert nlp.create_pipe(name1)() == "base"
    with pytest.raises(ValueError):
        nlp.create_pipe(name2)
    nlp_en = English()
    assert nlp_en.create_pipe(name1)() == "en"
    with pytest.raises(ValueError):
        nlp_en.create_pipe(name2)
    nlp_de = German()
    assert nlp_de.create_pipe(name1)() == "base"
    assert nlp_de.create_pipe(name2)() == "de"


def test_language_factories_invalid():
    """Test that assigning directly to Language.factories is now invalid and
    raises a custom error."""
    assert isinstance(Language.factories, SimpleFrozenDict)
    with pytest.raises(NotImplementedError):
        Language.factories["foo"] = "bar"
    nlp = Language()
    assert isinstance(nlp.factories, SimpleFrozenDict)
    assert len(nlp.factories)
    with pytest.raises(NotImplementedError):
        nlp.factories["foo"] = "bar"


@pytest.mark.parametrize(
    "weights,override,expected",
    [
        ([{"a": 1.0}, {"b": 1.0}, {"c": 1.0}], {}, {"a": 0.33, "b": 0.33, "c": 0.33}),
        ([{"a": 1.0}, {"b": 50}, {"c": 100}], {}, {"a": 0.01, "b": 0.33, "c": 0.66}),
        (
            [{"a": 0.7, "b": 0.3}, {"c": 1.0}, {"d": 0.5, "e": 0.5}],
            {},
            {"a": 0.23, "b": 0.1, "c": 0.33, "d": 0.17, "e": 0.17},
        ),
        (
            [{"a": 100, "b": 300}, {"c": 50, "d": 50}],
            {},
            {"a": 0.2, "b": 0.6, "c": 0.1, "d": 0.1},
        ),
        ([{"a": 0.5, "b": 0.5}, {"b": 1.0}], {}, {"a": 0.33, "b": 0.67}),
        ([{"a": 0.5, "b": 0.0}], {}, {"a": 1.0, "b": 0.0}),
        ([{"a": 0.5, "b": 0.5}, {"b": 1.0}], {"a": 0.0}, {"a": 0.0, "b": 1.0}),
        ([{"a": 0.0, "b": 0.0}, {"c": 0.0}], {}, {"a": 0.0, "b": 0.0, "c": 0.0}),
        ([{"a": 0.0, "b": 0.0}, {"c": 1.0}], {}, {"a": 0.0, "b": 0.0, "c": 1.0}),
        (
            [{"a": 0.0, "b": 0.0}, {"c": 0.0}],
            {"c": 0.2},
            {"a": 0.0, "b": 0.0, "c": 1.0},
        ),
        (
            [{"a": 0.5, "b": 0.5, "c": 1.0, "d": 1.0}],
            {"a": 0.0, "b": 0.0},
            {"a": 0.0, "b": 0.0, "c": 0.5, "d": 0.5},
        ),
        (
            [{"a": 0.5, "b": 0.5, "c": 1.0, "d": 1.0}],
            {"a": 0.0, "b": 0.0, "f": 0.0},
            {"a": 0.0, "b": 0.0, "c": 0.5, "d": 0.5, "f": 0.0},
        ),
    ],
)
def test_language_factories_combine_score_weights(weights, override, expected):
    result = combine_score_weights(weights, override)
    assert sum(result.values()) in (0.99, 1.0, 0.0)
    assert result == expected


def test_language_factories_scores():
    name = "test_language_factories_scores"
    func = lambda nlp, name: lambda doc: doc
    weights1 = {"a1": 0.5, "a2": 0.5}
    weights2 = {"b1": 0.2, "b2": 0.7, "b3": 0.1}
    Language.factory(f"{name}1", default_score_weights=weights1, func=func)
    Language.factory(f"{name}2", default_score_weights=weights2, func=func)
    meta1 = Language.get_factory_meta(f"{name}1")
    assert meta1.default_score_weights == weights1
    meta2 = Language.get_factory_meta(f"{name}2")
    assert meta2.default_score_weights == weights2
    nlp = Language()
    nlp._config["training"]["score_weights"] = {}
    nlp.add_pipe(f"{name}1")
    nlp.add_pipe(f"{name}2")
    cfg = nlp.config["training"]
    expected_weights = {"a1": 0.25, "a2": 0.25, "b1": 0.1, "b2": 0.35, "b3": 0.05}
    assert cfg["score_weights"] == expected_weights
    # Test with custom defaults
    config = nlp.config.copy()
    config["training"]["score_weights"]["a1"] = 0.0
    config["training"]["score_weights"]["b3"] = 1.3
    nlp = English.from_config(config)
    score_weights = nlp.config["training"]["score_weights"]
    expected = {"a1": 0.0, "a2": 0.12, "b1": 0.05, "b2": 0.17, "b3": 0.65}
    assert score_weights == expected
    # Test with null values
    config = nlp.config.copy()
    config["training"]["score_weights"]["a1"] = None
    nlp = English.from_config(config)
    score_weights = nlp.config["training"]["score_weights"]
    expected = {"a1": None, "a2": 0.12, "b1": 0.05, "b2": 0.17, "b3": 0.66}
    assert score_weights == expected


def test_pipe_factories_from_source():
    """Test adding components from a source model."""
    source_nlp = English()
    source_nlp.add_pipe("tagger", name="my_tagger")
    nlp = English()
    with pytest.raises(ValueError):
        nlp.add_pipe("my_tagger", source="en_core_web_sm")
    nlp.add_pipe("my_tagger", source=source_nlp)
    assert "my_tagger" in nlp.pipe_names
    with pytest.raises(KeyError):
        nlp.add_pipe("custom", source=source_nlp)


def test_pipe_factories_from_source_language_subclass():
    class CustomEnglishDefaults(English.Defaults):
        stop_words = set(["custom", "stop"])

    @registry.languages("custom_en")
    class CustomEnglish(English):
        lang = "custom_en"
        Defaults = CustomEnglishDefaults

    source_nlp = English()
    source_nlp.add_pipe("tagger")

    # custom subclass
    nlp = CustomEnglish()
    nlp.add_pipe("tagger", source=source_nlp)
    assert "tagger" in nlp.pipe_names

    # non-subclass
    nlp = German()
    nlp.add_pipe("tagger", source=source_nlp)
    assert "tagger" in nlp.pipe_names

    # mismatched vectors
    nlp = English()
    nlp.vocab.vectors.resize((1, 4))
    nlp.vocab.vectors.add("cat", vector=[1, 2, 3, 4])
    with pytest.warns(UserWarning):
        nlp.add_pipe("tagger", source=source_nlp)


def test_pipe_factories_from_source_custom():
    """Test adding components from a source model with custom components."""
    name = "test_pipe_factories_from_source_custom"

    @Language.factory(name, default_config={"arg": "hello"})
    def test_factory(nlp, name, arg: str):
        return lambda doc: doc

    source_nlp = English()
    source_nlp.add_pipe("tagger")
    source_nlp.add_pipe(name, config={"arg": "world"})
    nlp = English()
    nlp.add_pipe(name, source=source_nlp)
    assert name in nlp.pipe_names
    assert nlp.get_pipe_meta(name).default_config["arg"] == "hello"
    config = nlp.config["components"][name]
    assert config["factory"] == name
    assert config["arg"] == "world"


def test_pipe_factories_from_source_config():
    name = "test_pipe_factories_from_source_config"

    @Language.factory(name, default_config={"arg": "hello"})
    def test_factory(nlp, name, arg: str):
        return lambda doc: doc

    source_nlp = English()
    source_nlp.add_pipe("tagger")
    source_nlp.add_pipe(name, name="yolo", config={"arg": "world"})
    dest_nlp_cfg = {"lang": "en", "pipeline": ["parser", "custom"]}
    with make_tempdir() as tempdir:
        source_nlp.to_disk(tempdir)
        dest_components_cfg = {
            "parser": {"factory": "parser"},
            "custom": {"source": str(tempdir), "component": "yolo"},
        }
        dest_config = {"nlp": dest_nlp_cfg, "components": dest_components_cfg}
        nlp = English.from_config(dest_config)
    assert nlp.pipe_names == ["parser", "custom"]
    assert nlp.pipe_factories == {"parser": "parser", "custom": name}
    meta = nlp.get_pipe_meta("custom")
    assert meta.factory == name
    assert meta.default_config["arg"] == "hello"
    config = nlp.config["components"]["custom"]
    assert config["factory"] == name
    assert config["arg"] == "world"


class PipeFactoriesIdempotent:
    def __init__(self, nlp, name): ...

    def __call__(self, doc): ...


@pytest.mark.parametrize(
    "i,func,func2",
    [
        (0, lambda nlp, name: lambda doc: doc, lambda doc: doc),
        (1, PipeFactoriesIdempotent, PipeFactoriesIdempotent(None, None)),
    ],
)
def test_pipe_factories_decorator_idempotent(i, func, func2):
    """Check that decorator can be run multiple times if the function is the
    same. This is especially relevant for live reloading because we don't
    want spaCy to raise an error if a module registering components is reloaded.
    """
    name = f"test_pipe_factories_decorator_idempotent_{i}"
    for i in range(5):
        Language.factory(name, func=func)
    nlp = Language()
    nlp.add_pipe(name)
    Language.factory(name, func=func)
    # Make sure it also works for component decorator, which creates the
    # factory function
    name2 = f"{name}2"
    for i in range(5):
        Language.component(name2, func=func2)
    nlp = Language()
    nlp.add_pipe(name)
    Language.component(name2, func=func2)


def test_pipe_factories_config_excludes_nlp():
    """Test that the extra values we temporarily add to component config
    blocks/functions are removed and not copied around.
    """
    name = "test_pipe_factories_config_excludes_nlp"
    func = lambda nlp, name: lambda doc: doc
    Language.factory(name, func=func)
    config = {
        "nlp": {"lang": "en", "pipeline": [name]},
        "components": {name: {"factory": name}},
    }
    nlp = English.from_config(config)
    assert nlp.pipe_names == [name]
    pipe_cfg = nlp.get_pipe_config(name)
    pipe_cfg == {"factory": name}
    assert nlp._pipe_configs[name] == {"factory": name}
