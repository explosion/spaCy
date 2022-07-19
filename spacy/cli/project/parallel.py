from typing import Any, List, Literal, Optional, Dict, Union, cast
import sys
from pathlib import Path
from time import time
import multiprocessing
from multiprocessing import Manager as MultiprocessingManager, Queue, Process
from os import kill, environ, linesep, mkdir, sep
from shutil import rmtree
from signal import SIGTERM
from subprocess import STDOUT, Popen, TimeoutExpired
from wasabi import msg
from wasabi.util import color, supports_ansi

from .._util import check_rerun, check_deps, update_lockfile, load_project_config
from ...util import SimpleFrozenDict, working_dir
from ...util import check_bool_env_var, ENV_VARS, split_command, join_command
from ...errors import Errors


# How often the worker processes managing the commands in a parallel group
# send keepalive messages to the main processes
PARALLEL_GROUP_STATUS_INTERVAL = 1

# The dirname where the temporary logfiles for a parallel group are written
# before being copied to stdout when the group has completed
PARALLEL_LOGGING_DIR_NAME = "parrTmp"

DISPLAY_STATUS_COLORS = {
    "pending": "yellow",
    "not rerun": "blue",
    "starting": "green",
    "running": "green",
    "succeeded": "green",
    "failed": "red",
    "killed": "red",
    "hung": "red",
    "cancelled": "red",
}


class _ParallelCommandInfo:
    def __init__(self, cmd_name: str, cmd: Dict, cmd_ind: int):
        self.cmd_name = cmd_name
        self.cmd = cmd
        self.cmd_ind = cmd_ind
        self.len_os_cmds = len(cmd["script"])
        self.status: Literal[
            "pending",
            "not rerun",
            "starting",
            "running",
            "hung",
            "succeeded",
            "failed",
            "killed",
            "cancelled",
        ] = "pending"
        self.pid: Optional[int] = None
        self.last_status_time: Optional[int] = None
        self.os_cmd_ind: Optional[int] = None
        self.rc: Optional[int] = None
        self.output: Optional[str] = None

    @property
    def disp_status(self) -> str:
        status_str = str(self.status)
        status_color = DISPLAY_STATUS_COLORS[status_str]
        if status_str == "running" and self.os_cmd_ind is not None:
            status_str = f"{status_str} ({self.os_cmd_ind + 1}/{self.len_os_cmds})"
        return color(status_str, status_color)


def _start_process(
    process: Process, proc_to_cmd_infos: Dict[Process, _ParallelCommandInfo]
) -> None:
    cmd_info = proc_to_cmd_infos[process]
    if cmd_info.status == "pending":
        cmd_info.status = "starting"
        cmd_info.last_status_time = int(time())
        process.start()


