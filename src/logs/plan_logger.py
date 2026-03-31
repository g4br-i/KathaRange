import os
import yaml
from datetime import datetime

LOG_DIR = "logs"

class PlanLogger:
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
    def save_plan_log_yaml(self, plan_name: str, plan_result: str,
                           total_time: str, steps: dict):
        """
        Save all executed steps of a single plan into one YAML log file.

        Automatically creates directories:
            <lab_path>/logs/plans/<plan_name>/

        Parameters:
        - plan_name: name of the plan
        - plan_result: final result (Success / Fail)
        - total_time: total execution time
        - steps: dict with 'need' and 'actions' logs
        """

        try:
            # Ensure general logs folder
            logs_dir = os.path.join(self.lab_path, LOG_DIR)
            self._ensure_dir(logs_dir)

            # Ensure plan folder
            plan_dir = os.path.join(logs_dir, "plans", plan_name)
            self._ensure_dir(plan_dir)

            # Prepare file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{plan_name}_{timestamp}.yaml"
            filepath = os.path.join(plan_dir, filename)

            # Wrap data for YAML
            data = {
                "plan_name": plan_name,
                "timestamp": timestamp,
                "total_time": total_time,
                "final_result": plan_result,
                "steps": steps
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
            print(f"[ERROR] Failed to save log for plan {plan_name}: {e}")
            traceback.print_exc()
            return None
