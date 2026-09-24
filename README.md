
# Reconnaissance Automation Utilities

A collection of personal Python utilities developed to automate repetitive tasks during network reconnaissance and penetration testing.

These utilities support common security assessment activities, including domain extraction, HTTP header retrieval, port scanning, host prioritisation, Shodan intelligence gathering, WordPress fingerprinting, and percent encoding.

The project focuses on developing lightweight, practical tools that simplify repetitive reconnaissance tasks, particularly when working with large numbers of IP addresses, domains, subdomains, and network services.

Each script is designed to perform a specific task and can be executed independently.

---

## 1. Project Overview

Reconnaissance is an important stage of penetration testing. When assessing a large number of targets, manually collecting, processing, and organising information can become repetitive and time-consuming.

This project contains six Python utilities that automate different parts of the reconnaissance process.

| Utility | Description |
|---|---|
| `curl_scan.py` | Retrieves HTTP and HTTPS response headers from a list of IP addresses. |
| `domain_extractor.py` | Extracts unique domains and subdomains from CSV files. |
| `masscan_parser.py` | Automates port scanning using Masscan and generates a prioritised host report. |
| `percent_encoder.py` | Fully percent-encodes input strings at the UTF-8 byte level. |
| `shodan_scanner.py` | Retrieves existing host and service information through the Shodan API. |
| `wpsite_scanner.py` | Performs concurrent HTTP fingerprinting to identify potential WordPress installations. |

These utilities are intended to support reconnaissance and preliminary security assessments rather than replace comprehensive penetration-testing tools.

---

## 2. Repository Structure

```text
Reconnaissance-Automation-Utilities/
│
├── README.md
├── curl_scan.py
├── domain_extractor.py
├── masscan_parser.py
├── percent_encoder.py
├── shodan_scanner.py
├── top-1000-ports.txt
└── wpsite_scanner.py
```

The repository also includes `top-1000-ports.txt`, a port-list file that can be supplied to the Masscan utility, provided its entries follow the numeric format expected by the script.

Each Python script is independent and can be executed according to the requirements of a particular reconnaissance task.

---

## 3. Requirements and Installation

### Python

Python 3 is required to execute the utilities.

Check your installed Python version:

```bash
python3 --version
```

### Python dependencies

Most utilities use Python's standard library and do not require additional Python packages.

Two scripts require external packages:

| Script | Required package |
|---|---|
| `shodan_scanner.py` | `shodan` |
| `wpsite_scanner.py` | `requests` |

Install the required packages:

```bash
python3 -m pip install shodan requests
```

### External tools

Two utilities depend on external command-line tools:

| Script | Required tool |
|---|---|
| `curl_scan.py` | curl |
| `masscan_parser.py` | Masscan |

Ensure the required tools are installed and accessible through your system's `PATH`.

The Masscan utility may require elevated privileges depending on the operating system and network configuration.

### Shodan API

The Shodan utility requires a valid API key with access to the host lookup endpoint.

API access and request limits depend on the user's Shodan account and subscription.

---

# 4. HTTP/HTTPS Header Checker

**Script:** `curl_scan.py`

## Description

A lightweight Python utility that automates HTTP and HTTPS header retrieval for a list of IP addresses.

The script reads IP addresses from a text file, generates HTTP and HTTPS URLs for each address, and executes curl to retrieve the corresponding HTTP response headers.

This reduces the need to execute individual curl commands manually when inspecting multiple hosts.

## Features

- Reads multiple IP addresses from a text file.
- Automatically generates HTTP and HTTPS URLs for each IP address.
- Retrieves HTTP response headers using curl.
- Applies a five-second maximum execution time to each request.
- Allows HTTPS requests to proceed despite TLS certificate verification errors.
- Displays the requested URLs and curl output in the terminal.

## Usage

Create a file named `web_ips.txt` containing the target IP addresses, with one IP address per line.

Example:

```text
192.0.2.10
198.51.100.20
203.0.113.30
```