def project_run_parallel_group(
    project_dir: Path,
    cmd_names: List[str],
    *,
    overrides: Dict[str, Any] = SimpleFrozenDict(),
    force: bool = False,
    dry: bool = False,
) -> None:
    """Run a parallel group of commands. Note that because of the challenges of managing
    parallel output streams it is not possible to specify a value for 'capture'. Essentially,
    with parallel groups 'capture==True' for stdout and 'capture==False' for stderr.

    project_dir (Path): Path to project directory.
    cmd_infos: a list of objects containing information about he commands to run.
    overrides (Dict[str, Any]): Optional config overrides.
    force (bool): Force re-running, even if nothing changed.
    dry (bool): Perform a dry run and don't execute commands.
    """
    config = load_project_config(project_dir, overrides=overrides)
    commands = {cmd["name"]: cmd for cmd in config.get("commands", [])}

    parallel_group_status_queue = MultiprocessingManager().Queue()
    max_parallel_processes = config.get("max_parallel_processes")
    check_spacy_commit = check_bool_env_var(ENV_VARS.PROJECT_USE_GIT_VERSION)
    multiprocessing.set_start_method("spawn", force=True)
    DISPLAY_STATUS = sys.stdout.isatty() and supports_ansi()
    cmd_infos = [
        _ParallelCommandInfo(cmd_name, commands[cmd_name], cmd_ind)
        for cmd_ind, cmd_name in enumerate(cmd_names)
    ]

    with working_dir(project_dir) as current_dir:
        for cmd_info in cmd_infos:
            check_deps(cmd_info.cmd, cmd_info.cmd_name, project_dir, dry)
            if (
                not check_rerun(
                    current_dir, cmd_info.cmd, check_spacy_commit=check_spacy_commit
                )
                and not force
            ):
                cmd_info.status = "not rerun"
        rmtree(PARALLEL_LOGGING_DIR_NAME, ignore_errors=True)
        mkdir(PARALLEL_LOGGING_DIR_NAME)
        processes: List[Process] = []
        proc_to_cmd_infos: Dict[Process, _ParallelCommandInfo] = {}
        num_processes = 0
        for cmd_info in cmd_infos:
            if cmd_info.status == "not rerun":
                continue
            process = Process(
                target=_project_run_parallel_cmd,
                args=(cmd_info,),
                kwargs={
                    "dry": dry,
                    "current_dir": str(current_dir),
                    "parallel_group_status_queue": parallel_group_status_queue,
                },
            )
            processes.append(process)
            proc_to_cmd_infos[process] = cmd_info
        num_processes = len(processes)
        if (
            max_parallel_processes is not None
            and max_parallel_processes < num_processes
        ):
            num_processes = max_parallel_processes
        process_iterator = iter(processes)
        for _ in range(num_processes):
            _start_process(next(process_iterator), proc_to_cmd_infos)
        divider_parallel_descriptor = parallel_descriptor = (
            "parallel[" + ", ".join(cmd_info.cmd_name for cmd_info in cmd_infos) + "]"
        )
        if len(divider_parallel_descriptor) > 60:
            divider_parallel_descriptor = divider_parallel_descriptor[:57] + "..."
        msg.divider(divider_parallel_descriptor)
        if not DISPLAY_STATUS:
            print(parallel_descriptor)
        else:
            first = True

        while any(
            cmd_info.status in ("pending", "starting", "running")
            for cmd_info in cmd_infos
        ):
            try:
                mess: Dict[str, Union[str, int]] = parallel_group_status_queue.get(
                    timeout=PARALLEL_GROUP_STATUS_INTERVAL * 20
                )
            except Exception as e:
                for other_cmd_info in (c for c in cmd_infos if c.status == "running"):
                    other_cmd_info.status = "hung"
                for other_cmd_info in (c for c in cmd_infos if c.status == "pending"):
                    other_cmd_info.status = "cancelled"
            cmd_info = cmd_infos[cast(int, mess["cmd_ind"])]
            if mess["status"] in ("started", "alive"):
                cmd_info.last_status_time = int(time())
            for other_cmd_info in (
                c for c in cmd_infos if c.status in ("starting", "running")
            ):
                if (
                    other_cmd_info.last_status_time is not None
                    and time() - other_cmd_info.last_status_time
                    > PARALLEL_GROUP_STATUS_INTERVAL * 20
                ):
                    other_cmd_info.status = "hung"
            if mess["status"] == "started":
                cmd_info.status = "running"
                cmd_info.os_cmd_ind = cast(int, mess["os_cmd_ind"])
                cmd_info.pid = cast(int, mess["pid"])
            if mess["status"] == "completed":
                cmd_info.rc = cast(int, mess["rc"])
                if cmd_info.rc == 0:
                    cmd_info.status = "succeeded"
                    if not dry:
                        update_lockfile(current_dir, cmd_info.cmd)
                    working_process = next(process_iterator, None)
                    if working_process is not None:
                        _start_process(working_process, proc_to_cmd_infos)
                elif cmd_info.rc > 0:
                    cmd_info.status = "failed"
                else:
                    cmd_info.status = "killed"
                cmd_info.output = cast(str, mess["output"])
            if any(c for c in cmd_infos if c.status in ("failed", "killed", "hung")):
                for other_cmd_info in (c for c in cmd_infos if c.status == "running"):
                    try:
                        kill(cast(int, other_cmd_info.pid), SIGTERM)
                    except:
                        pass
                for other_cmd_info in (c for c in cmd_infos if c.status == "pending"):
                    other_cmd_info.status = "cancelled"
            if mess["status"] != "alive" and DISPLAY_STATUS:
                if first:
                    first = False
                else:
                    print("\033[2K\033[F" * (4 + len(cmd_infos)))
                data = [[c.cmd_name, c.disp_status] for c in cmd_infos]
                header = ["Command", "Status"]
                msg.table(data, header=header)

        for cmd_info in (c for c in cmd_infos if c.status != "cancelled"):
            msg.divider(cmd_info.cmd_name)
            if cmd_info.status == "not rerun":
                msg.info(f"Skipping '{cmd_info.cmd_name}': nothing changed")
            else:
                print(cmd_info.output)
        process_rcs = [c.rc for c in cmd_infos if c.rc is not None]
        if len(process_rcs) > 0:
            group_rc = max(process_rcs)
            if group_rc <= 0:
                group_rc = min(process_rcs)
            if group_rc != 0:
                sys.exit(group_rc)
        if any(c for c in cmd_infos if c.status == "hung"):
            sys.exit(-1)


