from typing import List
from pathlib import Path
from wasabi import Printer

from ._app import app, Arg, Opt
from .. import util


@app.command("debug-model")
def debug_model_cli(
    # fmt: off
    config_path: Path = Arg(..., help="Path to config file", exists=True),
    layers: str = Opt("", "--layers", "-l", help="Comma-separated names of pipeline components to train"),
    dimensions: bool = Opt(False, "--dimensions", "-d", help="Show dimensions"),
    parameters: bool = Opt(False, "--parameters", "-p", help="Show parameters"),
    gradients: bool = Opt(False, "--gradients", "-g", help="Show gradients"),
    attributes: bool = Opt(False, "--attributes", "-a", help="Show attributes"),
    ignore_warnings: bool = Opt(False, "--ignore-warnings", "-IW", help="Ignore warnings, only show stats and errors"),
    no_format: bool = Opt(False, "--no-format", "-NF", help="Don't pretty-print the results"),
    # fmt: on
):
    """
    Analyze a Thinc ML model - internal structure (TODO: and activations during training)
    """
    debug_model(
        config_path,
        layers=[int(l.strip()) for l in layers.split(",")] if layers else [],
        dimensions=dimensions,
        parameters=parameters,
        gradients=gradients,
        attributes=attributes,
        ignore_warnings=ignore_warnings,
        no_format=no_format,
        silent=False
    )


def debug_model(
    config_path: Path,
    *,
    layers: List[str] = None,
    dimensions: bool = False,
    parameters: bool = False,
    gradients: bool = False,
    attributes: bool = False,
    ignore_warnings: bool = False,
    no_format: bool = True,
    silent: bool = True,
):
    msg = Printer(
        no_print=silent, pretty=not no_format, ignore_warnings=ignore_warnings
    )
    model = util.load_config(config_path, create_objects=True)["model"]

    msg.info(f"Analysing model with ID {model.id}: '{model.name}'")
    for i, node in enumerate(model.walk()):
        if not layers or i in layers:
            msg.info(f"Layer {i}: model ID {node.id}: '{node.name}'")

            if dimensions:
                for name in node.dim_names:
                    if node.has_dim(name):
                        msg.info(f" - dim {name}: {node.get_dim(name)}")
                    else:
                        msg.info(f" - dim {name}: {node.has_dim(name)}")

            if parameters:
                for name in node.param_names:
                    if node.has_param(name):
                        msg.info(f" - param {name}: {node.get_param(name)}")
                    else:
                        msg.info(f" - param {name}: {node.has_param(name)}")
            if gradients:
                for name in node.param_names:
                    if node.has_grad(name):
                        msg.info(f" - grad {name}: {node.get_grad(name)}")
                    else:
                        msg.info(f" - grad {name}: {node.has_grad(name)}")
            if attributes:
                attrs = node.attrs
                for name, value in attrs.items():
                    msg.info(f" - attr {name}: {value}")