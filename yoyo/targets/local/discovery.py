from loguru import logger
from yoyo.utils import search_processes, extract_port_from_cmd


def discover_local(service: str) -> str:
    matches = search_processes(['uvicorn', service, '--port'])
    if not len(matches):
        raise RuntimeError(f"Service {service} undiscoverable...")
    if len(matches) > 1:
        logger.warning(f"Found more than one instance of '{service}' running, choosing most recent.")
    proc_info = sorted(matches, key=lambda p: p['create_time'], reverse=True)[0]
    logger.debug(f"Found service '{service}' (PID: {proc_info['pid']})")
    port = extract_port_from_cmd(proc_info['cmdline'])
    return f"http://0.0.0.0:{port}"
