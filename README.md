# sudos

Layer 7 DDoS Tool.

Too rich? Send all your Bitcoins here (Donation): 17nXfqRRiSGDpx1XEh3veHA6gyCLAktFk9

Discord for hackers: https://discord.com/invite/Bnf3e8pkyj

Follow me for more free hacking tools :3

Cool proxy servers provider: https://openproxy.space/premium

# Introducing sudos 2.7.0
Too long have passed since the last update, so I decided to upgrade this tool to a new level. New attack methods and features have been added, more of them will be added later. I will be documenting about it all later. Thank you for your support!

Help
```
                                                                                      __                     
                                                                                     |  \                    
                                                             _______  __    __   ____| $$  ______    _______ 
                                                            /       \|  \  |  \ /      $$ /      \  /       \
                                                           |  $$$$$$$| $$  | $$|  $$$$$$$|  $$$$$$\|  $$$$$$$
                                                            \$$    \ | $$  | $$| $$  | $$| $$  | $$ \$$    \ 
                                                            _\$$$$$$\| $$__/ $$| $$__| $$| $$__/ $$ _\$$$$$$\
                                                           |       $$ \$$    $$ \$$    $$ \$$    $$|       $$
                                                            \$$$$$$$   \$$$$$$   \$$$$$$$  \$$$$$$  \$$$$$$$ 
                                                           
                                                            Source: https://github.com/lilmond/sudos V:2.7.0
                                                           
                                                                 Try out the other attack methods, list:
                                                               ["http-get", "http-get-rapid", "http-post",
                                                                  "http-post-slow", "http-post-custom",
                                                                     "ssl-flood", "websocket-flood"]
                                                           
                                                           
usage: sudos.py [-h] [-t THREADS] [-m ATTACK METHOD] [-d DELAY] [-c TIMEOUT] [-l FILE] [-H HEADERS] [-q] [--duration DURATION] [--payload PAYLOAD] [--test] [--tor]
                URL

Layer-7 Python DDoS Tool.

positional arguments:
  URL                   Target's full URL.

options:
  -h, --help            show this help message and exit
  -t THREADS, --threads THREADS
                        Attack threads. The more, the stronger. Default: 20
  -m ATTACK METHOD, --method ATTACK METHOD
  -d DELAY, --delay DELAY
                        Sleep time between HTTP requests. Tip: setting this to 0 with http-get-rapid method may cause critical damage to the target, even with only 20
                        threads. Though may cause the statistics to be innacurate, so set only to at least 0.1.
  -c TIMEOUT, --timeout TIMEOUT
                        Socket connection timeout. Default: 10
  -l FILE, --proxy-list FILE
                        Use a custom proxy list. You can use Proxal to get a good proxy list.
  -H HEADERS, --headers HEADERS
                        Add an HTTP header. Example: -H/--header "Authorization: someauthorizationheadervalue"
  -q, --quiet           Supress error messages.
  --duration DURATION   Set how long the attack will be running for. This is by default is set to None and will keep running forever until stopped manually.
  --payload PAYLOAD     This is required to define HTTP-POST-CUSTOM payload.
  --test                Use this for testing and viewing the web server's response to the attack's request.
  --tor                 Use Tor proxies for the attack.

```
