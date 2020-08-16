from typing import Optional, List, Tuple
from enum import Enum
from pathlib import Path
from wasabi import Printer, diff_strings
from thinc.api import Config
from pydantic import BaseModel
import srsly
import re

from .. import util
from ._util import init_cli, Arg, Opt, show_validation_error, COMMAND


TEMPLATE_ROOT = Path(__file__).parent / "templates"
TEMPLATE_PATH = TEMPLATE_ROOT / "quickstart_training.jinja"
RECOMMENDATIONS_PATH = TEMPLATE_ROOT / "quickstart_training_recommendations.json"


class Optimizations(str, Enum):
    efficiency = "efficiency"
    accuracy = "accuracy"


class RecommendationsTrfItem(BaseModel):
    name: str
    size_factor: int


class RecommendationsTrf(BaseModel):
    efficiency: RecommendationsTrfItem
    accuracy: RecommendationsTrfItem


class RecommendationSchema(BaseModel):
    word_vectors: Optional[str] = None
    transformer: Optional[RecommendationsTrf] = None


@init_cli.command("config")
def init_config_cli(
    # fmt: off
    output_file: Path = Arg("-", help="File to save config.cfg to (or - for stdout)", allow_dash=True),
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


@init_cli.command("fill-config")
def init_fill_config_cli(
    # fmt: off
    base_path: Path = Arg(..., help="Base config to fill", exists=True, dir_okay=False),
    output_file: Path = Arg("-", help="File to save config.cfg to (or - for stdout)", allow_dash=True),
    diff: bool = Opt(False, "--diff", "-D", help="Print a visual diff highlighting the changes")
    # fmt: on
):
    """
    Fill partial config.cfg with default values. Will add all missing settings
    from the default config and will create all objects, check the registered
    functions for their default values and update the base config. This command
    can be used with a config generated via the training quickstart widget:
    https://nightly.spacy.io/usage/training#quickstart
    """
    fill_config(output_file, base_path, diff=diff)


def fill_config(
    output_file: Path, base_path: Path, *, diff: bool = False
) -> Tuple[Config, Config]:
    is_stdout = str(output_file) == "-"
    msg = Printer(no_print=is_stdout)
    with show_validation_error(hint_fill=False):
        config = util.load_config(base_path)
        nlp, _ = util.load_model_from_config(config, auto_fill=True)
    before = config.to_str()
    after = nlp.config.to_str()
    if before == after:
        msg.warn("Nothing to auto-fill: base config is already complete")
    else:
        msg.good("Auto-filled config with all values")
    if diff and not is_stdout:
        if before == after:
            msg.warn("No diff to show: nothing was auto-filled")
        else:
            msg.divider("START CONFIG DIFF")
            print("")
            print(diff_strings(before, after))
            msg.divider("END CONFIG DIFF")
            print("")
    save_config(nlp.config, output_file, is_stdout=is_stdout)


def init_config(
    output_file: Path, *, lang: str, pipeline: List[str], optimize: str, cpu: bool
) -> None:
    is_stdout = str(output_file) == "-"
    msg = Printer(no_print=is_stdout)
    try:
        from jinja2 import Template
    except ImportError:
        msg.fail("This command requires jinja2", "pip install jinja2", exits=1)
    recommendations = srsly.read_json(RECOMMENDATIONS_PATH)
    lang_defaults = util.get_lang_class(lang).Defaults
    has_letters = lang_defaults.writing_system.get("has_letters", True)
    # Filter out duplicates since tok2vec and transformer are added by template
    pipeline = [pipe for pipe in pipeline if pipe not in ("tok2vec", "transformer")]
    reco = RecommendationSchema(**recommendations.get(lang, {})).dict()
    with TEMPLATE_PATH.open("r") as f:
        template = Template(f.read())
    variables = {
        "lang": lang,
        "components": pipeline,
        "optimize": optimize,
        "hardware": "cpu" if cpu else "gpu",
        "transformer_data": reco["transformer"],
        "word_vectors": reco["word_vectors"],
        "has_letters": has_letters,
    }
    base_template = template.render(variables).strip()
    # Giving up on getting the newlines right in jinja for now
    base_template = re.sub(r"\n\n\n+", "\n\n", base_template)
    # Access variables declared in templates
    template_vars = template.make_module(variables)
    use_case = {
        "Language": lang,
        "Pipeline": ", ".join(pipeline),
        "Optimize for": optimize,
        "Hardware": variables["hardware"].upper(),
        "Transformer": template_vars.transformer.get("name", False),
    }
    msg.info("Generated template specific for your use case")
    for label, value in use_case.items():
        msg.text(f"- {label}: {value}")
    use_transformer = bool(template_vars.use_transformer)
    if use_transformer:
        require_spacy_transformers(msg)
    with show_validation_error(hint_fill=False):
        config = util.load_config_from_str(base_template)
        nlp, _ = util.load_model_from_config(config, auto_fill=True)
    if use_transformer:
        nlp.config.pop("pretraining", {})  # TODO: solve this better
    msg.good("Auto-filled config with all values")
    save_config(nlp.config, output_file, is_stdout=is_stdout)


def save_config(config: Config, output_file: Path, is_stdout: bool = False) -> None:
    msg = Printer(no_print=is_stdout)
    if is_stdout:
        print(config.to_str())
    else:
        config.to_disk(output_file, interpolate=False)
        msg.good("Saved config", output_file)
        msg.text("You can now add your data and train your model:")
        variables = ["--paths.train ./train.spacy", "--paths.dev ./dev.spacy"]
        print(f"{COMMAND} train {output_file.parts[-1]} {' '.join(variables)}")


def require_spacy_transformers(msg: Printer) -> None:
    try:
        import spacy_transformers  # noqa: F401
    except ImportError:
        msg.fail(
            "Using a transformer-based pipeline requires spacy-transformers "
            "to be installed.",
            exits=1,
        )
