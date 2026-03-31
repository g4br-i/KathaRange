from src.command_system.utils import setup_history_and_completion
from src.command_system.commands.help import cmd_help
from src.command_system.commands.exit import cmd_exit
from src.command_system.commands.status import cmd_status
from src.command_system.commands.terminal import cmd_terminal
from src.command_system.commands.deploy import cmd_deploy
from src.command_system.commands.undeploy import cmd_undeploy
from src.command_system.commands.restart import cmd_restart
from src.command_system.commands.action import cmd_action
from src.command_system.commands.plan import cmd_plan


from threading import Event

class CommandManager:
    
    def __init__(self, lab, lab_name, devices, actions, plans, processes, action_logger, plan_logger, spawn_terminals=True):
        self.lab = lab
        self.lab_name = lab_name
        self.devices = devices
        self.actions = actions
        self.plans = plans
        self.processes = processes
        self.action_logger = action_logger
        self.plan_logger = plan_logger
        self.stop_event = Event()
        self.spawn_terminals = spawn_terminals

        setup_history_and_completion(self)

        # Commands
        self.cmd_commands = {
            "help": cmd_help,
            "exit": cmd_exit,
            "status": cmd_status,
            "terminal": cmd_terminal,
            "deploy": cmd_deploy,
            "undeploy": cmd_undeploy,
            "restart": cmd_restart,
            "action" : cmd_action,
            "plan" : cmd_plan
        }
    
    def run_command(self, command_name, args=None):
        cmd = self.cmd_commands.get(command_name)
        if cmd:
            cmd(args=args, cmd_manager=self)
        else:
            print(f"No such command: {command_name}")
