import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Proxy formatter")
    parser.add_argument("file", metavar="FILE", nargs="?", help="Proxy list file to format")
    parser.add_argument("-t", "--type", metavar="PROXY TYPE", choices=["http", "socks4", "socks5"], help="Proxy type of the provided proxy list")
    parser.add_argument("-o", "--output", metavar="OUTPUT NAME", help="Output file name")

    args = parser.parse_args()

    if not args.file:
        print(f"ERROR: Proxy file must be defined.")
        parser.print_usage()
        exit()

    if not args.type:
        print(f"ERROR: Proxy type must be defined.")
        parser.print_usage()
        exit()

    if not os.path.exists(args.file):
        print(f"ERROR: The proxy list file you entered does not exist")
        exit()

    if os.path.isdir(args.file):
        print(f"ERROR: The file you entered is a DIR")
        exit()

    try:
        with open(args.file) as file:
            proxy_list1 = file.read().splitlines()
            file.close()
    except Exception as e:
        print(f"ERROR: {e}")
        exit()

    proxy_list2 = []
    for proxy in proxy_list1:
        proxy_format = f"{args.type}://{proxy}"
        proxy_list2.append(proxy_format)

    if args.output:
        outfile = args.output
    else:
        outfile = f"formatted_{args.file}"

    if os.path.exists(outfile):
        prompt = input("The output file already exists. Overwrite? [Y/n]: ").strip()
        if not prompt.startswith("y"):
            exit()

    with open(outfile, "a") as file:
        file.write("\n".join(proxy_list2))
        file.close()

    print(f"OUTPUT FILE: {outfile}")

if __name__ == "__main__":
    main()
