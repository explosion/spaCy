from typing import Optional, List
from enum import Enum
from pathlib import Path
from thinc.api import Config
from wasabi import Printer
import srsly
import re

from ..util import load_model_from_config, get_lang_class
from ._util import init_cli, Arg, Opt, show_validation_error, COMMAND


TEMPLATE_PATH = Path(__file__).parent / "templates" / "quickstart_training.jinja"


class Optimizations(str, Enum):
    efficiency = "efficiency"
    accuracy = "accuracy"


@init_cli.command("config")
def init_config_cli(
    # fmt: off
    output_file: Path = Arg("-", help="File to save config.cfg to (or - for stdout)", allow_dash=True),
    # TODO: base_path: Optional[Path] = Opt(None, "--base", "-b", help="Optional base config to fill", exists=True, dir_okay=False),
    lang: Optional[str] = Opt("en", "--lang", "-l", help="Two-letter code of the language to use"),
    pipeline: Optional[str] = Opt("tagger,parser,ner", "--pipeline", "-p", help="Comma-separated names of trainable pipeline components to include in the model (without 'tok2vec' or 'transformer')"),
    optimize: Optimizations = Opt(Optimizations.efficiency.value, "--optimize", "-o", help="Whether to optimize for efficiency (faster inference, smaller model, lower memory consumption) or higher accuracy (potentially larger and slower model). This will impact the choice of architecture, pretrained weights and related hyperparameters."),
    cpu: bool = Opt(False, "--cpu", "-C", help="Whether the model needs to run on CPU. This will impact the choice of architecture, pretrained weights and related hyperparameters."),
    # fmt: on
):
    """
    Generate a starter config.cfg for training. Based on your requirements
    specified via the CLI arguments, this command generates a config with the
    optimal settings for you use case. This includes the choice of architecture,
    pretrained weights and related hyperparameters.
    """
    if isinstance(optimize, Optimizations):  # instance of enum from the CLI
        optimize = optimize.value
    pipeline = [p.strip() for p in pipeline.split(",")]
    init_config(output_file, lang=lang, pipeline=pipeline, optimize=optimize, cpu=cpu)


def init_config(
    output_file: Path, *, lang: str, pipeline: List[str], optimize: str, cpu: bool
) -> None:
    is_stdout = str(output_file) == "-"
    msg = Printer(no_print=is_stdout)
    try:
        from jinja2 import Template
    except ImportError:
        msg.fail("This command requires jinja2", "pip install jinja2", exits=1)
    lang_defaults = get_lang_class(lang).Defaults
    has_letters = lang_defaults.writing_system.get("has_letters", True)
    has_transformer = False  # TODO: check this somehow
    if has_transformer:
        require_spacy_transformers(msg)
    with TEMPLATE_PATH.open("r") as f:
        template = Template(f.read())
    variables = {
        "lang": lang,
        "pipeline": srsly.json_dumps(pipeline).replace(",", ", "),
        "components": pipeline,
        "optimize": optimize,
        "hardware": "cpu" if cpu else "gpu",
        "has_transformer": has_transformer,
        "has_letters": has_letters,
    }
    base_template = template.render(**variables).strip()
    # Giving up on getting the newlines right in jinja for now
    base_template = re.sub(r"\n\n\n+", "\n\n", base_template)
    use_case = {
        "Language": lang,
        "Pipeline": ", ".join(pipeline),
        "Optimize for": optimize,
        "Hardware": variables["hardware"].upper(),
    }
    msg.good("Generated template specific for your use case:")
    for label, value in use_case.items():
        msg.text(f"- {label}: {value}")
    with show_validation_error(hint_init=False):
        with msg.loading("Auto-filling config..."):
            config = Config().from_str(base_template, interpolate=False)
            try:
                nlp, _ = load_model_from_config(config, auto_fill=True)
            except ValueError as e:
                msg.fail(str(e), exits=1)
    msg.good("Auto-filled config with all values")
    if is_stdout:
        print(nlp.config.to_str())
    else:
        nlp.config.to_disk(output_file, interpolate=False)
        msg.good("Saved config", output_file)
        msg.text("You can now add your data and train your model:")
        variables = ["--paths.train ./train.spacy", "--paths.dev ./dev.spacy"]
        print(f"{COMMAND} train {output_file.parts[-1]} {' '.join(variables)}")


def require_spacy_transformers(msg):
    try:
        import spacy_transformers  # noqa: F401
    except ImportError:
        msg.fail(
            "Using a transformer-based pipeline requires spacy-transformers "
            "to be installed.",
            exits=1,
        )
