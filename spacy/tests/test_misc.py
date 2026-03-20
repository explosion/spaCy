import ctypes
import os
from pathlib import Path

import pytest

try:
    from pydantic.v1 import ValidationError
except ImportError:
    from pydantic import ValidationError  # type: ignore

from thinc.api import (
    Config,
    ConfigValidationError,
    CupyOps,
    MPSOps,
    NumpyOps,
    Optimizer,
    get_current_ops,
    set_current_ops,
)
from thinc.compat import has_cupy_gpu, has_torch_mps_gpu

from spacy import prefer_gpu, require_cpu, require_gpu, util
from spacy.about import __version__ as spacy_version
from spacy.lang.en import English
from spacy.lang.nl import Dutch
from spacy.language import DEFAULT_CONFIG_PATH
from spacy.ml._precomputable_affine import (
    PrecomputableAffine,
    _backprop_precomputable_affine_padding,
)
from spacy.schemas import ConfigSchemaTraining, TokenPattern, TokenPatternSchema
from spacy.training.batchers import minibatch_by_words
from spacy.util import (
    SimpleFrozenList,
    dot_to_object,
    find_available_port,
    import_file,
    to_ternary_int,
)

from .util import get_random_doc, make_tempdir


@pytest.fixture
def is_admin():
    """Determine if the tests are run as admin or not."""
    try:
        admin = os.getuid() == 0
    except AttributeError:
        admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    return admin


@pytest.mark.issue(6207)
def test_issue6207(en_tokenizer):
    doc = en_tokenizer("zero one two three four five six")

    # Make spans
    s1 = doc[:4]
    s2 = doc[3:6]  # overlaps with s1
    s3 = doc[5:7]  # overlaps with s2, not s1

    result = util.filter_spans((s1, s2, s3))
    assert s1 in result
    assert s2 not in result
    assert s3 in result


@pytest.mark.issue(6258)
def test_issue6258():
    """Test that the non-empty constraint pattern field is respected"""
    # These one is valid
    TokenPatternSchema(pattern=[TokenPattern()])
    # But an empty pattern list should fail to validate
    # based on the schema's constraint
    with pytest.raises(ValidationError):
        TokenPatternSchema(pattern=[])


@pytest.mark.parametrize("text", ["hello/world", "hello world"])
def test_util_ensure_path_succeeds(text):
    path = util.ensure_path(text)
    assert isinstance(path, Path)


@pytest.mark.parametrize(
    "package,result", [("numpy", True), ("sfkodskfosdkfpsdpofkspdof", False)]
)
def test_util_is_package(package, result):
    """Test that an installed package via pip is recognised by util.is_package."""
    assert util.is_package(package) is result


@pytest.mark.parametrize("package", ["thinc"])
def test_util_get_package_path(package):
    """Test that a Path object is returned for a package name."""
    path = util.get_package_path(package)
    assert isinstance(path, Path)


def test_PrecomputableAffine(nO=4, nI=5, nF=3, nP=2):
    model = PrecomputableAffine(nO=nO, nI=nI, nF=nF, nP=nP).initialize()
    assert model.get_param("W").shape == (nF, nO, nP, nI)
    tensor = model.ops.alloc((10, nI))
    Y, get_dX = model.begin_update(tensor)
    assert Y.shape == (tensor.shape[0] + 1, nF, nO, nP)
    dY = model.ops.alloc((15, nO, nP))
    ids = model.ops.alloc((15, nF))
    ids[1, 2] = -1
    dY[1] = 1
    assert not model.has_grad("pad")
    d_pad = _backprop_precomputable_affine_padding(model, dY, ids)
    assert d_pad[0, 2, 0, 0] == 1.0
    ids.fill(0.0)
    dY.fill(0.0)
    dY[0] = 0
    ids[1, 2] = 0
    ids[1, 1] = -1
    ids[1, 0] = -1
    dY[1] = 1
    ids[2, 0] = -1
    dY[2] = 5
    d_pad = _backprop_precomputable_affine_padding(model, dY, ids)
    assert d_pad[0, 0, 0, 0] == 6
    assert d_pad[0, 1, 0, 0] == 1
    assert d_pad[0, 2, 0, 0] == 0


