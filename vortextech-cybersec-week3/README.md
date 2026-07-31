# OWASP Juice Shop — Web Application Security Assessment

**Track:** Web Application Penetration Testing
**Intern:** [Your Name]
**Program:** [Your Program / Course Name]
**Focus:** Hands-On OWASP Top 10 Exploitation & Reporting

---

## What this project was about

Reading about SQL injection and reading the results of a working SQL injection are two different skill levels. This project closes that gap. Everything here was run against a real, locally-hosted application — OWASP Juice Shop — using the same tools and methodology a professional AppSec assessment would use: an intercepting proxy, automated injection tooling, offline hash cracking, and a JWT manipulation workflow.

Juice Shop isn't a toy. Its vulnerabilities are deliberately built to mirror real production bugs — the same broken access control pattern here is the same class of bug behind real IDOR breaches; the same MD5 password hashing here is the same mistake behind real credential-stuffing campaigns. Practicing against it in a safe, legal, self-hosted environment is the right way to build this skill before touching anything with real stakes.

---

## Repository structure

```
├── db
│   ├── Cards.csv
│   └── Users.csv
├── img
│   ├── broken-add-request-altered.png ......
│   └── xss-dom-score.png
├── recon
│   ├── api_endpoints.txt
│   ├── ffuf.txt
│   └── whatweb.txt
├── reports
│   ├── Juice-Shop-Security-Assessment-Report.html
│   ├── OWASP-Top-10-Internship-Assessment-Report.html
│   ├── OWASP-Top-10-Internship-Assessment-Report.md
│   └── OWASP_JuiceShop_Security_Assessment_Report.pdf
├── screenshots
│   ├── 01-homepage.jpg
│   ├── IMG_20260722_092244_432.jpg .....
│   └── IMG_20260722_092435_632.jpg
├── scripts
│   └── idor_scan.sh
└── README.md
lists
```

---

## What was tested

Eleven findings were identified, exploited, and documented across the following classes:

| # | Finding | CWE | Severity |
|---|---|---|---|
| 1 | Directory Listing Exposure | CWE-538 | High |
| 2 | Sensitive Info Disclosure (client JS) | CWE-922 | Medium |
| 3 | SQL Injection — Auth Bypass | CWE-89 | Critical |
| 4 | SQL Injection — Data Exfiltration | CWE-89 | Critical |
| 5 | Weak Password Hashing (MD5) | CWE-328 | Critical |
| 6 | CSRF — Password Change | CWE-352 | High |
| 7 | DOM-Based XSS — Search | CWE-79 | Medium |
| 8 | Broken Access Control — Basket | CWE-284 | High |
| 9 | Improper Input Validation — Quantity | CWE-20 | Medium |
| 10 | File Upload Restriction Bypass | CWE-434 | High |
| 11 | Insecure JWT Design | CWE-347 | High |

Full write-up for each — root cause, exploitation steps, CVSS scoring, and remediation — lives in `report.html`.

---

## Tools used

| Category | Tools |
|---|---|
| Proxy / request manipulation | Burp Suite Community Edition |
| Automated injection testing | SQLMap |
| JWT analysis | JWT Editor (Burp Extension), jwt.io |
| Offline hash cracking | CrackStation, Hashcat |
| Recon / enumeration | FFUF, cURL, WhatWeb |
| Environment | Docker, Kali Linux |

### How to reproduce the environment

```bash
# Pull and run Juice Shop locally
docker run --rm -p 127.0.0.1:3000:3000 bkimminich/juice-shop

# Confirm it's up
curl -i http://localhost:3000
```

No target outside this local container was ever touched.

---

## Why these findings are grouped together

Every finding here traces back to one of two root causes: **the server trusting something it shouldn't** (a client-supplied ID, an unsigned token, an un-validated quantity) or **a missing server-side check that only existed client-side** (file type, file size, current-password verification). That's not a coincidence — it's the single most common failure pattern behind real-world breaches, which is exactly why Juice Shop is built to teach it.

Fixing input validation without fixing access control still leaves accounts exposed. Fixing access control without fixing weak password hashing still leaves a breached database fully crackable. The findings reinforce each other, and the report treats them that way — as one coherent picture of how a handful of missing checks compound into full compromise.

---

## Full documentation

For the complete technical assessment — exploitation walkthroughs, CVSS breakdowns, and remediation guidance for every finding — see:

**[`report.html`](./Juice-Shop-Security-Assessment-Report.html)**

---

## About the author

**[Your Name]**
[Your Degree / Program] — [Your Institution]
[Your Role/Track], [Your Program Name]
Certifications: [list if any]
Currently pursuing: [if applicable]

GitHub: [your-github-url]
Contact: [your-email]

---

> All testing in this repository was performed exclusively against a personally deployed, local OWASP Juice Shop instance — an application intentionally built to be vulnerable for training purposes. No unauthorized or production systems were tested.
