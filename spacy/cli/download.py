import requests
import os
import subprocess
import sys
from wasabi import msg

from .. import about


def download(
    model: ("Model to download (shortcut or name)", "positional", None, str),
    direct: ("Force direct download of name + version", "flag", "d", bool) = False,
    *pip_args: ("Additional arguments to be passed to `pip install` on model install"),
):
    """
    Download compatible model from default download path using pip. If --direct
    flag is set, the command expects the full model name with version.
    For direct downloads, the compatibility check will be skipped.
    """
    if not require_package("spacy") and "--no-deps" not in pip_args:
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
        dl = download_model(dl_tpl.format(m=model_name, v=version), pip_args)
    else:
        shortcuts = get_json(about.__shortcuts__, "available shortcuts")
        model_name = shortcuts.get(model, model)
        compatibility = get_compatibility()
        version = get_version(model_name, compatibility)
        dl = download_model(dl_tpl.format(m=model_name, v=version), pip_args)
        if dl != 0:  # if download subprocess doesn't return 0, exit
            sys.exit(dl)
        msg.good(
            "Download and installation successful",
            f"You can now load the model via spacy.load('{model_name}')",
        )
        # If a model is downloaded and then loaded within the same process, our
        # is_package check currently fails, because pkg_resources.working_set
        # is not refreshed automatically (see #3923). We're trying to work
        # around this here be requiring the package explicitly.
        require_package(model_name)


def require_package(name):
    try:
        import pkg_resources

        pkg_resources.working_set.require(name)
        return True
    except:  # noqa: E722
        return False


def get_json(url, desc):
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


def get_compatibility():
    version = about.__version__
    version = version.rsplit(".dev", 1)[0]
    comp_table = get_json(about.__compatibility__, "compatibility table")
    comp = comp_table["spacy"]
    if version not in comp:
        msg.fail(f"No compatible models found for v{version} of spaCy", exits=1)
    return comp[version]


def get_version(model, comp):
    model = model.rsplit(".dev", 1)[0]
    if model not in comp:
        msg.fail(
            f"No compatible model found for '{model}' (spaCy v{about.__version__})",
            exits=1,
        )
    return comp[model][0]


def download_model(filename, user_pip_args=None):
    download_url = about.__download_url__ + "/" + filename
    pip_args = ["--no-cache-dir"]
    if user_pip_args:
        pip_args.extend(user_pip_args)
    cmd = [sys.executable, "-m", "pip", "install"] + pip_args + [download_url]
    return subprocess.call(cmd, env=os.environ.copy())