def test_prefer_gpu():
    current_ops = get_current_ops()
    if has_cupy_gpu:
        assert prefer_gpu()
        assert isinstance(get_current_ops(), CupyOps)
    elif has_torch_mps_gpu:
        assert prefer_gpu()
        assert isinstance(get_current_ops(), MPSOps)
    else:
        assert not prefer_gpu()
    set_current_ops(current_ops)


def test_require_gpu():
    current_ops = get_current_ops()
    if has_cupy_gpu:
        require_gpu()
        assert isinstance(get_current_ops(), CupyOps)
    elif has_torch_mps_gpu:
        require_gpu()
        assert isinstance(get_current_ops(), MPSOps)
    set_current_ops(current_ops)


def test_require_cpu():
    current_ops = get_current_ops()
    require_cpu()
    assert isinstance(get_current_ops(), NumpyOps)
    try:
        import cupy  # noqa: F401

        require_gpu()
        assert isinstance(get_current_ops(), CupyOps)
    except ImportError:
        pass
    require_cpu()
    assert isinstance(get_current_ops(), NumpyOps)
    set_current_ops(current_ops)


def test_ascii_filenames():
    """Test that all filenames in the project are ASCII.
    See: https://twitter.com/_inesmontani/status/1177941471632211968
    """
    root = Path(__file__).parent.parent
    for path in root.glob("**/*"):
        assert all(ord(c) < 128 for c in path.name), path.name


def test_load_model_blank_shortcut():
    """Test that using a model name like "blank:en" works as a shortcut for
    spacy.blank("en").
    """
    nlp = util.load_model("blank:en")
    assert nlp.lang == "en"
    assert nlp.pipeline == []

    # ImportError for loading an unsupported language
    with pytest.raises(ImportError):
        util.load_model("blank:zxx")

    # ImportError for requesting an invalid language code that isn't registered
    with pytest.raises(ImportError):
        util.load_model("blank:fjsfijsdof")


@pytest.mark.parametrize(
    "version,constraint,compatible",
    [
        (spacy_version, spacy_version, True),
        (spacy_version, f">={spacy_version}", True),
        ("3.0.0", "2.0.0", False),
        ("3.2.1", ">=2.0.0", True),
        ("2.2.10a1", ">=1.0.0,<2.1.1", False),
        ("3.0.0.dev3", ">=1.2.3,<4.5.6", True),
        ("n/a", ">=1.2.3,<4.5.6", None),
        ("1.2.3", "n/a", None),
        ("n/a", "n/a", None),
    ],
)
def test_is_compatible_version(version, constraint, compatible):
    assert util.is_compatible_version(version, constraint) is compatible


@pytest.mark.parametrize(
    "constraint,expected",
    [
        ("3.0.0", False),
        ("==3.0.0", False),
        (">=2.3.0", True),
        (">2.0.0", True),
        ("<=2.0.0", True),
        (">2.0.0,<3.0.0", False),
        (">=2.0.0,<3.0.0", False),
        ("!=1.1,>=1.0,~=1.0", True),
        ("n/a", None),
    ],
)
def test_is_unconstrained_version(constraint, expected):
    assert util.is_unconstrained_version(constraint) is expected


@pytest.mark.parametrize(
    "a1,a2,b1,b2,is_match",
    [
        ("3.0.0", "3.0", "3.0.1", "3.0", True),
        ("3.1.0", "3.1", "3.2.1", "3.2", False),
        ("xxx", None, "1.2.3.dev0", "1.2", False),
    ],
)
def test_minor_version(a1, a2, b1, b2, is_match):
    assert util.get_minor_version(a1) == a2
    assert util.get_minor_version(b1) == b2
    assert util.is_minor_version_match(a1, b1) is is_match
    assert util.is_minor_version_match(a2, b2) is is_match


@pytest.mark.parametrize(
    "dot_notation,expected",
    [
        (
            {"token.pos": True, "token._.xyz": True},
            {"token": {"pos": True, "_": {"xyz": True}}},
        ),
        (
            {"training.batch_size": 128, "training.optimizer.learn_rate": 0.01},
            {"training": {"batch_size": 128, "optimizer": {"learn_rate": 0.01}}},
        ),
        (
            {"attribute_ruler.scorer.@scorers": "spacy.tagger_scorer.v1"},
            {"attribute_ruler": {"scorer": {"@scorers": "spacy.tagger_scorer.v1"}}},
        ),
    ],
)
def test_dot_to_dict(dot_notation, expected):
    result = util.dot_to_dict(dot_notation)
    assert result == expected
    assert util.dict_to_dot(result) == dot_notation


