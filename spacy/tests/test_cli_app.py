import os
import subprocess
import sys
from pathlib import Path

import pytest
import srsly
from typer.testing import CliRunner

import spacy
from spacy.cli._util import app, get_git_version
from spacy.tokens import Doc, DocBin

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


NOOP_CONFIG = """
[paths]
train = null
dev = null
vectors = null
init_tok2vec = null

[system]
seed = 0
gpu_allocator = null

[nlp]
lang = "mul"
pipeline = ["noop", "noop2"]
disabled = []
before_creation = null
after_creation = null
after_pipeline_creation = null
batch_size = 1000
tokenizer = {"@tokenizers":"spacy.Tokenizer.v1"}

[components]

[components.noop]
factory = "noop"

[components.noop2]
factory = "noop2"

[corpora]

[corpora.dev]
@readers = "spacy.Corpus.v1"
path = ${paths.dev}
gold_preproc = false
max_length = 0
limit = 0
augmenter = null

[corpora.train]
@readers = "spacy.Corpus.v1"
path = ${paths.train}
gold_preproc = false
max_length = 0
limit = 0
augmenter = null

[training]
seed = ${system.seed}
gpu_allocator = ${system.gpu_allocator}
dropout = 0.1
accumulate_gradient = 1
patience = 1600
max_epochs = 0
max_steps = 100
eval_frequency = 200
frozen_components = []
annotating_components = []
dev_corpus = "corpora.dev"

train_corpus = "corpora.train"
before_to_disk = null
before_update = null

[training.batcher]
@batchers = "spacy.batch_by_words.v1"
discard_oversize = false
tolerance = 0.2
get_length = null

[training.batcher.size]
@schedules = "compounding.v1"
start = 100
stop = 1000
compound = 1.001
t = 0.0

[training.logger]
@loggers = "spacy.ConsoleLogger.v1"
progress_bar = false

[training.optimizer]
@optimizers = "Adam.v1"
beta1 = 0.9
beta2 = 0.999
L2_is_weight_decay = true
L2 = 0.01
grad_clip = 1.0
use_averages = false
eps = 0.00000001
learn_rate = 0.001

[training.score_weights]

[pretraining]

[initialize]
vectors = ${paths.vectors}
init_tok2vec = ${paths.init_tok2vec}
vocab_data = null
lookups = null
before_init = null
after_init = null

[initialize.components]

[initialize.tokenizer]
"""


@pytest.fixture
def data_paths():
    nlp = spacy.blank("mul")
    doc = nlp("ok")
    with make_tempdir() as tdir:
        db = DocBin()
        # debug data will *fail* if there aren't enough docs
        for ii in range(100):
            db.add(doc)
        fpath = tdir / "data.spacy"
        db.to_disk(fpath)

        args = [
            "--paths.train",
            str(fpath),
            "--paths.dev",
            str(fpath),
        ]
        yield args


@pytest.fixture
def code_paths():
    noop_base = """
from spacy.language import Language

@Language.component("{}")
def noop(doc):
    return doc
"""

    with make_tempdir() as temp_d:
        # write code files to load
        paths = []
        for ff in ["noop", "noop2"]:
            pyfile = temp_d / f"{ff}.py"
            pyfile.write_text(noop_base.format(ff))
            paths.append(pyfile)

        args = ["--code", ",".join([str(pp) for pp in paths])]
        yield args


@pytest.fixture
def noop_config():
    with make_tempdir() as temp_d:
        cfg = temp_d / "config.cfg"
        cfg.write_text(NOOP_CONFIG)

        yield cfg


@pytest.mark.slow
@pytest.mark.parametrize(
    "cmd",
    ["debug config", "debug data", "train", "assemble"],
)
def test_multi_code(cmd, code_paths, data_paths, noop_config):
    # check that it fails without the code arg
    cmd = cmd.split()
    output = ["."] if cmd[0] == "assemble" else []
    cmd = [sys.executable, "-m", "spacy"] + cmd
    result = subprocess.run([*cmd, str(noop_config), *output, *data_paths])
    assert result.returncode == 1

    # check that it succeeds with the code arg
    result = subprocess.run([*cmd, str(noop_config), *output, *data_paths, *code_paths])
    assert result.returncode == 0


@pytest.mark.slow
def test_multi_code_evaluate(code_paths, data_paths, noop_config):
    # Evaluation requires a model, not a config, so this works differently from
    # the other commands.

    # Train a model to evaluate
    cmd = f"{sys.executable} -m spacy train {noop_config} -o model".split()
    result = subprocess.run([*cmd, *data_paths, *code_paths])
    assert result.returncode == 0

    # now do the evaluation

    eval_data = data_paths[-1]
    cmd = f"{sys.executable} -m spacy evaluate model/model-best {eval_data}".split()

    # check that it fails without the code arg
    result = subprocess.run(cmd)
    assert result.returncode == 1

    # check that it succeeds with the code arg
    result = subprocess.run([*cmd, *code_paths])
    assert result.returncode == 0


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

CFG_FILE = "myconfig.cfg"

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
            "script": [f"python -m spacy init config {CFG_FILE}"],
            "outputs": [f"{CFG_FILE}"],
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
    test_file = project_dir / CFG_FILE
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

        test_file = project_dir / CFG_FILE
        result = CliRunner().invoke(app, ["project", "run", "create", str(project_dir)])
        assert result.exit_code == 0
        assert test_file.is_file()
        result = CliRunner().invoke(app, ["project", "push", remote, str(project_dir)])
        assert result.exit_code == 0
        test_file.unlink()
        assert not test_file.exists()
        result = CliRunner().invoke(app, ["project", "pull", remote, str(project_dir)])
        assert result.exit_code == 0
        assert test_file.is_file()
