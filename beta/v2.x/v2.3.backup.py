#!/usr/bin/env python
#version: beta-2.3

# *** Modules *** #
import argparse
import logging
import sys
import os
# *** Modules End *** #

# *** Arguments *** #
parser = argparse.ArgumentParser()
parser.add_argument("url", nargs="?", type=str, help="Target url to perform the attack on")
parser.add_argument("-pl", "--proxy-list", type=str, help="Text file that contains proxy list. Format must be like: socks5://127.0.0.1:9050 or else it will try every protocol or you can use -pt or --proxy-type to use specified protocol")
parser.add_argument("-pt", "--proxy-type", type=str, help="Proxy type/protocol that will be used to flood a host. Types: HTTP, SOCKS4, SOCKS5")
parser.add_argument("-rt", "--requests-per-threads", type=int, default=777, help="HTTP requests that will be sent per threads")
parser.add_argument("-l", "--socket-limit", type=int, default=1, help="Waits until reaching the connected sockets limit before sending HTTP floods")
parser.add_argument("-t", "--threads", type=int, default=100, help="Max threads to use during the attack. Default is 100")
parser.add_argument("--timeout", type=int, default=15, help="Proxy and socket connection timeout. Default is 15")
parser.add_argument("--delay", type=int, default=1, help="Delay time to send HTTP requests per threads")
parser.add_argument("--no-color", action="store_true", help="Disables text colors also prevents from clearing the console logs")
parser.add_argument("--debug", action="store_true", help="Enables debug mode. Increases verbose log")
# *** Arguments End *** #

# ** Initial Variables ** #
use_proxy = False
# ** Initial Variables End ** #

# ** Argument Parser ** #
args = parser.parse_args()
url = args.url
proxy_list = args.proxy_list
proxy_type = args.proxy_type
requests_per_threads = args.requests_per_threads
socket_limit = args.socket_limit
max_threads = args.threads
timeout = args.timeout
delay = args.delay
no_color = args.no_color
debug = args.debug
# ** Argument Parser End ** #

# *** Logger Format And Filters *** #
logging.basicConfig(
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)
if debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
# *** Logger Format And Filters End *** #

# ** Valid Variables ** #
# - used to validate your inputs such as proxy protocol
proxy_protocols = ["http", "socks4", "socks5"]
url_protocols = ["http", "https"]
# ** Valid Variables End ** #

# *** Variable Colors *** #
# - clears screen
if not no_color:
    if sys.platform == "linux":
        os.system("clear")
    elif sys.platform == "win32":
        os.system("cls")
# - sets color variables
if not no_color:
    RED = "\u001b[31;1m"
    GREEN = "\u001b[32;1m"
    YELLOW = "\u001b[33;1m"
    BLUE = "\u001b[34;1m"
    MAGENTA = "\u001b[35;1m"
    CYAN = "\u001b[36;1m"
    WHITE = "\u001b[37;0m"
    RESET = "\u001b[0;0m"
else:
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    MAGENTA = ""
    CYAN = ""
    WHITE = ""
    RESET = ""
# *** Variable Colors End *** #

logger.debug("Setting initial configurations and filters")

# ** Argument Filters ** #
# * Argument Host Filter * #
# - exits when host is unspecified
if not url:
    parser.print_help()
    print("\r\nurl is required\r\n")
    sys.exit()
# * Argument Host Filter End ** #
# * Proxy Filter * #
# - sets use_proxy variable if proxy_list is specified
if proxy_list:
    use_proxy = True
# - validates if proxy list file exists or available
if use_proxy:
    try:
        proxy_list = open(proxy_list, "r")
        proxies = proxy_list.readlines()
        proxy_list.close()
    except FileNotFoundError:
        print(f"{RED}Initial Error{RESET} => {WHITE}Proxy list file not found.{RESET}")
        sys.exit()
    except Exception as e:
        print(f"{RED}Initial Error{RESET} => {WHITE}{e}{RESET}")
        sys.exit()
# * Proxy Filter End * #

logger.debug("Initial configurations successfully set")
