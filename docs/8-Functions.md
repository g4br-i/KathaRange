# Functions and Classes

This document lists the main functions and classes used in KathaRange with concise descriptions.

---

## Entry Point (`start_lab.py`)

* **main()** – Initializes the lab environment, loads configuration, deploys the lab, and starts the interactive CLI loop.

---

## LabManager (`src/lab_manager`)

* **load_lab()** – Parse `lab_conf.yaml` and return lab metadata and normalized device configuration.
* **prepare_startup_file()** – Generate or update a startup file for a device based on configured addresses or existing file.

---

### Utils (`src/lab_manager/utils`)

* **parse_args()** – Parse startup arguments for `start_lab.py` (lab name and optional flags).
* **monitor_processes()** – Monitor terminal processes and mark closed ones.
* **spawn_terminal()** – Open an xterm window and attach it to the device TTY for interactive use.

---

## Command System (`src/command_system`)

* **parse_actions()** – Parse `actions.yaml` and return structured action definitions.
* **parse_plans()** – Parse `plans.yaml` and return structured plan definitions.
* **CommandManager()** – Central controller that dispatches CLI commands and orchestrates execution.

### Utilities (src/command_system/utils.py)

* **handle_errors()**: Decorator to catch exceptions and Ctrl+C, printing errors gracefully.  
* **sanitize_filename()**: Remove unsafe characters from filenames.  
* **completer()**: Provide tab completion for commands and machine names.  
* **setup_history_and_completion()**: Initialize in-memory CLI history and tab completion.

---

## Logging (`src/logs`)

* **ActionLogger()** – Handles structured YAML logging for action execution.
* **PlanLogger()** – Handles structured YAML logging for plan execution.

---

## OSPF (`src/ospf`)

* **OSPFManager()** – Deploy and validate OSPF routing configuration when enabled.
