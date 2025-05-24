# interface_setup.py - Detects and prepares external WiFi adapter

import subprocess
import os

def setup_monitor_interface():
    from dotenv import load_dotenv
    load_dotenv()

    adapter_id = os.getenv("ADAPTER_ID")
    result = subprocess.run(["lsusb"], capture_output=True, text=True)

    interface_name = None
    if adapter_id in result.stdout:
        iw_result = subprocess.run(["iw", "dev"], capture_output=True, text=True)
        for line in iw_result.stdout.splitlines():
            if "Interface" in line:
                interface_name = line.strip().split()[-1]
                break
        if interface_name:
            subprocess.run(["sudo", "ip", "link", "set", interface_name, "down"])
            subprocess.run(["sudo", "iw", interface_name, "set", "monitor", "control"])
            subprocess.run(["sudo", "ip", "link", "set", interface_name, "up"])
            print(f"Interface {interface_name} set to monitor mode.")
            return interface_name
    print("External adapter not found.")
    return None
