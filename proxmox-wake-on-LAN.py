import socket
import time
from pythonping import ping
from rich.console import Console
from wakeonlan import send_magic_packet

console = Console()

ip_address = '192.175.1.1'
service_port = 8006 #example proxmox
mac_address = 'AA:AA:AA:AA:AA:AA'

TIMEOUT = 60
SEND_MAGIC_PACKET_INTERVAL = 2  # Interval in seconds

def check_host(ip_address, mac_address):
    start_time = time.time()
    magic_packet_sent = False
    last_magic_packet_time = 0
    with console.status("[bold cyan]Waiting for host...", spinner="dots"):
        while True:
            response = ping(ip_address, count=1, timeout=1)
            if response.success():
                console.print(f"Erfolgreich: Host mit der IP {ip_address} ist online!", style="green")
                return True
            elif time.time() - start_time > TIMEOUT:
                console.print("Fehler: Der Host ist nicht verfügbar.", style="red")
                return False
            elif not magic_packet_sent and time.time() - last_magic_packet_time >= SEND_MAGIC_PACKET_INTERVAL:
                send_magic_packet(mac_address)
                console.print(f"Magic Packet gesendet an {mac_address}", style="yellow")
                magic_packet_sent = True  # Markiert, dass das Magic Packet gesendet wurde
                last_magic_packet_time = time.time()

def check_service(ip_address, service_port):
    start_time = time.time()
    with console.status("[bold cyan]Warte auf Service...", spinner="dots"):
        while True:
            if is_port_open(ip_address, service_port):
                console.print(f"Erfolgreich: Service mit dem Port {service_port} ist online!", style="green")
                return
            elif time.time() - start_time > TIMEOUT:
                console.print("Fehler: Der Service ist nicht verfügbar.", style="red")
                return

def is_port_open(ip_address, service_port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((ip_address, service_port))
        return True
    except (socket.timeout, socket.error):
        return False

if __name__ == "__main__":


    if check_host(ip_address, mac_address):
        check_service(ip_address, service_port)
