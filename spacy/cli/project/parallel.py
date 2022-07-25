"""
Permits the execution of a parallel command group.

The main process starts a worker process for each spaCy projects command in the parallel group.
Each spaCy projects command consists of n OS level commands. The worker process starts
subprocesses for these OS level commands serially, and sends status information about their
execution back to the main process.

The main process maintains a state machine for each spaCy projects command/worker process. The meaning
of the states is documented alongside the _ParallelCommandInfo.STATES code. Note that the distinction
between the states 'failed' and 'terminated' is not meaningful on Windows, so that both are displayed
as 'failed/terminated' on Windows systems.
"""
from typing import Any, List, Optional, Dict, Union, cast, Iterator
import os
import sys
import queue
from pathlib import Path
from time import time
from multiprocessing import Manager, Queue, get_context
from multiprocessing.context import SpawnProcess
from tempfile import mkdtemp
from signal import SIGTERM
from subprocess import STDOUT, Popen, TimeoutExpired
from dataclasses import dataclass, field
from wasabi import msg
from wasabi.util import color, supports_ansi

from .._util import check_rerun, check_deps, update_lockfile, load_project_config
from ...util import SimpleFrozenDict, working_dir, split_command, join_command
from ...util import check_bool_env_var, ENV_VARS
from ...errors import Errors

# Use spawn to create worker processes on all OSs for consistency
mp_context = get_context("spawn")

# How often the worker processes managing the commands in a parallel group
# send keepalive messages to the main process (seconds)
PARALLEL_GROUP_STATUS_INTERVAL = 1

# The maximum permissible width of divider text describing a parallel command group
MAX_WIDTH_DIVIDER = 60

# Whether or not to display realtime status information
DISPLAY_STATUS_TABLE = sys.stdout.isatty() and supports_ansi()


@dataclass
class _ParallelCommandState:
    name: str
    display_color: str
    # transitions: the names of states that can legally follow this state
    transitions: List = field(default_factory=list)


class _ParallelCommandInfo:

    STATES = (
        # The command has not yet been run
        _ParallelCommandState(
            "pending", "yellow", ["starting", "cancelled", "not rerun"]
        ),
        # The command was not run because its settings, inputs and outputs had not changed
        # since a previous successful run
        _ParallelCommandState("not rerun", "blue"),
        # The main process has spawned a worker process for the command but not yet received
        # an acknowledgement
        _ParallelCommandState("starting", "green", ["running", "failed", "hung"]),
        # The command is running
        _ParallelCommandState(
            "running", "green", ["running", "succeeded", "failed", "terminated", "hung"]
        ),
        # The command succeeded (rc=0)
        _ParallelCommandState("succeeded", "green"),
        # The command failed (rc>0)
        _ParallelCommandState("failed", "red"),
        # The command was terminated (rc<0), usually but not necessarily by the main process because
        # another command within the same parallel group failed
        _ParallelCommandState("terminated", "red"),
        # The main process would expect the worker process to be running, but the worker process has
        # not communicated with the main process for an extended period of time
        _ParallelCommandState("hung", "red"),
        # The main process did not attempt to execute the command because another command in the same
        # parallel group had already failed
        _ParallelCommandState("cancelled", "red"),
    )

    state_dict = {state.name: state for state in STATES}

    def __init__(self, cmd_name: str, cmd: Dict, cmd_index: int):
        self.cmd_name = cmd_name
        self.cmd = cmd
        self.cmd_index = cmd_index
        self.state = _ParallelCommandInfo.state_dict["pending"]
        self.pid: Optional[int] = None
        self.last_keepalive_time: Optional[int] = None
        self.running_os_cmd_index: Optional[int] = None
        self.rc: Optional[int] = None
        self.console_output: Optional[str] = None

    def change_state(self, new_state: str):
        if new_state not in self.state.transitions:
            raise RuntimeError(
                Errors.E1044.format(old_state=self.state.name, new_state=new_state)
            )
        self.state = _ParallelCommandInfo.state_dict[new_state]

    @property
    def state_repr(self) -> str:
        state_str = self.state.name
        if state_str == "running" and self.running_os_cmd_index is not None:
            number_of_os_cmds = len(self.cmd["script"])
            state_str = (
                f"{state_str} ({self.running_os_cmd_index + 1}/{number_of_os_cmds})"
            )
        elif state_str in ("failed", "terminated") and os.name == "nt":
            state_str = "failed/terminated"
        # we know ANSI commands are available because otherwise
        # the status table would not be being displayed in the first place
        return color(state_str, self.state.display_color)


