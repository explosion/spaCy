from wasabi import msg

from ._util import app, setup_cli  # noqa: F401
from .apply import apply  # noqa: F401
from .assemble import assemble_cli  # noqa: F401

# These are the actual functions, NOT the wrapped CLI commands. The CLI commands
# are registered automatically and won't have to be imported here.
from .benchmark_speed import benchmark_speed_cli  # noqa: F401
from .convert import convert  # noqa: F401
from .debug_config import debug_config  # noqa: F401
from .debug_data import debug_data  # noqa: F401
from .debug_diff import debug_diff  # noqa: F401
from .debug_model import debug_model  # noqa: F401
from .download import download  # noqa: F401
from .evaluate import evaluate  # noqa: F401
from .find_function import find_function  # noqa: F401
from .find_threshold import find_threshold  # noqa: F401
from .info import info  # noqa: F401
from .init_config import fill_config, init_config  # noqa: F401
from .init_pipeline import init_pipeline_cli  # noqa: F401
from .package import package  # noqa: F401
from .pretrain import pretrain  # noqa: F401
from .profile import profile  # noqa: F401
from .project.assets import project_assets  # type: ignore[attr-defined]  # noqa: F401
from .project.clone import project_clone  # type: ignore[attr-defined]  # noqa: F401
from .project.document import (  # type: ignore[attr-defined]  # noqa: F401
    project_document,
)
from .project.dvc import project_update_dvc  # type: ignore[attr-defined]  # noqa: F401
from .project.pull import project_pull  # type: ignore[attr-defined]  # noqa: F401
from .project.push import project_push  # type: ignore[attr-defined]  # noqa: F401
from .project.run import project_run  # type: ignore[attr-defined]  # noqa: F401
from .train import train_cli  # type: ignore[attr-defined]  # noqa: F401
from .validate import validate  # type: ignore[attr-defined]  # noqa: F401


@app.command("link", no_args_is_help=True, deprecated=True, hidden=True)
def link(*args, **kwargs):
    """As of spaCy v3.0, symlinks like "en" are not supported anymore. You can load trained
    pipeline packages using their full names or from a directory path."""
    msg.warn(
        "As of spaCy v3.0, model symlinks are not supported anymore. You can load trained "
        "pipeline packages using their full names or from a directory path."
    )
