# KathaRange

## What is it?
**KathaRange** is a cybersecurity network-emulation framework built on the Kathará Framework API (https://github.com/KatharaFramework/Kathara).
It enables the creation of dynamic, containerized networks for cyber attack and defense scenarios, integrating leading open-source technologies such as:

-   **Snort 3** (IDS)
-   **Wazuh** (SIEM)
-   **MITRE Caldera** (adversary emulation)
-   **Kali Linux** with **Atomic Red Team** tools

KathaRange also allows you to define custom actions and automation plans to streamline experiments and testing scenarios.

The project originated from g4br-i's repository **KathaRange** (https://github.com/g4br-i/KathaRange).

## Requirements:
- Linux host machine
- Docker
- Python 3
- Katharà Python API (installation instructions in Getting Started section)

## Demo Lab Setup
### Getting Started
First, give execution permissions to the build script:
```bash
chmod +x ./build_images.sh
```
Then launch the script from the root of the project:
```bash
sudo ./build_images.sh
```
The script will automatically clone all dependencies and build all images needed by the demo lab. You can go grab a coffee, it will take some time to complete :coffee:

Once the process is completed, run the following commands to install Katharà Python API:
```
python3 -m pip install git+https://github.com/saghul/pyuv@master#egg=pyuv
python3 -m pip install "kathara"
```
Then you can start a lab with:

```bash
python3 start_lab.py
```
**Note:** make sure you are in the `docker` group or use `sudo` if necessary:

```bash
sudo python3 start_lab.py
```

You can also view all available options by running:

```
python3 start_lab.py --help
```
Then enter lab name or path (for demo use `lab`).

⚠️ Wait for all terminals to completely load the startup scripts, then you will able to access all services.

Caldera will be listening on:
http://localhost:8888/
depending on which team you want to play:

usr/psw

    red/lRGXTicDZEh_TW23gFoLLrB8uqhat_EogkJD-a2foVg
    blue/e-1yjrXMhf6lKXoKcHAl8VS7P2-aIbFymQqBvwOJ4Xc

or if you restart the server in the container with `--insecure` (edit caldera.startup and restart the container or kill the process in the machine and restart `python3 server.py --insecure`) 

    admin/admin

Wazuh will be at:
https://localhost

usr/psw

    admin/SecretPassword


## Documentation

Full documentation is available [here](https://github.com/francesco-pittacolo/KathaRange/tree/main/docs)
