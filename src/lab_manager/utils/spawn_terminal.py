import shlex
import subprocess
import sys
import os

def spawn_terminal(machine_name, lab_name):
    """
    Open an xterm window and attach it to the device TTY for interactive use.
    """
    python_path = sys.executable
    try:
        cmd = (
            f"{shlex.quote(python_path)} -c "
            f"\"from Kathara.manager.Kathara import Kathara; "
            f"Kathara.get_instance().connect_tty('{machine_name}', lab_name='{lab_name}', logs=True)\""
        )
        # Use preexec_fn=os.setsid to run the xterm in a separate process group
        return subprocess.Popen(
            ["xterm", "-hold", "-e", "bash", "-c", cmd],
            preexec_fn=os.setsid
        )
    except Exception:
        print("Something went wrong")