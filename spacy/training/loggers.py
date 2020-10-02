from typing import Dict, Any, Tuple, Callable, List, Optional
import wasabi
import tqdm

from ..util import registry
from .. import util
from ..errors import Errors


@registry.loggers("spacy.ConsoleLogger.v1")
def console_logger(progress_bar: bool=False):
    def setup_printer(
        nlp: "Language",
        printer: Optional[wasabi.Printer]=wasabi.Printer()
    ) -> Tuple[Callable[[Dict[str, Any]], None], Callable]:
        msg = printer if printer is not None else Printer(no_print=True)
        # we assume here that only components are enabled that should be trained & logged
        logged_pipes = nlp.pipe_names
        eval_frequency = nlp.config["training"]["eval_frequency"]
        score_weights = nlp.config["training"]["score_weights"]
        score_cols = [col for col, value in score_weights.items() if value is not None]
        score_widths = [max(len(col), 6) for col in score_cols]
        loss_cols = [f"Loss {pipe}" for pipe in logged_pipes]
        loss_widths = [max(len(col), 8) for col in loss_cols]
        table_header = ["E", "#"] + loss_cols + score_cols + ["Score"]
        table_header = [col.upper() for col in table_header]
        table_widths = [3, 6] + loss_widths + score_widths + [6]
        table_aligns = ["r" for _ in table_widths]
        msg.row(table_header, widths=table_widths)
        msg.row(["-" * width for width in table_widths])
        progress = None

        def log_step(info: Optional[Dict[str, Any]]):
            nonlocal progress

            if info is None:
                # If we don't have a new checkpoint, just return.
                if progress is not None:
                    progress.update(1)
                return 
            try:
                losses = [
                    "{0:.2f}".format(float(info["losses"][pipe_name]))
                    for pipe_name in logged_pipes
                ]
            except KeyError as e:
                raise KeyError(
                    Errors.E983.format(
                        dict="scores (losses)",
                        key=str(e),
                        keys=list(info["losses"].keys()),
                    )
                ) from None

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
            msg.row(data, widths=table_widths, aligns=table_aligns)
            if progress_bar:
                progress = create_tqdm_progress(info["epoch"] + 1, eval_frequency)


        def finalize():
            pass

        return log_step, finalize

    return setup_printer


@registry.loggers("spacy.WandbLogger.v1")
def wandb_logger(project_name: str, remove_config_values: List[str] = []):
    import wandb

    console = console_logger(progress_bar=False)

    def setup_logger(
        nlp: "Language",
        printer: Optional[wasabi.Printer]=wasabi.Printer()
    ) -> Tuple[Callable[[Dict[str, Any]], None], Callable]:
        config = nlp.config.interpolate()
        config_dot = util.dict_to_dot(config)
        for field in remove_config_values:
            del config_dot[field]
        config = util.dot_to_dict(config_dot)
        wandb.init(project=project_name, config=config, reinit=True)
        console_log_step, console_finalize = console(nlp, printer)

        def log_step(info: Optional[Dict[str, Any]]):
            console_log_step(info)
            if info is not None:
                score = info["score"]
                other_scores = info["other_scores"]
                losses = info["losses"]
                wandb.log({"score": score})
                if losses:
                    wandb.log({f"loss_{k}": v for k, v in losses.items()})
                if isinstance(other_scores, dict):
                    wandb.log(other_scores)

        def finalize():
            console_finalize()
            wandb.join()

        return log_step, finalize

    return setup_logger


def create_tqdm_progress(epoch: int, eval_frequency: int):
    # Set disable=None, so that it disables on non-TTY
    progress = tqdm.tqdm(total=eval_frequency, disable=None, leave=False)
    progress.set_description(f"Epoch {epoch}")
    return progress