@pytest.mark.parametrize(
    "dot_notation,expected",
    [
        (
            {"token.pos": True, "token._.xyz": True},
            {"token": {"pos": True, "_": {"xyz": True}}},
        ),
        (
            {"training.batch_size": 128, "training.optimizer.learn_rate": 0.01},
            {"training": {"batch_size": 128, "optimizer": {"learn_rate": 0.01}}},
        ),
        (
            {"attribute_ruler.scorer": {"@scorers": "spacy.tagger_scorer.v1"}},
            {"attribute_ruler": {"scorer": {"@scorers": "spacy.tagger_scorer.v1"}}},
        ),
    ],
)
def test_dot_to_dict_overrides(dot_notation, expected):
    result = util.dot_to_dict(dot_notation)
    assert result == expected
    assert util.dict_to_dot(result, for_overrides=True) == dot_notation


def test_set_dot_to_object():
    config = {"foo": {"bar": 1, "baz": {"x": "y"}}, "test": {"a": {"b": "c"}}}
    with pytest.raises(KeyError):
        util.set_dot_to_object(config, "foo.bar.baz", 100)
    with pytest.raises(KeyError):
        util.set_dot_to_object(config, "hello.world", 100)
    with pytest.raises(KeyError):
        util.set_dot_to_object(config, "test.a.b.c", 100)
    util.set_dot_to_object(config, "foo.bar", 100)
    assert config["foo"]["bar"] == 100
    util.set_dot_to_object(config, "foo.baz.x", {"hello": "world"})
    assert config["foo"]["baz"]["x"]["hello"] == "world"
    assert config["test"]["a"]["b"] == "c"
    util.set_dot_to_object(config, "foo", 123)
    assert config["foo"] == 123
    util.set_dot_to_object(config, "test", "hello")
    assert dict(config) == {"foo": 123, "test": "hello"}


@pytest.mark.parametrize(
    "doc_sizes, expected_batches",
    [
        ([400, 400, 199], [3]),
        ([400, 400, 199, 3], [4]),
        ([400, 400, 199, 3, 200], [3, 2]),
        ([400, 400, 199, 3, 1], [5]),
        ([400, 400, 199, 3, 1, 1500], [5]),  # 1500 will be discarded
        ([400, 400, 199, 3, 1, 200], [3, 3]),
        ([400, 400, 199, 3, 1, 999], [3, 3]),
        ([400, 400, 199, 3, 1, 999, 999], [3, 2, 1, 1]),
        ([1, 2, 999], [3]),
        ([1, 2, 999, 1], [4]),
        ([1, 200, 999, 1], [2, 2]),
        ([1, 999, 200, 1], [2, 2]),
    ],
)
def test_util_minibatch(doc_sizes, expected_batches):
    docs = [get_random_doc(doc_size) for doc_size in doc_sizes]
    tol = 0.2
    batch_size = 1000
    batches = list(
        minibatch_by_words(docs, size=batch_size, tolerance=tol, discard_oversize=True)
    )
    assert [len(batch) for batch in batches] == expected_batches

    max_size = batch_size + batch_size * tol
    for batch in batches:
        assert sum([len(doc) for doc in batch]) < max_size


@pytest.mark.parametrize(
    "doc_sizes, expected_batches",
    [
        ([400, 4000, 199], [1, 2]),
        ([400, 400, 199, 3000, 200], [1, 4]),
        ([400, 400, 199, 3, 1, 1500], [1, 5]),
        ([400, 400, 199, 3000, 2000, 200, 200], [1, 1, 3, 2]),
        ([1, 2, 9999], [1, 2]),
        ([2000, 1, 2000, 1, 1, 1, 2000], [1, 1, 1, 4]),
    ],
)
def test_util_minibatch_oversize(doc_sizes, expected_batches):
    """Test that oversized documents are returned in their own batch"""
    docs = [get_random_doc(doc_size) for doc_size in doc_sizes]
    tol = 0.2
    batch_size = 1000
    batches = list(
        minibatch_by_words(docs, size=batch_size, tolerance=tol, discard_oversize=False)
    )
    assert [len(batch) for batch in batches] == expected_batches


