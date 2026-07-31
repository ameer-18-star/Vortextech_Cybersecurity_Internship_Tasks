# VortexTech Cybersecurity Internship — Week 4 (Final)

**Track:** Advanced
**Intern:** Ali Ameer
**Program:** VortexTech Cybersecurity Internship 2026
**Week:** 4 of 4 — Mini Incident Response Plan

---

## What this week was about

The first three weeks were about tools: passwords, ports, scanning, hardening. Week 4 is different. It's not about running a command, it's about thinking like the team that gets paged at 2am when something has already gone wrong.

This week's task was to step into the mindset of a security team responding to a real breach, research how professional incident response actually works, and write a structured, realistic incident response plan for a hypothetical company breach.

Incident response plans aren't written during an incident. They're written before one, tested in drills, and followed calmly when things go wrong instead of being improvised under pressure. That's the skill this week builds.

---

## Repository structure

```
vortextech-cybersec-week4/
│
├── VortexTech_Week4_IncidentResponsePlan_AliAmeer.html   # Task deliverable — full IR plan
├── README.md                                              # This file
```

---

## Task A — Mini Incident Response Plan

### What it does

`VortexTech_Week4_IncidentResponsePlan_AliAmeer.html` is a complete, structured incident response plan built around a hypothetical breach at a fictional company, **Lumora Retail**. The scenario: a customer-data API endpoint was accidentally left exposed without authentication after a staging build was promoted to production, and roughly 120,000 customer records were reachable for six days before an external researcher reported it.

The plan is built around the **NIST SP 800-61 incident response lifecycle**, the six-phase framework most real security teams reference:

1. Preparation — what should already have been in place before the breach
2. Detection & Analysis — how the breach is realistically discovered and triaged
3. Containment — immediate actions to stop it from spreading
4. Eradication — removing the root cause for good
5. Recovery — safely restoring normal operations
6. Post-Incident Activity (Lessons Learned) — what the retrospective changes going forward

It also includes an internal communication plan (who gets notified, and roughly when, from the moment the incident is confirmed) and three preventative measures tied directly to the root cause.

### How to view it

No build step, no dependencies. It's a single self-contained HTML file.

```bash
# Clone the repository
git clone https://github.com/ali-ameer/vortextech-cybersec-week4
cd vortextech-cybersec-week4

# Open directly in any browser
open VortexTech_Week4_IncidentResponsePlan_AliAmeer.html      # macOS
xdg-open VortexTech_Week4_IncidentResponsePlan_AliAmeer.html  # Linux
start VortexTech_Week4_IncidentResponsePlan_AliAmeer.html     # Windows
```

### Scenario summary

| Element | Detail |
|---|---|
| Company | Lumora Retail (fictional mid-size e-commerce retailer) |
| Root cause | Auth middleware disabled in staging, accidentally promoted to production |
| Exposure window | ~6 days |
| Data exposed | Names, emails, phone numbers, shipping addresses, order history, bcrypt password hashes |
| Data **not** exposed | Full payment card numbers (tokenized by third-party processor) |
| How it was discovered | External security researcher's responsible disclosure + internal bandwidth anomaly, roughly simultaneously |
| Severity classification | Critical |

### Communication plan at a glance

| Timeframe | Who is notified |
|---|---|
| T+0–15 min | On-call engineer, IR lead |
| T+30 min | Head of Engineering, CEO |
| T+2 hrs | Legal & compliance |
| T+4–6 hrs | Support & PR teams (internal briefing only) |
| Within 72 hrs | Relevant data protection authority, if legally required |
| Within 3–5 days | Affected customers, directly by email |

### Requirements

```
Any modern browser
No external libraries or dependencies
Renders identically on Windows, Linux, macOS
```

---

## Why this task matters

Weeks 1 through 3 taught detection: weak passwords, open ports, exposed services. Week 4 teaches response: what happens the moment detection turns into an actual incident.

Most breaches aren't stopped by having the perfect tool. They're contained or made worse by whether the team already knew who to call, what to shut down first, and what to say to customers. A password checker or a port scan tells you where the risk lives. An incident response plan tells you what to do the day that risk becomes real.

That's the difference between knowing security concepts and being able to act on them under pressure, which is exactly what this final week of the internship was designed to test.

---

## Full deliverable

For the complete incident response plan, including the full scenario writeup, all six NIST phases mapped to this specific breach, the communication timeline, and preventative measures, see:

**`VortexTech_Week4_IncidentResponsePlan_AliAmeer.html`** in this repository.

---

## About the author

**Ali Ameer**
BS Information Technology — GC University Faisalabad (Class of 2025, CGPA 3.5/4.0)
Cybersecurity Intern — VortexTech (Advanced Track)
Certifications: Cisco Networking Academy, TCM Security
Currently pursuing: EC-Council CEH v13

GitHub: [github.com/ali-ameer](https://github.com/ali-ameer)
Program contact: vortextechnologies77@gmail.com

---

> This is a hypothetical breach scenario written for training purposes as part of the VortexTech internship. No real company, breach, or individual is referenced or implicated.
