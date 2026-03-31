from src.command_system.utils import handle_errors
from Kathara.manager.Kathara import Kathara
import time
import re

def exec_command(cmd_manager, machine_name, command):
    """
    Execute a shell command on the given machine using Kathara.
    Returns a tuple (stdout, stderr, code).
    """
    try:
        stdout, stderr, code = Kathara.get_instance().exec(
            machine_name=machine_name,
            command=["sh", "-c", command],
            lab=cmd_manager.lab,
            stream=False
        )
        return stdout, stderr, code
    except Exception as e:
        print(f"Exception while executing action on {machine_name}: {e}\n")
        return None, str(e), 1  

def substitute_params(text: str, override_params: dict, warn_missing=True):
    """
    Replace placeholders <$KEY:DEFAULT> in a command string with final values.
    Logic:
      - If an override is provided via CLI, use it.
      - Otherwise, use the default defined in the action.
      - Warn if no value is found for a placeholder.
    """
    def replacer(match):
        key, default = match.groups()
        param_name = f"${key}"
        if param_name in override_params:
            return str(override_params[param_name])
        elif default is not None:
            return str(default)
        else:
            if warn_missing:
                print(f"[WARNING] Parameter '{param_name}' is not defined and has no default!")
            return f"<{param_name}:?>"

    pattern = r"<\$(\w+):([^>]*)>"
    return re.sub(pattern, replacer, text)


@handle_errors
def cmd_action(args, cmd_manager):
    """
    Execute actions defined in actions.yaml for the selected machines.

    Usage: action <machine1> <action1> <action2> <machine2> <action1>

    Examples:
      action kali test          -> runs 'test' on kali using defaults
      action kali -a            -> runs all actions on kali
      action kali test r1 -a    -> runs 'test' on kali and all actions on r1
      action kali -a r2 testr2  -> runs all actions on kali and 'testr2' on r2

    Notes on parameters:
      - Parameters defined in the action as <$KEY:DEFAULT> will be substituted.
      - CLI overrides take priority over defaults but only for that execution.
      - Actions without parameters are executed as-is.
    """
    if not args:
        print("You must specify at least one machine name.")
        return

    lab_devices = list(cmd_manager.lab.machines.keys())
    if args[0] not in lab_devices:
        print(f"Syntax error: first argument must be a machine. Got '{args[0]}'")
        return

    # Build targets: { machine: [ (action_name, cli_params) ] }
    targets = {}
    current_machine = None
    i = 0
    n = len(args)

    while i < n:
        token = args[i]

        # Machine selection
        if token in lab_devices:
            current_machine = token
            targets.setdefault(current_machine, [])
            i += 1
            continue

        # '-a' means: run all actions for this machine
        if token == "-a":
            if current_machine is None:
                print("Syntax error: '-a' must follow a machine.")
                return
            for action_name in cmd_manager.actions.keys():
                targets[current_machine].append((action_name, {}))
            i += 1
            continue

        # CLI parameter $KEY=VALUE
        if token.startswith("$"):
            if current_machine is None or not targets[current_machine]:
                print(f"Syntax error: parameter '{token}' without an action.")
                return
            if "=" not in token:
                print(f"Invalid parameter format: {token}")
                return
            key, value = token.split("=", 1)
            # Attach to last action of this machine
            last_action, last_params = targets[current_machine][-1]
            new_params = last_params.copy()
            new_params[key] = value
            targets[current_machine][-1] = (last_action, new_params)
            i += 1
            continue

        # Token = action name
        if current_machine is None:
            print(f"Syntax error: action '{token}' without a machine.")
            return

        if token not in cmd_manager.actions:
            print(f"\nAction '{token}' not found. Skipping.")
        else:
            targets[current_machine].append((token, {}))

        i += 1

    # Execute each action for each machine
    for machine, action_list in targets.items():
        for action_name, cli_params in action_list:
            result, total_time, commands_log = run_action(cmd_manager, machine, action_name, cli_params=cli_params)

            cmd_manager.action_logger.save_action_log_yaml(
                machine=machine,
                action_result=result,
                total_time=round(total_time, 2),
                action_name=action_name,
                commands=commands_log
            )

            print(f"\nACTION {action_name} on {machine}: {result}, see logs for more info\n")


