from typing import Optional, Tuple

from catalogue import RegistryError
from wasabi import msg

from ..util import registry
from ._util import Arg, Opt, app


@app.command("find-function")
def find_function_cli(
    # fmt: off
    func_name: str = Arg(..., help="Name of the registered function."),
    registry_name: Optional[str] = Opt(None, "--registry", "-r", help="Name of the catalogue registry."),
    # fmt: on
):
    """
    Find the module, path and line number to the file the registered
    function is defined in, if available.

    func_name (str): Name of the registered function.
    registry_name (Optional[str]): Name of the catalogue registry.

    DOCS: https://spacy.io/api/cli#find-function
    """
    if not registry_name:
        registry_names = registry.get_registry_names()
        for name in registry_names:
            if registry.has(name, func_name):
                registry_name = name
                break

    if not registry_name:
        msg.fail(
            f"Couldn't find registered function: '{func_name}'",
            exits=1,
        )

    assert registry_name is not None
    find_function(func_name, registry_name)


def find_function(func_name: str, registry_name: str) -> Tuple[str, int]:
    registry_desc = None
    try:
        registry_desc = registry.find(registry_name, func_name)
    except RegistryError as e:
        msg.fail(
            f"Couldn't find registered function: '{func_name}' in registry '{registry_name}'",
        )
        msg.fail(f"{e}", exits=1)
    assert registry_desc is not None

    registry_path = None
    line_no = None
    if registry_desc["file"]:
        registry_path = registry_desc["file"]
        line_no = registry_desc["line_no"]

    if not registry_path or not line_no:
        msg.fail(
            f"Couldn't find path to registered function: '{func_name}' in registry '{registry_name}'",
            exits=1,
        )
    assert registry_path is not None
    assert line_no is not None

    msg.good(f"Found registered function '{func_name}' at {registry_path}:{line_no}")
    return str(registry_path), int(line_no)
