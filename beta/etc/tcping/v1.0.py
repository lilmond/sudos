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
parser.add_argument("-t", "--timeout", default=3, type=int, help="TCP connection timeout value")

args = parser.parse_args()

if not args.host:
    parser.print_help()
    print("Host is required!")
    sys.exit()

host = args.host
port = args.port
timeout = args.timeout
socket.setdefaulttimeout(timeout)
sequence = 1

try:
    ip = socket.gethostbyname(host)
except Exception as e:
    print(f"Unable to resolve domain name: {e}")
    sys.exit()

print(f"Initializing TCP ping to \u001b[32;1m{host}\u001b[0;0m:\u001b[32;1m{port}\u001b[0;0m...")
print(f"")
while True:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        time1 = time.time()
        sock.connect((ip, port))
        time2 = time.time()
        ping = (time2 - time1) * 1000
        print(f"Host=\u001b[32;1m{ip}\u001b[0;0m Port=\u001b[32;1m{port}\u001b[0;0m Time=\u001b[32;1m{ping:.2f}ms\u001b[0;0m Sequence=\u001b[32;1m{sequence}\u001b[0;0m")
        sock.close()
        time.sleep(1)
    except Exception as e:
        print(f"\u001b[31;1mError\u001b[0;0m: message=\u001b[32;1m{e}\u001b[0;0m Sequence=\u001b[32;1m{sequence}\u001b[0;0m")
        pass
    except KeyboardInterrupt:
        sys.exit()
    finally:
        sequence += 1
