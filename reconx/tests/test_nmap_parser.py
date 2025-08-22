from pathlib import Path
from reconx.parsers import parse_nmap_xml


def test_parse_basic_nmap_xml():
    xml_path = Path(__file__).resolve().parent.parent / "fixtures" / "nmap_basic.xml"
    result = parse_nmap_xml(xml_path)

    assert "hosts" in result
    assert len(result["hosts"]) == 1

    host = result["hosts"][0]
    assert host["address"] == "192.0.2.1"
    assert len(host["ports"]) == 2

    ports = {p["port"]: p for p in host["ports"]}
    assert ports[22]["service"] == "ssh"
    assert ports[80]["service"] == "http"
    assert ports[80]["product"] == "Apache httpd"
    assert ports[22]["product"] == "OpenSSH"
