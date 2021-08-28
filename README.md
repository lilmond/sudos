# SuDOS

SuDOS is a pseudo-botnet. Sorry for bad code and documentation. I will fix it later!

Discord: https://discord.com/invite/dZSDbjJPHx

# Disclaimer
- I will not be responsible for any misuse of this tool. Do it at your own risk!
- This content is currently on early version and made experimentaly. Many bugs may occur!

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

# Attack Modes
You can set the attack mode with the `-m <MODE>` parameter.

## Attack Mode 1
Attack mode 1 (Default) aka Slowloris sends numerous amount of HTTP GET requests. You can set the HTTP request sending speed with the `-c <INT>` parameter.

## Attack Mode 2
Attack mode 2 aka R-U-Dead-Yet sends a POST request and slowly send the content to the server. You can also set the content sending speed with the `-c <INT>` parameter.

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
