# Architecture

## System Overview

KathaRange is a framework built on top of Kathara API.
It provides automated lab deployment, action execution, plan orchestration, and structured logging within a controlled lab environment.

The system is designed around clear separation of responsibilities between infrastructure management, execution logic, and logging.

Core concepts:

* **Lab** – Virtual network environment composed of machines and links
* **Action** – Ordered set of commands executed on a machine
* **Plan** – Orchestration of multiple actions and/or commands
* **Command** – Single executable shell instruction
* **Log** – Structured YAML trace of execution

---

## Architectural Layers

The system follows a layered architecture to ensure modularity and maintainability.

### Infrastructure Layer

Responsible for provisioning and managing the virtual lab environment.

#### Responsibilities

* Load lab configuration
* Instantiate machines
* Configure network topology
* Connect interfaces and links
* Copy assets and startup files
* Deploy and undeploy lab
* Optional OSPF deployment and convergence validation

#### Main Components

* `LabManager`
* `OSPFManager`
* `Kathara`

This layer abstracts Docker/Kathara details from the execution engine.

---

### Execution Layer

The Execution Layer serves as the system's orchestration engine. It is responsible for interpreting YAML definitions, orchestrating execution, managing user-invoked commands, and connecting actions and plans to the logging system.

#### Responsibilities

* Parse `actions.yaml` (`action_parser`)
* Parse `plans.yaml` (`plan_parser`)
* Inject parameters from plan sections and CLI variables into action definitions (handled by `action` and `plan` commands)
* Execute commands on target machines, delegating each command to perform its specific task and return a result (`action` and `plan` commands)
* Evaluate expected results (`action` and `plan` commands)
* Handle logical operators (AND / OR) in compound commands (`action` command)
* Aggregate execution results and log metadata (`CommandManager`)
* Manage user-invoked utility commands such as `status`, `deploy`, and `help` (`CommandManager`)

#### Main Components

* `CommandManager` – central hub that receives user commands and delegates execution
* `action_parser` – parses action definitions from `actions.yaml`
* `plan_parser` – parses plan definitions from `plans.yaml`
* Available commands – implement execution logic for actions, plans, and utility operations

---

### Logging Layer

Responsible for structured and reproducible execution tracing.

#### Responsibilities

* Generate YAML logs for actions and plans
* Automatically create directory structure if missing
* Store execution metadata
* Record timing information
* Record expected vs actual output
* Ensure proper ownership when running with sudo

#### Components

* `ActionLogger`
* `PlanLogger`

Logs are deterministic, structured, and machine-readable.

---

### Interface Layer

The Interface Layer is responsible for user interaction and runtime control. It provides the operational interface without embedding execution logic and serves as the entry point for user commands and runtime management.

#### Responsibilities

* Parse CLI arguments (`parse_args`)
* Handle interactive command input (`cli`)
* Spawn terminals for machines (`spawn_terminal`)
* Monitor running processes (`monitor_processes`)
* Dispatch commands to the execution engine (`CommandManager`)

#### Utilities

* `parse_args` – parses command-line arguments and configuration options
* `cli` – manages interactive command input from the user
* `spawn_terminal` – opens terminals for lab machines
* `monitor_processes` – monitors and maintains running processes
---

## Startup Workflow

When the system starts:

1. CLI arguments are parsed
2. Lab configuration is loaded
3. Actions and plans are parsed
4. Previous lab instance is undeployed (if present)
5. Lab topology is created
6. Machines are configured and connected
7. Assets and startup files are injected
8. Lab is deployed via Kathara
9. CommandManager is initialized
10. Interactive loop begins

---

## Runtime Execution Flow

### Action Execution Flow

1. User triggers an action
2. CommandManager retrieves action definition
3. Parameters are resolved
4. Commands are executed sequentially
5. Expected outputs are validated
6. Logical groups (AND / OR) are evaluated
7. Final result is computed
8. Action log is generated

### Plan Execution Flow

1. User triggers a plan
2. Prerequisite steps (`need`) are executed
3. If prerequisites succeed, main actions run
4. Each action generates its own detailed breakdown
5. Plan aggregates step results
6. Plan log is generated

---

## Infrastructure Command Flow

In addition to actions and plans, the system supports direct infrastructure commands triggered via CLI, such as:

- `deploy`
- `undeploy`
- `restart`
- `status`
- `terminal`
- `exit`

These commands interact directly with the **Infrastructure Layer** and at the moment they do **not** generate logs.

### Command Data Flow
```
User Input (CLI)
    ↓
CLI Parser / CommandManager
    ↓
Infrastructure Layer (LabManager / Kathara)
    ↓
Lab / Machines / Network
    ↓
Output to Terminal
```
---
## Action/Plan Data Flow

High-level execution data flow:

```
User Input
    ↓
CommandManager
    ↓
Action / Plan Engine
    ↓
Command Execution (inside machine)
    ↓
Result Evaluation
    ↓
Logger
    ↓
YAML Log File
```

This flow guarantees full traceability from user input to persisted log.

---

## Directory Structure Logic

The architecture enforces a structured directory organization:

```
<lab>/
├── actions.yaml
├── plans.yaml
├── assets/
├── startups/
└── logs/
```

Logs are automatically created if the directory hierarchy does not exist.

This ensures:

* No manual preparation required
* Consistent structure across labs
* Clean separation between configuration and runtime artifacts

---

## Design Principles

The architecture is based on the following principles:

### YAML-Driven Configuration

Execution behavior and orchestration are defined declaratively through YAML files.
This enables readable, version-controlled, and easily modifiable lab scenarios.

### Flexible Lab Definition

Any lab topology can be defined through configuration, including:
- Arbitrary number of machines
- Custom network segments
- Dynamic interface mappings
- Custom startup scripts and assets

This makes the system adaptable to a wide range of scenarios, from simple testing environments to complex multi-network infrastructures.

### Separation of Concerns

Infrastructure, execution logic, logging, and user interaction are isolated in dedicated components.

### Deterministic Execution

Expected outputs are explicitly defined and validated, ensuring predictable and controlled behavior during execution.

### Parameterized Execution
Actions and plans support parameter injection, allowing reusable definitions that can adapt dynamically to different environments or scenarios.

### Reproducibility

Each execution of actions and plans is fully traceable via structured, timestamped YAML logs, enabling debugging and auditing.

### Automatic Environment Preparation

Required directories and runtime structures are automatically created.

### Extensibility

The architecture allows future extensions such as:

* Additional routing protocols
* New execution operators
* Extended validation mechanisms

Because components are modular, new features can be added without impacting unrelated layers.


