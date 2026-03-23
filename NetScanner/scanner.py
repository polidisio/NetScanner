"""
Network scanner module with Pi-hole integration
Uses multiple methods: ARP table, arp command, and Pi-hole API
"""
import socket
import json
import subprocess
import re
import pandas as pd
import requests
import datetime

class NetworkScanner:
    """Scans network for connected devices."""
    
    def __init__(self, network='192.168.1.0/24'):
        self.network = network
        self.pihole_url = None
        self.history_file = 'history.json'
        self.known_devices = {}
        self._load_history()
        self._load_known_devices()
        # Common MAC prefixes for quick vendor identification
        self._mac_prefixes = {
            'A4:5E:60': 'Apple',
            'B8:27:EB': 'Raspberry Pi',
            'DC:A6:32': 'Raspberry Pi',
            'E4:5F:01': 'Raspberry Pi',
            '00:1A:2B': 'Ayecom',
            '00:04:4B': 'Nvidia',
            '3C:5A:B4': 'Google',
            'F4:F5:D8': 'Google',
            '94:EB:2C': 'TP-Link',
            '50:C7:BF': 'TP-Link',
            'AC:84:C6': 'TP-Link',
            '00:27:0E': 'Cisco',
            '00:1B:2B': 'Cisco',
            '00:23:69': 'Cisco',
            'D8:BB:2C': 'Apple',
            'F0:18:98': 'Apple',
            '3C:06:30': 'Apple',
            'A0:D8:15': 'Microsoft',
            '7C:1E:52': 'Microsoft',
            '94:10:3E': 'Microsoft',
        }
    
    def _load_history(self):
        """Load scan history from file."""
        try:
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.history = []
    
    def _save_history(self):
        """Save scan history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception:
            pass
    
    def _load_known_devices(self):
        """Load known devices from file."""
        try:
            with open('known_devices.json', 'r') as f:
                self.known_devices = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.known_devices = {}
    
    def _save_known_devices(self):
        """Save known devices to file."""
        try:
            with open('known_devices.json', 'w') as f:
                json.dump(self.known_devices, f, indent=2)
        except Exception:
            pass
    
    def add_known_device(self, mac, name):
        """Add a device to known devices list."""
        mac_normalized = mac.upper().replace(':', '').replace('-', '')
        self.known_devices[mac_normalized] = {'name': name, 'mac': mac}
        self._save_known_devices()
    
    def set_pihole(self, url):
        """Set Pi-hole URL for DHCP data."""
        self.pihole_url = url.rstrip('/')
    
    def get_hostname(self, ip):
        """Get hostname for IP via reverse DNS."""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except (socket.herror, socket.gaierror, socket.timeout):
            return None
    
    def get_vendor_from_mac(self, mac):
        """Get vendor from MAC address using known prefixes."""
        mac_clean = mac.upper().replace(':', '')
        prefix = mac_clean[:8]
        
        if prefix in self._mac_prefixes:
            return self._mac_prefixes[prefix]
        
        return "Unknown"
    
    def _parse_arp_table(self):
        """Parse ARP table using system command."""
        devices = []
        
        try:
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=10)
            
            for line in result.stdout.split('\n'):
                ip_match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)', line)
                mac_match = re.search(r'([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})', line)
                
                if ip_match and mac_match:
                    ip = ip_match.group(1)
                    mac = mac_match.group(1)
                    
                    if ip and mac and '(incomplete)' not in line.lower():
                        device = {
                            'ip': ip,
                            'mac': mac,
                            'hostname': self.get_hostname(ip),
                            'vendor': self.get_vendor_from_mac(mac),
                            'last_seen': 'now'
                        }
                        devices.append(device)
        
        except Exception as e:
            print(f"Error parsing ARP: {e}")
        
        return devices
    
    def _ping_sweep(self):
        """Ping sweep to populate ARP table."""
        parts = self.network.split('/')[0].split('.')
        network_prefix = '.'.join(parts[:3])
        
        for i in range(1, 255):
            ip = f"{network_prefix}.{i}"
            subprocess.Popen(['ping', '-c', '1', '-W', '1', ip], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    def scan(self):
        """Scan network and return device list."""
        self._ping_sweep()
        devices = self._parse_arp_table()
        
        # Remove duplicates based on IP
        seen_ips = set()
        unique_devices = []
        for d in devices:
            if d['ip'] not in seen_ips:
                seen_ips.add(d['ip'])
                unique_devices.append(d)
        
        if self.pihole_url:
            dhcp_devices = self.get_pihole_dhcp()
            self.merge_pihole_data(unique_devices, dhcp_devices)
        
        self._check_for_new_devices(unique_devices)
        self._save_scan_to_history(unique_devices)
        
        return unique_devices
    
    def _check_for_new_devices(self, devices):
        """Check for unknown devices and print alerts."""
        for device in devices:
            mac_normalized = device['mac'].upper().replace(':', '').replace('-', '')
            if mac_normalized not in self.known_devices:
                print(f"\n⚠️  ALERT: New device detected!")
                print(f"   IP: {device['ip']}")
                print(f"   MAC: {device['mac']}")
                print(f"   Vendor: {device.get('vendor', 'Unknown')}")
                print(f"   Hostname: {device.get('hostname', 'Unknown')}")
    
    def _save_scan_to_history(self, devices):
        """Save scan results with timestamp to history."""
        scan_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'device_count': len(devices),
            'devices': devices
        }
        self.history.append(scan_entry)
        if len(self.history) > 100:
            self.history = self.history[-100:]
        self._save_history()
    
    def get_pihole_dhcp(self):
        """Get DHCP leases from Pi-hole."""
        try:
            url = f"{self.pihole_url}/api/dhcp/leases"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []
    
    def merge_pihole_data(self, devices, dhcp_data):
        """Merge Pi-hole DHCP data with scanned devices."""
        for device in devices:
            for dhcp in dhcp_data:
                dhcp_mac = dhcp.get('mac', '').upper().replace(':', '').replace('-', '')
                device_mac = device['mac'].upper().replace(':', '').replace('-', '')
                if dhcp_mac == device_mac:
                    device['hostname'] = dhcp.get('hostname', device['hostname'])
                    break
    
    def export(self, devices, format='json'):
        """Export devices to file."""
        if not devices:
            return
        
        if format == 'json':
            with open('devices.json', 'w') as f:
                json.dump(devices, f, indent=2)
        elif format == 'csv':
            df = pd.DataFrame(devices)
            df.to_csv('devices.csv', index=False)
    
    def identify_device(self, device):
        """Identify device type based on vendor/hostname."""
        vendor = (device.get('vendor') or '').lower()
        hostname = (device.get('hostname') or '').lower()
        
        if 'apple' in vendor or 'iphone' in hostname or 'ipad' in hostname:
            return '🍎 Apple Device'
        elif 'samsung' in vendor:
            return '📱 Samsung Device'
        elif 'raspberry' in vendor or 'raspi' in hostname:
            return '🫐 Raspberry Pi'
        elif 'cisco' in vendor or 'tp-link' in vendor or 'netgear' in vendor:
            return '🌐 Network Device'
        elif 'intel' in vendor or 'realtek' in vendor:
            return '💻 Computer'
        elif 'xiaomi' in vendor or 'huawei' in vendor:
            return '📶 Router/Modem'
        else:
            return '❓ Unknown'
    
    def print_report(self, devices):
        """Print formatted device report."""
        print(f"\n🔍 Found {len(devices)} devices:\n")
        print(f"{'IP':<16} {'MAC':<18} {'HOSTNAME':<25} {'VENDOR':<20} {'TYPE'}")
        print("-" * 100)
        
        for d in devices:
            hostname = d.get('hostname') or '-'
            vendor = d.get('vendor') or '-'
            device_type = self.identify_device(d)
            
            hostname = hostname[:24] if hostname else '-'
            vendor = vendor[:19] if vendor else '-'
            
            print(f"{d['ip']:<16} {d['mac']:<18} {hostname:<25} {vendor:<20} {device_type}")
    
    def wake_on_lan(self, mac_address):
        """Send Wake-on-LAN packet to specified MAC address."""
        mac_normalized = mac_address.replace(':', '').replace('-', '').upper()
        if len(mac_normalized) != 12:
            print("Invalid MAC address format")
            return False
        
        magic_packet = bytes.fromhex('FF' * 6 + mac_normalized * 16)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, ('<broadcast>', 9))
            sock.close()
            print(f"WoL packet sent to {mac_address}")
            return True
        except Exception as e:
            print(f"Failed to send WoL packet: {e}")
            return False
    
    def export_to_dashboard(self, devices):
        """Export devices to dashboard-compatible format."""
        dashboard_data = {
            'last_scan': datetime.datetime.now().isoformat(),
            'device_count': len(devices),
            'devices': []
        }
        
        for d in devices:
            mac_normalized = d['mac'].upper().replace(':', '').replace('-', '')
            known_info = self.known_devices.get(mac_normalized, {})
            
            dashboard_device = {
                'ip': d['ip'],
                'mac': d['mac'],
                'hostname': d.get('hostname'),
                'vendor': d.get('vendor'),
                'device_type': self.identify_device(d),
                'known_name': known_info.get('name'),
                'is_known': mac_normalized in self.known_devices
            }
            dashboard_data['devices'].append(dashboard_device)
        
        try:
            with open('dashboard.json', 'w') as f:
                json.dump(dashboard_data, f, indent=2)
            print("Dashboard data exported to dashboard.json")
        except Exception as e:
            print(f"Failed to export dashboard: {e}")
