# Lab Configuration

KathaRange uses **YAML configuration files** (`lab_conf.yaml`) to define **laboratory topologies**.
These files allow users to declare **nodes, network interfaces, IP addresses, services, and optional properties**, enabling the deployment of fully customizable cyber-range environments.

---

## Lab Metadata

Each lab configuration file begins with metadata:

```yaml
name: "Lab name"
description: "Lab description"
version: "Lab version"
author: "Author Name"
```

* **name**: Name of the lab
* **description**: Short description of the lab scenario
* **version**: Configuration version
* **author**: Creator or maintainer of the lab

---

## Devices

The `devices` section defines all machines in the lab. Each device can represent a router, server, workstation, or security tool.

Each device typically includes:

* **image**: Docker image to deploy
* **type**: Node type (e.g., router, server, workstation) *(optional)*
* **interfaces**: Mapping of virtual NICs to network segments
* **addresses**: IP addresses assigned to each interface

This structure enables the orchestration engine to deploy **modular and flexible lab topologies**.

---

## Device Categories *(Optional)*

Devices can be logically grouped using the `type` field:

1. **Routers** – Connect networks and forward traffic
2. **Servers** – Host applications or vulnerable services
3. **Workstations** – Represent endpoints (attackers or users)
4. **Security & Monitoring Nodes** – IDS, SIEM, or adversary simulation tools

---

## Optional Device Properties

Devices may include **optional fields** to customize behavior and runtime environment:

* **spawn_terminal**: Automatically open a terminal on startup
* **assets**: Copy files into the container root (`/`). Defaults to `<lab_name>/assets/<device_name>/` if present
* **options**: Additional configurations

  * **bridged**: Enable bridged networking (e.g., `bridged: true`)
  * **envs**: Environment variables for service configuration
  * **ports**: Host-to-container port mappings for external access
  * **ulimits**: Resource limits (e.g., memory, file descriptors)

---

## Device Example

```yaml
caldera:
  image: caldera:5.0.0-kathaRange
  spawn_terminal: true
  interfaces:
    eth0: B1
  addresses:
    eth0: 192.168.0.20/24
  options:
    bridged: true
    ports:
      - "8888:8888/tcp"
```

---

## Networks and Interfaces

* Networks are defined implicitly through interface mappings
* Routers enable communication between network segments
* Devices can be bridged to the host network when required
* IP addressing should be consistent to avoid conflicts

---

## Startup Files

The `startups` folder can contain custom initialization scripts for devices.
Each file must be named:

```
<device_name>.startup
```

to match the corresponding device configuration.

---

## Extending Labs

To create or modify a lab:

1. Copy an existing configuration or create a new YAML file
2. Define all devices in the `devices` section
3. Assign interfaces and IP addresses
4. Specify Docker images and optional properties (`ports`, `envs`, `ulimits`, etc.)
5. Update metadata (`name`,`description`, `version`, `author`)
6. Add required assets (e.g., certificates for Wazuh) if not already included
7. Define startup files *(optional)*
8. Define actions and plans for automation *(optional)*
9. Launch the lab using `start_lab.py` and validate the deployment

This approach supports **arbitrary lab topologies**, from small experiments to complex enterprise-like environments.
