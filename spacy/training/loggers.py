from typing import TYPE_CHECKING, Dict, Any, Tuple, Callable, List, Optional, IO
from wasabi import Printer
import tqdm
import sys

from ..util import registry
from ..errors import Errors

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


@registry.loggers("spacy.ConsoleLogger.v1")
def console_logger(progress_bar: bool = False):
    def setup_printer(
        nlp: "Language", stdout: IO = sys.stdout, stderr: IO = sys.stderr
    ) -> Tuple[Callable[[Optional[Dict[str, Any]]], None], Callable[[], None]]:
        write = lambda text: print(text, file=stdout, flush=True)
        msg = Printer(no_print=True)
        # ensure that only trainable components are logged
        logged_pipes = [
            name
            for name, proc in nlp.pipeline
            if hasattr(proc, "is_trainable") and proc.is_trainable
        ]
        eval_frequency = nlp.config["training"]["eval_frequency"]
        score_weights = nlp.config["training"]["score_weights"]
        score_cols = [col for col, value in score_weights.items() if value is not None]
        loss_cols = [f"Loss {pipe}" for pipe in logged_pipes]
        spacing = 2
        table_header, table_widths, table_aligns = setup_table(
            cols=["E", "#"] + loss_cols + score_cols + ["Score"],
            widths=[3, 6] + [8 for _ in loss_cols] + [6 for _ in score_cols] + [6],
        )
        write(msg.row(table_header, widths=table_widths, spacing=spacing))
        write(msg.row(["-" * width for width in table_widths], spacing=spacing))
        progress = None

        def log_step(info: Optional[Dict[str, Any]]) -> None:
            nonlocal progress

            if info is None:
                # If we don't have a new checkpoint, just return.
                if progress is not None:
                    progress.update(1)
                return
            losses = [
                "{0:.2f}".format(float(info["losses"][pipe_name]))
                for pipe_name in logged_pipes
            ]

            scores = []
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

            data = (
                [info["epoch"], info["step"]]
                + losses
                + scores
                + ["{0:.2f}".format(float(info["score"]))]
            )
            if progress is not None:
                progress.close()
            write(
                msg.row(data, widths=table_widths, aligns=table_aligns, spacing=spacing)
            )
            if progress_bar:
                # Set disable=None, so that it disables on non-TTY
                progress = tqdm.tqdm(
                    total=eval_frequency, disable=None, leave=False, file=stderr
                )
                progress.set_description(f"Epoch {info['epoch']+1}")

        def finalize() -> None:
            pass

        return log_step, finalize

    return setup_printer
