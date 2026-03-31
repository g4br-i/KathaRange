import time
from src.command_system.utils import handle_errors
from src.command_system.commands.action import exec_command, run_action

@handle_errors
def cmd_plan(args, cmd_manager):
    """
    Execute plans defined in the file plans.yaml.
    Usage: plan <plan1> <plan2> (at least 1 plan)
    Examples:
      plan test                 -> runs plan 'test' (machine defined inside plans.yaml)
      plan -a                   -> runs all plans
    """

    if not args:
        print("You must specify at least one plan.")
        return

    # -------------------------
    # BUILD PLAN LIST
    # -------------------------
    plans_to_run = []

    if args == ["-a"]:
        plans_to_run = list(cmd_manager.plans.keys())
    else:
        for token in args:
            if token == "-a":
                print("Syntax error: '-a' must be used alone.")
                return

            if token not in cmd_manager.plans:
                print(f"\nPlan '{token}' not found. Skipping.")
            else:
                plans_to_run.append(token)

    if not plans_to_run:
        print("No valid plans to execute.")
        return

    # -------------------------
    # EXECUTE PLANS
    # -------------------------
    for plan_name in plans_to_run:
        print(f"\nExecuting PLAN '{plan_name}'\n")

        start = time.time()
        result, total_time, plan_log = run_plan(cmd_manager, plan_name)

        # save the plan log using PlanLogger
        cmd_manager.plan_logger.save_plan_log_yaml(
            plan_name=plan_name,
            plan_result=result,
            total_time=round(total_time, 2),
            steps=plan_log
        )

        print(f"\nPLAN {plan_name}: {result}, see logs for more info\n")


# -------------------------
# RUN PLAN
# -------------------------
def run_plan(cmd_manager, plan_name):
    """
    Executes a plan and returns:
      (result, total_time, plan_log)
    result ∈ {"Success", "Fail"}
    """

    if plan_name not in cmd_manager.plans:
        return ("Fail", 0, {})

    plan = cmd_manager.plans[plan_name]
    start_plan = time.time()

    # -------------------------
    # INITIALIZE PLAN LOG
    # -------------------------
    plan_log = {
        "need": {
            "success": True,
            "steps": {}
        },
        "actions": {
            "success": True,
            "steps": {}
        }
    }

    # -------------------------
    # EXECUTE PREREQUISITES (NEED)
    # -------------------------
    for idx, step in enumerate(plan.get("need", []), 1):
        result = run_plan_step(cmd_manager, step, plan_log["need"]["steps"], idx)

        # update global success of need
        if result != "Success":
            plan_log["need"]["success"] = False
            return ("Fail", round(time.time() - start_plan, 2), plan_log)

        # check global plan timeout
        if plan.get("plan_timeout") and time.time() - start_plan > plan["plan_timeout"]:
            plan_log["need"]["success"] = False
            return ("Fail", round(time.time() - start_plan, 2), plan_log)

    # -------------------------
    # EXECUTE MAIN ACTIONS
    # -------------------------
    for idx, step in enumerate(plan.get("actions", []), 1):
        result = run_plan_step(cmd_manager, step, plan_log["actions"]["steps"], idx)

        # update global success of actions
        if result != "Success":
            plan_log["actions"]["success"] = False
            return ("Fail", round(time.time() - start_plan, 2), plan_log)

        # check global plan timeout
        if plan.get("plan_timeout") and time.time() - start_plan > plan["plan_timeout"]:
            plan_log["actions"]["success"] = False
            return ("Fail", round(time.time() - start_plan, 2), plan_log)

    return ("Success", round(time.time() - start_plan, 2), plan_log)


# -------------------------
# RUN PLAN STEP
# -------------------------
def run_plan_step(cmd_manager, step, log_section, idx):
    """
    Executes a single plan step.
    """

    machine = step["machine"]
    expected = step.get("expected", "Success")
    timeout = step.get("timeout")
    parameters = step.get("parameters", {})

    # -------------------------
    # STEP = ACTION
    # -------------------------
    if step["type"] == "action":
        action_name = step["name"]
        parameters = step.get("parameters", {})

        start = time.time()

        result, elapsed, sublog = run_action(cmd_manager, machine, action_name, cli_params=parameters)

        log_section[idx] = {
            "type": "action",
            "action": action_name,
            "machine": machine,
            "expected": expected,
            "result": result,
            "time": elapsed,
            "commands": sublog
        }

        # step-specific timeout
        if timeout and time.time() - start > timeout:
            log_section[idx]["result"] = "Fail"
            log_section[idx]["error"] = "Action timeout"
            return "Fail"

        return result if result == expected else "Fail"

    # -------------------------
    # STEP = COMMAND
    # -------------------------
    if step["type"] == "command":
        command = step["command"]

        # parameter substitution
        for k, v in parameters.items():
            command = command.replace(k, str(v))

        start = time.time()
        stdout, stderr, code = exec_command(cmd_manager, machine, command)
        elapsed = round(time.time() - start, 2)

        output = stdout.decode().strip() if stdout else ""
        result = "Success" if code == 0 and (not expected or expected in output) else "Fail"

        log_section[idx] = {
            "type": "command",
            "command": command,
            "machine": machine,
            "expected": expected,
            "output": output,
            "time": elapsed,
            "result": result
        }

        # step-specific timeout
        if timeout and elapsed > timeout:
            log_section[idx]["result"] = "Fail"
            log_section[idx]["error"] = "Command timeout"
            return "Fail"

        return result

    # -------------------------
    # UNKNOWN STEP
    # -------------------------
    log_section[idx] = {
        "result": "Fail",
        "error": f"Unsupported step type: {step}"
    }
    return "Fail"
