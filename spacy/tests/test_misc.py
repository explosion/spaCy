import pytest
import os
import ctypes
from pathlib import Path
from spacy.about import __version__ as spacy_version
from spacy import util
from spacy import prefer_gpu, require_gpu
from spacy.ml._precomputable_affine import PrecomputableAffine
from spacy.ml._precomputable_affine import _backprop_precomputable_affine_padding


@pytest.fixture
def is_admin():
    """Determine if the tests are run as admin or not."""
    try:
        admin = os.getuid() == 0
    except AttributeError:
        admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    return admin


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
    try:
        import cupy  # noqa: F401
    except ImportError:
        assert not prefer_gpu()


def test_require_gpu():
    try:
        import cupy  # noqa: F401
    except ImportError:
        with pytest.raises(ValueError):
            require_gpu()


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
