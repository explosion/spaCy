import json
from functools import lru_cache
from importlib.metadata import entry_points
from importlib.resources import files
from typing import Any, Dict, Set


HELP_OPTIONS = {"--help", "-h"}
PLUGIN_ENTRY_POINT_GROUP = "spacy_cli"
MANIFEST_FILE = "cli_manifest.json"
UNKNOWN_COMMAND_TOKEN = "__SPACY_UNKNOWN_COMMAND__"
UNKNOWN_SUBCOMMAND_TOKEN = "__SPACY_UNKNOWN_SUBCOMMAND__"


@lru_cache(maxsize=1)
def load_manifest() -> Dict[str, Any]:
    data = files("spacy_cli").joinpath(MANIFEST_FILE).read_text(encoding="utf8")
    return json.loads(data)


def get_plugin_command_names() -> Set[str]:
    return {
        entry_point.name for entry_point in entry_points(group=PLUGIN_ENTRY_POINT_GROUP)
    }
