# Usage
This shows how you can use SuDOS easily.

## Parameters
Parameters of latest version of SuDOS. If you're using the older version, please update it.

### `url`
This parameter is a must. URL must also be be defined in complete format including the protocol!

Type: URL

Example: `http://example.com/`, `https://example.com/`

### `-t` `--threads`
Set max thread.

Default: 100

Type: INTEGER

### `-z` `--proxy-type`
Define the proxy protocol of the proxy list you're using. This is required when you're using a proxy list.

Type: PROXY TYPE

Example: `socks5`, `socks4`, `http`

### `x` `--proxy-list`
Proxy list path. List format must be like: `127.0.0.1:9050`

Type: FILE PATH

### `-c` `--timeout`
Set socket connection timeout.

Default: 5

Type: INTEGER

### `-v` `--delay`
Wait time of sending an HTTP request of every sockets.

Default: 1

Type: INTEGER

### `-b` `--no-verify`
Set the SSL verification mode to CERT_NONE. Use this only when the server uses self signed certificate.

Default: False

Type: NONE

### `-n` `--receive`
When this is set. You will receive HTTP response per HTTP request the socket send.

Default: False

Type: NONE

### `-m` `--mode`
Set mode.

Default: 1

Type: INTEGER

## Examples
So if you're having trouble figuring out how to use SuDOS, try using the example commands below!

URL parameter is also always required so we will exclude it from required parameter values.

### Basic
This is the easiest way of using SuDOS. Take note that this won't use proxies and will use your real own IP address for the attack and your IP may get blocked by your target.

Required Parameters: NONE
```
python sudos.py http://example.com/
```

### Proxy Mode
This is how you can use proxies for the attack.

Required Parameters: [-z | --proxy-type](https://github.com/lilmond/sudos/blob/main/docs/usage.md#-z---proxy-type), [-x | --proxy-list](https://github.com/lilmond/sudos/blob/main/docs/usage.md#x---proxy-list)
```
python sudos.py -z socks5 -x socks5_list.txt https://example.com/
```
