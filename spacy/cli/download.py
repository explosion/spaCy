from typing import Optional, Sequence
import requests
import sys
from wasabi import msg
import typer

from ._util import app, Arg, Opt, WHEEL_SUFFIX, SDIST_SUFFIX
from .. import about
from ..util import is_package, get_minor_version, run_command
from ..errors import OLD_MODEL_SHORTCUTS


@app.command(
    "download",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def download_cli(
    # fmt: off
    ctx: typer.Context,
    model: str = Arg(..., help="Name of pipeline package to download"),
    direct: bool = Opt(False, "--direct", "-d", "-D", help="Force direct download of name + version"),
    sdist: bool = Opt(False, "--sdist", "-S", help="Download sdist (.tar.gz) archive instead of pre-built binary wheel")
    # fmt: on
):
    """
    Download compatible trained pipeline from the default download path using
    pip. If --direct flag is set, the command expects the full package name with
    version. For direct downloads, the compatibility check will be skipped. All
    additional arguments provided to this command will be passed to `pip install`
    on package installation.

    DOCS: https://spacy.io/api/cli#download
    AVAILABLE PACKAGES: https://spacy.io/models
    """
    download(model, direct, sdist, *ctx.args)


def download(model: str, direct: bool = False, sdist: bool = False, *pip_args) -> None:
    if (
        not (is_package("spacy") or is_package("spacy-nightly"))
        and "--no-deps" not in pip_args
    ):
        msg.warn(
            "Skipping pipeline package dependencies and setting `--no-deps`. "
            "You don't seem to have the spaCy package itself installed "
            "(maybe because you've built from source?), so installing the "
            "package dependencies would cause spaCy to be downloaded, which "
            "probably isn't what you want. If the pipeline package has other "
            "dependencies, you'll have to install them manually."
        )
        pip_args = pip_args + ("--no-deps",)
    suffix = SDIST_SUFFIX if sdist else WHEEL_SUFFIX
    dl_tpl = "{m}-{v}/{m}-{v}{s}#egg={m}=={v}"
    if direct:
        components = model.split("-")
        model_name = "".join(components[:-1])
        version = components[-1]
        download_model(dl_tpl.format(m=model_name, v=version, s=suffix), pip_args)
    else:
        model_name = model
        if model in OLD_MODEL_SHORTCUTS:
            msg.warn(
                f"As of spaCy v3.0, shortcuts like '{model}' are deprecated. Please "
                f"use the full pipeline package name '{OLD_MODEL_SHORTCUTS[model]}' instead."
            )
            model_name = OLD_MODEL_SHORTCUTS[model]
        compatibility = get_compatibility()
        version = get_version(model_name, compatibility)
        download_model(dl_tpl.format(m=model_name, v=version, s=suffix), pip_args)
    msg.good(
        "Download and installation successful",
        f"You can now load the package via spacy.load('{model_name}')",
    )


def get_compatibility() -> dict:
    version = get_minor_version(about.__version__)
    r = requests.get(about.__compatibility__)
    if r.status_code != 200:
        msg.fail(
            f"Server error ({r.status_code})",
            f"Couldn't fetch compatibility table. Please find a package for your spaCy "
            f"installation (v{about.__version__}), and download it manually. "
            f"For more details, see the documentation: "
            f"https://spacy.io/usage/models",
            exits=1,
        )
    comp_table = r.json()
    comp = comp_table["spacy"]
    if version not in comp:
        msg.fail(f"No compatible packages found for v{version} of spaCy", exits=1)
    return comp[version]


def get_version(model: str, comp: dict) -> str:
    if model not in comp:
        msg.fail(
            f"No compatible package found for '{model}' (spaCy v{about.__version__})",
            exits=1,
        )
    return comp[model][0]


def download_model(
    filename: str, user_pip_args: Optional[Sequence[str]] = None
) -> None:
    download_url = about.__download_url__ + "/" + filename
    pip_args = list(user_pip_args) if user_pip_args is not None else []
    cmd = [sys.executable, "-m", "pip", "install"] + pip_args + [download_url]
    run_command(cmd)