def project_run_parallel_group(
    project_dir: Path,
    cmd_names: List[str],
    *,
    overrides: Dict[str, Any] = SimpleFrozenDict(),
    force: bool = False,
    dry: bool = False,
) -> None:
    """Run a parallel group of commands. Note that because of the challenges of managing
    parallel console output streams it is not possible to specify a value for 'capture' as
    when executing commands serially. Essentially, with parallel groups 'capture==True'.

    project_dir (Path): Path to project directory.
    cmd_names: the names of the spaCy projects commands to run.
    overrides (Dict[str, Any]): Optional config overrides.
    force (bool): Force re-running, even if nothing changed.
    dry (bool): Perform a dry run and don't execute commands.
    """
    config = load_project_config(project_dir, overrides=overrides)
    commands = {cmd["name"]: cmd for cmd in config.get("commands", [])}
    check_spacy_commit = check_bool_env_var(ENV_VARS.PROJECT_USE_GIT_VERSION)
    max_parallel_processes = config.get("max_parallel_processes")
    cmd_infos = [
        _ParallelCommandInfo(cmd_name, commands[cmd_name], cmd_index)
        for cmd_index, cmd_name in enumerate(cmd_names)
    ]
    temp_log_dir = mkdtemp()

    with working_dir(project_dir) as current_dir:

        divider_parallel_descriptor = parallel_descriptor = (
            "parallel[" + ", ".join(cmd_info.cmd_name for cmd_info in cmd_infos) + "]"
        )
        if len(divider_parallel_descriptor) > MAX_WIDTH_DIVIDER:
            divider_parallel_descriptor = (
                divider_parallel_descriptor[: (MAX_WIDTH_DIVIDER - 3)] + "..."
            )
        msg.divider(divider_parallel_descriptor)
        if not DISPLAY_STATUS_TABLE and len(parallel_descriptor) > MAX_WIDTH_DIVIDER:
            # reprint the descriptor if it was too long and had to be cut short
            print(parallel_descriptor)
        msg.info("Temporary logs are being written to " + temp_log_dir)

        parallel_group_status_queue = Manager().Queue()

        for cmd_info in cmd_infos:
            check_deps(cmd_info.cmd, cmd_info.cmd_name, project_dir, dry)
            if (
                not check_rerun(
                    current_dir, cmd_info.cmd, check_spacy_commit=check_spacy_commit
                )
                and not force
            ):
                cmd_info.change_state("not rerun")
        worker_processes: List[SpawnProcess] = []
        proc_to_cmd_infos: Dict[SpawnProcess, _ParallelCommandInfo] = {}
        num_concurr_worker_processes = 0
        for cmd_info in cmd_infos:
            if cmd_info.state.name == "not rerun":
                continue
            worker_process = mp_context.Process(
                target=_project_run_parallel_cmd,
                args=(cmd_info,),
                kwargs={
                    "dry": dry,
                    "temp_log_dir": temp_log_dir,
                    "parallel_group_status_queue": parallel_group_status_queue,
                },
            )
            worker_processes.append(worker_process)
            proc_to_cmd_infos[worker_process] = cmd_info

        num_concurr_worker_processes = len(worker_processes)
        if (
            max_parallel_processes is not None
            and max_parallel_processes < num_concurr_worker_processes
        ):
            num_concurr_worker_processes = max_parallel_processes

        worker_process_iterator = iter(worker_processes)
        for _ in range(num_concurr_worker_processes):
            _start_worker_process(next(worker_process_iterator), proc_to_cmd_infos)
        _process_worker_status_messages(
            cmd_infos,
            proc_to_cmd_infos,
            parallel_group_status_queue,
            worker_process_iterator,
            current_dir,
            dry,
        )
        for cmd_info in (c for c in cmd_infos if c.state.name != "cancelled"):
            msg.divider(cmd_info.cmd_name)
            if cmd_info.state.name == "not rerun":
                msg.info(f"Skipping '{cmd_info.cmd_name}': nothing changed")
            elif cmd_info.console_output is not None:
                print(cmd_info.console_output)
        # Occasionally when something has hung there may still be worker processes to tidy up
        for hung_worker_process in (wp for wp in worker_processes if wp.is_alive()):
            hung_worker_process.terminate()
        process_rcs = [c.rc for c in cmd_infos if c.rc is not None]
        if len(process_rcs) > 0:
            group_rc = max(process_rcs)
            if group_rc > 0:
                msg.fail("A command in the parallel group failed.")
                sys.exit(group_rc)
        if any(c for c in cmd_infos if c.state.name in ("hung", "terminated")):
            msg.fail("Command(s) in the parallel group hung or were terminated.")
            sys.exit(-1)


