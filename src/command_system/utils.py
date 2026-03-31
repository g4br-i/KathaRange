
import functools
import atexit
import os
import readline
import re

def handle_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\nOperation interrupted by user (Ctrl+C).")
        except Exception as e:
            print(f"\nUnexpected error in {func.__name__}: {e}")
    return wrapper

def sanitize_filename(file_name: str) -> str:
    file_base = os.path.basename(file_name)
    file_clean = re.sub(r'[^A-Za-z0-9_-]', '', file_base)
    return file_clean

def completer(cmd_manager, text, state):
    """
    Auto-complete commands and machine names:
    - First token: suggest commands that start with typed text
    - Second token:
        - If the first command is 'help', suggest other commands
        - Otherwise, suggest machine names
    """
    buffer = readline.get_line_buffer()
    tokens = buffer.strip().split()
    options = []

    if len(tokens) == 0 or (len(tokens) == 1 and not buffer.endswith(' ')):
        # First token incomplete, suggest commands matching text
        options = [cmd for cmd in cmd_manager.cmd_commands.keys() if cmd.startswith(text)]
    elif len(tokens) >= 2 or (len(tokens) == 1 and buffer.endswith(' ')):
        first_cmd = tokens[0]
        if first_cmd == "help":
            # Second token after "help": suggest commands
            options = [cmd for cmd in cmd_manager.cmd_commands.keys() if cmd.startswith(text)]
        else:
            # For other commands: suggest machine names
            options = [m for m in cmd_manager.lab.machines.keys() if m.startswith(text)]

    if state < len(options):
        return options[state]
    return None


import readline

def setup_history_and_completion(cmd_manager):
    """
    Setup tab completion and in-memory command history for the current session.
    No persistent history is stored on disk.
    """
    # Clear any previous in-memory history
    readline.clear_history()

    # Set tab completion using the provided completer
    readline.set_completer(lambda text, state: completer(cmd_manager, text, state))
    readline.parse_and_bind("tab: complete")