def run_action(cmd_manager, machine, action_name, cli_params=None):
    """
    Execute a single action with support for:
      - Simple commands
      - Compound commands (AND/OR)
      - Calls to sub-actions
    Each command tuple is (cmd_str, expected, params) where:
      - cmd_str = the shell command
      - expected = expected output (optional)
      - params = dict of parameters for this command
    CLI parameters override the action defaults for this execution only.
    Returns: (result, total_time, commands_log)
    """
    action_block = cmd_manager.actions[action_name]
    commands = action_block["commands"]
    default_params = action_block.get("parameters", {})  # default parameters from action
    commands_log = {}
    action_time = 0

    # Merge CLI overrides with defaults (CLI overrides take priority)
    combined_params = default_params.copy()
    if cli_params:
        combined_params.update(cli_params)

    print(f"\nExecuting action '{action_name}' on {machine}\n")

    for idx, command in enumerate(commands, 1):
        # CASE: compound action
        if isinstance(command, tuple) and command[0].upper() in ("AND", "OR"):
            operator = command[0].upper()
            sub_commands = command[1:]
            success = operator == "AND"
            parent_label = idx

            print(f"Executing compound action {parent_label} ({operator})")

            commands_log[parent_label] = {
                "operator": operator,
                "group_time": 0,
                "group_result": "Success"
            }

            for sub_idx, sub_command_raw in enumerate(sub_commands, 1):
                label = f"{parent_label}{chr(96 + sub_idx)}"

                # Normalize sub_command
                if len(sub_command_raw) == 2:
                    sub_cmd, expected = sub_command_raw
                    params = {}
                elif len(sub_command_raw) == 3:
                    sub_cmd, expected, params = sub_command_raw
                else:
                    raise ValueError(f"Invalid sub-command format: {sub_command_raw}")

                # Merge parameters for this command
                final_params = combined_params.copy()
                if cli_params:                             # CLI overrides
                    final_params.update(cli_params)
                else:
                    final_params.update(params)

                display_cmd = substitute_params(sub_cmd, final_params)
                expected = substitute_params(expected, final_params)
                print(f"({label}) -> {display_cmd}")

                used_overrides = {}
                for key in (cli_params or {}):
                    placeholder = f"<{key}:"
                    if placeholder in sub_cmd or (expected and placeholder in expected):
                        used_overrides[key] = final_params[key]

                if used_overrides:
                    print(f"    expected: {expected}\n    params: {used_overrides}")
                else:
                    print(f"    expected: {expected}")

                start = time.time()
                stdout, stderr, code = exec_command(cmd_manager, machine, display_cmd)
                elapsed = round(time.time() - start, 2)
                action_time += elapsed
                commands_log[parent_label]["group_time"] = round(commands_log[parent_label]["group_time"] + elapsed, 2)

                output = stdout.decode().strip() if stdout else (stderr.strip() if stderr else "")
                commands_log[parent_label][label] = {
                    "command": display_cmd,
                    "expected": expected,
                    "output": output,
                    "command_time": elapsed,
                    "result": "Success"
                }

                if code != 0 or (expected and operator == "AND" and expected not in output):
                    success = False
                    commands_log[parent_label][label]["result"] = "Fail"
                    break
                if operator == "OR" and expected and expected in output:
                    success = True
                    break

            if not success:
                commands_log[parent_label]["group_result"] = "Fail"
                return ("Fail", action_time, commands_log)

            continue

        # CASE: call sub-action
        if command[0] == "call":
            _, called_action, expected, params = command  
            print(f"\nCalling action '{called_action}' inside '{action_name}'")

            # Merge CLI params con eventuali params della call
            sub_cli_params = {}
            if cli_params:
                sub_cli_params.update(cli_params)
            if params:
                sub_cli_params.update(params)

            sub_result, sub_time, sub_log = run_action(
                cmd_manager,
                machine,
                called_action,
                cli_params=sub_cli_params
            )

            action_time += sub_time
            commands_log[idx] = {
                "call": called_action,
                "expected": expected,
                "result": "Success" if sub_result == expected else "Fail",
                "action_time": sub_time,
                "commands": sub_log
            }
            if sub_result != expected:
                print(f"\nAction {called_action} failed\n")
                return ("Fail", action_time, commands_log)
            print(f"\nAction {called_action} completed successfully. Returning to {action_name}\n")
            continue

        # CASE: simple command
        if len(command) == 2:
            cmd_str, expected = command
            params = {}
        elif len(command) == 3:
            cmd_str, expected, params = command
        else:
            raise ValueError(f"Invalid command format: {command}")

        # Merge parameters
        final_params = combined_params.copy()
        if cli_params:  # CLI overrides
            final_params.update(cli_params)
        else:
            final_params.update(params)

        display_cmd = substitute_params(cmd_str, final_params)
        expected = substitute_params(expected, final_params)

        used_overrides = {}
        for key in (cli_params or {}):
            if f"<{key}:" in cmd_str:
                used_overrides[key] = final_params[key]

        print(f"({idx}) -> {display_cmd}")
        if used_overrides:
            print(f"    expected: {expected}\n    params: {used_overrides}")
        else:
            print(f"    expected: {expected}")


        start = time.time()
        stdout, stderr, code = exec_command(cmd_manager, machine, display_cmd)
        elapsed = round(time.time() - start, 2)
        action_time += elapsed

        output = stdout.decode().strip() if stdout else (stderr.strip() if stderr else "")
        commands_log[idx] = {
            "command": display_cmd,
            "expected": expected,
            "output": output,
            "command_time": elapsed,
            "result": "Success"
        }

        if code != 0 or (expected and expected not in output):
            commands_log[idx]["result"] = "Fail"
            return ("Fail", action_time, commands_log)

    return ("Success", action_time, commands_log)

