import socket
import time

TIMEOUT = 5

def main():
    try:
        host = input("Host: ").strip()
        port = int(input("Port: ").strip())

        print("checking hostname...")
        try:
            ip = socket.gethostbyname(host)
        except Exception:
            print("error: invalid host")
            return

        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            connect_time = time.time()

            try:
                sock.connect((ip, port))
            except Exception as e:
                print(f"error: {e}")
                time.sleep(1)
                continue

            connected_time = time.time()
            timestamp = connected_time - connect_time
            timestamp_ms = timestamp * 1000
            timestamp_ms = f"{float(timestamp_ms):.2f}"
            print(f"ping: {timestamp_ms} ms")
            time.sleep(1)
    except KeyboardInterrupt:
        return

if __name__ == "__main__":
    main()
