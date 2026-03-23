#!/usr/bin/env python3
import re, subprocess, json
from datetime import datetime

VENDORS = {
    'B4:14:E6': 'Router/Gateway', 'D4:90:9C': 'TP-Link', '6C:56:97': 'Amazon',
    '34:3E:A4': 'Ring', 'A6:3A:5C': 'Apple', 'F0:2F:9E': 'Amazon',
    'DE:96:23': 'Unknown', 'E4:23:54': 'Gosund', '8C:85:80': 'Imou',
    'DC:A0:D0': 'Amazon', '68:5E:DD': 'Apple', '72:1B:8E': 'Xiaomi',
    '64:E7:D8': 'Samsung', 'B8:27:EB': 'Raspberry Pi', '8:66:98': 'Unknown',
    '64:64:4A': 'Xiaomi Router', '40:31:3C': 'Unknown', 'A4:EE:57': 'Epson',
    '58:D9:D5': 'TP-Link', '64:64:4A': 'TP-Link', '00:11:32': 'Synology',
    'A4:5E:60': 'Apple', 'B8:27:EB': 'Raspberry Pi', '18:60:24': 'Ubuntu',
    '86:A3:6B': 'Apple', '3C:5A:B4': 'Google', 'DC:A6:32': 'Raspberry Pi',
}

KNOWN = {
    '86A36B17AF8F': 'Mac Remoto (clot)',
    '0AA8A388D3D5': 'Mac Jose',
    'B827EB1BDD2E': 'Pi-hole',
    '186024F1ABF9': 'Ubuntu Server',
    '48E15C770FBD': 'Salon-475',
    'D4909CF2280B': 'Salon-2',
    '58D9D53FCF90': 'meshd',
    '58D9D53FCF60': 'meshs',
    '58D9D53FCFC0': 'mesh1',
    '001132369A7F': 'NAS Synology',
    'D4909CF228B': 'Salon-2',
    '0D4909CF228B': 'Salon-2',
    '48E15C770FBD': 'Salon-475',
    '866898975C9A': 'Dispositivo Desván',
    '4ECE5DBCE5C2': 'IoT Device',
    '8C8580C92': 'Imou Camera',
    'DC68EBB154E': 'IoT Device',
    '0DC5D5DD96': 'IoT Device',
    '30B5C2F8C1A': 'IoT Device',
    'D446497EBF4': 'IoT Device',
    'B414E6B28FA': 'Router/Gateway',
    'D4909CF228B': 'Salon-2 (IP157)',
    '48E15C770FBD': 'Salon-475 (IP239)',
    '866898975C9A': 'Dispositivo Desván',
    '866898975C9A': 'Desván IP203',
    '98E25573A27C': 'Unknown Device',
    '42EDCF8FBD33': 'IoT Device',
    'DE9623B8227F': 'IoT Device',
    '40313CA9E4CF': 'IoT Device',
    '8C8580C92': 'Imou Camera 2',
    'DC68EBB154E': 'IoT Device',
    '0DC5D5DD96': 'IoT Device',
    '30B5C2F8C1A': 'IoT Device',
    '8416F976F341': 'IoT Device',
    'D446497EBF4': 'IoT Device',
    'D0D2B093D8AC': 'IoT Device',
    'B414E6B28FA': 'Router Gateway',
    'A0C9A0D96A4D': 'Router Gateway',
    'D4909CF228B': 'Salon-2',
    '0D4909CF228B': 'Salon-2',
    '48E15C770FBD': 'Salon-475',
    '866898975C9A': 'Dispositivo Desván',
    '721B8EEF4F16': 'POCO X6 Pro',
    '64E7D84FC858': 'Samsung TV',
    '2AD7114CFD18': 'iPhone Jose',
    '48E15C770FBD': 'Salon-475',
    '645D84F228B': 'Salon-2',
    '4264E7D84FC8': 'IoT Device',
    '426EDCF8FBD': 'IoT Device',
    '429E966B822': 'IoT Device',
    '8C8580C92': 'Imou Camera',
    'DC68EBB154E': 'IoT Device',
    '7AEDBFDD4C66': 'Apple Device',
    '64644ABD9F33': 'Xiaomi Router',
    'D46E497EBF': 'IoT Device',
    'D4D2B093D8AC': 'IoT Device',

    # From hostnames
    'A63A5C6C8032': 'iPad de Jose',
    '685EDD64282F': 'MacBook Air Jose',
    '6427D84FC858': 'Samsung TV',
    '721B8EEF4F16': 'POCO X6 Pro',
    'B827EBE64F57': 'Raspberry Pi',
    'E42354118A52': 'Gosund Plug',
    '8C8580DA43DD': 'Indoor Cam',
    '343EA4B0B378': 'Ring Doorbell',
    '645D84F228B': 'Salon-2',
    '6C569794353F': 'Amazon Echo',
    'F02F9EB1A68B': 'Amazon Device',
    'DCA0D0C06A83': 'Amazon Device',
    'A4EE571829DB': 'Epson Printer',
    '64644ABD9F30': 'Xiaomi Router',
    'B414E6B28FA': 'Router Gateway',
}

