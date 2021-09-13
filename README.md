# SuDOS

SuDOS is a proxy-based DDOS tool (pseudo-botnet) written in Python with live console status display program.

Discord: https://discord.com/invite/dZSDbjJPHx

# Updates
2.5.4.1
- Fixed initialization bug

2.5.4.2
- Fixed useragent loading bug

# Disclaimer
- I will not be responsible for any misuses nor damages causes by this tool. Use it at your own risk!

# Usages
- Basic usage
```
python sudos.py http://example.com/
```
- Basic usage (proxies)
```
python sudos.py -z socks5 -x socks5_list.txt https://target.com/
```
- Harder testing usage
```
python sudos.py -z socks5 -x socks5_list.txt -t 500 -v 0 https://target.com/
```
- Server bandwidth consuming test
```
python sudos.py -z socks5 -x socks5_list.txt -v 0 -n https://target.com/
```

# Attack Modes
You can set the attack mode using the `-m <MODE>` parameter.

## Attack Mode 1
Attack mode 1 (Default) aka Slowloris sends numerous amount of HTTP GET requests. You can set the HTTP request sending speed using the `-v <INT>` parameter.

## Attack Mode 2
Attack mode 2 aka R-U-Dead-Yet sends a POST request and slowly send data content to the server repeatedly overwhelming the server with tons of open TCP connections. You can also set the content sending speed using the `-v <INT>` parameter.

# Where do I get proxy lists?
Just visit the websites listed below and find a best proxy list for yourself.
- https://openproxy.space/list
- https://www.proxy-list.download/
- https://www.proxyscrape.com/free-proxy-list

# Screenshots
<img src="https://raw.githubusercontent.com/lilmond/sudos/main/screenshots/sudos_6.png" width=300/>
<img src="https://raw.githubusercontent.com/lilmond/sudos/main/screenshots/sudos_1.jpg" width=300/>
<img src="https://raw.githubusercontent.com/lilmond/sudos/main/screenshots/sudos_5.jpg" width=300/>
<img src="https://raw.githubusercontent.com/lilmond/sudos/main/screenshots/sudos_4.png" width=300/>
