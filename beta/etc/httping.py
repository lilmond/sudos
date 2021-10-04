import argparse
import socket
import time
import ssl

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", nargs="?", type=str, help="host to ping")
    parser.add_argument("-p", "--port", type=int, default=80, help="port number to connect to")
    parser.add_argument("-s", "--ssl", action="store_true", help="use ssl for socket on connect")
    parser.add_argument("--path", type=str, default="/", help="path to send http request")
    args = parser.parse_args()

    if not args.host:
        print(f"ERROR: host is required")
        return

    if any([args.port < 1, args.port > 65535]):
        print(f"ERROR: invalid port number")
        return

    host = socket.gethostbyname(args.host)

    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            time1 = time.time()
            sock.connect((host, args.port))
            time2 = time.time()
            connect_timestamp = f"{((time2 - time1) * 1000):.2f} ms"

            if args.ssl:
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=args.host)

            http = f"GET {args.path} HTTP/1.1\r\nHost: {args.host}\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0\r\n\r\n"
            sock.send(http.encode())
            response = sock.recv(4096).decode().strip()

            if len(response) == 0: status = "no response"
            else:
                response = response.splitlines()[0]
                response = response.split(" ")
                response.pop(0)
                response = " ".join(response)
                status = response

                if len(status) > 15:
                    status = f"{status[:15]}..."

                print(f"ping={connect_timestamp} status={status}")
                time.sleep(1)
        except Exception as e:
            print("ERROR: {e}")
            time.sleep(1)
            continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
