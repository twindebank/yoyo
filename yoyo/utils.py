import colorsys
import contextlib
import importlib
import os
import shlex
import socket
import subprocess
import sys
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Tuple, List, Optional

import psutil
from loguru import logger


@contextlib.contextmanager
def cd_python(path: Path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    os.chdir(path)
    sys.path.insert(0, str(path))
    try:
        yield
    finally:
        os.chdir(prev_cwd)
        del sys.path[0]


def load_module(python_root: Path, module_path: Path) -> Optional[ModuleType]:
    with cd_python(python_root):
        spec = importlib.util.spec_from_file_location("*", module_path)
        if not spec:
            return
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except FileNotFoundError:
            return
        if python_root not in Path(module.__file__).parents:
            return
        return module


class StrEnum(str, Enum):
    """from dbt"""

    def __str__(self) -> str:
        return self.value

    # https://docs.python.org/3.6/library/enum.html#using-automatic-values
    def _generate_next_value_(name, start, count, last_values):
        return name


def colorize(line, color):
    line = line.replace('<', '\\<')
    return f"<{color}>{line}</{color}>"


def rgb_to_logger_rgb(rgb):
    r, g, b = rgb
    return f"fg {r},{g},{b}"


def get_env(env=None):
    os_env = os.environ.copy()
    if not env:
        return os_env
    os_env.update(env)
    return os_env


def run_cmd(cmd, env=None):
    return subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=get_env(env),
                            universal_newlines=True)


def run_cmd_get_output(cmd, env=None):
    result = subprocess.run(
        shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', env=get_env(env)
    )
    result.check_returncode()
    return result.stdout.strip()


def run_cmd_stream_output(cmd, env=None):
    print(f"Executing command: {cmd}")
    result = subprocess.run(shlex.split(cmd), env=get_env(env))
    result.check_returncode()
    return result


@dataclass
class ProcessToStream:
    name: str
    process: subprocess.Popen
    colour: str

    @property
    def stdout(self):
        return self.process.stdout


def stream_multiple_processes(processes: List[Tuple[str, subprocess.Popen]]):
    colours = [rgb_to_logger_rgb(c) for c in get_n_colours(len(processes))]
    processes_to_stream = [
        ProcessToStream(process_name, process, colour)
        for (process_name, process), colour in zip(processes, colours)
    ]
    executor = ThreadPoolExecutor(max_workers=len(processes))
    executor.map(stream_process_output, processes_to_stream)


def stream_process_output(process: ProcessToStream):
    for line in process.stdout:
        logline = line.strip('\n')
        logger.opt(colors=True).info(f"[{process.name}] {colorize(logline, process.colour)}")


def get_n_colours(n):
    hsv_tuples = [(x * 1.0 / n, 0.5, 0.5) for x in range(n)]
    rgb = [[int(i * 255) for i in colorsys.hsv_to_rgb(*hsv)] for hsv in hsv_tuples]
    return rgb


def find_free_port():
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def newer_than(target_file: Path, *comparison_files: Path):
    newest = max(f.stat().st_mtime for f in comparison_files)
    return target_file.stat().st_mtime > newest


@contextlib.contextmanager
def build_virtualenv(loc: Path, force=False):
    env = {
        "POETRY_VIRTUALENVS_CREATE": 'false',
    }
    with cd_python(loc):
        if force:
            run_cmd_stream_output(f"pyenv uninstall --force {loc.name}", env=env)
            run_cmd_stream_output(f"pyenv virtualenv --force 3.9.0 {loc.name}", env=env)
        env = set_venv(str(loc.name), env)
        run_cmd_stream_output(f"poetry install", env=env)
        yield env


def set_venv(name, env):
    env['PYENV_VERSION'] = name
    try:
        run_cmd_stream_output(f"pyenv local {name}", env=env)
    except subprocess.CalledProcessError:
        print(f"Creating virtualenv: {name}")
        run_cmd_stream_output(f"pyenv virtualenv 3.9.0 {name}", env=env)
        run_cmd_stream_output(f"pyenv local {name}", env=env)
    path = Path(run_cmd_get_output("pyenv which python", env=env))
    virtualenv_dir = path.parent.parent
    env.update({
        'PYENV_VIRTUAL_ENV': str(virtualenv_dir),
        'VIRTUAL_ENV': str(virtualenv_dir),
    })
    return env


def search_processes(keywords: List[str]) -> List[dict]:
    matches = []
    for p in psutil.process_iter(attrs=["pid", "name", "cmdline", "create_time"]):
        if p.info['cmdline'] is None:
            continue
        cmd = ' '.join(p.info['cmdline'])
        if all([keyword in cmd for keyword in keywords]):
            matches.append(p.info)
    return matches


def extract_port_from_cmd(cmd):
    port_idx = cmd.index('--port')
    return cmd[port_idx + 1]
