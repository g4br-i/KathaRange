from src.command_system.utils import handle_errors
from Kathara.manager.Kathara import Kathara

@handle_errors
def cmd_undeploy(args, cmd_manager):
    """
    Undeploy specific machines in the lab.
    Usage: undeploy <machine1> <machine2> ...
    """
    if not args:
        print("You must specify at least one machine name.")
        return

    if len(args) == 1 and args[0] == "-a":
        args = list(cmd_manager.lab.machines.keys())
    
    undeployed = []
    for name in args:
        try:
            stats_gen = Kathara.get_instance().get_machine_stats(name, lab=cmd_manager.lab)
            stats = next(stats_gen, None)
            
            if stats is None:
                print(f"{name} is already stopped.")
                continue

            Kathara.get_instance().undeploy_lab(lab=cmd_manager.lab, selected_machines=[name])
            # terminate terminal if it exists
            p = cmd_manager.processes.get(name)
            if p and p.poll() is None:
                p.terminate()
                print(f"Terminal for {name} closed.")
            undeployed.append(name)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"Error: Failed to undeploy machine {name}: {e}")

    if undeployed:
        print(f"Machines undeployed: {', '.join(undeployed)}")
    else:
        print("No machines were undeployed")