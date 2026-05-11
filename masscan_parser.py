#!/usr/bin/env python3

# To run:
# sudo python3 masscan_parser.py ips.txt ports.txt raw.txt pretty.txt

import subprocess
import sys
from collections import defaultdict
import os

# -----------------------------
# Argument handling (UPDATED)
# -----------------------------
if len(sys.argv) != 5:
    print("Usage: python3 masscan_parser.py <ips.txt> <ports.txt> <raw_output.txt> <pretty_output.txt>")
    sys.exit(1)

ips_file = sys.argv[1]
ports_file = sys.argv[2]
output_file = sys.argv[3]    # raw masscan output
report_file = sys.argv[4]    # pretty report output

# -----------------------------
# Service name mapping
# -----------------------------
service_map = {
    "21": "ftp", "22": "ssh", "23": "telnet", "25": "smtp", "53": "dns",
    "80": "http", "110": "pop3", "111": "rpcbind", "135": "msrpc",
    "139": "netbios", "143": "imap", "161": "snmp", "389": "ldap",
    "443": "https", "445": "smb", "587": "smtp-submission",
    "631": "ipp", "873": "rsync", "902": "vmware-auth",
    "1433": "mssql", "1521": "oracle", "2049": "nfs",
    "2375": "docker", "2376": "docker-ssl", "3306": "mysql",
    "3389": "rdp", "5432": "postgres", "5900": "vnc",
    "6379": "redis", "8080": "http-proxy", "8443": "https-alt"
}

# -----------------------------
# Severity model
# -----------------------------
severity_map = {
    "critical": ["21", "22", "3389", "3306", "5432", "389"],
    "high": ["80", "443", "445", "587"],
    "medium": ["8080", "8443", "5900"],
    "low": []
}

severity_score = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1
}

def get_severity(port):
    for level, plist in severity_map.items():
        if port in plist:
            return level
    return "low"

def host_total_score(port_list):
    return sum(severity_score[get_severity(p)] for p in port_list)

# -----------------------------
# Load and compact ports file
# -----------------------------
with open(ports_file) as f:
    raw_ports = f.read().replace(',', '\n').splitlines()

# Extract valid integers, sort them, and remove duplicates
port_nums = sorted(set(int(p.strip()) for p in raw_ports if p.strip().isdigit()))

if not port_nums:
    print("[-] No valid ports found.")
    sys.exit(1)

# Compact into ranges (e.g., [1, 2, 3, 5, 8, 9] -> "1-3,5,8-9")
ranges = []
start = port_nums[0]
end = port_nums[0]

for p in port_nums[1:]:
    if p == end + 1:
        end = p
    else:
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")
        start = p
        end = p

# Append the last range/port
if start == end:
    ranges.append(str(start))
else:
    ranges.append(f"{start}-{end}")

ports = ",".join(ranges)
print(f"[*] Compressed port list length: {len(ports)} characters")

# -----------------------------
# Run masscan
# -----------------------------
print("[*] Running masscan...")

cmd = [
    "masscan",
    "-iL", ips_file,
    "-p", ports,
    "--retries", "2",
    "--rate", "1000",
    "--wait", "0",
    "-oL", output_file
]

subprocess.run(cmd)

if not os.path.exists(output_file):
    print("[-] Masscan did not produce output.")
    sys.exit(1)

print("[+] Masscan scan complete.")
print("[*] Parsing results...")

# -----------------------------
# Parse masscan output
# -----------------------------
hosts = defaultdict(list)

with open(output_file, "r") as f:
    for line in f:
        if line.startswith("open"):
            parts = line.split()
            if len(parts) >= 4:
                port = parts[2]
                ip = parts[3]
                hosts[ip].append(port)

# -----------------------------
# Sort hosts by severity
# -----------------------------
sorted_hosts = sorted(
    hosts.items(),
    key=lambda x: host_total_score(x[1]),
    reverse=True
)

# -----------------------------
# Pretty print + write results
# -----------------------------
with open(report_file, "w") as out:
    for ip, ports in sorted_hosts:
        separator = "=" * 22
        header = f"{ip} is open\n"

        formatted_ports = []
        for p in sorted(ports, key=int):
            service = service_map.get(p, "unknown")
            severity = get_severity(p)
            formatted_ports.append(f"{p} ({service}, {severity})")

        ports_line = "Ports: " + ", ".join(formatted_ports) + "\n\n"

        # Print to terminal
        print(separator)
        print(header.strip())
        print(ports_line.strip())

        # Write to file
        out.write(separator + "\n")
        out.write(header)
        out.write(ports_line)

print(f"\n[+] Done.")
print(f"[+] Raw output written to    : {output_file}")
print(f"[+] Pretty report written to : {report_file}")
