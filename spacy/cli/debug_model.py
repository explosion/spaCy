from typing import List
from pathlib import Path
from wasabi import msg

from ._app import app, Arg, Opt
from .. import util
from thinc.api import require_gpu, fix_random_seed, set_dropout_rate, Adam
from ..lang.en import English


@app.command("debug-model")
def debug_model_cli(
    # fmt: off
    config_path: Path = Arg(..., help="Path to config file", exists=True),
    layers: str = Opt("", "--layers", "-l", help="Comma-separated names of pipeline components to train"),
    dimensions: bool = Opt(False, "--dimensions", "-DIM", help="Show dimensions"),
    parameters: bool = Opt(False, "--parameters", "-PAR", help="Show parameters"),
    gradients: bool = Opt(False, "--gradients", "-GRAD", help="Show gradients"),
    attributes: bool = Opt(False, "--attributes", "-ATTR", help="Show attributes"),
    P0: bool = Opt(False, "--print-step0", "-P0", help="Print model before training"),
    P1: bool = Opt(False, "--print-step1", "-P1", help="Print model after initialization"),
    P2: bool = Opt(False, "--print-step2", "-P2", help="Print model after training"),
    P3: bool = Opt(True, "--print-step3", "-P3", help="Print final predictions"),
    use_gpu: int = Opt(-1, "--use-gpu", "-g", help="Use GPU"),
    seed: int = Opt(None, "--seed", "-s", help="Use GPU"),
    # fmt: on
):
    """
    Analyze a Thinc ML model - internal structure and activations during training
    """
    print_settings = {
        "dimensions": dimensions,
        "parameters": parameters,
        "gradients": gradients,
        "attributes": attributes,
        "layers": [int(x.strip()) for x in layers.split(",")] if layers else [],
        "print_before_training": P0,
        "print_after_init": P1,
        "print_after_training": P2,
        "print_prediction": P3,
    }

    if seed is not None:
        msg.info(f"Fixing random seed: {seed}")
        fix_random_seed(seed)
    if use_gpu >= 0:
        msg.info(f"Using GPU: {use_gpu}")
        require_gpu(use_gpu)
    else:
        msg.info(f"Using CPU")

    debug_model(
        config_path,
        print_settings=print_settings,
    )


def debug_model(
    config_path: Path,
    *,
    print_settings=None
):
    if print_settings is None:
        print_settings = {}

    model = util.load_config(config_path, create_objects=True)["model"]

    # STEP 0: Printing before training
    msg.info(f"Analysing model with ID {model.id}")
    if print_settings.get("print_before_training"):
        msg.info(f"Before training:")
        _print_model(model, print_settings)

    # STEP 1: Initializing the model and printing again
    model.initialize(X=_get_docs(), Y=_get_output(model.ops.xp))
    if print_settings.get("print_after_init"):
        msg.info(f"After initialization:")
        _print_model(model, print_settings)

    # STEP 2: Updating the model and printing again
    optimizer = Adam(0.001)
    set_dropout_rate(model, 0.2)
    for e in range(3):
        Y, get_dX = model.begin_update(_get_docs())
        dY = get_gradient(model, Y)
        _ = get_dX(dY)
        model.finish_update(optimizer)
    if print_settings.get("print_after_training"):
        msg.info(f"After training:")
        _print_model(model, print_settings)

    # STEP 3: the final prediction
    prediction = model.predict(_get_docs())
    if print_settings.get("print_prediction"):
        msg.info(f"Prediction:", str(prediction))


def get_gradient(model, Y):
    goldY = _get_output(model.ops.xp)
    return Y - goldY


def _sentences():
    return [
        "Apple is looking at buying U.K. startup for $1 billion",
        "Autonomous cars shift insurance liability toward manufacturers",
        "San Francisco considers banning sidewalk delivery robots",
        "London is a big city in the United Kingdom.",
    ]


def _get_docs():
    nlp = English()
    return list(nlp.pipe(_sentences()))


def _get_output(xp):
    return xp.asarray([xp.asarray([i+10, i+20, i+30], dtype="float32") for i, _ in enumerate(_get_docs())])


def _print_model(model, print_settings):
    layers = print_settings.get("layers", "")
    parameters = print_settings.get("parameters", False)
    dimensions = print_settings.get("dimensions", False)
    gradients = print_settings.get("gradients", False)
    attributes = print_settings.get("attributes", False)

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
                        print_value = _print_matrix(node.get_param(name))
                        msg.info(f" - param {name}: {print_value}")
                    else:
                        msg.info(f" - param {name}: {node.has_param(name)}")
            if gradients:
                for name in node.param_names:
                    if node.has_grad(name):
                        print_value = _print_matrix(node.get_grad(name))
                        msg.info(f" - grad {name}: {print_value}")
                    else:
                        msg.info(f" - grad {name}: {node.has_grad(name)}")
            if attributes:
                attrs = node.attrs
                for name, value in attrs.items():
                    msg.info(f" - attr {name}: {value}")


def _print_matrix(value):
    if value is None or isinstance(value, bool):
        return value
    result = str(value.shape) + " - sample: "
    sample_matrix = value
    for d in range(value.ndim-1):
        sample_matrix = sample_matrix[0]
    sample_matrix = sample_matrix[0:5]
    result = result + str(sample_matrix)
    return result
