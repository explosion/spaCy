import sys
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

import srsly
import tqdm
from wasabi import Printer

from .. import util
from ..errors import Errors
from ..util import registry

if TYPE_CHECKING:
    from ..language import Language  # noqa: F401


def setup_table(
    *, cols: List[str], widths: List[int], max_width: int = 13
) -> Tuple[List[str], List[int], List[str]]:
    final_cols = []
    final_widths = []
    for col, width in zip(cols, widths):
        if len(col) > max_width:
            col = col[: max_width - 3] + "..."  # shorten column if too long
        final_cols.append(col.upper())
        final_widths.append(max(len(col), width))
    return final_cols, final_widths, ["r" for _ in final_widths]


# We cannot rename this method as it's directly imported
# and used by external packages such as spacy-loggers.
@registry.loggers("spacy.ConsoleLogger.v2")
def console_logger(
    progress_bar: bool = False,
    console_output: bool = True,
    output_file: Optional[Union[str, Path]] = None,
):
    """The ConsoleLogger.v2 prints out training logs in the console and/or saves them to a jsonl file.
    progress_bar (bool): Whether the logger should print a progress bar tracking the steps till the next evaluation pass.
    console_output (bool): Whether the logger should print the logs on the console.
    output_file (Optional[Union[str, Path]]): The file to save the training logs to.
    """
    return console_logger_v3(
        progress_bar=None if progress_bar is False else "eval",
        console_output=console_output,
        output_file=output_file,
    )


@registry.loggers("spacy.ConsoleLogger.v3")
def console_logger_v3(
    progress_bar: Optional[str] = None,
    console_output: bool = True,
    output_file: Optional[Union[str, Path]] = None,
):
    """The ConsoleLogger.v3 prints out training logs in the console and/or saves them to a jsonl file.
    progress_bar (Optional[str]): Type of progress bar to show in the console. Allowed values:
        train - Tracks the number of steps from the beginning of training until the full training run is complete (training.max_steps is reached).
        eval - Tracks the number of steps between the previous and next evaluation (training.eval_frequency is reached).
    console_output (bool): Whether the logger should print the logs on the console.
    output_file (Optional[Union[str, Path]]): The file to save the training logs to.
    """
    _log_exist = False
    if output_file:
        output_file = util.ensure_path(output_file)  # type: ignore
        if output_file.exists():  # type: ignore
            _log_exist = True
        if not output_file.parents[0].exists():  # type: ignore
            output_file.parents[0].mkdir(parents=True)  # type: ignore

    def setup_printer(
        nlp: "Language", stdout: IO = sys.stdout, stderr: IO = sys.stderr
    ) -> Tuple[Callable[[Optional[Dict[str, Any]]], None], Callable[[], None]]:
        write = lambda text: print(text, file=stdout, flush=True)
        msg = Printer(no_print=True)

        nonlocal output_file
        output_stream = None
        if _log_exist:
            write(
                msg.warn(
                    f"Saving logs is disabled because {output_file} already exists."
                )
            )
            output_file = None
        elif output_file:
            write(msg.info(f"Saving results to {output_file}"))
            output_stream = open(output_file, "w", encoding="utf-8")

        # ensure that only trainable components are logged
        logged_pipes = [
            name
            for name, proc in nlp.pipeline
            if hasattr(proc, "is_trainable") and proc.is_trainable
        ]
        max_steps = nlp.config["training"]["max_steps"]
        eval_frequency = nlp.config["training"]["eval_frequency"]
        score_weights = nlp.config["training"]["score_weights"]
        score_cols = [col for col, value in score_weights.items() if value is not None]
        loss_cols = [f"Loss {pipe}" for pipe in logged_pipes]

        if console_output:
            spacing = 2
            table_header, table_widths, table_aligns = setup_table(
                cols=["E", "#"] + loss_cols + score_cols + ["Score"],
                widths=[3, 6] + [8 for _ in loss_cols] + [6 for _ in score_cols] + [6],
            )
            write(msg.row(table_header, widths=table_widths, spacing=spacing))
            write(msg.row(["-" * width for width in table_widths], spacing=spacing))
        progress = None
        expected_progress_types = ("train", "eval")
        if progress_bar is not None and progress_bar not in expected_progress_types:
            raise ValueError(
                Errors.E1048.format(
                    unexpected=progress_bar, expected=expected_progress_types
                )
            )

        def log_step(info: Optional[Dict[str, Any]]) -> None:
            nonlocal progress

            if info is None:
                # If we don't have a new checkpoint, just return.
                if progress is not None:
                    progress.update(1)
                return

            losses = []
            log_losses = {}
            for pipe_name in logged_pipes:
                losses.append("{0:.2f}".format(float(info["losses"][pipe_name])))
                log_losses[pipe_name] = float(info["losses"][pipe_name])

            scores = []
            log_scores = {}
            for col in score_cols:
                score = info["other_scores"].get(col, 0.0)
                try:
                    score = float(score)
                except TypeError:
                    err = Errors.E916.format(name=col, score_type=type(score))
                    raise ValueError(err) from None
                if col != "speed":
                    score *= 100
                scores.append("{0:.2f}".format(score))
                log_scores[str(col)] = score

            data = (
                [info["epoch"], info["step"]]
                + losses
                + scores
                + ["{0:.2f}".format(float(info["score"]))]
            )

            if output_stream:
                # Write to log file per log_step
                log_data = {
                    "epoch": info["epoch"],
                    "step": info["step"],
                    "losses": log_losses,
                    "scores": log_scores,
                    "score": float(info["score"]),
                }
                output_stream.write(srsly.json_dumps(log_data) + "\n")

            if progress is not None:
                progress.close()
            if console_output:
                write(
                    msg.row(
                        data, widths=table_widths, aligns=table_aligns, spacing=spacing
                    )
                )
                if progress_bar:
                    if progress_bar == "train":
                        total = max_steps
                        desc = f"Last Eval Epoch: {info['epoch']}"
                        initial = info["step"]
                    else:
                        total = eval_frequency
                        desc = f"Epoch {info['epoch']+1}"
                        initial = 0
                    # Set disable=None, so that it disables on non-TTY
                    progress = tqdm.tqdm(
                        total=total,
                        disable=None,
                        leave=False,
                        file=stderr,
                        initial=initial,
                    )
                    progress.set_description(desc)

        def finalize() -> None:
            if output_stream:
                output_stream.close()

        return log_step, finalize

    return setup_printer
