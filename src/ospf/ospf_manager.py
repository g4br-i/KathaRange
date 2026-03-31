from Kathara.manager.Kathara import Kathara
import os
import re
import time

class OSPFManager:
    def __init__(self, lab_folder, lab, devices, routers):
        self.lab_folder = lab_folder
        self.lab = lab
        self.devices = devices
        self.routers = routers


    def parse_ospfd_conf(self, conf_file):
        """
        Parse ospfd.conf and return:
        - networks: list of networks advertised in OSPF
        - is_stub: True if the router has a stub area
        - has_default_originate: True if 'default-information originate' is present
        """
        networks = []
        stub_areas = set()
        has_default_originate = False

        if not os.path.isfile(conf_file):
            return networks, stub_areas, has_default_originate

        with open(conf_file, "r") as f:
            for line in f:
                line = line.strip().lower()  # rimuove spazi e ignora case

                if not line or line.startswith("!"):
                    continue

                # Reti OSPF
                if line.startswith("network"):
                    # cattura il network e verifica se contiene stub
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+/\d+)', line)
                    area_match = re.search(r'area\s+([\d\.]+)', line)
                    if match and area_match:
                        networks.append(match.group(1))
                        if "stub" in line:
                            stub_areas.add(area_match.group(1))

                # Righe dedicate alle aree stub
                elif "area" in line and "stub" in line:
                    area_match = re.search(r'area\s+([\d\.]+)', line)
                    if area_match:
                        stub_areas.add(area_match.group(1))

                # Default originate
                elif "default-information originate" in line:
                    has_default_originate = True

        return networks, list(stub_areas), has_default_originate
    
    def generate_expected_routes(self):
        """
        Generate expected_routes dynamically from ospfd.conf files.
        - Stub routers (area X.X.X.X stub) -> only default route
        - Backbone routers -> all stub networks
        """
        stub_networks = set()
        router_confs = {}

        # First pass: parse all routers, collect stub networks
        for name, dev in self.devices.items():
            if dev.get("type") != "router":
                continue
            conf_path = os.path.join(self.lab_folder, "assets", "routers", name, "etc", "zebra", "ospfd.conf")
            networks, is_stub, has_default = self.parse_ospfd_conf(conf_path)
            router_confs[name] = (networks, is_stub, has_default)
            if is_stub:
                stub_networks.update(networks)

        # Second pass: build expected_routes
        expected_routes = {}
        for name, (networks, is_stub, has_default) in router_confs.items():
            routes = list(stub_networks)  # all routers should see the stub networks
            if has_default:
                routes.append("0.0.0.0/0")  # add default route if advertised
            expected_routes[name] = routes  # store expected routes for this router

        print("Expected OSPF routes:", expected_routes)  # debug: print expected routes
        return expected_routes
    
    def check_ospf(self, router, expected_routes):
        """
        Verify that a router has learned all expected OSPF routes.
        Returns True if successful, False otherwise.
        """
        name = router.name
        if name not in expected_routes:
            return True  # No OSPF expectations defined for this router

        # Run OSPF route check inside the container
        stdout, stderr, rc = Kathara.get_instance().exec(
            machine_name=name,
            command=["vtysh", "-c", "show ip route ospf"],
            lab=self.lab,
            stream=False  # wait for command to finish
        )

        if rc != 0:
            print(f"[{name}] Command failed: {stderr.decode().strip()}")
            return False

        if stdout:
            try:
                ospf_routes = stdout.decode().strip()
            except Exception:
                pass
        elif stderr:
            try:
                ospf_routes = stderr.decode().strip()
            except Exception:
                pass
        else:
            ospf_routes = ""
        print(f"\n=== {name} OSPF Routes ===\n{ospf_routes}\n")

        # Verify that each expected prefix is present
        for prefix in expected_routes[name]:
            if prefix not in ospf_routes:
                print(f"[{name}] Missing {prefix}")
                return False

        print(f"[{name}] All expected routes present")
        return True
    
    def check_and_deploy(self):
        
        # Generate dynamic expected_routes
        expected_routes = self.generate_expected_routes()
        Kathara.get_instance().deploy_lab(self.lab, selected_machines=self.routers)

        print("\nWaiting for OSPF convergence...")
        converged = False
        timeout = 180
        start_time = time.time()

        while not converged and (time.time() - start_time < timeout):
            checks = []
            for name in self.routers:
                r = self.lab.get_machine(name)
                checks.append(self.check_ospf(r, expected_routes))
            if all(checks):
                converged = True
            else:
                time.sleep(5)

        if converged:
            print("\nOSPF convergence achieved!")
        else:
            print("\nTimeout reached, OSPF did not fully converge.")

        Kathara.get_instance().deploy_lab(self.lab, excluded_machines=self.routers)
