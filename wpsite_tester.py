#!/usr/bin/env python3

import argparse
import requests
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

# -----------------------------
# Configuration (lightweight)
# -----------------------------

WP_PATHS = [
    "/wp-login.php",
    "/wp-admin/",
    "/wp-json/",
    "/wp-includes/",
    "/wp-content/",
    "/xmlrpc.php",
]

HEADERS = {
    "User-Agent": "PassiveHTTPFingerprint/1.0",
}


# -----------------------------
# Startup
# -----------------------------

def startup_header():
    print("------------------------------------------------------")
    print("[+] Detection    : WordPress fingerprinting")
    print("[+] Mode         : Passive (read-only HTTP GET)")
    print("------------------------------------------------------\n")


# -----------------------------
# WordPress detection
# -----------------------------

def is_wordpress(domain: str, timeout: int) -> bool:
    if not domain.startswith("http"):
        base_url = "https://" + domain.strip()
    else:
        base_url = domain.strip()

    for path in WP_PATHS:
        try:
            r = requests.get(
                urljoin(base_url + "/", path.lstrip("/")),
                headers=HEADERS,
                timeout=timeout,
                allow_redirects=True,
            )

            if r.status_code in (200, 301, 302, 403):
                body = r.text.lower()
                if "wordpress" in body or "wp-" in body:
                    return True

        except requests.RequestException:
            continue

    return False


# -----------------------------
# Main
# -----------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fast passive WordPress subdomain fingerprinting"
    )
    parser.add_argument("--input", required=True, help="Input file with subdomains")
    parser.add_argument("--output", required=True, help="Output file (WordPress only)")
    parser.add_argument(
        "--timeout",
        type=int,
        default=3,
        help="Request timeout in seconds (default: 3)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=15,
        help="Number of parallel workers (default: 15)",
    )

    args = parser.parse_args()

    startup_header()

    with open(args.input, "r") as f:
        subdomains = [line.strip() for line in f if line.strip()]

    total = len(subdomains)
    print(f"[*] Scanning {total} subdomain(s)...\n")

    wordpress_sites = []
    completed = 0

    print(f"[*] Progress: 0/{total}", end="\r", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(is_wordpress, sub, args.timeout): sub
            for sub in subdomains
        }

        for future in as_completed(futures):
            sub = futures[future]
            completed += 1

            try:
                if future.result():
                    print()  # move off progress line
                    print(f"[+] WordPress detected: {sub}")
                    wordpress_sites.append(sub)
            except Exception:
                pass

            # Restore progress line
            print(f"[*] Progress: {completed}/{total}", end="\r", flush=True)

    print("\n")

    with open(args.output, "w") as f:
        for site in wordpress_sites:
            f.write(site + "\n")

    print("[+] Scan completed")
    print(f"[+] {len(wordpress_sites)} WordPress site(s) saved to {args.output}")


if __name__ == "__main__":
    main()
