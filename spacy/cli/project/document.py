from pathlib import Path

from wasabi import MarkdownRenderer, msg

from ...util import working_dir
from .._util import PROJECT_FILE, Arg, Opt, load_project_config, project_cli

DOCS_URL = "https://spacy.io"
INTRO_PROJECT = f"""The [`{PROJECT_FILE}`]({PROJECT_FILE}) defines the data assets required by the
project, as well as the available commands and workflows. For details, see the
[spaCy projects documentation]({DOCS_URL}/usage/projects)."""
INTRO_COMMANDS = f"""The following commands are defined by the project. They
can be executed using [`spacy project run [name]`]({DOCS_URL}/api/cli#project-run).
Commands are only re-run if their inputs have changed."""
INTRO_WORKFLOWS = f"""The following workflows are defined by the project. They
can be executed using [`spacy project run [name]`]({DOCS_URL}/api/cli#project-run)
and will run the specified commands in order. Commands are only re-run if their
inputs have changed."""
INTRO_ASSETS = f"""The following assets are defined by the project. They can
be fetched by running [`spacy project assets`]({DOCS_URL}/api/cli#project-assets)
in the project directory."""
# These markers are added to the Markdown and can be used to update the file in
# place if it already exists. Only the auto-generated part will be replaced.
MARKER_START = "<!-- SPACY PROJECT: AUTO-GENERATED DOCS START (do not remove) -->"
MARKER_END = "<!-- SPACY PROJECT: AUTO-GENERATED DOCS END (do not remove) -->"
# If this marker is used in an existing README, it's ignored and not replaced
MARKER_IGNORE = "<!-- SPACY PROJECT: IGNORE -->"


@project_cli.command("document")
def project_document_cli(
    # fmt: off
    project_dir: Path = Arg(Path.cwd(), help="Path to cloned project. Defaults to current working directory.", exists=True, file_okay=False),
    output_file: Path = Opt("-", "--output", "-o", help="Path to output Markdown file for output. Defaults to - for standard output"),
    no_emoji: bool = Opt(False, "--no-emoji", "-NE", help="Don't use emoji")
    # fmt: on
):
    """
    Auto-generate a README.md for a project. If the content is saved to a file,
    hidden markers are added so you can add custom content before or after the
    auto-generated section and only the auto-generated docs will be replaced
    when you re-run the command.

    DOCS: https://spacy.io/api/cli#project-document
    """
    project_document(project_dir, output_file, no_emoji=no_emoji)


def project_document(
    project_dir: Path, output_file: Path, *, no_emoji: bool = False
) -> None:
    is_stdout = str(output_file) == "-"
    config = load_project_config(project_dir)
    md = MarkdownRenderer(no_emoji=no_emoji)
    md.add(MARKER_START)
    title = config.get("title")
    description = config.get("description")
    md.add(md.title(1, f"spaCy Project{f': {title}' if title else ''}", "🪐"))
    if description:
        md.add(description)
    md.add(md.title(2, PROJECT_FILE, "📋"))
    md.add(INTRO_PROJECT)
    # Commands
    cmds = config.get("commands", [])
    data = [(md.code(cmd["name"]), cmd.get("help", "")) for cmd in cmds]
    if data:
        md.add(md.title(3, "Commands", "⏯"))
        md.add(INTRO_COMMANDS)
        md.add(md.table(data, ["Command", "Description"]))
    # Workflows
    wfs = config.get("workflows", {}).items()
    data = [(md.code(n), " &rarr; ".join(md.code(w) for w in stp)) for n, stp in wfs]
    if data:
        md.add(md.title(3, "Workflows", "⏭"))
        md.add(INTRO_WORKFLOWS)
        md.add(md.table(data, ["Workflow", "Steps"]))
    # Assets
    assets = config.get("assets", [])
    data = []
    for a in assets:
        source = "Git" if a.get("git") else "URL" if a.get("url") else "Local"
        dest_path = a["dest"]
        dest = md.code(dest_path)
        if source == "Local":
            # Only link assets if they're in the repo
            with working_dir(project_dir) as p:
                if (p / dest_path).exists():
                    dest = md.link(dest, dest_path)
        data.append((dest, source, a.get("description", "")))
    if data:
        md.add(md.title(3, "Assets", "🗂"))
        md.add(INTRO_ASSETS)
        md.add(md.table(data, ["File", "Source", "Description"]))
    md.add(MARKER_END)
    # Output result
    if is_stdout:
        print(md.text)
    else:
        content = md.text
        if output_file.exists():
            with output_file.open("r", encoding="utf8") as f:
                existing = f.read()
            if MARKER_IGNORE in existing:
                msg.warn("Found ignore marker in existing file: skipping", output_file)
                return
            if MARKER_START in existing and MARKER_END in existing:
                msg.info("Found existing file: only replacing auto-generated docs")
                before = existing.split(MARKER_START)[0]
                after = existing.split(MARKER_END)[1]
                content = f"{before}{content}{after}"
            else:
                msg.warn("Replacing existing file")
        with output_file.open("w", encoding="utf8") as f:
            f.write(content)
        msg.good("Saved project documentation", output_file)
