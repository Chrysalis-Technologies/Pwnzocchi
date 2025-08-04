# Warwalker

Warwalker is a simple cross-platform Wi-Fi handshake collector. It combines a Python backend that configures a wireless interface into monitor mode and runs `airodump-ng` with a desktop UI built using Avalonia and .NET 8.

## Features
- Detects an external USB Wi-Fi adapter and enables monitor mode.
- Captures packets and saves them as `.pcapng` files.
- Desktop interface built with Avalonia to start scans and display status messages.

## Prerequisites
- Python 3 with the [`python-dotenv`](https://pypi.org/project/python-dotenv/) package.
- Aircrack-ng tools (`airodump-ng`, `iw`, `ip`, `lsusb`).
- .NET 8 SDK to build and run the Avalonia UI.
- A Wi-Fi adapter that supports monitor mode.

## Configuration
Create a `.env` file in the project root with at least the following values:

```dotenv
ADAPTER_ID=0bda:c811    # USB vendor:product ID for the adapter
DATA_DIR=./captures     # Where capture files will be stored
```

## Running the CLI scanner
```
python core/main.py
```
The script will search for the adapter, switch it to monitor mode and launch `airodump-ng` writing captures under `DATA_DIR`.

## Running the UI
The Avalonia front end wraps the Python scanner and exposes a simple button to start scans.

```
dotnet run --project ui/Warwalker.UI.csproj
```

## Repository layout
- `core/` – Python modules for interface setup and packet capture.
- `ui/` – Avalonia desktop application.
- `Warwalker.sln` – .NET solution file.
