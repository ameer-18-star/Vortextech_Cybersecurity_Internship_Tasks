# VortexTech Cybersecurity Internship — Week 2

**Track:** Beginner–Intermediate  
**Intern:** Ali Ameer  
**Program:** VortexTech Cybersecurity Internship 2026  
**Week:** 2 of 4 — Hands-On with Basic Security Tools

---

## What this week was about

Most beginners spend months reading about cybersecurity without touching a single tool. Week 2 fixes that. Two foundational tasks — a Python password strength evaluator and a network port scanner using Nmap — both run on your own machine, both completely legal, both immediately practical.

Passwords and open ports aren't flashy topics. They're also responsible for the majority of real-world breaches. Understanding them at a hands-on level before moving into more advanced territory is the right order to learn security.

---

## Repository structure

```
vortextech-cybersec-week2/
│
├── password_checker.py                        # Task A — Python password evaluator
├── scan_results/
│   ├── localhost_scan.txt                     # Task B — Nmap output, localhost
│   └── network_scan.txt                      # Task B — Nmap output, home network
├── VortexTech_Week2_Documentation_AliAmeer.md # Full technical report
└── README.md                                  # This file
```

---

## Task A — Password Strength Evaluator

### What it does

`password_checker.py` takes any password string and runs it through six checks:

1. Common-password override — if the password matches any entry in a built-in wordlist of 50 commonly used passwords, it's flagged as Very Weak immediately, before any other check runs
2. Length check — must be at least 8 characters
3. Uppercase check — must contain at least one A–Z character
4. Lowercase check — must contain at least one a–z character
5. Digit check — must contain at least one 0–9 character
6. Special character check — must contain at least one character from `!@#$%^&*()_+-=` etc.

Each check that passes adds 1 point to a score out of 5. The score maps to a strength rating displayed with a visual bar.

| Score | Rating | Visual |
|-------|--------|--------|
| 0–2 | Very Weak | `[█░░░░]` |
| 3 | Weak | `[██░░░]` |
| 4 | Medium | `[███░░]` |
| 5 | Strong | `[█████]` |

### How to run it

No external libraries needed. Pure Python 3. No `pip install` required.

```bash
# Clone the repository
git clone https://github.com/ali-ameer/vortextech-cybersec-week2
cd vortextech-cybersec-week2

# Run the built-in test suite (8 sample passwords)
python password_checker.py

# On Linux / Kali
python3 password_checker.py
```

The test suite runs automatically and evaluates 8 passwords covering every possible rating — Very Weak, Weak, Medium, and Strong — so you can see exactly how the scoring works.

### Interactive mode

Want to test your own passwords? Run it with the `--interactive` flag:

```bash
python password_checker.py --interactive
```

Type any password, get instant results. Type `quit` to exit. The password is masked with asterisks in the output so nothing is logged in plaintext.

### Sample output

```
==================================================
  PASSWORD STRENGTH EVALUATOR
  VortexTech Internship — Week 2  |  Ali Ameer
==================================================

  Test: Weak — no uppercase, no special char

  Password : ********  (length: 8)
  Score    : 3/5
  Rating   : [██░░░]  Weak
  Feedback :
      ❌  Add at least one uppercase letter (A–Z).
      ❌  Add at least one special character (!@#$%^&* etc.).
  ────────────────────────────────────────────────

  Test: Strong — all 5 checks pass

  Password : *********  (length: 9)
  Score    : 5/5
  Rating   : [█████]  Strong
  Feedback :
      ✅  All checks passed. This is a strong password.
  ────────────────────────────────────────────────
```

### Requirements

```
Python 3.6 or higher
No external libraries
Works on Windows, Linux, macOS, Kali Linux
```

---

## Task B — Network Port Scanning with Nmap

### What it does

Nmap (Network Mapper) scans a target IP address or range and reports every open port it finds, along with the service running on each port. Think of it as knocking on every door of a building and noting which ones open and what's behind them.

Two scans were performed:

**Scan 1 — Localhost (`127.0.0.1`)**  
Always safe. Points at your own machine only. Reveals every service currently listening for connections on your device.

**Scan 2 — Home network (`192.168.1.0/24`)**  
Scans all 256 addresses in the home network subnet. Reveals every device connected to the router and what services each one is running.

> **Legal notice:** Both scans were performed exclusively on personally owned equipment. Scanning any network or device you don't own without explicit written permission is illegal. Don't do it.

### How to run it

Install Nmap first:

```bash
# Windows — download installer from https://nmap.org/download.html
# Kali Linux — pre-installed, no action needed
# Ubuntu / Debian
sudo apt update && sudo apt install nmap -y

# Verify installation
nmap --version
```

