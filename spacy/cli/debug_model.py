import itertools
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from thinc.api import (
    Model,
    data_validation,
    fix_random_seed,
    set_dropout_rate,
    set_gpu_allocator,
)
from wasabi import msg

from spacy.training import Example
from spacy.util import resolve_dot_names

from .. import util
from ..schemas import ConfigSchemaTraining
from ..util import registry
from ._util import (
    Arg,
    Opt,
    debug_cli,
    parse_config_overrides,
    setup_gpu,
    show_validation_error,
    string_to_list,
)


@debug_cli.command(
    "model",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def debug_model_cli(
    # fmt: off
    ctx: typer.Context,  # This is only used to read additional arguments
    config_path: Path = Arg(..., help="Path to config file", exists=True, allow_dash=True),
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

    DOCS: https://spacy.io/api/cli#debug-model
    """
    setup_gpu(use_gpu)
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
        raw_config = util.load_config(
            config_path, overrides=config_overrides, interpolate=False
        )
    config = raw_config.interpolate()
    allocator = config["training"]["gpu_allocator"]
    if use_gpu >= 0 and allocator:
        set_gpu_allocator(allocator)
    with show_validation_error(config_path):
        nlp = util.load_model_from_config(raw_config)
        config = nlp.config.interpolate()
        T = registry.resolve(config["training"], schema=ConfigSchemaTraining)
    seed = T["seed"]
    if seed is not None:
        msg.info(f"Fixing random seed: {seed}")
        fix_random_seed(seed)
    pipe = nlp.get_pipe(component)

    debug_model(config, T, nlp, pipe, print_settings=print_settings)


def debug_model(
    config,
    resolved_train_config,
    nlp,
    pipe,
    *,
    print_settings: Optional[Dict[str, Any]] = None,
):
    if not hasattr(pipe, "model"):
        msg.fail(
            f"The component '{pipe}' does not specify an object that holds a Model.",
            exits=1,
        )
    model = pipe.model
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
    with data_validation(False):
        try:
            dot_names = [resolved_train_config["train_corpus"]]
            with show_validation_error():
                (train_corpus,) = resolve_dot_names(config, dot_names)
                nlp.initialize(lambda: train_corpus(nlp))
            msg.info("Initialized the model with the training corpus.")
            examples = list(itertools.islice(train_corpus(nlp), 5))
        except ValueError:
            try:
                _set_output_dim(nO=7, model=model)
                with show_validation_error():
                    examples = [Example.from_dict(x, {}) for x in _get_docs()]
                    nlp.initialize(lambda: examples)
                msg.info("Initialized the model with dummy data.")
            except Exception:
                msg.fail(
                    "Could not initialize the model: you'll have to provide a valid 'train_corpus' argument in the config file.",
                    exits=1,
                )

    if print_settings.get("print_after_init"):
        msg.divider(f"STEP 1 - after initialization")
        _print_model(model, print_settings)

    # STEP 2: Updating the model and printing again
    set_dropout_rate(model, 0.2)
    # ugly hack to deal with Tok2Vec/Transformer listeners
    upstream_component = None
    if model.has_ref("tok2vec") and "tok2vec-listener" in model.get_ref("tok2vec").name:
        upstream_component = nlp.get_pipe("tok2vec")
    if (
        model.has_ref("tok2vec")
        and "transformer-listener" in model.get_ref("tok2vec").name
    ):
        upstream_component = nlp.get_pipe("transformer")
    for e in range(3):
        if upstream_component:
            upstream_component.update(examples)
        pipe.update(examples)
    if print_settings.get("print_after_training"):
        msg.divider(f"STEP 2 - after training")
        _print_model(model, print_settings)

    # STEP 3: the final prediction
    prediction = model.predict([ex.predicted for ex in examples])
    if print_settings.get("print_prediction"):
        msg.divider(f"STEP 3 - prediction")
        msg.info(str(prediction))

    msg.good(f"Succesfully ended analysis - model looks good.")


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


def _set_output_dim(model, nO):
    # simulating dim inference by directly setting the nO argument of the model
    if model.has_dim("nO") is None:
        model.set_dim("nO", nO)
    if model.has_ref("output_layer"):
        if model.get_ref("output_layer").has_dim("nO") is None:
            model.get_ref("output_layer").set_dim("nO", nO)


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
                    msg.info(f" - dim {name}: {node.maybe_get_dim(name)}")
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
