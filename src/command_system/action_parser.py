import yaml
import re

def extract_params_from_text(text: str):
    """
    Extract parameters defined as <$KEY:DEFAULT> in text
    Returns a dict { "$KEY": DEFAULT }
    """
    params = {}
    pattern = r"<\$(\w+):([^>]+)>"  # <$KEY:DEFAULT>
    matches = re.findall(pattern, text)
    for key, default in matches:
        params[f"${key}"] = default
    return params

def parse_actions(filename: str):
    """
    Parse YAML actions file.
    Returns a dict:
        { action_name: { "parameters": {defaults}, "commands": [(cmd, expected, params), ...] } }
    
    Notes:
        - Supports simple commands, compound commands (AND/OR), and calls.
        - Each command is normalized to a tuple: (command_str, expected_output, parameters)
    """
    with open(filename, "r") as f:
        data = yaml.safe_load(f) or {}

    actions = data.get("actions", {})
    parsed_actions = {}

    def normalize_action(action):
        """
        Convert action block into (cmd_str, expected, params)
        """
        if isinstance(action, str):
            return (action, None, {})
        if isinstance(action, (list, tuple)):
            if len(action) == 2:
                cmd_str, expected = action
                return (cmd_str, expected, {})
            elif len(action) == 3:
                cmd_str, expected, params = action
                return (cmd_str, expected, params)
            else:
                raise ValueError(f"Invalid list/tuple action: {action}")
        if isinstance(action, dict):
            if "call" in action:
                # call action format: {"call": action_name, "expected": "Success", "parameters": {...}}
                return ("call", action["call"], action.get("expected", "Success"), action.get("parameters", {}))
            if "command" not in action:
                raise ValueError(f"Dict action missing 'command': {action}")
            cmd_str = action["command"]
            expected = action.get("expected")
            params = extract_params_from_text(cmd_str)
            return (cmd_str, expected, params)
        raise ValueError(f"Unsupported action format: {action}")

    for action_name, action_content in actions.items():
        parsed_actions[action_name] = {"parameters": {}, "commands": []}

        # Extract default parameters from action-level "parameters" if present
        if isinstance(action_content, dict) and "parameters" in action_content:
            parsed_actions[action_name]["parameters"] = action_content.get("parameters", {})

        # Normalize action_content to always be a dict of commands
        if isinstance(action_content, list):
            action_content = {1: action_content}
        elif isinstance(action_content, dict) and 1 not in action_content:
            # Already in action-level dict, keep as is
            pass

        for key, value in sorted(action_content.items()):
            # Compound command (AND / OR)
            if isinstance(value, dict) and "operator" in value:
                operator = value["operator"].upper()
                if operator not in ("AND", "OR"):
                    raise ValueError(f"Unsupported operator: {operator}")
                sub_actions = [normalize_action(v) for k, v in sorted(value.items()) if k != "operator"]
                parsed_actions[action_name]["commands"].append((operator, *sub_actions))
            else:
                parsed_actions[action_name]["commands"].append(normalize_action(value))

    return parsed_actions
