#!/usr/bin/env python3
"""
NetScanner - Network scanner with Pi-hole integration
"""
import click
from scanner import NetworkScanner

@click.command()
@click.option('--network', '-n', default='192.168.1.0/24', help='Network to scan (CIDR notation)')
@click.option('--export', '-e', type=click.Choice(['json', 'csv']), default=None, help='Export results')
@click.option('--pihole', '-p', default=None, help='Pi-hole URL (e.g., http://192.168.1.100)')
def main(network, export, pihole):
    """🔍 Scan network and list connected devices."""
    click.echo(f"🔍 Scanning {network}...")
    
    scanner = NetworkScanner(network)
    
    if pihole:
        scanner.set_pihole(pihole)
        click.echo(f"📡 Using Pi-hole at {pihole}")
    
    devices = scanner.scan()
    
    if not devices:
        click.echo("❌ No devices found")
        return
    
    scanner.print_report(devices)
    
    if export:
        scanner.export(devices, export)
        click.echo(f"\n💾 Exported to devices.{export}")

if __name__ == '__main__':
    main()
