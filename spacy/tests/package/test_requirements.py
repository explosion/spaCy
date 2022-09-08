import re
import pkg_resources
from pathlib import Path

from .setup import INSTALL_REQUIRES


def test_build_dependencies():
    # Check that library requirements are pinned exactly the same across different setup files.
    libs_ignore_requirements = [
        "black",
        "cython",
        "flake8",
        "hypothesis",
        "ml-datasets",
        "mock",
        "mypy",
        "numpy",  # added dynamically to setup
        "pre-commit",
        "pytest",
        "pytest-timeout",
        "types-dataclasses",
        "types-mock",
        "types-requests",
        "types-setuptools",
    ]

    # load requirements.txt
    req_dict = {}

    root_dir = Path(__file__).parent
    req_file = root_dir / "requirements.txt"
    with req_file.open() as f:
        for r in pkg_resources.parse_requirements(f):
            if r.key not in libs_ignore_requirements:
                req_dict[r.key] = r
    # check setup.py and compare to requirements.txt
    # also fails when there are missing or additional libs
    setup_keys = set()
    for setup_req in pkg_resources.parse_requirements(INSTALL_REQUIRES):
        lib = setup_req.key
        req_req = req_dict.get(lib, None)
        assert req_req is not None, "{} in setup.py but not in requirements.txt".format(
            lib
        )
        assert req_req == setup_req, (
            "{} has different version in setup.py and in requirements.txt: "
            "{} and {} respectively".format(lib, setup_req, req_req)
        )
        setup_keys.add(lib)
    # if fail: requirements.txt contains a lib not in setup.py
    assert setup_keys == set(req_dict.keys())

    # check pyproject.toml and compare the versions of the libs to requirements.txt
    # does not fail when there are missing or additional libs
    toml_file = root_dir / "pyproject.toml"
    with toml_file.open() as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip().strip(",").strip('"')
        if not line.startswith("#"):
            lib, v = _parse_req(line)
            if lib and lib not in libs_ignore_requirements:
                pyproject_req = pkg_resources.Requirement.parse(line)
                req_req = req_dict.get(lib, None)
                assert req_req == pyproject_req, (
                    "{} has different version in pyproject.toml and in requirements.txt: "
                    "{} and {} respectively".format(lib, pyproject_req, req_req)
                )


def _parse_req(line):
    lib = re.match(r"^[a-z0-9\-]*", line).group(0)
    v = line.replace(lib, "").strip()
    if not re.match(r"^[<>=][<>=].*", v):
        return None, None
    return lib, v
