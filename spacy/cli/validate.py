from pathlib import Path
import sys
import requests
from wasabi import msg

from .. import about


def validate():
    """
    Validate that the currently installed version of spaCy is compatible
    with the installed models. Should be run after `pip install -U spacy`.
    """
    model_pkgs, compat = get_model_pkgs()
    spacy_version = about.__version__.rsplit(".dev", 1)[0]
    current_compat = compat.get(spacy_version, {})
    if not current_compat:
        msg.warn(f"No compatible models found for v{spacy_version} of spaCy")
    incompat_models = {d["name"] for _, d in model_pkgs.items() if not d["compat"]}
    na_models = [m for m in incompat_models if m not in current_compat]
    update_models = [m for m in incompat_models if m in current_compat]
    spacy_dir = Path(__file__).parent.parent

    msg.divider(f"Installed models (spaCy v{about.__version__})")
    msg.info(f"spaCy installation: {spacy_dir}")

    if model_pkgs:
        header = ("NAME", "VERSION", "")
        rows = []
        for name, data in model_pkgs.items():
            if data["compat"]:
                comp = msg.text("", color="green", icon="good", no_print=True)
                version = msg.text(data["version"], color="green", no_print=True)
            else:
                version = msg.text(data["version"], color="red", no_print=True)
                comp = f"--> {compat.get(data['name'], ['n/a'])[0]}"
            rows.append((data["name"], version, comp))
        msg.table(rows, header=header)
    else:
        msg.text("No models found in your current environment.", exits=0)
    if update_models:
        msg.divider("Install updates")
        msg.text("Use the following commands to update the model packages:")
        cmd = "python -m spacy download {}"
        print("\n".join([cmd.format(pkg) for pkg in update_models]) + "\n")
    if na_models:
        msg.warn(
            f"The following models are not available for spaCy v{about.__version__}:",
            ", ".join(na_models),
        )
    if incompat_models:
        sys.exit(1)


def get_model_pkgs():
    import pkg_resources

    with msg.loading("Loading compatibility table..."):
        r = requests.get(about.__compatibility__)
        if r.status_code != 200:
            msg.fail(
                f"Server error ({r.status_code})",
                "Couldn't fetch compatibility table.",
                exits=1,
            )
    msg.good("Loaded compatibility table")
    compat = r.json()["spacy"]
    all_models = set()
    for spacy_v, models in dict(compat).items():
        all_models.update(models.keys())
        for model, model_vs in models.items():
            compat[spacy_v][model] = [reformat_version(v) for v in model_vs]
    pkgs = {}
    for pkg_name, pkg_data in pkg_resources.working_set.by_key.items():
        package = pkg_name.replace("-", "_")
        if package in all_models:
            version = pkg_data.version
            pkgs[pkg_name] = {
                "name": package,
                "version": version,
                "compat": package in compat and version in compat[package],
            }
    return pkgs, compat


def reformat_version(version):
    """Hack to reformat old versions ending on '-alpha' to match pip format."""
    if version.endswith("-alpha"):
        return version.replace("-alpha", "a0")
    return version.replace("-alpha", "a")
