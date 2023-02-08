import pytest
import os
from pathlib import Path
from spacy.tokens import DocBin, Doc
from spacy.cli._util import cli

from .util import make_tempdir, normalize_whitespace


@pytest.fixture(scope="session")
def all_commands():
    result = [*cli.commands.values()]
    for subcommands in cli.subcommands.values():
        result.extend(subcommands.values())
    return result


def test_help_texts(all_commands):
    """Test that all commands provide docstrings and argument help texts."""
    for command in all_commands:
        assert command.description, f"no docstring for {command.display_name}"
        for arg in command.args:
            if arg.id == cli.extra_key:
                continue
            assert arg.arg.help, f"no help text for {command.display_name} -> {arg.id}"


def test_convert_auto(capsys):
    with make_tempdir() as d_in, make_tempdir() as d_out:
        for f in ["data1.iob", "data2.iob", "data3.iob"]:
            Path(d_in / f).touch()

        # ensure that "automatic" suffix detection works
        cli.run(["spacy", "convert", str(d_in), str(d_out)])
        captured = capsys.readouterr()
        assert "Generated output file" in captured.out
        out_files = os.listdir(d_out)
        assert len(out_files) == 3
        assert "data1.spacy" in out_files
        assert "data2.spacy" in out_files
        assert "data3.spacy" in out_files


def test_convert_auto_conflict(capsys):
    with make_tempdir() as d_in, make_tempdir() as d_out:
        for f in ["data1.iob", "data2.iob", "data3.json"]:
            Path(d_in / f).touch()

        # ensure that "automatic" suffix detection warns when there are different file types
        with pytest.raises(SystemExit):
            cli.run(["spacy", "convert", str(d_in), str(d_out)])
        captured = capsys.readouterr()
        assert "All input files must be same type" in captured.out
        out_files = os.listdir(d_out)
        assert len(out_files) == 0


def test_benchmark_accuracy_alias(capsys):
    # Verify that the `evaluate` alias works correctly.
    with pytest.raises(SystemExit):
        cli.run(["spacy", "benchmark", "accuracy", "--help"])
    captured = capsys.readouterr()
    result_benchmark = normalize_whitespace(str(captured.out))
    with pytest.raises(SystemExit):
        cli.run(["spacy", "evaluate", "--help"])
    captured = capsys.readouterr()
    result_evaluate = normalize_whitespace(str(captured.out))
    assert result_benchmark == result_evaluate.replace(
        "spacy evaluate", "spacy benchmark accuracy"
    )


def test_debug_data_trainable_lemmatizer_cli(en_vocab, capsys):
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
        args = [
            "spacy",
            "init",
            "config",
            f"{d_in}/config.cfg",
            "--lang",
            "en",
            "--pipeline",
            "trainable_lemmatizer",
        ]
        cli.run(args)
        args = [
            "spacy",
            "debug",
            "data",
            f"{d_in}/config.cfg",
            "--paths.train",
            f"{d_in}/train.spacy",
            "--paths.dev",
            f"{d_in}/dev.spacy",
        ]
        with pytest.raises(SystemExit):
            cli.run(args)
        captured = capsys.readouterr()
        # Instead of checking specific wording of the output, which may change,
        # we'll check that this section of the debug output is present.
        assert "= Trainable Lemmatizer =" in captured.out
