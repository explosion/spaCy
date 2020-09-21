from typing import Dict, Any, Optional
from pathlib import Path
from wasabi import msg
from thinc.api import require_gpu, fix_random_seed, set_dropout_rate, Adam
from thinc.api import Model, data_validation, set_gpu_allocator
import typer

from ._util import Arg, Opt, debug_cli, show_validation_error
from ._util import parse_config_overrides, string_to_list
from .. import util


@debug_cli.command("model")
def debug_model_cli(
    # fmt: off
    ctx: typer.Context,  # This is only used to read additional arguments
    config_path: Path = Arg(..., help="Path to config file", exists=True),
    component: str = Arg(..., help="Name of the pipeline component of which the model should be analysed"),
    layers: str = Opt("", "--layers", "-l", help="Comma-separated names of layer IDs to print"),
    dimensions: bool = Opt(False, "--dimensions", "-DIM", help="Show dimensions"),
    parameters: bool = Opt(False, "--parameters", "-PAR", help="Show parameters"),
    gradients: bool = Opt(False, "--gradients", "-GRAD", help="Show gradients"),
    attributes: bool = Opt(False, "--attributes", "-ATTR", help="Show attributes"),
    P0: bool = Opt(False, "--print-step0", "-P0", help="Print model before training"),
    P1: bool = Opt(False, "--print-step1", "-P1", help="Print model after initialization"),
    P2: bool = Opt(False, "--print-step2", "-P2", help="Print model after training"),
    P3: bool = Opt(False, "--print-step3", "-P3", help="Print final predictions"),
    use_gpu: int = Opt(-1, "--gpu-id", "-g", help="GPU ID or -1 for CPU")
    # fmt: on
):
    """
    Analyze a Thinc model implementation. Includes checks for internal structure
    and activations during training.

    DOCS: https://nightly.spacy.io/api/cli#debug-model
    """
    if use_gpu >= 0:
        msg.info("Using GPU")
        require_gpu(use_gpu)
    else:
        msg.info("Using CPU")
    layers = string_to_list(layers, intify=True)
    print_settings = {
        "dimensions": dimensions,
        "parameters": parameters,
        "gradients": gradients,
        "attributes": attributes,
        "layers": layers,
        "print_before_training": P0,
        "print_after_init": P1,
        "print_after_training": P2,
        "print_prediction": P3,
    }
    config_overrides = parse_config_overrides(ctx.args)
    with show_validation_error(config_path):
        config = util.load_config(
            config_path, overrides=config_overrides, interpolate=True
        )
        allocator = config["training"]["gpu_allocator"]
        if use_gpu >= 0 and allocator:
            set_gpu_allocator(allocator)
        nlp, config = util.load_model_from_config(config_path)
    seed = config["training"]["seed"]
    if seed is not None:
        msg.info(f"Fixing random seed: {seed}")
        fix_random_seed(seed)
    pipe = nlp.get_pipe(component)
    if hasattr(pipe, "model"):
        model = pipe.model
    else:
        msg.fail(
            f"The component '{component}' does not specify an object that holds a Model.",
            exits=1,
        )
    debug_model(model, print_settings=print_settings)


def debug_model(model: Model, *, print_settings: Optional[Dict[str, Any]] = None):
    if not isinstance(model, Model):
        msg.fail(
            f"Requires a Thinc Model to be analysed, but found {type(model)} instead.",
            exits=1,
        )
    if print_settings is None:
        print_settings = {}

    # STEP 0: Printing before training
    msg.info(f"Analysing model with ID {model.id}")
    if print_settings.get("print_before_training"):
        msg.divider(f"STEP 0 - before training")
        _print_model(model, print_settings)

    # STEP 1: Initializing the model and printing again
    X = _get_docs()
    Y = _get_output(model.ops.xp)
    # The output vector might differ from the official type of the output layer
    with data_validation(False):
        model.initialize(X=X, Y=Y)
    if print_settings.get("print_after_init"):
        msg.divider(f"STEP 1 - after initialization")
        _print_model(model, print_settings)

    # STEP 2: Updating the model and printing again
    optimizer = Adam(0.001)
    set_dropout_rate(model, 0.2)
    for e in range(3):
        Y, get_dX = model.begin_update(_get_docs())
        dY = get_gradient(model, Y)
        get_dX(dY)
        model.finish_update(optimizer)
    if print_settings.get("print_after_training"):
        msg.divider(f"STEP 2 - after training")
        _print_model(model, print_settings)

    # STEP 3: the final prediction
    prediction = model.predict(_get_docs())
    if print_settings.get("print_prediction"):
        msg.divider(f"STEP 3 - prediction")
        msg.info(str(prediction))


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


def _get_docs(lang: str = "en"):
    nlp = util.get_lang_class(lang)()
    return list(nlp.pipe(_sentences()))


def _get_output(xp):
    return xp.asarray([i + 10 for i, _ in enumerate(_get_docs())], dtype="float32")


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
    for d in range(value.ndim - 1):
        sample_matrix = sample_matrix[0]
    sample_matrix = sample_matrix[0:5]
    result = result + str(sample_matrix)
    return result
