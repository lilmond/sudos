from urllib.parse import urlparse
import threading
import argparse
import requests
import logging
import socket
import socks
import time
import sys
import os

class Config:
    OUTPUT_FILE: argparse.FileType = None
    THREADS = 20
    TRIES = 3
    TIMEOUT = 10
    FETCHED_PROXIES = []
    PROXY_FETCHER_THREADS = 0
    PROXY_CHECKER_THREADS = 0
    CHECKED_PROXIES_COUNT = 0
    GOOD_PROXIES_COUNT = 0
    BAD_PROXIES_COUNT = 0

logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    datefmt="%m-%d-%Y-%H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger(__file__)

class Colors:
    RED = "\u001b[31;1m"
    GREEN = "\u001b[32;1m"
    YELLOW = "\u001b[33;1m"
    BLUE = "\u001b[34;1m"
    PURPLE = "\u001b[35;1m"
    CYAN = "\u001b[36;1m"
    RESET = "\u001b[0;0m"

with open("proxal_banner.txt", "r") as file:
    BANNER = f"{Colors.PURPLE}{file.read()}{Colors.RESET}"
    file.close()

def fetch_proxies():
    logger.info("Fetching public proxies...")

    proxy_types = ["socks5", "socks4", "http"]
    for proxy_type in proxy_types:
        threading.Thread(target=fetch_proxy, args=[proxy_type], daemon=True).start()

    time.sleep(1)

    while True:
        if Config.PROXY_FETCHER_THREADS <= 0: break
    
    logging.info("Public proxies successfully fetched.")

def fetch_proxy(proxy_type):
    Config.PROXY_FETCHER_THREADS += 1

    while True:
        try:
            proxy_list = requests.get(f"https://api.openproxy.space/lists/{proxy_type}").json()

            for proxy in proxy_list["data"]:
                proxy_addresses = proxy["items"]

                for proxy_address in proxy_addresses:
                    proxy_address = f"{proxy_type}://{proxy_address}"
                    Config.FETCHED_PROXIES.append(proxy_address)
            
            Config.PROXY_FETCHER_THREADS -= 1

            return
        except Exception as e:
            time.sleep(1)
            continue

def clear_console():
    if sys.platform == "win32":
        os.system("cls")
    elif sys.platform in ["linux"," linux2"]:
        os.system("clear")

def check_proxy(proxy_address: str):
    Config.PROXY_CHECKER_THREADS += 1

    is_good_proxy = False

    for tries in range(Config.TRIES):
        try:
            # try_number = tries + 1

            proxy_url = urlparse(proxy_address)
            proxy_type = getattr(socks, f"PROXY_TYPE_{proxy_url.scheme.upper()}")
            proxy_host = proxy_url.hostname
            proxy_port = proxy_url.port

            sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            sock.set_proxy(proxy_type=proxy_type, addr=proxy_host, port=proxy_port)
            sock.connect(("www.roblox.com", 80))

            http_data = "GET / HTTP/1.1\r\nHost: www.roblox.com\r\n\r\n"

            sock.send(http_data.encode())

            response_headers = b""

            while True:
                chunk = sock.recv(1)

                if not chunk:
                    break

                response_headers += chunk

                if response_headers.endswith(b"\r\n\r\n"):
                    break

            if len(response_headers) == 0:
                raise Exception
            
            sock.close()

            logger.info(f"Good proxy found: {Colors.BLUE}{proxy_address}{Colors.RESET}")


            with open(Config.OUTPUT_FILE.name, "a") as file:
                file.write(f"{proxy_address}\n")
                file.close()

            is_good_proxy = True

            break
        except Exception:
            time.sleep(1)
            continue
    
    if is_good_proxy:
        Config.GOOD_PROXIES_COUNT += 1
    else:
        Config.BAD_PROXIES_COUNT += 1

    Config.CHECKED_PROXIES_COUNT += 1
    Config.PROXY_CHECKER_THREADS -= 1

