from app.objects.secondclass.c_fact import Fact
from app.objects.secondclass.c_relationship import Relationship
from app.utility.base_parser import BaseParser


class Parser(BaseParser):

    def parse(self, blob):
        relationships = []
        for match in self.line(blob):
            version = self._extract_version(match)
            if version:
                for mp in self.mappers:
                    source = self.set_value(mp.source, version, self.used_facts)
                    target = self.set_value(mp.target, version, self.used_facts)
                    relationships.append(
                        Relationship(source=Fact(mp.source, source),
                                     edge=mp.edge,
                                     target=Fact(mp.target, target))
                    )
        return relationships

    @staticmethod
    def _extract_version(line):
        """
        Extracts service version from an Nmap output line.
        Example line: '80/tcp open  http Apache httpd 2.4.49 ((Unix))'
        """
        try:
            if 'open' in line:
                # Extract the part after the service and before additional info
                import re
                match = re.search(r'open\s+\S+\s+(.+? \d+\.\d+(\.\d+)?)', line)
                if match:
                    return match.group(1).strip()
        except Exception:
            pass
        return None
