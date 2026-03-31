import os
import re
import sys
import yaml
import argparse


class LabManager:

    def __init__(self, script_dir, lab_folder, lab_name):    
        self.script_dir = script_dir
        self.conf_file = os.path.join(lab_folder, "lab_conf.yaml")
        self.lab_name = lab_name

    
    def load_lab(self):
        """
        Parse the YAML lab configuration file and return lab info + devices.
        """
        if self.conf_file:
            with open(self.conf_file, "r") as f:
                data = yaml.safe_load(f)
        else:
            print("[ERROR] lab_conf.yaml not found.")
            return 
        lab_info = data.get("lab", {})
        devices = data.get("devices", {})

        # Normalize devices structure into a dictionary
        parsed_devices = {}
        for name, cfg in devices.items():
            parsed_devices[name] = {
                "image": cfg.get("image", None),
                "type": cfg.get("type", None),
                "assets": cfg.get("assets", None),
                "interfaces": cfg.get("interfaces", {}),
                "addresses": cfg.get("addresses", None),
                "options": cfg.get("options") or {},
                "spawn_terminal": cfg.get("spawn_terminal", False),
            }

        return lab_info, parsed_devices

    def prepare_startup_file(self, startup_file, name, dev, lab):
        """
        Create or update a startup file for a device.
        """
        addresses = dev.get("addresses")

        if addresses:
            existing_lines = []
            if os.path.isfile(startup_file):
                with open(startup_file, "r", encoding="utf-8") as f:
                    existing_lines = f.read().splitlines()

            address_lines = [
                f"ip address add {addr} dev {iface}"
                for iface, addr in addresses.items()
                if f"ip address add {addr} dev {iface}" not in existing_lines
            ]

            final_lines = address_lines + existing_lines
            lab.create_file_from_list(final_lines, f"{name}.startup")
        else:
            if os.path.isfile(startup_file):
                lab.create_file_from_path(startup_file, f"{name}.startup")
            else:
                print(f"No addresses and no existing startup file for {name}")

    
 

