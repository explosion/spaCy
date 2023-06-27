from catalogue import RegistryError
from wasabi import msg

from ..util import registry
from ._util import Arg, Opt, app


@app.command("find-loc")
def find_loc_cli(
    # fmt: off
    func_name: str = Arg(..., help="Name of the registered function."),
    registry_name: str = Opt(None, help="Name of the catalogue registry."),
    # fmt: on
):
    """
    Find the module, path and line number to the file the registered
    function is defined in, if available.

    func_name (str): Name of the registered function.
    registry_name (str): Name of the catalogue registry.
    """
    registry_names = registry.get_registry_names()
    for name in registry_names:
        if registry.has(name, func_name):
            registry_name = name
            break

    find_loc(func_name, registry_name)


def find_loc(func_name: str, registry_name: str) -> None:
    try:
        registry_desc = registry.find(registry_name, func_name)

    except RegistryError as e:
        msg.fail(
            f"Couldn't find registered function: {func_name}\n\n{e}",
            exits=1,
        )

    if registry_desc["file"]:
        registry_path = registry_desc["file"]
        line_no = registry_desc["line_no"]
    else:
        msg.fail(
            f"Couldn't find path to registered function: {func_name}",
            exits=1,
        )

    msg.good(f"Found registered function at file://{registry_path}:{line_no}")
