import json
import re
from pathlib import Path


def test_universe_json():

    root_dir = Path(__file__).parent
    universe_file = root_dir / "universe.json"

    with universe_file.open() as f:
        universe_data = json.load(f)
        for entry in universe_data["resources"]:
            if "github" in entry:
                assert not re.match(
                    r"^(http:)|^(https:)", entry["github"]
                ), "Github field should be user/repo, not a url"
