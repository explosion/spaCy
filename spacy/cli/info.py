from typing import Optional, Dict, Any, Union
import platform
from pathlib import Path
from wasabi import Printer
import srsly

from ._app import app, Arg, Opt
from .. import util
from .. import about


@app.command("info")
def info_cli(
    # fmt: off
    model: Optional[str] = Arg(None, help="Optional model name"),
    markdown: bool = Opt(False, "--markdown", "-md", help="Generate Markdown for GitHub issues"),
    silent: bool = Opt(False, "--silent", "-s", "-S", help="Don't print anything (just return)"),
    # fmt: on
):
    """
    Print info about spaCy installation. If a model is speficied as an argument,
    print model information. Flag --markdown prints details in Markdown for easy
    copy-pasting to GitHub issues.
    """
    info(model, markdown=markdown, silent=silent)


def info(
    model: Optional[str] = None, *, markdown: bool = False, silent: bool = True
) -> Union[str, dict]:
    msg = Printer(no_print=silent, pretty=not silent)
    if model:
        title = f"Info about model '{model}'"
        data = info_model(model, silent=silent)
    else:
        title = "Info about spaCy"
        data = info_spacy()
    raw_data = {k.lower().replace(" ", "_"): v for k, v in data.items()}
    if "Models" in data and isinstance(data["Models"], dict):
        data["Models"] = ", ".join(f"{n} ({v})" for n, v in data["Models"].items())
    markdown_data = get_markdown(data, title=title)
    if markdown:
        if not silent:
            print(markdown_data)
        return markdown_data
    if not silent:
        table_data = dict(data)
        msg.table(table_data, title=title)
    return raw_data


def info_spacy() -> Dict[str, any]:
    """Generate info about the current spaCy intallation.

    RETURNS (dict): The spaCy info.
    """
    all_models = {}
    for pkg_name in util.get_installed_models():
        package = pkg_name.replace("-", "_")
        all_models[package] = util.get_package_version(pkg_name)
    return {
        "spaCy version": about.__version__,
        "Location": str(Path(__file__).parent.parent),
        "Platform": platform.platform(),
        "Python version": platform.python_version(),
        "Models": all_models,
    }


def info_model(model: str, *, silent: bool = True) -> Dict[str, Any]:
    """Generate info about a specific model.

    model (str): Model name of path.
    silent (bool): Don't print anything, just return.
    RETURNS (dict): The model meta.
    """
    msg = Printer(no_print=silent, pretty=not silent)
    if util.is_package(model):
        model_path = util.get_package_path(model)
    else:
        model_path = model
    meta_path = model_path / "meta.json"
    if not meta_path.is_file():
        msg.fail("Can't find model meta.json", meta_path, exits=1)
    meta = srsly.read_json(meta_path)
    if model_path.resolve() != model_path:
        meta["link"] = str(model_path)
        meta["source"] = str(model_path.resolve())
    else:
        meta["source"] = str(model_path)
    return {k: v for k, v in meta.items() if k not in ("accuracy", "speed")}


def get_markdown(data: Dict[str, Any], title: Optional[str] = None) -> str:
    """Get data in GitHub-flavoured Markdown format for issues etc.

    data (dict or list of tuples): Label/value pairs.
    title (str / None): Title, will be rendered as headline 2.
    RETURNS (str): The Markdown string.
    """
    markdown = []
    for key, value in data.items():
        if isinstance(value, str) and Path(value).exists():
            continue
        markdown.append(f"* **{key}:** {value}")
    result = "\n{}\n".format("\n".join(markdown))
    if title:
        result = f"\n## {title}\n{result}"
    return result
