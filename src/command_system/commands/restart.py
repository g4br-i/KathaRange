from src.command_system.utils import handle_errors
from Kathara.manager.Kathara import Kathara

@handle_errors
def cmd_restart(args, cmd_manager):
    """
    Restart machines in the lab.
    Usage: restart <machine1> <machine2>
    Example: restart pc1 caldera
    """
    if not args:
        print("You must specify at least one machine name.")
        return
    if len(args) == 1 and args[0] == "-a":
        print("\nRestarting all machines:")
        args = list(cmd_manager.lab.machines.keys())
    #print(args)  
    cmd_manager.run_command("undeploy",args)
    cmd_manager.run_command("deploy",args)


