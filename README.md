# sudos

SuDOS or Super Denial of Service is a proxy-based DoS tool used to crash unprotected websites from this kind of attack. It is highly recommended to use proxychains or VPN while using this tool to hide your own IP address from proxy servers or even from your target.

# Disclaimer
- This tool is for educational purposes only.
- I will not be responsible for any damage this tool cause. Use it at your own risk!
- This tool is in early version. Many bugs may occur!

# Installation
Please copy and paste the step-by-step commands below to successfully install **SuDOS** in your computer. I will not be providing how to install [Python](https://python.org/) in your computer. Do some research!
```
git clone https://github.com/lilmond/sudos.git
pip install -r requirements.txt
```

# Usage examples
```
python sudos.py "https://example.com/path/page.php?parameter=parameter_value" ./proxies/http/1.txt http --timeout 5
python sudos.py "https://example.com/path/page.php?parameter=parameter_value" ./proxies/socks5/1.txt socks5 -t 100
python sudos.py "https://example.com/path/page.php?parameter=parameter_value" ./proxies/socks4/1.txt socks4 -m POST
```
