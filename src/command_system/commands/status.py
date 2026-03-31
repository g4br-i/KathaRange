from src.command_system.utils import handle_errors
from Kathara.manager.Kathara import Kathara

def get_stats(machine, cmd_manager):
    stats_gen = Kathara.get_instance().get_machine_stats(machine, lab=cmd_manager.lab)
    stats = next(stats_gen, None)
    if stats:
        print(stats)
    else:
        print(f"{machine}: Not running")

@handle_errors
def cmd_status(args, cmd_manager):
    """
    Show the status of specific machine or the status of all machines
    Usage status <machine1> <machine2> ...
    Example status pc1 r1
    """
    if not args:
        print("You must specify at least one machine name.")
        return
    
    #Case -a
    if len(args) == 1 and args[0] == "-a":
        args = list(cmd_manager.lab.machines.keys())
    
    #Specific machines case
    for name in args:
        try:
            get_stats(name, cmd_manager)
        except KeyboardInterrupt:
            raise    
        except:
            print(f"{name}: Status not found")