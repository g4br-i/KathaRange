from Kathara.manager.Kathara import Kathara
from src.lab_manager.utils.spawn_terminal import spawn_terminal

def cmd_terminal(args, cmd_manager):
    """
    Spawn terminal for specific machines (1+)
    Usage: terminal <machine1> <machine2> ...
    Example: terminal pc1 r2

    Use flag -a to spawn terminal for all machines
    Usage terminal -a
    """
    if not args:
        print("You must specify at least one machine name.")
        return

    spawned = []

    if len(args) == 1 and args[0] == "-a":
        args = list(cmd_manager.lab.machines.keys())

    try:
        for name in args:
            # Skip machines not running or not in lab
            stats_gen = Kathara.get_instance().get_machine_stats(name, lab=cmd_manager.lab)
            stats = next(stats_gen, None)
            if stats is None or name not in cmd_manager.lab.machines:
                print(f"{name}: Machine not running or not found.")
                continue

            # Skip if terminal already exists
            p = cmd_manager.processes.get(name)
            if p and p.poll() is None:
                print(f"Terminal for {name} is already running.")
                continue

            # Spawn terminal
            p = spawn_terminal(name, cmd_manager.lab_name)
            cmd_manager.processes[name] = p
            spawned.append(name)

    except KeyboardInterrupt:
        print("\nTerminal spawning interrupted by user. Already spawned terminals remain open.")

    if spawned:
        print(f"Spawned terminals for: {', '.join(spawned)}")