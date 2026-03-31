def cli(cmd_manager, stop_event):
    try:
        while not stop_event.is_set():
            line = input("> ").strip()
            if not line:
                continue
            parts = line.split()
            cmd_name, args = parts[0].lower(), parts[1:]
            cmd_func = cmd_manager.cmd_commands.get(cmd_name)
            if cmd_func: 
                cmd_func(args=args, cmd_manager=cmd_manager)
            else:
                print(f"Unknown command: {cmd_name}")
    except KeyboardInterrupt:
            print("\nLab interrupted by user.")
            cmd_manager.cmd_commands.get("exit")(args=None, cmd_manager=cmd_manager)