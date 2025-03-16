# KathaRange Cyber Lab
KathaRange is a cybersecurity training platform built on the [Kathará framework](https://github.com/KatharaFramework) for cyber attack and defense emulation. It creates a dynamic, containerized network of machines featuring leading open-source technologies like Snort3 IDS, Wazuh SIEM, MITRE's Caldera, and a Kali machine equipped with Atomic Red Team tools.

### Requirements:
- Linux host machine
- Docker
  
### Getting Started
Launch the script in the root of the project.[^1]

    ./init.sh
the script will automatically clone all dependencies and build all images needed by the Kathará lab. You can go grab a coffee, it will take some time to complete :coffee:

Once the process is completed, navigate to the folder:
```
cd lab
kathara lstart
```
⚠️ Wait for all terminals to completely load the startup scripts, then you will able to access all servicies.

Caldera will be listening on:
http://localhost:8888/

depending on which team you want to play:

usr/psw

    red/lRGXTicDZEh_TW23gFoLLrB8uqhat_EogkJD-a2foVg
    blu/e-1yjrXMhf6lKXoKcHAl8VS7P2-aIbFymQqBvwOJ4Xc

or if you restart the server in the container with `--insecure` (edit caldera.startup and restart the container or kill the process in the machine and restart `python3 server.py --insecure`) 

    admin/admin

Wazuh will be at:
https://localhost

usr/psw

    Admin/SecretPassword

