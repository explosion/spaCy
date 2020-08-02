from typing import Optional, List
from pathlib import Path
from thinc.api import Config
from wasabi import msg

from ..util import load_model_from_config, get_lang_class, load_model
from ._util import init_cli, Arg, Opt, show_validation_error


@init_cli.command("config")
def init_config_cli(
    # fmt: off
    output_path: Path = Arg("-", help="Output path or - for stdout", allow_dash=True),
    base_path: Optional[Path] = Opt(None, "--base", "-b", help="Optional base config to fill", exists=True, dir_okay=False),
    model: Optional[str] = Opt(None, "--model", "-m", help="Optional model to copy config from"),
    lang: Optional[str] = Opt(None, "--lang", "-l", help="Optional language code for blank config"),
    pipeline: Optional[str] = Opt(None, "--pipeline", "-p", help="Optional pipeline components to use")
    # fmt: on
):
    """Generate a starter config.cfg for training."""
    validate_cli_args(base_path, model, lang)
    is_stdout = str(output_path) == "-"
    pipeline = [p.strip() for p in pipeline.split(",")] if pipeline else []
    cfg = init_config(output_path, base_path, model, lang, pipeline, silent=is_stdout)
    if is_stdout:
        print(cfg.to_str())
    else:
        cfg.to_disk(output_path)
        msg.good("Saved config", output_path)


def init_config(
    output_path: Path,
    config_path: Optional[Path],
    model: Optional[str],
    lang: Optional[str],
    pipeline: Optional[List[str]],
    silent: bool = False,
) -> Config:
    if config_path is not None:
        msg.info("Generating config from base config", show=not silent)
        with show_validation_error(config_path, hint_init=False):
            config = Config().from_disk(config_path)
            try:
                nlp, _ = load_model_from_config(config, auto_fill=True)
            except ValueError as e:
                msg.fail(str(e), exits=1)
        return nlp.config
    if model is not None:
        ext = f" with pipeline {pipeline}" if pipeline else ""
        msg.info(f"Generating config from model {model}{ext}", show=not silent)
        nlp = load_model(model)
        for existing_pipe_name in nlp.pipe_names:
            if existing_pipe_name not in pipeline:
                nlp.remove_pipe(existing_pipe_name)
        for pipe_name in pipeline:
            if pipe_name not in nlp.pipe_names:
                nlp.add_pipe(pipe_name)
        return nlp.config
    if lang is not None:
        ext = f" with pipeline {pipeline}" if pipeline else ""
        msg.info(f"Generating config for language '{lang}'{ext}", show=not silent)
        nlp = get_lang_class(lang)()
        for pipe_name in pipeline:
            nlp.add_pipe(pipe_name)
        return nlp.config


def validate_cli_args(
    config_path: Optional[Path], model: Optional[str], lang: Optional[str]
) -> None:
    args = {"--base": config_path, "--model": model, "--lang": lang}
    if sum(arg is not None for arg in args.values()) != 1:
        existing = " ".join(f"{a} {v}" for a, v in args.items() if v is not None)
        msg.fail(
            "The init config command expects only one of the following arguments: "
            "--base (base config to fill and update), --lang (language code to "
            "use for blank config) or --model (base model to copy config from).",
            f"Got: {existing if existing else 'no arguments'}",
            exits=1,
        )
