import os
from time import time
import pytest
import srsly
from spacy.cli._util import load_project_config
from spacy.cli.project.run import project_run
from .util import make_tempdir


def test_project_config_multiprocessing_good_case():
    """Confirms that a correct parallel command group is loaded from the project file."""
    project = {
        "commands": [
            {"name": "command1", "script": ["echo", "command1"]},
            {"name": "command2", "script": ["echo", "command2"]},
            {"name": "command3", "script": ["echo", "command3"]},
        ],
        "workflows": {"all": ["command1", {"parallel": ["command2", "command3"]}]},
    }
    with make_tempdir() as d:
        srsly.write_yaml(d / "project.yml", project)
        load_project_config(d)


@pytest.mark.parametrize(
    "workflows",
    [
        {"all": ["command1", {"parallel": ["command2"]}, "command3"]},
        {"all": ["command1", {"parallel": ["command2", "command4"]}]},
        {"all": ["command1", {"parallel": ["command2", "command2"]}]},
        {"all": ["command1", {"serial": ["command2", "command3"]}]},
    ],
)
def test_project_config_multiprocessing_bad_case_workflows(workflows):
    """Confirms that parallel command groups that do not obey various rules
    result in errors:

    - a parallel group with only one command
    - a parallel group with a non-existent command
    - a parallel group containing the same command more than once
    - a parallel group whose dictionary name is not 'parallel'
    """
    project = {
        "commands": [
            {"name": "command1", "script": ["echo", "command1"]},
            {"name": "command2", "script": ["echo", "command2"]},
            {"name": "command3", "script": ["echo", "command3"]},
        ],
        "workflows": workflows,
    }
    with make_tempdir() as d:
        srsly.write_yaml(d / "project.yml", project)
        with pytest.raises(SystemExit):
            load_project_config(d)


@pytest.mark.parametrize("max_parallel_processes", [-1, 0, 1])
def test_project_config_multiprocessing_max_processes_bad_case(max_parallel_processes):
    """Confirms that invalid max_parallel_processes values are not accepted:

    - negative value
    - zero
    - 1 (because the commands in the group can then be executed serially)
    """

    with make_tempdir() as d:
        project = {
            "max_parallel_processes": max_parallel_processes,
            "commands": [
                {
                    "name": "commandA",
                    "script": [" ".join(("touch", os.sep.join((str(d), "A"))))],
                },
                {
                    "name": "commandB",
                    "script": [" ".join(("touch", os.sep.join((str(d), "B"))))],
                },
                {
                    "name": "commandC",
                    "script": [" ".join(("touch", os.sep.join((str(d), "C"))))],
                },
            ],
            "workflows": {"all": [{"parallel": ["commandA", "commandB", "commandC"]}]},
        }
        with make_tempdir() as d:
            srsly.write_yaml(d / "project.yml", project)
            with pytest.raises(SystemExit):
                load_project_config(d)


def test_project_run_multiprocessing_good_case():
    """Executes a parallel command group. The script pscript.py writes to a file, then polls until
    a second file exists. It is executed twice by commands in a parallel group that write
    and read opposite files, thus proving that the commands are being executed simultaneously. It
    then checks if a file f exists, writes to f if f does not already exist and writes to a
    second file if f does already exist. Although the workflow is run twice, the fact that both
    commands should be skipped on the second run mean that these second files should never be written.
    """
    with make_tempdir() as d:

        pscript = """
import sys, os
from time import sleep

_, d_path, in_filename, out_filename, first_flag_filename, second_flag_filename = sys.argv
with open(os.sep.join((d_path, out_filename)), 'w') as out_file:
    out_file.write("")
while True:
    if os.path.exists(os.sep.join((d_path, in_filename))):
        break
    sleep(0.1)
if not os.path.exists(os.sep.join((d_path, first_flag_filename))):    
    with open(os.sep.join((d_path, first_flag_filename)), 'w') as first_flag_file:
        first_flag_file.write("")
else: # should never happen because of skipping
    with open(os.sep.join((d_path, second_flag_filename)), 'w') as second_flag_file:
        second_flag_file.write("")
        """

        pscript_loc = os.sep.join((str(d), "pscript.py"))
        with open(pscript_loc, "w") as pscript_file:
            pscript_file.write(pscript)
        os.chmod(pscript_loc, 0o777)
        project = {
            "commands": [
                {
                    "name": "commandA",
                    "script": [
                        " ".join(("python", pscript_loc, str(d), "a", "b", "c", "d"))
                    ],
                    "outputs": [os.sep.join((str(d), "f"))],
                    # output should work even if file doesn't exist
                },
                {
                    "name": "commandB",
                    "script": [
                        " ".join(("python", pscript_loc, str(d), "b", "a", "e", "f"))
                    ],
                    "outputs": [os.sep.join((str(d), "e"))],
                },
            ],
            "workflows": {
                "all": [
                    {"parallel": ["commandA", "commandB"]},
                    {"parallel": ["commandB", "commandA"]},
                ]
            },
        }
        srsly.write_yaml(d / "project.yml", project)
        load_project_config(d)
        project_run(d, "all")
        assert os.path.exists(os.sep.join((str(d), "c")))
        assert os.path.exists(os.sep.join((str(d), "e")))
        assert not os.path.exists(os.sep.join((str(d), "d")))
        assert not os.path.exists(os.sep.join((str(d), "f")))


