import platform
import uuid
import psutil


AGENT_ID = str(uuid.uuid4())


def collect_system_info():
    return {
        "agent_id": AGENT_ID,
        "hostname": platform.node(),
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
    }


def collect_processes():
    processes = []

    for process in psutil.process_iter(["pid", "name"]):
        try:
            info = process.info

            processes.append({
                "pid": info["pid"],
                "name": info["name"],
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes


def detect_new_processes(previous_processes, current_processes):
    previous_pids = {
        process["pid"]
        for process in previous_processes
    }

    return [
        process
        for process in current_processes
        if process["pid"] not in previous_pids
    ]