def main():
    clear_console()
    print(f"{BANNER}\n")

    parser = argparse.ArgumentParser(description="Proxal, automated working proxy servers finder.")
    parser.add_argument("-o", "--output", type=argparse.FileType("a"), required=True, help="Output file after checking if a proxy is alive.")
    parser.add_argument("-t", "--threads", type=int, default=Config.THREADS, help=f"Max threads for checking proxies. Default: {Config.THREADS}")
    parser.add_argument("--tries", type=int, default=Config.TRIES, help=f"Max tries for connecting to a proxy server. Default: {Config.TRIES}")
    parser.add_argument("--timeout", type=int, default=Config.TIMEOUT, help=f"Socket connection timeout. Default: {Config.TIMEOUT}")

    args = parser.parse_args()

    Config.OUTPUT_FILE = args.output
    Config.THREADS = args.threads
    Config.TRIES = args.tries
    Config.TIMEOUT = args.timeout
    socket.setdefaulttimeout(args.timeout)

    fetch_proxies()

    start_time = time.time()
    last_elapsed = None

    for proxy in Config.FETCHED_PROXIES:
        while True:
            elapsed = int(time.time() - start_time)
    
            if not elapsed == 0:
                if elapsed % 5 == 0:
                    if not elapsed == last_elapsed:
                        logger.info(f"Good: {Colors.GREEN}{Config.GOOD_PROXIES_COUNT}{Colors.RESET} | Bad: {Colors.RED}{Config.BAD_PROXIES_COUNT}{Colors.RESET} | Checked: ({Colors.BLUE}{Config.CHECKED_PROXIES_COUNT}{Colors.RESET}/{Colors.BLUE}{len(Config.FETCHED_PROXIES)}{Colors.RESET}) Threads: ({Colors.BLUE}{Config.PROXY_CHECKER_THREADS}{Colors.RESET}/{Colors.BLUE}{Config.THREADS}{Colors.RESET})")
                        last_elapsed = elapsed

            if Config.PROXY_CHECKER_THREADS >= Config.THREADS:
                time.sleep(0.05)
                continue

            threading.Thread(target=check_proxy, args=[proxy], daemon=True).start()
            time.sleep(0.01)
            break
    
    while True:
        elapsed = int(time.time() - start_time)
    
        if not elapsed == 0:
            if elapsed % 5 == 0:
                if not elapsed == last_elapsed:
                    logger.info(f"Good: {Colors.GREEN}{Config.GOOD_PROXIES_COUNT}{Colors.RESET} | Bad: {Colors.RED}{Config.BAD_PROXIES_COUNT}{Colors.RESET} | Checked: ({Colors.BLUE}{Config.CHECKED_PROXIES_COUNT}{Colors.RESET}/{Colors.BLUE}{len(Config.FETCHED_PROXIES)}{Colors.RESET}) Threads: ({Colors.BLUE}{Config.PROXY_CHECKER_THREADS}{Colors.RESET}/{Colors.BLUE}{Config.THREADS}{Colors.RESET})")
                    last_elapsed = elapsed

        time.sleep(0.05)

        if Config.PROXY_CHECKER_THREADS <= 0:
            break
    
    logger.info(f"Proxy checking finished. Output file: {Config.OUTPUT_FILE.name}")
    logger.info(f"Good: {Colors.GREEN}{Config.GOOD_PROXIES_COUNT}{Colors.RESET} | Bad: {Colors.RED}{Config.BAD_PROXIES_COUNT}{Colors.RESET} | Checked: ({Colors.BLUE}{Config.CHECKED_PROXIES_COUNT}{Colors.RESET}/{Colors.BLUE}{len(Config.FETCHED_PROXIES)}{Colors.RESET}) Threads: ({Colors.BLUE}{Config.PROXY_CHECKER_THREADS}{Colors.RESET}/{Colors.BLUE}{Config.THREADS}{Colors.RESET})")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