@pytest.mark.parametrize("max_parallel_processes", [2, 3, 4, 5, 6])
def test_project_run_multiprocessing_max_processes_good_case(max_parallel_processes):
    """Confirms that no errors are thrown when a parallel group is executed
    with various values of max_parallel_processes.
    """
    with make_tempdir() as d:

        project = {
            "max_parallel_processes": max_parallel_processes,
            "commands": [
                {
                    "name": "commandA",
                    "script": [" ".join(("touch", os.sep.join((str(d), "A"))))],
                },
                {
                    "name": "commandB",
                    "script": [" ".join(("touch", os.sep.join((str(d), "B"))))],
                },
                {
                    "name": "commandC",
                    "script": [" ".join(("touch", os.sep.join((str(d), "C"))))],
                },
                {
                    "name": "commandD",
                    "script": [" ".join(("touch", os.sep.join((str(d), "D"))))],
                },
                {
                    "name": "commandE",
                    "script": [" ".join(("touch", os.sep.join((str(d), "E"))))],
                },
            ],
            "workflows": {
                "all": [
                    {
                        "parallel": [
                            "commandA",
                            "commandB",
                            "commandC",
                            "commandD",
                            "commandE",
                        ]
                    }
                ]
            },
        }
        srsly.write_yaml(d / "project.yml", project)
        load_project_config(d)
        project_run(d, "all")
        assert os.path.exists(os.sep.join((str(d), "A")))
        assert os.path.exists(os.sep.join((str(d), "B")))
        assert os.path.exists(os.sep.join((str(d), "C")))
        assert os.path.exists(os.sep.join((str(d), "D")))
        assert os.path.exists(os.sep.join((str(d), "E")))


@pytest.mark.parametrize("failing_command", ["python", "someNotExistentOSCommand"])
def test_project_run_multiprocessing_failure(failing_command: str):
    """Confirms that when one command in a parallel group fails, the other commands
    are terminated. The script has two arguments: the number of seconds for which
    to sleep, and the return code. One command in a group is terminated immediately
    with a non-zero return code, the other two commands after several seconds with
    zero return codes. Measuring the execution length for the whole group shows
    whether or not the sleeping processes were successfully terminated."""
    with make_tempdir() as d:

        pscript = """
import sys
from time import sleep

_, sleep_secs, rc = sys.argv
sleep(int(sleep_secs))
sys.exit(int(rc))
        """

        pscript_loc = os.sep.join((str(d), "pscript.py"))
        with open(pscript_loc, "w") as pscript_file:
            pscript_file.write(pscript)
        os.chmod(pscript_loc, 0o777)
        project = {
            "commands": [
                {
                    "name": "commandA",
                    "script": [" ".join(("python", pscript_loc, "15", "0"))],
                },
                {
                    "name": "commandB",
                    "script": [" ".join((failing_command, pscript_loc, "0", "1"))],
                },
                {
                    "name": "commandC",
                    "script": [" ".join(("python", pscript_loc, "10", "0"))],
                },
            ],
            "workflows": {
                "all": [
                    {"parallel": ["commandA", "commandB", "commandC"]},
                    "commandC",
                ]
            },
        }
        srsly.write_yaml(d / "project.yml", project)
        load_project_config(d)
        start = time()
        with pytest.raises(SystemExit) as rc_e:
            project_run(d, "all")
        if os.name == "nt":
            # because in Windows the terminated process has rc=15 rather than rc=-15,
            # 15 is the highest rc rather than 1.
            assert rc_e.value.code == 15
        else:
            assert rc_e.value.code == 1
        assert (
            time() - start < 5
        ), "Test took too long, subprocess seems not to have been terminated"
