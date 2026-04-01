#!/usr/bin/env python3

import csv
import re
import sys
import argparse
from urllib.parse import urlparse

# Match domains / subdomains of any depth
DOMAIN_REGEX = re.compile(
    r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'
)

def extract_domains_from_text(text: str):
    results = set()

    if not text:
        return results

    text = text.strip()

    # Extract hostname from URLs
    if "://" in text:
        try:
            parsed = urlparse(text)
            if parsed.hostname:
                results.add(parsed.hostname.lower())
        except Exception:
            pass

    # Regex fallback for plaintext / embedded domains
    for match in DOMAIN_REGEX.findall(text):
        results.add(match.lower())

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Extract domains and subdomains from any CSV column"
    )
    parser.add_argument(
        "--input", required=True,
        help="Input CSV file"
    )
    parser.add_argument(
        "--output", required=True,
        help="Output file (one domain per line)"
    )

    args = parser.parse_args()

    found_domains = set()

    with open(args.input, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            for cell in row:
                found_domains.update(extract_domains_from_text(cell))

    with open(args.output, "w") as out:
        for domain in sorted(found_domains):
            out.write(domain + "\n")

    print(f"[+] Extracted {len(found_domains)} unique domains")
    print(f"[+] Saved to {args.output}")


if __name__ == "__main__":
    main()

