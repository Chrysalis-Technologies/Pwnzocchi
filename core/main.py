# main.py - Warwalker Entry Point
from core.modules.interface_setup import setup_monitor_interface
from core.modules.scanner import start_scanning

if __name__ == "__main__":
    iface = setup_monitor_interface()
    if iface:
        start_scanning(iface)
    else:
        print("No valid external interface found. Exiting.")
