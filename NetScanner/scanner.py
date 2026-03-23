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
    

    def export_to_pdf(self, devices, filename='network_report.pdf'):
        """Export devices to PDF report."""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.units import inch
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        elements.append(Paragraph("📡 Network Scan Report", styles['Title']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        import datetime
        elements.append(Paragraph(f"<b>Fecha:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Total dispositivos:</b> {len(devices)}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Known vs Unknown
        known = [d for d in devices if d.get('is_known')]
        unknown = [d for d in devices if not d.get('is_known')]
        elements.append(Paragraph(f"<b>Dispositivos conocidos:</b> {len(known)}", styles['Normal']))
        elements.append(Paragraph(f"<b>Dispositivos nuevos:</b> {len(unknown)}", styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Table header
        data = [['IP', 'Nombre', 'MAC', 'Vendor', 'Tipo']]
        for d in devices:
            name = d.get('known_name') or d.get('hostname') or '-'
            ip = d.get('ip', '-')
            mac = d.get('mac', '-')
            vendor = d.get('vendor', '-') or '-'
            dtype = d.get('device_type', '-').replace('🍎 ', '').replace('📱 ', '').replace('🫐 ', '').replace('🌐 ', '').replace('💻 ', '').replace('📶 ', '').replace('❓ ', '')
            data.append([ip, name[:20], mac, vendor[:15], dtype[:15]])
        
        table = Table(data, colWidths=[1.1*inch, 1.5*inch, 1.4*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#334155')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#1e293b'), colors.HexColor('#0f172a')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        doc.build(elements)
        print(f"PDF exported to {filename}")
        return filename

    def export_full_report(self, devices):
        """Export complete report: JSON + PDF + Dashboard."""
        import os
        
        # 1. Export to JSON
        self.export_to_dashboard(devices)
        
        # 2. Export to PDF
        pdf_file = 'network_report.pdf'
        self.export_to_pdf(devices, pdf_file)
        
        # 3. Copy PDF to shared location
        import shutil
        dest = '/tmp/network_report.pdf'
        shutil.copy(pdf_file, dest)
        print(f"Report available at {dest}")
        
        return pdf_file


    # ============== NMAP Integration ==============
    
    def scan_ports(self, ip, ports=None):
        """Scan specific ports on an IP using nmap."""
        if ports is None:
            ports = [22, 80, 443, 8080, 5000, 139, 445, 3389, 5900]
        
        try:
            ports_str = ','.join(map(str, ports))
            result = subprocess.run(
                ['/opt/homebrew/bin/nmap', '-Pn', '-p', ports_str, '-oX', '-', ip],
                capture_output=True, text=True, timeout=30
            )
            
            open_ports = []
            for line in result.stdout.split('\n'):
                if 'state="open"' in line:
                    try:
                        port_match = line.split('portid="')[1].split('"')[0]
                        service = line.split('name="')[1].split('"')[0] if 'name="' in line else 'unknown'
                        open_ports.append({'port': port_match, 'service': service})
                    except:
                        pass
            
            return {'ip': ip, 'open_ports': open_ports, 'scanned': True}
        except Exception as e:
            return {'ip': ip, 'open_ports': [], 'error': str(e), 'scanned': False}
    
    def deep_scan(self, ip):
        """Deep scan with OS detection and service version."""
        try:
            result = subprocess.run(
                ['/opt/homebrew/bin/nmap', '-Pn', '-sV', '-O', '-oX', '-', ip],
                capture_output=True, text=True, timeout=60
            )
            
            info = {'ip': ip, 'os': None, 'services': [], 'scanned': True}
            
            for line in result.stdout.split('\n'):
                if 'osclass' in line:
                    try:
                        os_match = line.split('name="')[1].split('"')[0] if 'name="' in line else None
                        if os_match:
                            info['os'] = os_match
                    except:
                        pass
                if 'service name="' in line:
                    try:
                        svc = line.split('service name="')[1].split('"')[0]
                        version = ''
                        if 'version="' in line:
                            version = line.split('version="')[1].split('"')[0]
                        info['services'].append({'service': svc, 'version': version})
                    except:
                        pass
            
            return info
        except Exception as e:
            return {'ip': ip, 'error': str(e), 'scanned': False}
    
    def get_device_info(self, ip):
        """Get complete device info: ARP + NMAP ports."""
        device = {
            'ip': ip,
            'hostname': self.get_hostname(ip),
            'open_ports': self.scan_ports(ip).get('open_ports', [])
        }
        return device
    
    # ============== Analisis / History ==============
    
    def _load_events(self):
        """Load device events from file."""
        try:
            with open('device_events.json', 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_events(self, events):
        """Save device events to file."""
        with open('device_events.json', 'w') as f:
            json.dump(events, f, indent=2)
    
    def _save_device_event(self, event_type, device):
        """Save a device event (online/offline/new)."""
        import datetime
        events = self._load_events()
        
        mac = device.get('mac', '').upper().replace(':', '').replace('-', '')
        
        event = {
            'timestamp': datetime.datetime.now().isoformat(),
            'type': event_type,
            'ip': device.get('ip'),
            'mac': mac,
            'hostname': device.get('hostname'),
            'vendor': device.get('vendor')
        }
        
        events.append(event)
        
        if len(events) > 1000:
            events = events[-1000:]
        
        self._save_events(events)
    
    def get_device_history(self, mac):
        """Get history for a specific device MAC."""
        events = self._load_events()
        mac_normalized = mac.upper().replace(':', '').replace('-', '')
        return [e for e in events if e.get('mac', '').replace(':', '').replace('-', '').upper() == mac_normalized]
    
    def get_online_trend(self):
        """Get online/offline trends for all devices."""
        events = self._load_events()
        trends = {}
        
        for event in events:
            mac = event.get('mac', '').replace(':', '').replace('-', '').upper()
            if mac not in trends:
                trends[mac] = {
                    'mac': mac,
                    'first_seen': event['timestamp'],
                    'last_seen': event['timestamp'],
                    'events': [],
                    'online_count': 0,
                    'offline_count': 0
                }
            
            trends[mac]['events'].append({'type': event['type'], 'time': event['timestamp']})
            
            if event['type'] in ['online', 'new']:
                trends[mac]['online_count'] += 1
            elif event['type'] in ['offline', 'gone']:
                trends[mac]['offline_count'] += 1
            
            if event['timestamp'] > trends[mac]['last_seen']:
                trends[mac]['last_seen'] = event['timestamp']
        
        return list(trends.values())
    
    def _detect_anomaly(self, devices):
        """Detect anomalies: new devices or missing known devices."""
        anomalies = {'new': [], 'missing': []}
        
        current_macs = set()
        for d in devices:
            mac = d.get('mac', '').upper().replace(':', '').replace('-', '')
            if mac:
                current_macs.add(mac)
        
        for d in devices:
            mac = d.get('mac', '').upper().replace(':', '').replace('-', '')
            if mac and mac not in self.known_devices and mac not in ['', 'FFFFFFFFFFFF']:
                anomalies['new'].append(d)
                self._save_device_event('new', d)
        
        known_macs = set(self.known_devices.keys())
        missing = known_macs - current_macs
        for mac in missing:
            device = {'mac': mac, 'ip': None, 'hostname': None, 'vendor': None}
            anomalies['missing'].append(device)
            self._save_device_event('gone', device)
            print("ALERT: Known device " + str(self.known_devices[mac].get('name', mac)) + " is missing!")
        
        if anomalies['new']:
            print("ALERT: " + str(len(anomalies['new'])) + " new device(s) detected!")
            for d in anomalies['new']:
                print("   New: " + str(d.get('ip')) + " - " + str(d.get('mac')) + " - " + str(d.get('vendor')))
        
        return anomalies
    
    def export_trend_report(self):
        """Export trend report to JSON."""
        import datetime
        trends = self.get_online_trend()
        
        report = {
            'generated': datetime.datetime.now().isoformat(),
            'total_devices_tracked': len(trends),
            'trends': []
        }
        
        for mac, data in [(t['mac'], t) for t in trends]:
            known_name = self.known_devices.get(mac, {}).get('name', 'Unknown')
            report['trends'].append({
                'mac': mac,
                'name': known_name,
                'first_seen': data['first_seen'],
                'last_seen': data['last_seen'],
                'appearances': data['online_count'],
                'disappearances': data['offline_count'],
                'stability': 'high' if data['offline_count'] == 0 else 'medium' if data['offline_count'] < 3 else 'low'
            })
        
        with open('trend_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("Trend report exported: " + str(len(trends)) + " devices tracked")
        return report
    
    def full_analysis(self, devices=None):
        """Run complete analysis: scan + anomaly detection + trend report."""
        if devices is None:
            print("Running full network analysis...")
            devices = self.scan()
        
        print("\nAnalysis Results:")
        print("   Total devices: " + str(len(devices)))
        
        for d in devices:
            self._save_device_event('online', d)
        
        anomalies = self._detect_anomaly(devices)
        report = self.export_trend_report()
        
        print("\nTrend Summary:")
        for t in report['trends'][:5]:
            print("   " + str(t['name']) + ": " + str(t['appearances']) + "x online, " + str(t['disappearances']) + "x offline (" + str(t['stability']) + ")")
        
        if anomalies['new']:
            print("\n" + str(len(anomalies['new'])) + " NEW devices detected!")
        if anomalies['missing']:
            print("\n" + str(len(anomalies['missing'])) + " devices missing!")
        
        return {
            'devices': devices,
            'anomalies': anomalies,
            'report': report
        }

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
        """Export devices to dashboard-compatible format and send to web dashboard."""
        import subprocess
        
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
            print(f"Dashboard data exported ({len(devices)} devices)")
        except Exception as e:
            print(f"Failed to export: {e}")
        
        # Send to web dashboard via curl
        try:
            device_list = ', '.join([d.get('hostname') or d['ip'] for d in devices[:10]])
            if len(devices) > 10:
                device_list += f'... y {len(devices) - 10} mas'
            
            msg = {
                'title': f'NetScan - {len(devices)} devices',
                'category': 'ai',
                'content': f'Scan completo: {len(devices)} dispositivos. Principales: {device_list}'
            }
            
            curl_cmd = ['curl', '-s', '-X', 'POST', 'http://192.168.1.172:5000/api/messages',
                       '-H', 'Content-Type: application/json', '-d', json.dumps(msg)]
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("Summary sent to web dashboard!")
        except Exception as e:
            print(f"Failed to send to dashboard: {e}")
