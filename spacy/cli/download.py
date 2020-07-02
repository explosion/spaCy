from typing import Optional, Sequence, Union
import requests
import sys
from wasabi import msg
import typer

from ._app import app, Arg, Opt
from .. import about
from ..util import is_package, get_base_version, run_command


@app.command(
    "download",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def download_cli(
    # fmt: off
    ctx: typer.Context,
    model: str = Arg(..., help="Name of model to download"),
    direct: bool = Opt(False, "--direct", "-d", "-D", help="Force direct download of name + version"),
    # fmt: on
):
    """
    Download compatible model from default download path using pip. If --direct
    flag is set, the command expects the full model name with version.
    For direct downloads, the compatibility check will be skipped. All
    additional arguments provided to this command will be passed to `pip install`
    on model installation.
    """
    download(model, direct, *ctx.args)


def download(model: str, direct: bool = False, *pip_args) -> None:
    if not is_package("spacy") and "--no-deps" not in pip_args:
        msg.warn(
            "Skipping model package dependencies and setting `--no-deps`. "
            "You don't seem to have the spaCy package itself installed "
            "(maybe because you've built from source?), so installing the "
            "model dependencies would cause spaCy to be downloaded, which "
            "probably isn't what you want. If the model package has other "
            "dependencies, you'll have to install them manually."
        )
        pip_args = pip_args + ("--no-deps",)
    dl_tpl = "{m}-{v}/{m}-{v}.tar.gz#egg={m}=={v}"
    if direct:
        components = model.split("-")
        model_name = "".join(components[:-1])
        version = components[-1]
        download_model(dl_tpl.format(m=model_name, v=version), pip_args)
    else:
        shortcuts = get_json(about.__shortcuts__, "available shortcuts")
        model_name = shortcuts.get(model, model)
        compatibility = get_compatibility()
        version = get_version(model_name, compatibility)
        download_model(dl_tpl.format(m=model_name, v=version), pip_args)
    msg.good(
        "Download and installation successful",
        f"You can now load the model via spacy.load('{model_name}')",
    )


def get_json(url: str, desc: str) -> Union[dict, list]:
    r = requests.get(url)
    if r.status_code != 200:
        msg.fail(
            f"Server error ({r.status_code})",
            f"Couldn't fetch {desc}. Please find a model for your spaCy "
            f"installation (v{about.__version__}), and download it manually. "
            f"For more details, see the documentation: "
            f"https://spacy.io/usage/models",
            exits=1,
        )
    return r.json()


def get_compatibility() -> dict:
    version = get_base_version(about.__version__)
    comp_table = get_json(about.__compatibility__, "compatibility table")
    comp = comp_table["spacy"]
    if version not in comp:
        msg.fail(f"No compatible models found for v{version} of spaCy", exits=1)
    return comp[version]


def get_version(model: str, comp: dict) -> str:
    model = get_base_version(model)
    if model not in comp:
        msg.fail(
            f"No compatible model found for '{model}' (spaCy v{about.__version__})",
            exits=1,
        )
    return comp[model][0]


def download_model(
    filename: str, user_pip_args: Optional[Sequence[str]] = None
) -> None:
    download_url = about.__download_url__ + "/" + filename
    pip_args = ["--no-cache-dir"]
    if user_pip_args:
        pip_args.extend(user_pip_args)
    cmd = [sys.executable, "-m", "pip", "install"] + pip_args + [download_url]
    run_command(cmd)
