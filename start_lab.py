from Kathara.manager.Kathara import Kathara
from src.logs.action_logger import ActionLogger
from src.logs.plan_logger import PlanLogger
from Kathara.model.Lab import Lab
from src.lab_manager.LabManager import LabManager
from src.ospf.ospf_manager import OSPFManager
from src.lab_manager.utils.arg_parser import parse_args
from src.lab_manager.utils.process_monitor import monitor_processes
from src.command_system.action_parser import parse_actions
from src.command_system.plan_parser import parse_plans
from src.command_system.cmd_manager import CommandManager
from src.command_system.cli import cli
from src.lab_manager.utils.spawn_terminal import spawn_terminal
import threading
import sys
import os


if __name__ == "__main__":
    python_path = sys.executable 
    try:

        script_dir = os.path.dirname(os.path.abspath(__file__))
        args = parse_args(script_dir)
        
        lab_name_arg = args.lab_name
        spawn_terminals = args.spawn_terminals
        check_r_ospf = args.check_ospf
        

        lab_folder = os.path.join(script_dir, lab_name_arg)

        action_logger = ActionLogger(lab_folder)
        plan_logger = PlanLogger(lab_folder)
        lab_manager = LabManager(script_dir, lab_folder, lab_name=None)
        
        # Load lab configuration
        lab_info, devices = lab_manager.load_lab()
        lab_name = lab_info.get("name")
        lab_manager.lab_name = lab_name
        if os.path.isfile(os.path.join(lab_folder,"actions.yaml")):
            try: 
                actions = parse_actions(os.path.join(lab_folder,"actions.yaml"))
                actions = { str(k): v for k, v in actions.items() }
            except Exception as e:
                print(e)
                exit()
        if os.path.isfile(os.path.join(lab_folder,"plans.yaml")):
            try: 
                plans = parse_plans(os.path.join(lab_folder,"plans.yaml"))
                plans = { str(k): v for k, v in plans.items() }
            except Exception as e:
                print(e)
                exit()
        #print("Dynamic expected_routes:", expected_routes) # for debug

        Kathara.get_instance().undeploy_lab(lab_name=lab_name)

        # Initialize lab
        print(f"Creating Lab {lab_name}...")
        lab = Lab(lab_name)

        lab_devices = {}

        # Create devices from configuration
        for name, dev in devices.items():

            #print(f"\nCreating device '{name}'")
            #print(f"  Image: {dev['image']}")
            #print(f"  Interfaces: {dev['interfaces'] if dev['interfaces'] else 'None'}")
            #print(f"  Options: {dev['options'] if dev['options'] else 'None'}\n")

            lab_devices[name] = lab.new_machine(
                name,
                **{
                    "image": dev["image"],
                    **dev["options"],
                }
            )
            lab_devices[name].add_meta("type", dev["type"])

            # Connect interfaces
            for iface_name, link_name in dev.get("interfaces", {}).items():
                iface_index = int(iface_name.replace("eth", ""))
                lab.connect_machine_to_link(name, link_name, machine_iface_number=iface_index)

            # Ensure the image is available
            Kathara.get_instance().check_image(dev['image'])
            device = lab_devices[name]


            # Copy device-specific assets if available
            if dev["assets"] == None:
                machine_folder_name = os.path.join(lab_folder, "assets", name)
                if os.path.isdir(machine_folder_name):
                    device.copy_directory_from_path(machine_folder_name, f"/")
        
                # Copy router-specific assets if available
                router_folder_name = os.path.join(lab_folder, "assets", "routers", name)
                if os.path.isdir(router_folder_name):
                    device.copy_directory_from_path(router_folder_name, f"/")
            else:
                # If custom assets are defined as a list in the YAML
                try:
                    for asset_path in dev["assets"]:
                        abs_asset_path = os.path.abspath(asset_path)
                        if os.path.exists(abs_asset_path):
                            if os.path.isdir(abs_asset_path):
                                # Copy entire directory
                                dest_path = "/"
                                device.copy_directory_from_path(abs_asset_path, dest_path)
                            else:
                                # Copy single file (e.g., README.md)
                                dest_path = f"/{asset_path}"
                                device.create_file_from_path(abs_asset_path, dest_path)
                        else:
                            print(f"Asset not found: {abs_asset_path}")
                except Exception as e:
                    print(f"Failed to copy custom assets for {name}: {e}")

            # Handle startup files
            startup_file = os.path.join(lab_folder, "startups", f"{name}.startup")
            lab_manager.prepare_startup_file(startup_file, name, dev, lab)

            # Copy agent/snort dependencies if required
            if os.path.isfile(startup_file):
                with open(startup_file, "r") as sf:
                    content = sf.read()
                    if "init_caldera" in content:
                        try:
                            device.copy_directory_from_path(os.path.join(lab_folder, "assets", "agents"), "/agents")
                        except:
                            print("Directory agents not found")
                            continue
                    #Management of this part to be reviewed
                    lab_has_wazuh = any(map(lambda d: "wazuh" in d["image"].lower(), devices.values()))

                    if "wazuh" in content or ("snort" in dev["image"].lower() and lab_has_wazuh):
                        try:
                            device.create_file_from_path(
                                os.path.join(lab_folder, "assets", "wazuh-agent_4.9.0-1_amd64.deb"),
                                "/wazuh-agent_4.9.0-1_amd64.deb"
                            )
                        except:
                            print("file wazuh-agent_4.9.0-1_amd64.deb not found")
                            continue

                    if "wazuh-indexer" in dev["image"]:
                        wazuh_indexer_path = os.path.join(lab_folder, "assets", "wazuh_indexer")
                        device.add_meta("volume", f"{os.path.abspath(wazuh_indexer_path)}|/wazuh_indexer|ro")
                    if "wazuh-dashboard" in dev["image"]:
                        wazuh_dashboard_path = os.path.join(lab_folder, "assets", "wazuh_dashboard" )
                        device.add_meta("volume", f"{os.path.abspath(wazuh_dashboard_path)}|/wazuh_dashboard|ro")

                        #Bug, this test doesn't work, i can't copy folders in wazuh indexer and dashboard containers with copy_directory_from_path
                        test = os.path.join(lab_folder, "assets", "test")
                        if os.path.isdir(test):
                            device.copy_directory_from_path(test,"/")
                        
                    if "snort" in dev["image"]:
                        snort_path = os.path.join(lab_folder, "assets", "snort3")
                        if os.path.isdir(snort_path):
                            device.copy_directory_from_path(snort_path, "/snort3/")

        # Identify routers
        routers = set(map(lambda x: x.name, filter(lambda x: x.meta["type"] == "router", lab.machines.values())))

        # OSPF deployment and convergence check
        if check_r_ospf:

            ospf_manager = OSPFManager(lab_folder, lab, devices, routers)
            ospf_manager.check_and_deploy()

        else:
            Kathara.get_instance().deploy_lab(lab)
    
        # Open terminals
        processes = {}
        cmd_manager = CommandManager(
            lab=lab,
            lab_name = lab_name,
            devices=devices,
            actions=actions,
            plans = plans,
            processes=processes,
            action_logger=action_logger,
            plan_logger=plan_logger,
            spawn_terminals=spawn_terminals
        )

        for name, dev in devices.items():
            if spawn_terminals or dev.get("spawn_terminal", False):
                p = spawn_terminal(name, lab_name)
                cmd_manager.processes[name] = p
        stop_event = threading.Event()

        if processes:
            print("\nLab deployed. Type 'exit' to stop lab or 'help' to see available commands.")
            threading.Thread(target=monitor_processes, args=(processes, stop_event), daemon=True).start()
        else:
            print("\nLab deployed in background. Type 'exit' to stop.")

        cli(cmd_manager, stop_event)


    except Exception as e:
        if "Permission denied" in str(e) or "DockerDaemonConnectionError" in str(type(e)):
            print("You need root permissions to run this script (or add your user to the 'docker' group).")
            sys.exit(1)
        else:
            raise     