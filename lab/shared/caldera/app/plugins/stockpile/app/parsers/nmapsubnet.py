from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.utility.base_parser import BaseParser
import re
import logging 
class Parser(BaseParser):
    
    def parse(self, blob):
        
        relationships = [] 
        targets = self._extract_target_ip(blob)
        if targets:
            for ip in targets:
               #logging.info(f"ip:{ip}")
               for mp in self.mappers:
                        source = self.set_value(mp.source, ip, self.used_facts)
                        target = self.set_value(mp.target, ip, self.used_facts)
                        relationships.append(
                            Relationship(source=Fact(mp.source, source),
                                         edge=mp.edge,
                                         target=Fact(mp.target, target))
                        )
            return relationships

    @staticmethod
    def _extract_target_ip(blob):
        """
        Extracts possible target ips running a service on port 80 from an Nmap output line.
        Example line: 'Nmap scan report for 192.168.2.1
                        Host is up (0.0016s latency).

                        PORT   STATE  SERVICE
                        80/tcp open http'
        """
        try:
            
            pattern = r"Nmap scan report for (\S+).*?80/tcp\s+(\S+)\s"

            # Parse the output
            host_port_status = {}
            for match in re.finditer(pattern, blob, re.DOTALL):
                host, port_status = match.groups()
                if port_status == 'open':
                    host_port_status[host] = port_status
            if len(host_port_status) > 0 :
                return host_port_status
            else:
                return None

        except Exception as e:
            logging.info(f"failed {e}")
            pass
        return None
