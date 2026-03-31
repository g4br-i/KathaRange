from src.command_system.utils import handle_errors

@handle_errors
def cmd_help(args, cmd_manager):
    """
    Show available commands and their descriptions.
    Usage: help
    Usage: help [command]
    """
    if cmd_manager is None:
        print("Error: no manager provided")
        return

    cmd_commands = cmd_manager.cmd_commands

    if args:
        cmd_name = args[0].lower()
        cmd_func = cmd_commands.get(cmd_name)
        if cmd_func:
            doc = cmd_func.__doc__ or "No description available."
            print(doc.strip())
        else:
            print(f"No such command: {cmd_name}")
    else:
        print("\nAvailable commands:\n")
        for name, func in cmd_commands.items():
            doc = func.__doc__ or "No description available."
            print(f"{name}:\n{doc.strip()}\n")
