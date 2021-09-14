# Usage
This shows how you can use SuDOS easily.

## Parameters

### `-t` `--threads`
Set max thread.

Default: 100

Type: INTEGER

### `-z` `--proxy-type`
Define the proxy protocol of the proxy list you're using. This is required when you're using a proxy list.

Type: PROXY TYPE

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

### `-n` `--receive`
When this is set. You will receive HTTP response per HTTP request the socket send.

Default: False

Type: NONE

### `-m` `--mode`
Set mode.

Default: 1

Type: INTEGER