Run the script:

```bash
python3 curl_scan.py
```

The script reads `web_ips.txt` from the current working directory.

For each IP address, the script generates two URLs:

```text
http://192.0.2.10
https://192.0.2.10
```

It then executes the equivalent of:

```bash
curl -k -I --max-time 5 <URL>
```

### curl options

| Option | Description |
|---|---|
| `-k` | Disables TLS certificate verification. |
| `-I` | Sends an HTTP HEAD request to retrieve response headers. |
| `--max-time 5` | Limits each curl request to five seconds. |

## Output

The script prints the target URL and its corresponding curl output directly to the terminal.

Depending on the server response, the retrieved information may include:

- HTTP status codes.
- Server information.
- Content types.
- Redirect locations.
- HTTP security headers.
- Other response headers.

The current implementation does not save the results to a separate output file.

## Limitations

- Some servers may handle HEAD requests differently from GET requests.
- TLS certificate verification is disabled.
- Requests made directly to IP addresses may not reach the intended virtual host when multiple websites share an IP address.
- curl execution errors do not automatically terminate the script.
- The utility retrieves response headers but does not perform vulnerability detection.

---

# 5. CSV Domain Extractor

**Script:** `domain_extractor.py`

## Description

A Python utility that extracts unique domains and subdomains from CSV files.

The script processes every cell in the input CSV file and uses URL parsing and regular expression matching to identify domain names.

Extracted domains are converted to lowercase, deduplicated, sorted alphabetically, and written to a text file.

## Features

- Reads domains and subdomains from CSV files.
- Processes every row and column.
- Extracts hostnames from URLs.
- Identifies domain-like strings within plaintext.
- Supports subdomains of multiple levels.
- Removes duplicate entries.
- Converts extracted domains to lowercase.
- Sorts results alphabetically.
- Supports configurable input and output file paths.

## Usage

```bash
python3 domain_extractor.py \
    --input targets.csv \
    --output domains.txt
```

### Arguments

| Argument | Description |
|---|---|
| `--input` | Path to the input CSV file. |
| `--output` | Path to the output text file. |

Both arguments are required.

### Example input

`targets.csv`

```csv
ID,URL,Description
1,https://portal.example.com,Public portal
2,https://api.example.com/v1,API endpoint
3,portal.example.com,Duplicate entry
4,https://admin.dev.example.com/login,Administration portal
```

### Example output

`domains.txt`

```text
admin.dev.example.com
api.example.com
portal.example.com
```

The script also displays the number of unique domains extracted:

```text
[+] Extracted 3 unique domains
[+] Saved to domains.txt
```

## Limitations

- Domain extraction is based on URL parsing and regular expression matching rather than comprehensive DNS validation.
- Domain-like strings appearing in URL paths, query parameters, or other CSV content may also be extracted.
- The script does not verify whether extracted domains resolve or are reachable.
- IP addresses are not extracted by the domain-matching expression.

The resulting domain list can be used for further reconnaissance activities.

---

# 6. Masscan Parser and Host Prioritisation

**Script:** `masscan_parser.py`

## Description

A Python utility that automates Masscan execution, processes discovered open ports, and generates a formatted host report.

The script accepts a list of target IP addresses and a list of ports to scan.

Before executing Masscan, it removes duplicate port numbers and compresses consecutive ports into ranges.

After scanning, the script parses Masscan's list output, associates discovered open ports with their corresponding hosts, and assigns predefined numerical weights based on port numbers.

Hosts are then sorted by their aggregate scores to support reconnaissance prioritisation.

## Features

- Reads target IP addresses from a text file.
- Accepts a configurable port list.
- Removes duplicate port numbers.
- Compresses consecutive port numbers into ranges.
- Executes Masscan automatically.
- Saves raw Masscan scan results.
- Extracts discovered open ports and their associated IP addresses.
- Maps common port numbers to conventional service names.
- Assigns predefined severity labels and numerical weights to ports.
- Calculates an aggregate score for each host.
- Sorts hosts by their aggregate scores.
- Generates a formatted text report.

