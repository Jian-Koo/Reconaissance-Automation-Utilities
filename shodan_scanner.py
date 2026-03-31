#!/usr/bin/env python3

import argparse
import shodan
import sys
import threading
import itertools
import time

# -----------------------------
# Spinner animation
# -----------------------------
def spinner_task(stop_event):
    spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    while not stop_event.is_set():
        sys.stdout.write(f"\r[*] Querying Shodan database {next(spinner)}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r[*] Querying Shodan database done.   \n")
    sys.stdout.flush()

# -----------------------------
# Main logic
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="Query Shodan for a list of IPs")
    parser.add_argument("--input", required=True, help="Input file with IPs (one per line)")
    parser.add_argument("--output", required=True, help="Output report file")
    parser.add_argument("--api-key", required=True, help="Shodan API key")
    parser.add_argument(
        "--rate",
        type=float,
        default=1.0,
        help="Requests per second (default: 1.0, safe for free plans)"
    )

    args = parser.parse_args()

    if args.rate <= 0:
        print("[!] Rate must be greater than 0")
        sys.exit(1)

    request_delay = 1.0 / args.rate

    # -----------------------------
    # Startup banner (CORRECT PLACE)
    # -----------------------------
    print("\n[+] Initializing Shodan Scanner")
    print("    ███████╗██╗  ██╗ ██████╗ ██████╗  █████╗ ███╗   ██╗")
    print("    ██╔════╝██║  ██║██╔═══██╗██╔══██╗██╔══██╗████╗  ██║")
    print("    ███████╗███████║██║   ██║██║  ██║███████║██╔██╗ ██║")
    print("    ╚════██║██╔══██║██║   ██║██║  ██║██╔══██║██║╚██╗██║")
    print("    ███████║██║  ██║╚██████╔╝██████╔╝██║  ██║██║ ╚████║")
    print("    ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝")
    print("           SHODAN DATABASE RECON TOOL")
    print("------------------------------------------------------")
    print(f"[+] Rate limit: {args.rate} request(s) per second")
    print("[+] Mode      : Passive Shodan Intelligence Lookup\n")
    time.sleep(1)

    try:
        api = shodan.Shodan(args.api_key)
    except Exception as e:
        print(f"[!] Failed to initialize Shodan API: {e}")
        sys.exit(1)

    try:
        with open(args.input, "r") as f:
            ips = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[!] Failed to read input file: {e}")
        sys.exit(1)

    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=spinner_task, args=(stop_event,))
    spinner_thread.start()

    with open(args.output, "w") as out:
        for idx, ip in enumerate(ips, start=1):
            out.write("=" * 60 + "\n")
            out.write(f"IP: {ip} ({idx}/{len(ips)})\n")
            out.write("=" * 60 + "\n")

            try:
                host = api.host(ip)

                out.write(f"Organization : {host.get('org', 'N/A')}\n")
                out.write(f"ISP          : {host.get('isp', 'N/A')}\n")
                out.write(f"Country      : {host.get('country_name', 'N/A')}\n")
                out.write(f"ASN          : {host.get('asn', 'N/A')}\n")
                out.write(f"Ports        : {', '.join(str(p) for p in host.get('ports', []))}\n\n")

                for service in host.get("data", []):
                    out.write(f"  Port     : {service.get('port')}\n")
                    out.write(f"  Protocol : {service.get('transport')}\n")
                    out.write(f"  Product  : {service.get('product', 'N/A')}\n")
                    banner = service.get("data", "").strip()
                    out.write("  Banner   :\n")
                    out.write(banner + "\n" if banner else "N/A\n")
                    out.write("-" * 40 + "\n")

            except shodan.exception.APIError as e:
                msg = str(e).lower()
                if "rate limit" in msg or "too many requests" in msg:
                    out.write("[!] Rate limit hit – backing off for 10 seconds\n")
                    time.sleep(10)
                    continue
                else:
                    out.write(f"[!] No data or error: {e}\n")

            out.write("\n")
            time.sleep(request_delay)

    stop_event.set()
    spinner_thread.join()

    print("\n[✓] Shodan scanning complete!")
    print(f"[✓] Output saved to: {args.output}")
    print("[✓] Rate limiting enforced cleanly\n")

# -----------------------------
if __name__ == "__main__":
    main()
