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

### `-u`, `--update-proxy`
Update proxy list before initializing the attack.

Default: False

Type: NONE

### `-p`, `--no-proxy`
Don't use proxy for the attack.

Default: False

Type: NONE

### `-H`, `--headers`
Add a custom header. Format: "Header_Name: Header_Value"

Type: STRING

### `-l`, `--proxy-list`
Use custom proxy list. Use the proxy_formatter.py before using this parameter!

Type: FILE

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

### `-m` `--mode`
Set mode.

Default: 1

Type: INTEGER

## Examples
So if you're having trouble figuring out how to use SuDOS, try using the example command below.

### Basic
This is the easiest way of using SuDOS.

Required Parameters: URL
```
python sudos.py http://example.com/
```
