import argparse
import os
import re
import sys


def parse_args(script_dir):
    parser = argparse.ArgumentParser(
        description="Deploy Kathara lab.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    required_group = parser.add_argument_group("required arguments")
    required_group.add_argument(
        "lab_name",
        nargs="?", 
        help="Lab folder to use (e.g. 'lab', 'lab2', 'bob')\nAsked if not provided."
    )

    optional_group = parser.add_argument_group("optional features")
    optional_group.add_argument(
        "--spawn-terminals",
        action="store_true",
        help="Open a terminal for each device."
    )
    optional_group.add_argument(
        "--check-ospf",
        action="store_true",
        help="Check OSPF routing tables for convergence."
    )
    args = parser.parse_args()

    # Ask for lab_name if not provided
    if not args.lab_name:
        while True:
            try:
                lab_input = input("Enter lab name or path: ").strip()
                lab_base = os.path.basename(lab_input)
                if not re.fullmatch(r"[A-Za-z0-9_-]+", lab_base):
                    print("Invalid lab name! Only letters, numbers, underscores, and dashes are allowed.")
                    continue

                # Determine the lab folder (full path)
                if os.path.isabs(lab_input):
                    lab_folder = lab_input
                else:
                    # Always prioritize ./labs/
                    lab_folder_candidate = os.path.join(script_dir, "labs", lab_input)
                    if os.path.exists(lab_folder_candidate):
                        lab_folder = os.path.abspath(lab_folder_candidate)
                    elif os.path.exists(os.path.abspath(lab_input)):
                        # fallback: check relative to current working directory
                        lab_folder = os.path.abspath(lab_input)
                    else:
                        raise FileNotFoundError(f"Lab folder not found: {lab_input}")

                lab_conf_file = os.path.join(lab_folder, "lab_conf.yaml")
                if not os.path.isfile(lab_conf_file):
                    print(f"Lab '{lab_input}' not found at {lab_folder}. Try again (Ctrl+C to exit)")
                    continue

                args.lab_name = lab_folder
                break

            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                sys.exit(1)

    return args
