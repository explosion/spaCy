import os
from pathlib import Path
import pytest
import srsly
from typer.testing import CliRunner
from spacy.tokens import DocBin, Doc

from spacy.cli._util import app, get_git_version
from .util import make_tempdir, normalize_whitespace


def has_git():
    try:
        get_git_version()
        return True
    except RuntimeError:
        return False


def test_convert_auto():
    with make_tempdir() as d_in, make_tempdir() as d_out:
        for f in ["data1.iob", "data2.iob", "data3.iob"]:
            Path(d_in / f).touch()

        # ensure that "automatic" suffix detection works
        result = CliRunner().invoke(app, ["convert", str(d_in), str(d_out)])
        assert "Generated output file" in result.stdout
        out_files = os.listdir(d_out)
        assert len(out_files) == 3
        assert "data1.spacy" in out_files
        assert "data2.spacy" in out_files
        assert "data3.spacy" in out_files


def test_convert_auto_conflict():
    with make_tempdir() as d_in, make_tempdir() as d_out:
        for f in ["data1.iob", "data2.iob", "data3.json"]:
            Path(d_in / f).touch()

        # ensure that "automatic" suffix detection warns when there are different file types
        result = CliRunner().invoke(app, ["convert", str(d_in), str(d_out)])
        assert "All input files must be same type" in result.stdout
        out_files = os.listdir(d_out)
        assert len(out_files) == 0


def test_benchmark_accuracy_alias():
    # Verify that the `evaluate` alias works correctly.
    result_benchmark = CliRunner().invoke(app, ["benchmark", "accuracy", "--help"])
    result_evaluate = CliRunner().invoke(app, ["evaluate", "--help"])
    assert normalize_whitespace(result_benchmark.stdout) == normalize_whitespace(
        result_evaluate.stdout.replace("spacy evaluate", "spacy benchmark accuracy")
    )


def test_debug_data_trainable_lemmatizer_cli(en_vocab):
    train_docs = [
        Doc(en_vocab, words=["I", "like", "cats"], lemmas=["I", "like", "cat"]),
        Doc(
            en_vocab,
            words=["Dogs", "are", "great", "too"],
            lemmas=["dog", "be", "great", "too"],
        ),
    ]
    dev_docs = [
        Doc(en_vocab, words=["Cats", "are", "cute"], lemmas=["cat", "be", "cute"]),
        Doc(en_vocab, words=["Pets", "are", "great"], lemmas=["pet", "be", "great"]),
    ]
    with make_tempdir() as d_in:
        train_bin = DocBin(docs=train_docs)
        train_bin.to_disk(d_in / "train.spacy")
        dev_bin = DocBin(docs=dev_docs)
        dev_bin.to_disk(d_in / "dev.spacy")
        # `debug data` requires an input pipeline config
        CliRunner().invoke(
            app,
            [
                "init",
                "config",
                f"{d_in}/config.cfg",
                "--lang",
                "en",
                "--pipeline",
                "trainable_lemmatizer",
            ],
        )
        result_debug_data = CliRunner().invoke(
            app,
            [
                "debug",
                "data",
                f"{d_in}/config.cfg",
                "--paths.train",
                f"{d_in}/train.spacy",
                "--paths.dev",
                f"{d_in}/dev.spacy",
            ],
        )
        # Instead of checking specific wording of the output, which may change,
        # we'll check that this section of the debug output is present.
        assert "= Trainable Lemmatizer =" in result_debug_data.stdout


# project tests