## Usage

```bash
sudo python3 masscan_parser.py \
    ips.txt \
    top-1000-ports.txt \
    raw.txt \
    pretty.txt
```

The supplied port file must contain numeric port entries separated by commas or newlines.

### Arguments

| Argument | Description |
|---|---|
| `ips.txt` | File containing the target IP addresses. |
| `top-1000-ports.txt` | Input file containing the ports to scan. |
| `raw.txt` | Destination for raw Masscan output. |
| `pretty.txt` | Destination for the formatted host report. |

All four positional arguments are required.

The port-list filename is not fixed. Any compatible text file containing numeric port entries can be supplied.

### Example IP input

`ips.txt`

```text
192.0.2.10
198.51.100.20
203.0.113.30
```

### Example port input

```text
21
22
80
443
445
3306
3389
8080
8443
```

### Port compression

The script automatically compresses consecutive port numbers.

For example:

```text
21
22
23
80
443
8080
8081
8082
```

Becomes:

```text
21-23,80,443,8080-8082
```

This produces a compact port specification before executing Masscan.

### Masscan configuration

The script executes Masscan with the following options:

```bash
masscan \
    -iL ips.txt \
    -p <PORTS> \
    --retries 2 \
    --rate 1000 \
    --wait 0 \
    -oL raw.txt
```

| Option | Description |
|---|---|
| `-iL` | Reads target IP addresses from an input file. |
| `-p` | Specifies the ports to scan. |
| `--retries 2` | Configures packet retransmissions. |
| `--rate 1000` | Configures a transmission rate of 1,000 packets per second. |
| `--wait 0` | Sets the post-transmission waiting period to zero. |
| `-oL` | Writes scan results in Masscan's list output format. |

### Host prioritisation

The script uses the following predefined severity labels and scores:

| Severity | Score | Port numbers |
|---|---:|---|
| Critical | 4 | 21, 22, 3389, 3306, 5432, 389 |
| High | 3 | 80, 443, 445, 587 |
| Medium | 2 | 8080, 8443, 5900 |
| Low | 1 | All other ports |

The aggregate host score is calculated by summing the assigned weights of its discovered port entries.

Hosts are sorted in descending order of their aggregate scores.

**Important:** These severity labels represent predefined port-based reconnaissance priorities, not confirmed vulnerability severity ratings.

An open port does not necessarily indicate that a service is vulnerable. The scoring system is intended to assist with organising hosts for subsequent investigation.

### Example report

The following example illustrates the report format:

```text
======================
192.0.2.10 is open
Ports: 22 (ssh, critical), 80 (http, high), 443 (https, high)

======================
198.51.100.20 is open
Ports: 445 (smb, high), 8080 (http-proxy, medium)
```

The script saves the raw Masscan results to `raw.txt` and the formatted report to `pretty.txt`.

It also prints the formatted results to the terminal.

## Limitations

- The script identifies open ports but does not perform service version detection or vulnerability validation.
- Service names are inferred from conventional port assignments.
- Services running on non-standard ports may be labelled as unknown.
- Host scores depend on predefined port weights rather than verified exploitability or business impact.
- Hosts without discovered open ports are not included in the formatted report.
- The script uses a fixed Masscan transmission rate of 1,000 packets per second.
- Only numeric port entries are accepted by the port-list parser.

The resulting report is intended to support reconnaissance triage rather than provide a formal vulnerability assessment.

---

# 7. Full Percent Encoder

**Script:** `percent_encoder.py`

## Description

A lightweight Python utility that converts every UTF-8 byte of an input string into its corresponding percent-encoded representation.

Unlike conventional URL encoding, which may leave certain characters unchanged, this utility encodes every byte of the supplied input.

The script supports both interactive and one-time command-line execution.

## Features

