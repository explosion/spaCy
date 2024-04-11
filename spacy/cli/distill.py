import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union

import typer
from wasabi import msg

from .. import util
from ..pipeline.trainable_pipe import TrainablePipe
from ..schemas import ConfigSchemaDistill
from ..training.initialize import init_nlp_student
from ..training.loop import distill as distill_nlp
from ._util import (
    Arg,
    Opt,
    app,
    import_code_paths,
    parse_config_overrides,
    setup_gpu,
    show_validation_error,
)


@app.command(
    "distill",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def distill_cli(
    # fmt: off
    ctx: typer.Context,  # This is only used to read additional arguments
    teacher_model: str = Arg(..., help="Teacher model name or path"),
    student_config_path: Path = Arg(..., help="Path to config file", exists=True, allow_dash=True),
    output_path: Optional[Path] = Opt(None, "--output", "--output-path", "-o", help="Output directory to store trained pipeline in"),
    code_path: str = Opt("", "--code", "-c", help="Comma-separated paths to Python files with additional code (registered functions) to be imported"),
    verbose: bool = Opt(False, "--verbose", "-V", "-VV", help="Display more information for debugging purposes"),
    use_gpu: int = Opt(-1, "--gpu-id", "-g", help="GPU ID or -1 for CPU")
    # fmt: on
):
    """
    Distill a spaCy pipeline from a teacher model.

    DOCS: https://spacy.io/api/cli#distill
    """
    util.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    overrides = parse_config_overrides(ctx.args)
    import_code_paths(code_path)
    distill(
        teacher_model,
        student_config_path,
        output_path,
        use_gpu=use_gpu,
        overrides=overrides,
    )


def distill(
    teacher_model: Union[str, Path],
    student_config_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    *,
    use_gpu: int = -1,
    overrides: Dict[str, Any] = util.SimpleFrozenDict(),
):
    student_config_path = util.ensure_path(student_config_path)
    output_path = util.ensure_path(output_path)
    # Make sure all files and paths exist if they are needed
    if not student_config_path or (
        str(student_config_path) != "-" and not student_config_path.exists()
    ):
        msg.fail("Student config file not found", student_config_path, exits=1)
    if not output_path:
        msg.info("No output directory provided")
    else:
        if not output_path.exists():
            output_path.mkdir(parents=True)
            msg.good(f"Created output directory: {output_path}")
        msg.info(f"Saving to output directory: {output_path}")
    setup_gpu(use_gpu)
    teacher = util.load_model(teacher_model)
    with show_validation_error(student_config_path):
        config = util.load_config(
            student_config_path, overrides=overrides, interpolate=False
        )
    msg.divider("Initializing student pipeline")
    with show_validation_error(student_config_path, hint_fill=False):
        student = init_nlp_student(config, teacher, use_gpu=use_gpu)

    msg.good("Initialized student pipeline")
    msg.divider("Distilling student pipeline from teacher")
    distill_nlp(
        teacher,
        student,
        output_path,
        use_gpu=use_gpu,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
