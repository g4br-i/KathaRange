# CLI Commands

## Overview

When `start_lab.py` is executed, KathaRange starts an interactive terminal interface.

This terminal allows you to:

* Choose the lab to run
* Manage the lab lifecycle (deploy, undeploy, restart)
* Open device terminals (XTerm)
* Execute predefined actions and plans
* Monitor lab status
* Cleanly stop the environment

The terminal remains active until the lab is explicitly stopped (or interrupted with Ctrl + C).

If terminal spawning is enabled, device terminals may open automatically when the lab starts. Otherwise, you can manually open them using the `terminal` command.

---

## Available Commands

The following commands are available inside the KathaRange terminal:


### `help`
Show available commands.

```
help            #full list of commands
help [command]  #specific command
```
---

### `exit`

Stops the lab and exits the terminal.

```
exit
```

---

### `status`

Shows the status of a specific machine or all machines in the lab.

Usage:
```
status <machine1> <machine2> ...
```

Examples:
```
status          # Show all machines' status
status pc1 r1   # Show status for pc1 and r1
status -a       # Show all machines (alternative syntax)
```

---

### `terminal`

Spawn a terminal for specific machines.

Usage:
```
terminal <machine1> <machine2> ...
```

Examples:

```
terminal pc1 r2      # Open terminals for pc1 and r2
terminal -a          # Open terminals for all machines
```

---

### `deploy`

Deploy specific machines in the lab.

Usage:
```
deploy <machine1> <machine2> ...
```


Examples:

```
deploy pc1 r1        # Deploy only pc1 and r1
deploy -a            # Deploy all machines
```

---

### `undeploy`

Undeploy specific machines in the lab.

Usage:
```
undeploy <machine1> <machine2> ...
```

Examples:

```
undeploy pc1 r1        # Undeploy only pc1 and r1
undeploy -a            # Undeploy all machines
```

---

### `restart`

Restart specific machines in the lab (undeploy and then deploy them).

Usage:
```
restart <machine1> <machine2> ...
```

Examples:

```
restart pc1 r1        # Restart only pc1 and r1
restart -a            # Restart all machines
```

---

### `action`

Execute actions defined in `actions.yaml` for the selected machines.

Usage:
```
action <machine1> <action1> <action2> ... <machine2> <action1> ...
```

Examples
```
action kali test                # Runs 'test' on kali using defaults
action kali test $IP=10.10.1.1  # Runs 'test' on kali using 10.10.1.1 for $IP
action kali -a                  # Runs all actions on kali
action kali test r1 -a          # Runs 'test' on kali and all actions on r1
action kali -a r2 testr2        # Runs all actions on kali and 'testr2' on r2
```

You can find more information about actions in `4-Action.md`

---

### `plan`

Execute plans defined in `plans.yaml`.

Usage:
```
plan <plan1> <plan2> ... (at least 1 plan)
```
Examples:
```
plan test            # Run plan 'test' (machines defined inside plans.yaml)
plan -a              # Run all plans
plan test deploy     # Run 'test' and 'deploy' plans
```

---
### Command History & Tab Completion

The KathaRange terminal provides enhanced shell-like features:

* **Command History** – Use the **Up/Down arrow keys** to navigate previously executed commands.  
  * History is **local to the lab session** and is deleted when lab is closed.  

* **Tab Completion** – Press **Tab** to auto-complete commands and machine names

These features make navigating and executing commands faster and more convenient, similar to a standard Linux shell experience.

---
## Notes

* Command names are case-insensitive.
* You can type `help` at any time to see available commands.