- Performs full byte-level UTF-8 percent encoding.
- Encodes letters, numbers, spaces, and special characters.
- Supports Unicode input.
- Produces uppercase hexadecimal output.
- Supports interactive and one-time execution modes.
- Requires no external Python dependencies.

## Usage

### Interactive mode

Run the script without arguments:

```bash
python3 percent_encoder.py
```

Example:

```text
Full Percent Encoder (interactive mode)
Press Ctrl+C or Ctrl+D to exit

Input: admin
Output: %61%64%6D%69%6E

Input: hello world
Output: %68%65%6C%6C%6F%20%77%6F%72%6C%64
```

Press `Ctrl+C` or `Ctrl+D` to exit interactive mode.

### One-time mode

Provide the input string using the `--input` argument.

```bash
python3 percent_encoder.py --input "admin/test"
```

Output:

```text
%61%64%6D%69%6E%2F%74%65%73%74
```

### Unicode example

```bash
python3 percent_encoder.py --input "é"
```

Output:

```text
%C3%A9
```

The character `é` consists of two bytes in UTF-8, and each byte is independently percent-encoded.

## Limitations

- The utility performs a single encoding pass.
- It does not recursively encode previously encoded values.
- The output is a percent-encoded byte sequence rather than a complete URL.
- Different web applications and URL components may interpret encoded characters differently.
- The script does not automatically send encoded values to a target or validate how a server processes them.

The utility can be used for general encoding tasks and preparing encoded input strings during authorised web application security testing.

---

# 8. Shodan Intelligence Lookup

**Script:** `shodan_scanner.py`

## Description

A Python utility that automates Shodan API lookups for a list of IP addresses.

The script retrieves existing host and service information from Shodan's database and generates a structured text report containing available host metadata, discovered ports, service information, and banners.

Unlike direct network scanning, this utility retrieves information already indexed by Shodan.

## Features

- Reads multiple IP addresses from a text file.
- Integrates with the Shodan API.
- Retrieves available host metadata.
- Retrieves discovered ports and service information.
- Extracts available service banners.
- Supports configurable API request throttling.
- Displays an animated terminal spinner during execution.
- Handles Shodan API errors.
- Introduces a delay when an API rate-limit error occurs.
- Generates a readable text report.

## Usage

```bash
python3 shodan_scanner.py \
    --input ips.txt \
    --output shodan_report.txt \
    --api-key YOUR_SHODAN_API_KEY \
    --rate 1
```

### Arguments

| Argument | Description |
|---|---|
| `--input` | File containing IP addresses, one per line. |
| `--output` | Destination for the generated report. |
| `--api-key` | Shodan API key. |
| `--rate` | Configured request rate. Default: 1.0. |

The `--input`, `--output`, and `--api-key` arguments are required.

The configured rate must be greater than zero.

### Example input

`ips.txt`

```text
192.0.2.10
198.51.100.20
203.0.113.30
```

These are reserved documentation IP addresses. Replace them with real public IP addresses when performing authorised lookups.

### Information collected

For each IP address, the utility retrieves available Shodan information, including:

| Field | Description |
|---|---|
| Organization | Organization associated with the IP address. |
| ISP | Internet service provider. |
| Country | Country associated with the host. |
| ASN | Autonomous System Number. |
| Ports | Ports recorded in Shodan's database. |
| Protocol | Transport protocol associated with a service. |
| Product | Available service product information. |
| Banner | Service banner information collected by Shodan. |

### Example report format

```text
============================================================
IP: <IP_ADDRESS> (1/3)
============================================================
Organization : <ORGANIZATION>
ISP          : <ISP>
Country      : <COUNTRY>
ASN          : <ASN>
Ports        : <PORT_LIST>

  Port     : <PORT>
  Protocol : <PROTOCOL>
  Product  : <PRODUCT>
  Banner   :
  <SERVICE_BANNER>
----------------------------------------
```

The fields depend on the information available in Shodan's database.

Some fields may be unavailable or returned as `N/A`.

### Request throttling

