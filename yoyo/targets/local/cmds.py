from yoyo.exceptions import ServiceNotExecutable
from yoyo.targets.base.cmds import TargetCmds
from yoyo.targets.target_handler import TargetHandler
from yoyo.utils import build_virtualenv, run_cmd, stream_multiple_processes, find_free_port


class LocalCmds(TargetCmds):
    def up(self):
        """Run service locally"""
        processes = []
        for service in self.services:
            service_path = self._absolute_paths.service_dir(service)
            if not self._absolute_paths.main_file(service).exists():
                raise ServiceNotExecutable(f"No main.py found for service '{service}'.")

            with build_virtualenv(service_path) as env:
                TargetHandler.to_env_from_cli(self, env)
                port = str(find_free_port())
                cmd = f"uvicorn --app-dir {str(service_path)} main:app --host 0.0.0.0 --port {port}"
                processes.append((service, run_cmd(cmd, env=env)))

        stream_multiple_processes(processes)

    def rebuild(self):
        """Force rebuild venvs"""
        for service in self.services:
            service_path = self._absolute_paths.service_dir(service)
            with build_virtualenv(service_path, force=True):
                pass
