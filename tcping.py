import argparse
import socket
import time
import sys
import os

if sys.platform == "linux":
    os.system("clear")
elif sys.platform == "win32":
    os.system("cls")

parser = argparse.ArgumentParser()
parser.add_argument("host", nargs="?", help="Host to perform TCP ping on")
parser.add_argument("-p", "--port", default=80, type=int, help="Port of host to perforn TCP ping on")
parser.add_argument("-t", "--timeout", default=5, type=int, help="TCP connection timeout value")

args = parser.parse_args()

if not args.host:
    parser.print_help()
    print("Host is required!")
    sys.exit()

host = args.host
port = args.port
timeout = args.timeout
socket.setdefaulttimeout(1)
sequence = 1

ip = socket.gethostbyname(host)

if host != ip:
    domain_ip_string = f"(\u001b[32;1m{ip}\u001b[0;0m)"
    host = ip
else:
    domain_ip_string = ""


print(f"Initializing TCP ping to \u001b[32;1m{host}\u001b[0;0m{domain_ip_string}:\u001b[32;1m{port}\u001b[0;0m...\r\n")
try:
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        time1 = time.time()
        sock.connect((host, port))
        print(f"Host=\u001b[32;1m{host}\u001b[0;0m Port=\u001b[32;1m{port}\u001b[0;0m Time=\u001b[32;1m{1000 * (time.time() - time1):.2f}ms\u001b[0;0m Sequence=\u001b[32;1m{sequence}\u001b[0;0m")
        sock.close()
        sequence += 1
        time.sleep(1)
except KeyboardInterrupt:
    sys.exit()
except Exception as e:
    print(f"Error: {e}")
    pass