def test_util_dot_section():
    cfg_string = """
    [nlp]
    lang = "en"
    pipeline = ["textcat"]

    [components]

    [components.textcat]
    factory = "textcat"

    [components.textcat.model]
    @architectures = "spacy.TextCatBOW.v3"
    exclusive_classes = true
    length = 262144
    ngram_size = 1
    no_output_layer = false
    """
    nlp_config = Config().from_str(cfg_string)
    en_nlp = util.load_model_from_config(nlp_config, auto_fill=True)
    default_config = Config().from_disk(DEFAULT_CONFIG_PATH)
    default_config["nlp"]["lang"] = "nl"
    nl_nlp = util.load_model_from_config(default_config, auto_fill=True)
    # Test that creation went OK
    assert isinstance(en_nlp, English)
    assert isinstance(nl_nlp, Dutch)
    assert nl_nlp.pipe_names == []
    assert en_nlp.pipe_names == ["textcat"]
    # not exclusive_classes
    assert en_nlp.get_pipe("textcat").model.attrs["multi_label"] is False
    # Test that default values got overwritten
    assert en_nlp.config["nlp"]["pipeline"] == ["textcat"]
    assert nl_nlp.config["nlp"]["pipeline"] == []  # default value []
    # Test proper functioning of 'dot_to_object'
    with pytest.raises(KeyError):
        dot_to_object(en_nlp.config, "nlp.pipeline.tagger")
    with pytest.raises(KeyError):
        dot_to_object(en_nlp.config, "nlp.unknownattribute")
    T = util.registry.resolve(nl_nlp.config["training"], schema=ConfigSchemaTraining)
    assert isinstance(dot_to_object({"training": T}, "training.optimizer"), Optimizer)


def test_simple_frozen_list():
    t = SimpleFrozenList(["foo", "bar"])
    assert t == ["foo", "bar"]
    assert t.index("bar") == 1  # okay method
    with pytest.raises(NotImplementedError):
        t.append("baz")
    with pytest.raises(NotImplementedError):
        t.sort()
    with pytest.raises(NotImplementedError):
        t.extend(["baz"])
    with pytest.raises(NotImplementedError):
        t.pop()
    t = SimpleFrozenList(["foo", "bar"], error="Error!")
    with pytest.raises(NotImplementedError):
        t.append("baz")


def test_resolve_dot_names():
    config = {
        "training": {"optimizer": {"@optimizers": "Adam.v1"}},
        "foo": {"bar": "training.optimizer", "baz": "training.xyz"},
    }
    result = util.resolve_dot_names(config, ["training.optimizer"])
    assert isinstance(result[0], Optimizer)
    with pytest.raises(ConfigValidationError) as e:
        util.resolve_dot_names(config, ["training.xyz", "training.optimizer"])
    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0]["loc"] == ["training", "xyz"]


def test_import_code():
    code_str = """
from spacy import Language

class DummyComponent:
    def __init__(self, vocab, name):
        pass

    def initialize(self, get_examples, *, nlp, dummy_param: int):
        pass

@Language.factory(
    "dummy_component",
)
def make_dummy_component(
    nlp: Language, name: str
):
    return DummyComponent(nlp.vocab, name)
"""

    with make_tempdir() as temp_dir:
        code_path = os.path.join(temp_dir, "code.py")
        with open(code_path, "w") as fileh:
            fileh.write(code_str)

        import_file("python_code", code_path)
        config = {"initialize": {"components": {"dummy_component": {"dummy_param": 1}}}}
        nlp = English.from_config(config)
        nlp.add_pipe("dummy_component")
        nlp.initialize()


def test_to_ternary_int():
    assert to_ternary_int(True) == 1
    assert to_ternary_int(None) == 0
    assert to_ternary_int(False) == -1
    assert to_ternary_int(1) == 1
    assert to_ternary_int(1.0) == 1
    assert to_ternary_int(0) == 0
    assert to_ternary_int(0.0) == 0
    assert to_ternary_int(-1) == -1
    assert to_ternary_int(5) == -1
    assert to_ternary_int(-10) == -1
    assert to_ternary_int("string") == -1
    assert to_ternary_int([0, "string"]) == -1


def test_find_available_port():
    host = "0.0.0.0"
    port = 5001
    assert find_available_port(port, host) == port, "Port 5001 isn't free"

    from wsgiref.simple_server import demo_app, make_server

    with make_server(host, port, demo_app) as httpd:
        with pytest.warns(UserWarning, match="already in use"):
            found_port = find_available_port(port, host, auto_select=True)
        assert found_port == port + 1, "Didn't find next port"
