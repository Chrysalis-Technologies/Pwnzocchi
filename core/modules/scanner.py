# scanner.py - Captures Wi-Fi handshakes

import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

def start_scanning(interface):
    load_dotenv()
    data_dir = os.getenv("DATA_DIR", "./captures")
    os.makedirs(data_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{data_dir}/capture_{timestamp}.pcapng"

    print(f"Capturing packets on {interface} into {filename}...")
    subprocess.run(["sudo", "airodump-ng", "-w", filename.replace(".pcapng", ""), "--output-format", "pcapng", interface])
