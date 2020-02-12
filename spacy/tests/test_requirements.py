import re
from pathlib import Path


def test_build_dependencies(en_vocab):
    libs_ignore_requirements = ["pytest", "pytest-timeout", "mock", "flake8", "jsonschema"]
    libs_ignore_setup = ["fugashi", "natto-py", "pythainlp"]

    # check requirements.txt
    root_dir = Path(__file__).parent.parent.parent
    req_file = root_dir / "requirements.txt"
    req_dict = {}
    with req_file.open() as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line.startswith("#"):
            lib, v = _parse_req(line)
            if lib and lib not in libs_ignore_requirements:
                req_dict[lib] = v

    # check setup.cfg and compare to requirements.txt
    # also fails when there are missing or additional libs
    setup_file = root_dir / "setup.cfg"
    with setup_file.open() as f:
        lines = f.readlines()
    setup_keys = set()
    for line in lines:
        line = line.strip()
        if not line.startswith("#"):
            lib, v = _parse_req(line)
            if lib and not lib.startswith("cupy") and lib not in libs_ignore_setup:
                req_v = req_dict.get(lib, None)
                assert req_v is not None    # if fail: setup.cfg contains a lib not in requirements.txt
                assert (lib+v) == (lib+req_v)    # if fail: setup.cfg & requirements.txt have conflicting versions
                setup_keys.add(lib)
    assert sorted(setup_keys) == sorted(req_dict.keys()) # if fail: requirements.txt contains a lib not in setup.cfg

    # check pyproject.toml and compare the versions of the libs to requirements.txt
    # does not fail when there are missing or additional libs
    toml_file = root_dir / "pyproject.toml"
    with toml_file.open() as f:
        lines = f.readlines()
    toml_keys = set()
    for line in lines:
        line = line.strip()
        line = line.strip(",")
        line = line.strip("\"")
        if not line.startswith("#"):
            lib, v = _parse_req(line)
            if lib:
                req_v = req_dict.get(lib, None)
                assert (lib+v) == (lib+req_v)   # if fail: pyproject.toml & requirements.txt have conflicting versions
                toml_keys.add(lib)

def _parse_req(line):
    lib = re.match(r"^[a-z0-9\-]*", line).group(0)
    v = line.replace(lib, "").strip()
    if not re.match(r"^[<>=][<>=].*", v):
        return None, None
    return lib, v