import re
from pathlib import Path
from typing import Optional

import typer


def main(
    filename: Path, out_file: Optional[Path] = typer.Option(None), dry_run: bool = False
):
    """Add pytest issue markers on regression tests

    If --out-file is not used, it will overwrite the original file. You can set
    the --dry-run flag to just see the changeset and not write to disk.
    """
    lines = []
    with filename.open() as f:
        lines = f.readlines()

    # Regex pattern for matching common regression formats (e.g. test_issue1234)
    pattern = r"def test_issue\d{1,4}"
    regex = re.compile(pattern)

    new_lines = []
    for line_text in lines:
        if regex.search(line_text):  # if match, append marker first
            issue_num = int(re.findall(r"\d+", line_text)[0])  # Simple heuristic
            typer.echo(f"Found: {line_text} with issue number: {issue_num}")
            new_lines.append(f"@pytest.mark.issue({issue_num})\n")
        new_lines.append(line_text)

    # Save to file
    if not dry_run:
        out = out_file or filename
        with out.open("w") as f:
            for new_line in new_lines:
                f.write(new_line)


if __name__ == "__main__":
    typer.run(main)
