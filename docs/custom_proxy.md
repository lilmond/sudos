# Custom Proxy List
Hello there! In this tutorial we will explain you how to use your own proxy list in very basic way as easy as possible. We hope it helps you!

# How to
## Use my own proxy list
In order to use your own proxy list, you must first create a formatted version of it using our pre-made tool [proxy_formatter.py](https://github.com/lilmond/sudos/blob/main/proxy_formatter.py)

## Use proxy_formatter.py
Simple! Just follow the instructions below!

### Get a proxy list and save it as a text file.

Example: `proxy_list.txt`

```
184.181.217.204:4145
98.185.94.94:4145
184.178.172.18:15280
```

### Launch proxy_formatter.py
Now that you have a proxy list saved in a text file, you can now run the formatter tool! To use it, simply execute the command below.
```shell
python proxy_formatter.py proxy_list.txt -t socks5
```
Note that you can change the `-t` parameter to whatever protocol your proxy list uses. Examples: `socks5`, `socks4`, `http`

The tool will then generate a new file named `formatted_proxy_list.txt`

Output: `formatted_proxy_list.txt`

```
socks5://184.181.217.204:4145
socks5://98.185.94.94:4145
socks5://184.178.172.18:15280
```

### Launch sudos.py
Now that you have everything ready, you can now run sudos.py and use your own proxy list!
```shell
python sudos.py http://target.com/ -l formatted_proxy_list.txt
```