The script calculates a request delay using:

```python
request_delay = 1.0 / args.rate
```

With the default configuration, the script introduces a one-second delay after each normally processed IP address.

If a Shodan API rate-limit error is encountered, the script waits ten seconds before continuing to the next IP address.

The affected IP address is not automatically retried.

The configured request delay does not override the API limits imposed by Shodan.

## Limitations

- The utility requires a valid Shodan API key with access to the host lookup endpoint.
- Available information depends on Shodan's database and the user's API access.
- Shodan observations may be outdated or incomplete.
- Discovered ports and service information may not reflect the current state of a target.
- The script does not directly scan target IP addresses.
- An IP address that encounters an API rate-limit error is skipped after the ten-second delay.
- The API key is accepted through a command-line argument in the current implementation.

### API key security

Do not commit real API keys or credentials to this repository.

Passing API keys directly through command-line arguments may expose them through shell history or process listings.

---

# 9. WordPress Fingerprinting

**Script:** `wpsite_scanner.py`

## Description

A lightweight Python utility that identifies potential WordPress installations across multiple subdomains.

The script performs concurrent HTTP GET requests against three commonly associated WordPress endpoints and examines the returned response content for WordPress-related indicators.

Subdomains matching the detection conditions are saved to a text file for further investigation.

## Features

- Reads multiple subdomains from a text file.
- Checks three common WordPress endpoints.
- Uses concurrent HTTP requests through `ThreadPoolExecutor`.
- Supports configurable worker counts.
- Supports configurable connection and read timeouts.
- Disables automatic HTTP retries through the configured Requests adapter.
- Displays progress during execution.
- Saves a filtered list of potential WordPress installations.

## Usage

```bash
python3 wpsite_scanner.py \
    --input subdomains.txt \
    --output wordpress_sites.txt \
    --timeout 3 \
    --workers 8
```

### Arguments

| Argument | Description |
|---|---|
| `--input` | File containing target subdomains. |
| `--output` | Destination for the filtered results. |
| `--timeout` | Connection and read timeout in seconds. Default: 3. |
| `--workers` | Maximum number of concurrent worker threads. Default: 8. |

The input and output file arguments are required.

### Example input

`subdomains.txt`

```text
www.example.com
blog.example.com
portal.example.com
https://shop.example.com
```

If an input entry does not begin with `http`, the script automatically prepends `https://`.

The intended input is a list of hostnames or HTTP(S) base URLs.

The script does not automatically retry HTTP when an HTTPS request fails.

### WordPress endpoints

For each target, the script checks the following paths:

```text
/wp-login.php
/wp-admin/
/wp-json/
```

For example:

```text
https://blog.example.com/wp-login.php
https://blog.example.com/wp-admin/
https://blog.example.com/wp-json/
```

### Detection logic

The script performs an HTTP GET request for each endpoint and follows redirects.

It examines the response body when the final HTTP status code is one of:

```text
200
301
302
403
```

A target is identified as a potential WordPress installation when the response body contains either of the following strings:

```text
wordpress
wp-
```

Matching is case-insensitive.

When a match is found, the script stops checking additional paths for that target and returns a positive result.

Targets without a matching response are not included in the output file.

### Example output

An illustrative terminal output:

```text
[*] Scanning 3 subdomain(s)...

[+] WordPress detected: blog.example.com

[+] Scan completed
[+] 1 WordPress site(s) saved to wordpress_sites.txt
```

The corresponding output file:

`wordpress_sites.txt`

```text
blog.example.com
```

The output file contains the original input entries that satisfy the detection conditions.

### Concurrency and timeouts

The script uses a maximum of eight concurrent worker threads by default.

Each HTTP request has configurable connection and read timeouts.

The script also applies an overall timeout while collecting completed tasks, calculated from the total number of targets and the configured timeout value.

When the overall timeout is reached, the script attempts to cancel unfinished tasks.

Tasks that are already running may continue until completion.

## Limitations

