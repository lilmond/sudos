# Proxies And Tor

Using proxies and Tor with sudos is easy. Just use the `-l/--proxy-list [FILE]` or `--tor` keyword.

# Examples

## `http-get-rapid`
with proxies:
```
python sudos.py https://cia.gov/ -m http-get-rapid -d 0.1 -l proxy_list.txt
```
with Tor:
```
python sudos.py https://cia.gov/ -m http-get-rapid -d 0.1 --tor
```
