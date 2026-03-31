# Logs

KathaRange automatically generates structured **YAML logs** for both **actions** and **plans**.

Logs provide full traceability of execution, including:

* Executed commands
* Expected values
* Actual output
* Execution time
* Final result (Success / Fail)

All logs are stored inside the lab directory under the `logs/` folder.  
If the `logs/`, `actions/`, or `plans/` folders do not exist, they are automatically created at runtime.

---

## Log Directory Structure

Logs are organized as follows:

```
<lab_path>/logs/

├── actions/
│   └── <machine>/
│       └── <action_name>/
│           └── <action_name>_<timestamp>.yaml
│
└── plans/
    └── <plan_name>/
        └── <plan_name>_<timestamp>.yaml
```

Each execution generates a new timestamped YAML file.

### File Name Format

Plan log file name:

```
<plan_name>_<YYYYMMDD_HHMMSS>.yaml
```

Example:

```
my_plan_20260209_103137.yaml
```

Action log file name:

```
<action_name>_<YYYYMMDD_HHMMSS>.yaml
```

Example:

```
test_20260218_111157.yaml
```

The file name is always composed of:

* The action or plan name
* Date (YYYYMMDD)
* Time (HHMMSS)

This guarantees uniqueness and chronological ordering.

Timestamp format:

```
YYYYMMDD_HHMMSS
```

Example:

```
20260218_111157
```

---

## Action Logs

Action logs are generated after executing a single action.

They are saved under:

```
logs/actions/<machine>/<action_name>/
```

### Action Log Structure

Example:

```yaml
action_name: test
timestamp: '20260223_102353'
total_time: 9.63
final_result: Fail
commands:
  1:
    call: testping
    expected: Success
    result: Success
    action_time: 2.17
    commands:
      1:
        command: ping -c 3 192.168.2.10
        expected: 3 received
        output: 'PING 192.168.2.10 (192.168.2.10) 56(84) bytes of data.

          64 bytes from 192.168.2.10: icmp_seq=1 ttl=61 time=3.63 ms

          64 bytes from 192.168.2.10: icmp_seq=2 ttl=61 time=2.97 ms

          64 bytes from 192.168.2.10: icmp_seq=3 ttl=61 time=2.62 ms


          --- 192.168.2.10 ping statistics ---

          3 packets transmitted, 3 received, 0% packet loss, time 2003ms

          rtt min/avg/max/mdev = 2.621/3.072/3.628/0.417 ms'
        command_time: 2.1
        result: Success
      2:
        command: echo 'test'
        expected: test
        output: test
        command_time: 0.07
        result: Success
  2:
    operator: AND
    group_time: 7.35
    group_result: Success
    2a:
      command: nmap -sV 192.168.2.10 | fgrep 'Apache' | awk '/open/'
      expected: Apache
      output: 80/tcp open  http    Apache httpd 2.4.49 ((Unix))
      command_time: 7.27
      result: Success
    2b:
      command: echo 'test kali'
      expected: test kali
      output: test kali
      command_time: 0.08
      result: Success
  3:
    command: curl 'http://192.168.2.10/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh' -d 'A=|echo;ls'
    expected: bash
    output: '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">

      <html><head>

      <title>404 Not Found</title>

      </head><body>

      <h1>Not Found</h1>

      <p>The requested URL was not found on this server.</p>

      </body></html>'
    command_time: 0.11
    result: Fail

```

### Fields

* `action_name` – Name of the executed action
* `timestamp` – Execution time identifier
* `total_time` – Total execution time (seconds)
* `final_result` – Overall result of the action (Success / Fail)
* `commands` – Detailed execution breakdown

### Command-Level Fields

For each command:

* `command` – Executed shell command
* `expected` – Expected output string
* `output` – Actual command output
* `command_time` – Execution time (seconds)
* `result` – Success / Fail

### Compound Commands (AND / OR)

If the action contains logical operators:

* `operator` – AND / OR
* `group_time` – Total time for the group
* `group_result` – Final result of the group
* Nested steps (1a, 1b, …) contain individual command logs

---

## Plan Logs

Plan logs are generated after executing a full plan.

They are saved under:

```
logs/plans/<plan_name>/
```

