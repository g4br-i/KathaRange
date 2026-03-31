import time

def monitor_processes(processes, stop_event):
    """Monitor terminal processes and mark closed ones."""
    while not stop_event.is_set():
        for name, p in processes.items():
            if p and p.poll() is not None:
                processes[name] = None
        time.sleep(1)
