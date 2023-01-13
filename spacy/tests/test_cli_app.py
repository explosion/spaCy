import os
from pathlib import Path
from typer.testing import CliRunner

from spacy.cli._util import app
from .util import make_tempdir


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
    assert result_benchmark.stdout == result_evaluate.stdout.replace(
        "spacy evaluate", "spacy benchmark accuracy"
    )
