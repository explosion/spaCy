import importlib
import subprocess
import sys

import pytest

from spacy_cli.static import load_manifest

launcher_module = importlib.import_module("spacy_cli.main")


def _run_python(code: str) -> str:
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_cli_package_import_is_lazy():
    output = _run_python(
        "import sys; import spacy.cli; "
        "print('spacy.cli.train' in sys.modules); print('weasel' in sys.modules)"
    )
    assert output.splitlines() == ["False", "False"]


def test_load_for_argv_imports_only_requested_command():
    output = _run_python(
        "import sys; from spacy.cli import load_for_argv; "
        "load_for_argv(['train', '--help']); "
        "print('spacy.cli.train' in sys.modules); print('weasel' in sys.modules)"
    )
    assert output.splitlines() == ["True", "False"]


def test_load_for_argv_imports_project_on_demand():
    output = _run_python(
        "import sys; from spacy.cli import load_for_argv; "
        "load_for_argv(['project', '--help']); print('weasel' in sys.modules)"
    )
    assert output == "True"


def test_manifest_is_current():
    # Run in a subprocess to avoid command registration order being affected
    # by other test modules importing CLI submodules (which register commands
    # as a side effect of import).
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from spacy_cli.build_manifest import build_manifest; "
            "from spacy_cli.static import load_manifest; "
            "assert build_manifest() == load_manifest()",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_launcher_root_help_uses_static(capsys, monkeypatch):
    monkeypatch.setattr(
        launcher_module, "_run_live", lambda: (_ for _ in ()).throw(AssertionError)
    )
    with pytest.raises(SystemExit) as exc:
        launcher_module.main(["--help"])
    assert exc.value.code == 0
    assert capsys.readouterr().out == load_manifest()["root_help"]


def test_launcher_command_help_uses_static(capsys, monkeypatch):
    monkeypatch.setattr(
        launcher_module, "_run_live", lambda: (_ for _ in ()).throw(AssertionError)
    )
    with pytest.raises(SystemExit) as exc:
        launcher_module.main(["train", "--help"])
    assert exc.value.code == 0
    assert capsys.readouterr().out == load_manifest()["command_help"]["train"]


def test_launcher_unknown_command_uses_static_error(capsys, monkeypatch):
    monkeypatch.setattr(
        launcher_module, "_run_live", lambda: (_ for _ in ()).throw(AssertionError)
    )
    with pytest.raises(SystemExit) as exc:
        launcher_module.main(["definitely-not-a-command"])
    assert exc.value.code == 2
    assert "No such command 'definitely-not-a-command'" in capsys.readouterr().out


def test_launcher_non_help_command_falls_back_to_live(monkeypatch):
    called = []

    def fake_run_live():
        called.append(True)

    monkeypatch.setattr(launcher_module, "_run_live", fake_run_live)
    launcher_module.main(["train", "config.cfg"])
    assert called == [True]


def test_launcher_root_help_falls_back_with_plugins(monkeypatch):
    called = []

    def fake_run_live():
        called.append(True)

    monkeypatch.setattr(launcher_module, "_run_live", fake_run_live)
    monkeypatch.setattr(launcher_module, "get_plugin_command_names", lambda: {"custom"})
    launcher_module.main(["--help"])
    assert called == [True]
