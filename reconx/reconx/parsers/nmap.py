from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
from xml.etree import ElementTree as ET


def parse_nmap_xml(xml_path: Path) -> Dict[str, Any]:
    """Parse an Nmap XML output file.

    The returned dictionary contains a ``hosts`` key where each host has its
    IPv4 address and a list of ``ports``.  Each port entry includes common
    service information so that callers can easily convert the results into a
    :class:`~reconx.model.SummaryModel` ``Evidence`` object.

    Parameters
    ----------
    xml_path:
        Path to the Nmap XML file.

    Returns
    -------
    Dict[str, Any]
        Structured data describing hosts, ports and services.
    """

    tree = ET.parse(xml_path)
    root = tree.getroot()

    hosts: List[Dict[str, Any]] = []
    for host in root.findall("host"):
        addr_elem = host.find("address[@addrtype='ipv4']")
        if addr_elem is None:
            # Skip hosts without an IPv4 address
            continue
        host_dict: Dict[str, Any] = {"address": addr_elem.get("addr"), "ports": []}

        ports_elem = host.find("ports")
        if ports_elem is not None:
            for port in ports_elem.findall("port"):
                port_dict: Dict[str, Any] = {
                    "port": int(port.get("portid", 0)),
                    "proto": port.get("protocol"),
                }

                state_elem = port.find("state")
                if state_elem is not None:
                    port_dict["state"] = state_elem.get("state")

                service_elem = port.find("service")
                if service_elem is not None:
                    if service_elem.get("name"):
                        port_dict["service"] = service_elem.get("name")
                    if service_elem.get("product"):
                        port_dict["product"] = service_elem.get("product")
                    if service_elem.get("version"):
                        port_dict["version"] = service_elem.get("version")

                host_dict["ports"].append(port_dict)

        hosts.append(host_dict)

    return {"hosts": hosts}
