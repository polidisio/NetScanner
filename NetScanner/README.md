# NetScanner 🔍

Network scanner for local network with Pi-hole integration.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python netscanner.py --network 192.168.1.0/24
python netscanner.py --export json
python netscanner.py --pihole http://pi-hole.local
```

## Features

- ARP network scan
- Device identification
- Pi-hole integration
- MAC vendor lookup
- Export to JSON/CSV