- Detection is based on HTTP response content and may produce false positives or false negatives.
- A website containing WordPress-related strings is not necessarily running WordPress.
- WordPress installations that do not expose the expected indicators may not be detected.
- Only three predefined endpoints are checked.
- Targets without an explicit scheme are checked using HTTPS only.
- Redirects may result in detection based on content returned by another hostname.
- The script performs active HTTP fingerprinting because it sends GET requests directly to the target servers.
- Positive results are not automatically verified as confirmed WordPress installations.
- The utility does not perform WordPress vulnerability scanning or exploit validation.

The generated results are intended to identify potential WordPress targets for further investigation.

---

# 10. Reconnaissance Workflow

The utilities can support different stages of a penetration-testing engagement.

They are independent tools rather than components of a fully integrated automated pipeline.

A possible workflow is illustrated below:

```text
              Target Information
                      |
                      v
             domain_extractor.py
                      |
                      v
              Domain Inventory
                      |
           +----------+----------+
           |                     |
           v                     v
     DNS Resolution       wpsite_scanner.py
           |                     |
           v                     v
      IP Inventory        Potential WordPress
           |                Installations
           |
     +-----+----------------+---------------+
     |                      |               |
     v                      v               v
curl_scan.py       shodan_scanner.py  masscan_parser.py
     |                      |               |
     v                      v               v
 HTTP Headers        Host Intelligence   Port Inventory
                                            |
                                            v
                                     Prioritised Hosts
                                            |
                                            v
                                  Further Security Assessment
```

DNS resolution is shown as a separate step and is not implemented by the scripts in this repository.

The Full Percent Encoder is an independent supporting utility for preparing encoded input strings during web application testing.

The order in which the utilities are used depends on the assessment scope and available target information.

---

# 11. Responsible Usage

These utilities are intended for educational purposes, authorised penetration testing, and security assessment activities.

Only perform active network scanning or HTTP fingerprinting against systems for which you have explicit authorisation.

The HTTP Header Checker, Masscan Parser, and WordPress Fingerprinting utilities send requests directly to the supplied targets.

The Shodan Intelligence Lookup utility retrieves existing observations from Shodan's database rather than directly scanning the target systems.

Users are responsible for ensuring that their activities remain within the authorised assessment scope and comply with applicable laws, organisational policies, and service-provider requirements.

Review the target scope and scanning configuration before execution.

---

# 12. Project Scope and Limitations

This repository contains lightweight utilities developed to automate specific reconnaissance tasks.

The scripts are not intended to provide a comprehensive penetration-testing framework.

In particular:

- Open ports do not necessarily indicate vulnerabilities.
- Service identification based on port numbers is not definitive.
- HTTP response headers do not independently establish whether a system is secure.
- WordPress fingerprinting results may require manual verification.
- Shodan observations may not represent the current state of a target.
- Reconnaissance findings should be validated before being included in a formal penetration-testing report.

The utilities are intended to assist with information gathering, result organisation, and the identification of systems requiring further investigation.

---

# 13. Data Confidentiality

Do not commit sensitive information to this repository, including:

- Confidential IP addresses or domain inventories.
- Internal network information or sensitive assessment results.
- Real API keys, passwords, access tokens, or other credentials.
- Confidential service banners or penetration-testing reports.

Input and output files generated during actual security assessments should be kept separate from the public repository unless they are authorised for disclosure.

The example IP addresses used in this README belong to ranges reserved for documentation and are not intended to represent live targets.

---

# 14. Project Background

This repository contains a collection of personal Python utilities developed to automate repetitive tasks encountered during network reconnaissance and penetration testing.

The project demonstrates practical Python scripting techniques, including file processing, command-line automation, subprocess execution, external security tool integration, API interaction, multithreading, and structured report generation.

Each utility focuses on a specific task and is designed to be lightweight, reusable, and straightforward to execute.

The scripts are maintained as independent tools, allowing them to be used individually according to the requirements of a particular security assessment.