Then run the scans:

```bash
# Basic localhost scan — always safe
nmap 127.0.0.1

# Version detection on localhost — identifies service versions
nmap -sV 127.0.0.1

# Find your local IP first (Linux)
ip addr show

# Find your local IP first (Windows)
ipconfig

# Ping sweep — discover live hosts without scanning ports
nmap -sn 192.168.1.0/24

# Full home network scan — only on YOUR network
nmap 192.168.1.0/24

# Save output to a file
nmap -sV 127.0.0.1 -oN scan_results/localhost_scan.txt
nmap -sV 192.168.1.0/24 -oN scan_results/network_scan.txt
```

### Nmap flags reference

| Flag | What it does |
|------|-------------|
| `-sV` | Detects the version of the service on each open port |
| `-A` | Aggressive — enables OS detection, version detection, and script scanning |
| `-sn` | Ping sweep — finds live hosts without scanning ports |
| `-p` | Specify ports (e.g. `-p 22,80,443` or `-p 1-1000`) |
| `-oN` | Save output to a normal text file |
| `-oX` | Save output to XML format |

### Localhost scan results

```
PORT     STATE  SERVICE        VERSION
22/tcp   open   ssh            OpenSSH 9.2p1 Debian 2+deb12u2
80/tcp   open   http           Apache httpd 2.4.57
443/tcp  open   https          Apache httpd 2.4.57
3306/tcp open   mysql          MySQL 8.0.35
5432/tcp open   postgresql     PostgreSQL DB 15.4
8080/tcp open   http-proxy     Werkzeug/3.0.1 Python/3.11.6
```

### Home network scan results

```
192.168.1.1   (Router)
  80/tcp   open   http
  443/tcp  open   https
  8080/tcp open   http-alt

192.168.1.100  (Linux machine)
  22/tcp   open   ssh
  5900/tcp open   vnc

192.168.1.101  (Windows PC)
  135/tcp  open   msrpc
  139/tcp  open   netbios-ssn
  445/tcp  open   microsoft-ds
```

### Port-to-service reference

| Port | Service | Risk | Notes |
|------|---------|------|-------|
| 22 | SSH | Medium | Disable password auth. Use key pairs. |
| 80 | HTTP | High | Unencrypted. Redirect everything to HTTPS. |
| 135 | MSRPC | High | Windows RPC. Keep OS patched against EternalBlue. |
| 139 | NetBIOS | High | Legacy Windows sharing. Disable if SMBv2/v3 is active. |
| 443 | HTTPS | Low | Encrypted. Ensure TLS 1.2+ only. |
| 445 | SMB | Critical | WannaCry target port. Patch MS17-010. Firewall immediately. |
| 3306 | MySQL | Critical | Bind to 127.0.0.1 only. Never expose externally. |
| 5432 | PostgreSQL | Critical | Same as MySQL. Restrict in pg_hba.conf. |
| 5900 | VNC | Critical | Tunnel over SSH only. Never expose directly. |
| 8080 | HTTP Alt | High | Router admin panel. Change default credentials now. |

---

## Why these two tasks are paired

Weak passwords and open ports are the two most consistently exploited weaknesses in real-world breaches. The Verizon DBIR reports over 80% of breaches involve compromised credentials. Port 445 — found open in the home network scan above — is the exact port WannaCry ransomware used to cause $4 billion in global damage in 2017.

Each defence alone reduces risk significantly. Both together reduce it dramatically. Strong passwords stop brute-force attacks on open ports. Closing unnecessary ports removes the attack surface entirely. You can't defend a system you haven't mapped. You can't protect credentials you haven't evaluated. That's the lesson this week teaches.

---

## Full documentation

For the complete technical write-up — including the full script walkthrough, detailed scan analysis, port risk assessments, security reflection, and all test results — see:

**`VortexTech_Week2_Documentation_AliAmeer.md`** in this repository.

---

## About the author

**Ali Ameer**  
BS Information Technology — GC University Faisalabad (Class of 2025, CGPA 3.5/4.0)  
Cybersecurity Intern — VortexTech (Beginner–Intermediate Track)  
Certifications: Cisco Networking Academy, TCM Security  
Currently pursuing: EC-Council CEH v13  

GitHub: [github.com/ali-ameer](https://github.com/ali-ameer)  
Program contact: vortextechnologies77@gmail.com

---

> Unauthorized port scanning is illegal. Only scan systems you own or have explicit written permission to test. Every scan in this project was performed on personally owned equipment.
