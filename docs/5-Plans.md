# Plans

KathaRange allows you to **automate sequences of actions and commands** through **plans**, defined in a YAML file (`plans.yaml`).
Plans provide a way to orchestrate multiple steps, specify prerequisites, timeouts, and parameters, enabling complex attack/defense scenarios in your lab.

---

## Plan Structure

Each plan is defined under a unique name and can contain:

* `plan_timeout` – Optional overall timeout for the plan (seconds)
* `need` – Prerequisites to satisfy before running actions
* `actions` – Actions to execute as part of the plan

Example structure:

```yaml
plans:
  my_plan:
    plan_timeout: 120
    need:
      1:
        command: echo 'test'
        expected: test
        machine: kali
      2:
        action: testping
        machine: kali
    actions:
      1:
        action: test_plan
        machine: kali
        timeout: 50
        parameters:
          $IP: 192.168.2.10
      2:
        action: test
        machine: kali
```

---

## `plan_timeout`

* Optional overall timeout in **seconds** for the plan execution
* If the plan does not finish within this time, it will be interrupted

---

## `need` – Prerequisites

* Steps that **must be completed before executing the main actions**
* Each step can be an **action** or a **command** executed on a specific machine

Example:

```yaml
need:
  1:
    command: echo 'test'
    expected: test
    machine: kali
  2: 
    action: testping
    machine: kali
    parameters:
      $IP: 192.168.2.10 
```

---

## `actions`

* Sequence of actions to execute after prerequisites are satisfied 
* Each step must define the **machine** and either an **action** (from `actions.yaml`) or a **command**
* Optional **timeout** per step (seconds)
* Optional **parameters** to override defaults

Example:

```yaml
actions:
  1:
    action: test_plan
    machine: kali
    timeout: 50
    parameters:
      $IP: 192.168.2.10
  2:
    action: test
    machine: kali
```

* Steps are executed **in the order of numbering**.
* Multiple machines or actions can be coordinated using separate steps.

---

## Notes

* **Action vs. Command**:

  * `action` refers to an action defined in `actions.yaml`
  * `command` is a direct shell command to run on the machine

* **Expected Output**:

  * Each step can define `expected` (default is `"Success"`) to verify execution

* **Parameters**:

  * Step-level parameters override plan-level defaults
  * Useful for dynamic execution with variables like `$IP`

* **Timeouts**:

  * Step-level `timeout` overrides the global plan timeout for that action

---

## Example Plan Execution

CLI example to run a plan:

```bash
plan my_plan
```

This executes all steps in `my_plan`, respecting prerequisites, timeouts, and parameters.

---

This approach allows you to **orchestrate complex lab scenarios**, ensuring that prerequisites are met and multiple machines/actions are executed in sequence or with specific parameters.