def norm_mac(mac):
    # Remove all separators and pad to 12 chars
    clean = mac.replace(':', '').replace('-', '').upper()
    # Pad with leading zeros to 12 chars
    return clean.zfill(12)

def get_vendor(mac):
    mc = norm_mac(mac)
    for p, v in VENDORS.items():
        np = p.replace(':', '')
        if mc.startswith(np): return v
    return 'Unknown'

def get_type(v, h):
    hl = h.lower()
    vl = v.lower()
    if any(x in hl for x in ['iphone', 'ipad', 'macbook', 'mac-mini']): return '🍎 Apple'
    if any(x in hl for x in ['raspberry', '-pi', 'rpi']): return '🫐 Raspberry Pi'
    if any(x in hl for x in ['pihole', 'pi.hole']): return '🛡️ Pi-hole'
    if any(x in hl for x in ['ubuntu', 'server', 'linux']): return '🖥️ Server'
    if any(x in vl for x in ['tp-link', 'mesh']): return '📶 Router/Mesh'
    if any(x in hl for x in ['ring', 'doorbell']): return '📹 Ring'
    if any(x in hl for x in ['cam', 'camera', 'indoorcam']): return '📹 Camera'
    if any(x in hl for x in ['plug', 'gosund', 'smartplug']): return '🔌 Smart Plug'
    if any(x in hl for x in ['epson', 'printer']): return '🖨️ Printer'
    if any(x in vl for x in ['apple']): return '🍎 Apple'
    if any(x in hl for x in ['watch', 'apple-watch']): return '⌚ Watch'
    if any(x in vl for x in ['synology', 'nas']): return '💾 NAS'
    if any(x in hl for x in ['salon', 'desvan']): return '🏠 IoT'
    if any(x in vl for x in ['google', 'nest', 'amazon', 'echo']): return '📱 Smart Speaker'
    if any(x in vl for x in ['xiaomi', 'mi', 'poco']): return '📱 Xiaomi'
    if any(x in vl for x in ['shelly']): return '⚡ Shelly'
    if any(x in vl for x in ['tuya', 'smartlife']): return '📱 Tuya'
    if any(x in vl for x in ['samsung']): return '📺 Samsung'
    if any(x in vl for x in ['router', 'gateway']): return '📶 Router'
    if any(x in vl for x in ['esp']): return '🔧 ESP'
    return '❓ Unknown'
    
    # Extra hostname detection
    if 'poco' in hl: return '📱 Xiaomi'
    if 'samsung' in hl: return '📺 Samsung'
    if 'iphone' in hl: return '🍎 Apple'
    if 'iot' in hl or 'device' in hl: return '🏠 IoT'
    if 'gw-' in hl: return '📶 Gateway'
    if 'desvan' in hl: return '🏠 Dispositivo'
    if 'salon-2' in hl: return '🏠 Dispositivo'



for i in range(2, 255):
    subprocess.Popen(['ping', '-c', '1', '-W', '1', f'192.168.1.{i}'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(['sleep', '5'])

result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
devices = []
for line in result.stdout.split('\n'):
    if not line.strip() or 'incomplete' in line.lower(): continue
    m = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]+)', line)
    if not m: continue
    ip, mac = m.group(1), m.group(2).upper()
    if mac == 'FF:FF:FF:FF:FF:FF': continue
    hm = re.match(r'([^\s]+)\s+\(', line)
    hostname = hm.group(1) if hm and hm.group(1) != '?' else None
    mc = norm_mac(mac)
    vendor = get_vendor(mac)
    dtype = get_type(vendor, (hostname or '').lower())
    known_name = KNOWN.get(mc)
    devices.append({'ip': ip, 'mac': mac, 'hostname': hostname,
        'vendor': vendor, 'device_type': dtype,
        'known_name': known_name, 'is_known': mc in KNOWN})

devices.sort(key=lambda x: (not x['is_known'], x['ip']))
print(json.dumps({'last_scan': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    'device_count': len(devices), 'devices': devices}))
