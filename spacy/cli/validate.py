# coding: utf8
from __future__ import unicode_literals, print_function

import pkg_resources
from pathlib import Path
import sys
import requests
import srsly
from wasabi import Printer

from ..compat import path2str
from ..util import get_data_path
from .. import about


def validate():
    """
    Validate that the currently installed version of spaCy is compatible
    with the installed models. Should be run after `pip install -U spacy`.
    """
    msg = Printer()
    with msg.loading("Loading compatibility table..."):
        r = requests.get(about.__compatibility__)
        if r.status_code != 200:
            msg.fail(
                "Server error ({})".format(r.status_code),
                "Couldn't fetch compatibility table.",
                exits=1,
            )
    msg.good("Loaded compatibility table")
    compat = r.json()["spacy"]
    version = about.__version__
    version = version.rsplit(".dev", 1)[0]
    current_compat = compat.get(version)
    if not current_compat:
        msg.fail(
            "Can't find spaCy v{} in compatibility table".format(version),
            about.__compatibility__,
            exits=1,
        )
    all_models = set()
    for spacy_v, models in dict(compat).items():
        all_models.update(models.keys())
        for model, model_vs in models.items():
            compat[spacy_v][model] = [reformat_version(v) for v in model_vs]
    model_links = get_model_links(current_compat)
    model_pkgs = get_model_pkgs(current_compat, all_models)
    incompat_links = {l for l, d in model_links.items() if not d["compat"]}
    incompat_models = {d["name"] for _, d in model_pkgs.items() if not d["compat"]}
    incompat_models.update(
        [d["name"] for _, d in model_links.items() if not d["compat"]]
    )
    na_models = [m for m in incompat_models if m not in current_compat]
    update_models = [m for m in incompat_models if m in current_compat]
    spacy_dir = Path(__file__).parent.parent

    msg.divider("Installed models (spaCy v{})".format(about.__version__))
    msg.info("spaCy installation: {}".format(path2str(spacy_dir)))

    if model_links or model_pkgs:
        header = ("TYPE", "NAME", "MODEL", "VERSION", "")
        rows = []
        for name, data in model_pkgs.items():
            rows.append(get_model_row(current_compat, name, data, msg))
        for name, data in model_links.items():
            rows.append(get_model_row(current_compat, name, data, msg, "link"))
        msg.table(rows, header=header)
    else:
        msg.text("No models found in your current environment.", exits=0)
    if update_models:
        msg.divider("Install updates")
        msg.text("Use the following commands to update the model packages:")
        cmd = "python -m spacy download {}"
        print("\n".join([cmd.format(pkg) for pkg in update_models]) + "\n")
    if na_models:
        msg.text(
            "The following models are not available for spaCy "
            "v{}: {}".format(about.__version__, ", ".join(na_models))
        )
    if incompat_links:
        msg.text(
            "You may also want to overwrite the incompatible links using the "
            "`python -m spacy link` command with `--force`, or remove them "
            "from the data directory. "
            "Data path: {path}".format(path=path2str(get_data_path()))
        )
    if incompat_models or incompat_links:
        sys.exit(1)


def get_model_links(compat):
    links = {}
    data_path = get_data_path()
    if data_path:
        models = [p for p in data_path.iterdir() if is_model_path(p)]
        for model in models:
            meta_path = Path(model) / "meta.json"
            if not meta_path.exists():
                continue
            meta = srsly.read_json(meta_path)
            link = model.parts[-1]
            name = meta["lang"] + "_" + meta["name"]
            links[link] = {
                "name": name,
                "version": meta["version"],
                "compat": is_compat(compat, name, meta["version"]),
            }
    return links


def get_model_pkgs(compat, all_models):
    pkgs = {}
    for pkg_name, pkg_data in pkg_resources.working_set.by_key.items():
        package = pkg_name.replace("-", "_")
        if package in all_models:
            version = pkg_data.version
            pkgs[pkg_name] = {
                "name": package,
                "version": version,
                "compat": is_compat(compat, package, version),
            }
    return pkgs


def get_model_row(compat, name, data, msg, model_type="package"):
    if data["compat"]:
        comp = msg.text("", color="green", icon="good", no_print=True)
        version = msg.text(data["version"], color="green", no_print=True)
    else:
        version = msg.text(data["version"], color="red", no_print=True)
        comp = "--> {}".format(compat.get(data["name"], ["n/a"])[0])
    return (model_type, name, data["name"], version, comp)


def is_model_path(model_path):
    exclude = ["cache", "pycache", "__pycache__"]
    name = model_path.parts[-1]
    return model_path.is_dir() and name not in exclude and not name.startswith(".")


def is_compat(compat, name, version):
    return name in compat and version in compat[name]


def reformat_version(version):
    """Hack to reformat old versions ending on '-alpha' to match pip format."""
    if version.endswith("-alpha"):
        return version.replace("-alpha", "a0")
    return version.replace("-alpha", "a")