def _process_worker_status_messages(
    cmd_infos: List[_ParallelCommandInfo],
    proc_to_cmd_infos: Dict[SpawnProcess, _ParallelCommandInfo],
    parallel_group_status_queue: queue.Queue,
    worker_process_iterator: Iterator[SpawnProcess],
    current_dir: Path,
    dry: bool,
) -> None:
    """Listens on the status queue and processes messages received from the worker processes.

    cmd_infos: a list of info objects about the commands in the parallel group
    proc_to_cmd_infos: a dictionary from Process objects to command info objects
    parallel_group_status_queue: the status queue
    worker_process_iterator: an iterator over the processes, some or all of which
        will already have been iterated over and started
    current_dir: the current directory
    dry (bool): Perform a dry run and don't execute commands.
    """
    status_table_not_yet_displayed = True
    while any(
        cmd_info.state.name in ("pending", "starting", "running")
        for cmd_info in cmd_infos
    ):
        try:
            mess: Dict[str, Union[str, int]] = parallel_group_status_queue.get(
                timeout=PARALLEL_GROUP_STATUS_INTERVAL * 20
            )
        except Exception:
            # No more messages are being received: the whole group has hung
            for other_cmd_info in (
                c for c in cmd_infos if c.state.name in ("starting", "running")
            ):
                other_cmd_info.change_state("hung")
            for other_cmd_info in (c for c in cmd_infos if c.state.name == "pending"):
                other_cmd_info.change_state("cancelled")
            break
        cmd_info = cmd_infos[cast(int, mess["cmd_index"])]
        if mess["mess_type"] in ("started", "keepalive"):
            cmd_info.last_keepalive_time = int(time())
        for other_cmd_info in (
            c for c in cmd_infos if c.state.name in ("starting", "running")
        ):
            if (
                other_cmd_info.last_keepalive_time is not None
                and time() - other_cmd_info.last_keepalive_time
                > PARALLEL_GROUP_STATUS_INTERVAL * 20
            ):
                # a specific command has hung
                other_cmd_info.change_state("hung")
        if mess["mess_type"] == "started":
            cmd_info.change_state("running")
            cmd_info.running_os_cmd_index = cast(int, mess["os_cmd_index"])
            cmd_info.pid = cast(int, mess["pid"])
        if mess["mess_type"] == "completed":
            cmd_info.rc = cast(int, mess["rc"])
            if cmd_info.rc == 0:
                cmd_info.change_state("succeeded")
                if not dry:
                    update_lockfile(current_dir, cmd_info.cmd)
                next_worker_process = next(worker_process_iterator, None)
                if next_worker_process is not None:
                    _start_worker_process(next_worker_process, proc_to_cmd_infos)
            elif cmd_info.rc > 0:
                cmd_info.change_state("failed")
            else:
                cmd_info.change_state("terminated")
            cmd_info.console_output = cast(str, mess["console_output"])
        if any(
            c for c in cmd_infos if c.state.name in ("failed", "terminated", "hung")
        ):
            # a command in the group hasn't succeeded, so terminate/cancel the rest
            for other_cmd_info in (c for c in cmd_infos if c.state.name == "running"):
                try:
                    os.kill(cast(int, other_cmd_info.pid), SIGTERM)
                except:
                    # the subprocess the main process is trying to kill could already
                    # have completed, and the message from the worker process notifying
                    # the main process about this could still be in the queue
                    pass
            for other_cmd_info in (c for c in cmd_infos if c.state.name == "pending"):
                other_cmd_info.change_state("cancelled")
        if mess["mess_type"] != "keepalive" and DISPLAY_STATUS_TABLE:
            if status_table_not_yet_displayed:
                status_table_not_yet_displayed = False
            else:
                # overwrite the existing status table
                print("\033[2K\033[F" * (4 + len(cmd_infos)))
            data = [[c.cmd_name, c.state_repr] for c in cmd_infos]
            header = ["Command", "Status"]
            msg.table(data, header=header)


