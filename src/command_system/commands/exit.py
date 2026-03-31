from src.command_system.utils import handle_errors
from Kathara.manager.Kathara import Kathara
import os
import sys

@handle_errors
def cmd_exit(args=None, cmd_manager=None):
    """
    Stop the lab and close all terminals.
    """
    if cmd_manager is None:
        print("Error: manager not provided to cmd_exit")
        return

    # Ferma il loop principale
    cmd_manager.stop_event.set()

    # Termina tutti i terminali aperti
    for name, p in cmd_manager.processes.items():
        if p and p.poll() is None:
            p.terminate()

    # Undeploy lab
    try:
        print("Stopping and removing lab...")
        Kathara.get_instance().undeploy_lab(lab_name=cmd_manager.lab.name)
        print("Lab stopped and removed.")
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"Failed to undeploy lab: {e}")
    sys.exit(0)