def _project_run_parallel_cmd(
    cmd_info: _ParallelCommandInfo,
    *,
    dry: bool,
    current_dir: str,
    parallel_group_status_queue: Queue,
) -> None:
    log_file_name = sep.join(
        (current_dir, PARALLEL_LOGGING_DIR_NAME, cmd_info.cmd_name + ".log")
    )
    file_not_found = False
    with open(log_file_name, "wb", buffering=0) as logfile:
        for os_cmd_ind, os_cmd in enumerate(cmd_info.cmd["script"]):
            command = split_command(os_cmd)
            if len(command) and command[0] in ("python", "python3"):
                command = [sys.executable, "-u", *command[1:]]
            elif len(command) and command[0] in ("pip", "pip3"):
                command = [sys.executable, "-m", "pip", *command[1:]]
            logfile.write(
                bytes(
                    f"Running command: {join_command(command)}" + linesep,
                    encoding="UTF-8",
                )
            )
            if not dry:
                try:
                    sp = Popen(
                        command,
                        stdout=logfile,
                        stderr=STDOUT,
                        env=environ.copy(),
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
                        "cmd_ind": cmd_info.cmd_ind,
                        "os_cmd_ind": os_cmd_ind,
                        "status": "started",
                        "pid": sp.pid,
                    }
                )
                while True:
                    try:
                        sp.communicate(timeout=PARALLEL_GROUP_STATUS_INTERVAL)
                    except TimeoutExpired:
                        pass
                    if sp.returncode == None:
                        parallel_group_status_queue.put(
                            {
                                "cmd_ind": cmd_info.cmd_ind,
                                "status": "alive",
                            }
                        )
                    else:
                        break
                if sp.returncode != 0:
                    if sp.returncode > 0:
                        logfile.write(
                            bytes(
                                linesep + f"Failed (rc={sp.returncode})" + linesep,
                                encoding="UTF-8",
                            )
                        )
                    else:
                        logfile.write(
                            bytes(
                                linesep + f"Killed (rc={sp.returncode})" + linesep,
                                encoding="UTF-8",
                            )
                        )
                    break
    with open(log_file_name, "r") as logfile:
        if file_not_found:
            rc = 1
        elif dry:
            rc = 0
        else:
            rc = sp.returncode
        parallel_group_status_queue.put(
            {
                "cmd_ind": cmd_info.cmd_ind,
                "status": "completed",
                "rc": rc,
                "output": logfile.read(),
            }
        )