def _project_run_parallel_cmd(
    cmd_info: _ParallelCommandInfo,
    *,
    dry: bool,
    temp_log_dir: str,
    parallel_group_status_queue: Queue,
) -> None:
    """Run a single spaCy projects command as a worker process.

    Communicates with the main process via queue messages whose type is determined
    by the entry 'mess_type' and that are structured as dictionaries. Possible
    values of 'mess_type' are 'started', 'completed' and 'keepalive'. Each dictionary
    type contains different additional fields."""
    # we can use the command name as a unique log filename because a parallel
    # group is not allowed to contain the same command more than once
    log_file_name = os.sep.join((temp_log_dir, cmd_info.cmd_name + ".log"))
    file_not_found = False
    # buffering=0: make sure output is not lost if a subprocess is terminated
    with open(log_file_name, "wb", buffering=0) as logfile:
        for os_cmd_index, os_cmd in enumerate(cmd_info.cmd["script"]):
            command = split_command(os_cmd)
            if len(command) and command[0] in ("python", "python3"):
                # -u: prevent buffering within Python
                command = [sys.executable, "-u", *command[1:]]
            elif len(command) and command[0].startswith("python3"):  # e.g. python3.10
                command = [command[0], "-u", *command[1:]]
            elif len(command) and command[0] in ("pip", "pip3"):
                command = [sys.executable, "-m", "pip", *command[1:]]
            logfile.write(
                bytes(
                    f"Running command: {join_command(command)}" + os.linesep,
                    encoding="utf8",
                )
            )
            if not dry:
                try:
                    sp = Popen(
                        command,
                        stdout=logfile,
                        stderr=STDOUT,
                        env=os.environ.copy(),
                        encoding="utf8",
                    )
                except FileNotFoundError:
                    # Indicates the *command* wasn't found, it's an error before the command
                    # is run.
                    logfile.write(
                        bytes(
                            Errors.E970.format(
                                str_command=" ".join(command),
                                tool=command[0],
                            ),
                            encoding="UTF-8",
                        )
                    )
                    file_not_found = True
                    break
                parallel_group_status_queue.put(
                    {
                        "mess_type": "started",
                        "cmd_index": cmd_info.cmd_index,
                        "os_cmd_index": os_cmd_index,
                        "pid": sp.pid,
                    }
                )
                while True:
                    try:
                        sp.wait(timeout=PARALLEL_GROUP_STATUS_INTERVAL)
                    except TimeoutExpired:
                        pass
                    if sp.returncode == None:
                        parallel_group_status_queue.put(
                            {
                                "mess_type": "keepalive",
                                "cmd_index": cmd_info.cmd_index,
                            }
                        )
                    else:
                        break

                if sp.returncode != 0:
                    if os.name == "nt":
                        status = "Failed/terminated"
                    elif sp.returncode > 0:
                        status = "Failed"
                    else:
                        status = "Terminated"

                    logfile.write(
                        bytes(
                            os.linesep + f"{status} (rc={sp.returncode})" + os.linesep,
                            encoding="UTF-8",
                        )
                    )
                    break
            else:  # dry run
                parallel_group_status_queue.put(
                    {
                        "mess_type": "started",
                        "cmd_index": cmd_info.cmd_index,
                        "os_cmd_index": os_cmd_index,
                        "pid": -1,
                    }
                )

    with open(log_file_name, "r") as logfile:
        if file_not_found:
            rc = 1
        elif dry:
            rc = 0
        else:
            rc = sp.returncode
        parallel_group_status_queue.put(
            {
                "mess_type": "completed",
                "cmd_index": cmd_info.cmd_index,
                "rc": rc,
                "console_output": logfile.read(),
            }
        )


def _start_worker_process(
    worker_process: SpawnProcess,
    proc_to_cmd_infos: Dict[SpawnProcess, _ParallelCommandInfo],
) -> None:
    cmd_info = proc_to_cmd_infos[worker_process]
    if cmd_info.state.name == "pending":
        cmd_info.change_state("starting")
        cmd_info.last_keepalive_time = int(time())
        worker_process.start()