SAMPLE_PROJECT = {
    "title": "Sample project",
    "description": "This is a project for testing",
    "assets": [
        {
            "dest": "assets/spacy-readme.md",
            "url": "https://github.com/explosion/spaCy/raw/dec81508d28b47f09a06203c472b37f00db6c869/README.md",
            "checksum": "411b2c89ccf34288fae8ed126bf652f7",
        },
        {
            "dest": "assets/citation.cff",
            "url": "https://github.com/explosion/spaCy/raw/master/CITATION.cff",
            "checksum": "c996bfd80202d480eb2e592369714e5e",
            "extra": True,
        },
    ],
    "commands": [
        {
            "name": "ok",
            "help": "print ok",
            "script": ["python -c \"print('okokok')\""],
        },
        {
            "name": "create",
            "help": "make a file",
            "script": ["touch abc.txt"],
            "outputs": ["abc.txt"],
        },
        {
            "name": "clean",
            "help": "remove test file",
            "script": ["rm abc.txt"],
        },
    ],
}

SAMPLE_PROJECT_TEXT = srsly.yaml_dumps(SAMPLE_PROJECT)


@pytest.fixture
def project_dir():
    with make_tempdir() as pdir:
        (pdir / "project.yml").write_text(SAMPLE_PROJECT_TEXT)
        yield pdir


def test_project_document(project_dir):
    readme_path = project_dir / "README.md"
    assert not readme_path.exists(), "README already exists"
    result = CliRunner().invoke(
        app, ["project", "document", str(project_dir), "-o", str(readme_path)]
    )
    assert result.exit_code == 0
    assert readme_path.is_file()
    text = readme_path.read_text("utf-8")
    assert SAMPLE_PROJECT["description"] in text


def test_project_assets(project_dir):
    asset_dir = project_dir / "assets"
    assert not asset_dir.exists(), "Assets dir is already present"
    result = CliRunner().invoke(app, ["project", "assets", str(project_dir)])
    assert result.exit_code == 0
    assert (asset_dir / "spacy-readme.md").is_file(), "Assets not downloaded"
    # check that extras work
    result = CliRunner().invoke(app, ["project", "assets", "--extra", str(project_dir)])
    assert result.exit_code == 0
    assert (asset_dir / "citation.cff").is_file(), "Extras not downloaded"


def test_project_run(project_dir):
    # make sure dry run works
    test_file = project_dir / "abc.txt"
    result = CliRunner().invoke(
        app, ["project", "run", "--dry", "create", str(project_dir)]
    )
    assert result.exit_code == 0
    assert not test_file.is_file()
    result = CliRunner().invoke(app, ["project", "run", "create", str(project_dir)])
    assert result.exit_code == 0
    assert test_file.is_file()
    result = CliRunner().invoke(app, ["project", "run", "ok", str(project_dir)])
    assert result.exit_code == 0
    assert "okokok" in result.stdout


@pytest.mark.skipif(not has_git(), reason="git not installed")
@pytest.mark.parametrize(
    "options",
    [
        "",
        # "--sparse",
        "--branch v3",
        "--repo https://github.com/explosion/projects --branch v3",
    ],
)
def test_project_clone(options):
    with make_tempdir() as workspace:
        out = workspace / "project"
        target = "benchmarks/ner_conll03"
        if not options:
            options = []
        else:
            options = options.split()
        result = CliRunner().invoke(
            app, ["project", "clone", target, *options, str(out)]
        )
        assert result.exit_code == 0
        assert (out / "README.md").is_file()


def test_project_push_pull(project_dir):
    proj = dict(SAMPLE_PROJECT)
    remote = "xyz"

    with make_tempdir() as remote_dir:
        proj["remotes"] = {remote: str(remote_dir)}
        proj_text = srsly.yaml_dumps(proj)
        (project_dir / "project.yml").write_text(proj_text)

        test_file = project_dir / "abc.txt"
        result = CliRunner().invoke(app, ["project", "run", "create", str(project_dir)])
        assert result.exit_code == 0
        assert test_file.is_file()
        result = CliRunner().invoke(app, ["project", "push", remote, str(project_dir)])
        assert result.exit_code == 0
        result = CliRunner().invoke(app, ["project", "run", "clean", str(project_dir)])
        assert result.exit_code == 0
        assert not test_file.exists()
        result = CliRunner().invoke(app, ["project", "pull", remote, str(project_dir)])
        assert result.exit_code == 0
        assert test_file.is_file()
