import os
import yaml
from datetime import datetime

LOG_DIR = "logs"

class ActionLogger:
    def __init__(self, lab_path: str):
        """
        Initialize the logger with the root path for logs.

        Parameters:
        - lab_path: root folder where logs will be saved
        """
        self.lab_path = lab_path

    # ---------------------- PRIVATE UTILITY METHODS ----------------------
    def _get_uid_gid(self):
        """Return UID and GID of the user running the lab, fallback to current user."""
        uid = int(os.environ.get("SUDO_UID", os.getuid()))
        gid = int(os.environ.get("SUDO_GID", os.getgid()))
        return uid, gid

    def _ensure_dir(self, path: str):
        """
        Create directory if it doesn't exist and try to set ownership.
        """
        os.makedirs(path, exist_ok=True)
        uid, gid = self._get_uid_gid()
        try:
            os.chown(path, uid, gid)
        except PermissionError:
            pass

    # ---------------------- PUBLIC METHODS ----------------------
    def save_action_log_yaml(self, machine: str, action_result: str, action_name: str,
                             total_time: str, commands: dict):
        """
        Save all executed commands of a single action into one YAML log file.

        Parameters:
        - machine: machine name
        - action_name: name of the action
        - commands: dict mapping label -> {command, expected, output, return_code}

        Automatically creates directories:
            <lab_path>/logs/<machine>/actions/<action_name>/
        
        Ownership is set to the original user if the lab is run with sudo, but only for newly created
        folders/files.
        """
        try:
            # Ensure general logs folder
            logs_dir = os.path.join(self.lab_path, LOG_DIR)
            self._ensure_dir(logs_dir)

            # Ensure machine/action folder
            machine_dir = os.path.join(logs_dir, "actions", machine, action_name)
            self._ensure_dir(machine_dir)

            # Prepare file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{action_name}_{timestamp}.yaml"
            filepath = os.path.join(machine_dir, filename)

            # Wrap data for YAML
            data = {
                "action_name": action_name,
                "timestamp": timestamp,
                "total_time": total_time,
                "final_result": action_result,
                "commands": commands
            }

            # Write YAML file
            with open(filepath, "w") as f:
                yaml.dump(data, f, sort_keys=False)

            # Set ownership for file
            uid, gid = self._get_uid_gid()
            try:
                os.chown(filepath, uid, gid)
            except PermissionError:
                pass

            return filepath

        except Exception as e:
            import traceback
            print(f"[ERROR] Failed to save log for {machine}/{action_name}: {e}")
            traceback.print_exc()
            return None

