import subprocess

with open("web_ips.txt") as f:
    ips = [line.strip() for line in f if line.strip()]

urls = []
for ip in ips:
    urls.append(f"http://{ip}")
    urls.append(f"https://{ip}")

for url in urls:
    print("=" * 40)
    print(url)
    print("-" * 40)
    try:
        subprocess.run(
            ["curl", "-k", "-I", "--max-time", "5", url],
            check=False
        )
    except Exception as e:
        print(f"ERROR: {e}")
