from datetime import datetime
import threading
import requests
import time
import json
import os

dirname = os.path.dirname(__file__)
dir_proxy = f"{dirname}/proxies"
dir_http = f"{dir_proxy}/http"
dir_socks4 = f"{dir_proxy}/socks4"
dir_socks5 = f"{dir_proxy}/socks5"
dir_sequence = f"{dir_proxy}/.data"

active_threads = 0
proseq = []
try:
    with open(dir_sequence) as sfile:
        proseq = sfile.read().strip().splitlines()
        sfile.close()
except FileNotFoundError:
    pass

def get_proxy(code: str) -> list:
    try:
        global active_threads
        active_threads += 1
        if code in proseq:
            print(f"Already downloaded: {code}")
            return
        
        print(f"Downloading: {code}")
        proxies = requests.get(f"https://api.openproxy.space/list/{code}")
        proxies = json.loads(proxies.text)
        protocol = proxies["protocols"][0]
        proxies = proxies["data"][0]["items"]
        
        proxies_str = ""
        for proxy in proxies:
            proxy = proxy.strip()
            proxies_str += f"{proxy}\r\n"
        proxies_str = proxies_str.strip()
        
        if protocol == 1 or protocol == 2:
            path = dir_http
        elif protocol == 3:
            path = dir_socks4
        elif protocol == 4:
            path = dir_socks5
        
        sequence = 0
        while True:
            sequence += 1
            filename = f"{sequence}.txt"
            filepath = f"{path}/{filename}"
            if not os.path.exists(filepath):
                break
        
        with open(filepath, "w") as sfile:
            sfile.write(proxies_str)
            sfile.close()
        
        print(f"Saved: {filepath}")
        proseq.append(code)
    except Exception:
        pass
    finally:
        active_threads -= 1
    

def get_list() -> None:
    date = datetime.now().strftime("%F")
    year, month, day = date.split("-")
    today = datetime(int(year), int(month), int(day)).timestamp()
    today = int(today) * 1000

    proxies = requests.get(f"https://api.openproxy.space/list?skip=0&ts={today}")
    proxies = json.loads(proxies.text)
    
    if not os.path.exists(dir_proxy):
        os.mkdir(dir_proxy)
    if not os.path.exists(dir_http):
        os.mkdir(dir_http)
    if not os.path.exists(dir_socks4):
        os.mkdir(dir_socks4)
    if not os.path.exists(dir_socks5):
        os.mkdir(dir_socks5)

    for proxy in proxies:
        if not type(proxy) == dict:
            continue
        code = proxy["code"]
        threading.Thread(target=get_proxy, args=[code], daemon=True).start()

def main():
    try:
        get_list()
        while True:
            if active_threads == 0:
                break
    except Exception as e:
        print(f"error: {e}")
        pass
    except KeyboardInterrupt:
        exit()
    finally:
        proseq_str = ""
        for code in proseq:
            proseq_str += f"{code}\r\n"
        proseq_str = proseq_str.strip()
        with open(dir_sequence, "w") as sfile:
            sfile.write(proseq_str)
            sfile.close()

if __name__ == "__main__":
    main()
