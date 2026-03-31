from src.command_system.utils import handle_errors
from Kathara.manager.Kathara import Kathara
from src.lab_manager.utils.spawn_terminal import spawn_terminal

@handle_errors
def cmd_deploy(args, cmd_manager):
    """
    Deploy specific machines in the lab.
    Usage: deploy <machine1> <machine2> ...
    """
    if not args:
        print("You must specify at least one machine name.")
        return
    
    if len(args) == 1 and args[0] == "-a":
        args = list(cmd_manager.lab.machines.keys())

    deployed = []
    for name in args:
        try:
            stats_gen = Kathara.get_instance().get_machine_stats(name, lab=cmd_manager.lab)
            stats = next(stats_gen, None)
            
            if stats is not None:
                print(f"{name} is already running.")
                continue

            Kathara.get_instance().deploy_lab(lab=cmd_manager.lab, selected_machines=[name])
            # spawn terminal if needed
            dev = cmd_manager.devices.get(name)
            if dev and (cmd_manager.spawn_terminals or dev.get("spawn_terminal", False)):
                p = spawn_terminal(name, cmd_manager.lab_name)
                cmd_manager.processes[name] = p
            deployed.append(name)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"Error: Failed to deploy machine {name}: {e}")

    if deployed:
        print(f"Machines deployed: {', '.join(deployed)}")
    else:
        print("No machines were deployed")