### Plan Log Structure

Example:

```yaml
plan_name: my_plan
timestamp: '20260223_104459'
total_time: 11.76
final_result: Fail
steps:
  need:
    success: true
    steps:
      1:
        type: action
        action: testping
        machine: kali
        expected: Success
        result: Success
        time: 2.19
        commands:
          1:
            command: ping -c 3 192.168.2.10
            expected: 3 received
            output: 'PING 192.168.2.10 (192.168.2.10) 56(84) bytes of data.

              64 bytes from 192.168.2.10: icmp_seq=1 ttl=61 time=5.90 ms

              64 bytes from 192.168.2.10: icmp_seq=2 ttl=61 time=2.57 ms

              64 bytes from 192.168.2.10: icmp_seq=3 ttl=61 time=1.95 ms


              --- 192.168.2.10 ping statistics ---

              3 packets transmitted, 3 received, 0% packet loss, time 2003ms

              rtt min/avg/max/mdev = 1.947/3.471/5.902/1.737 ms'
            command_time: 2.1
            result: Success
          2:
            command: echo 'test'
            expected: test
            output: test
            command_time: 0.09
            result: Success
  actions:
    success: false
    steps:
      1:
        type: action
        action: test_plan
        machine: kali
        expected: Success
        result: Fail
        time: 9.56
        commands:
          1:
            operator: AND
            group_time: 7.29
            group_result: Success
            1a:
              command: nmap -sV 192.168.2.10 | fgrep 'Apache' | awk '/open/'
              expected: Apache
              output: 80/tcp open  http    Apache httpd 2.4.49 ((Unix))
              command_time: 7.2
              result: Success
            1b:
              command: echo 'test kali'
              expected: test kali
              output: test kali
              command_time: 0.09
              result: Success
          2:
            call: testping
            expected: Success
            result: Success
            action_time: 2.17
            commands:
              1:
                command: ping -c 3 192.168.2.10
                expected: 3 received
                output: 'PING 192.168.2.10 (192.168.2.10) 56(84) bytes of data.

                  64 bytes from 192.168.2.10: icmp_seq=1 ttl=61 time=3.97 ms

                  64 bytes from 192.168.2.10: icmp_seq=2 ttl=61 time=2.20 ms

                  64 bytes from 192.168.2.10: icmp_seq=3 ttl=61 time=2.83 ms


                  --- 192.168.2.10 ping statistics ---

                  3 packets transmitted, 3 received, 0% packet loss, time 2002ms

                  rtt min/avg/max/mdev = 2.196/3.000/3.971/0.734 ms'
                command_time: 2.09
                result: Success
              2:
                command: echo 'test'
                expected: test
                output: test
                command_time: 0.08
                result: Success
          3:
            command: curl 'http://192.168.2.10/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh'
              -d 'A=|echo;ls'
            expected: bash
            output: '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">

              <html><head>

              <title>404 Not Found</title>

              </head><body>

              <h1>Not Found</h1>

              <p>The requested URL was not found on this server.</p>

              </body></html>'
            command_time: 0.1
            result: Fail

```

### Plan-Level Fields

* `plan_name` – Name of the executed plan
* `timestamp` – Execution identifier
* `total_time` – Total execution time (seconds)
* `final_result` – Overall plan result of the plan
* `steps` – Breakdown of execution

---

### `need` Section

* Contains prerequisite steps
* Includes:

  * `success` – Whether all prerequisites passed
  * `steps` – Detailed log per prerequisite step

Each step contains:

* `type` – action or command
* `machine` – Machine executing the step
* `expected` – Expected result
* `result` – Step result
* `time` – Execution time
* `commands` – If type is action, full action breakdown

---

### `actions` Section

* Contains main execution steps
* Same structure as `need`
* Includes overall `success` flag

---

## Ownership and Permissions

If the lab is executed using `sudo`, log files and folders are automatically reassigned to the original user (using `SUDO_UID` and `SUDO_GID`).

This ensures:

* No root-owned log files
* Proper file access after execution

---

## Purpose of Logs

Logs provide:

* Full reproducibility of execution
* Debugging information
* Execution timing analysis
* Forensic traceability
* Structured machine-readable output (YAML)

---

