import yaml


def parse_plans(filename: str):
    with open(filename, "r") as f:
        data = yaml.safe_load(f) or {}

    plans = data.get("plans", {})
    parsed_plans = {}

    def normalize_plan_step(step: dict):
        if "machine" not in step:
            raise ValueError(f"Plan step missing 'machine': {step}")

        base = {
            "machine": step["machine"],
            "timeout": step.get("timeout"),
            "expected": step.get("expected", "Success"),
            "parameters": step.get("parameters", {})
        }

        if "action" in step:
            return {
                "type": "action",
                "name": step["action"],
                **base
            }

        if "command" in step:
            return {
                "type": "command",
                "command": step["command"],
                **base
            }

        raise ValueError(f"Unsupported plan step: {step}")

    for plan_name, plan_data in plans.items():
        if not isinstance(plan_data, dict):
            raise ValueError(f"Plan '{plan_name}' must be a dict")

        parsed_plans[plan_name] = {
            "plan_timeout": plan_data.get("plan_timeout"),
            "parameters": plan_data.get("parameters", {}),
            "need": [],
            "actions": []
        }

        for section in ("need", "actions"):
            steps = plan_data.get(section, {})
            if not isinstance(steps, dict):
                raise ValueError(f"'{section}' in plan '{plan_name}' must be a dict")

            for _, step in sorted(steps.items()):
                parsed_plans[plan_name][section].append(
                    normalize_plan_step(step)
                )
    return parsed_plans

