# 🔐 Bug Bounty Trainer

> **From Zero to First Bug Bounty Submission** — A structured CLI training system for Kali Linux.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-557C94?logo=linux&logoColor=white)
![Docker](https://img.shields.io/badge/Lab-Docker-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-Paid%20Course-orange)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 🎯 What Is This?

Bug Bounty Trainer is a fully CLI-based hacking mentor system.
It walks you through **5 structured levels**, **25 hands-on tasks** against real local lab targets,
a **no-hint final exam**, and guided steps toward your **first real bug bounty submission**.

No videos. No slides. You learn by doing — in a real terminal, against real vulnerable apps.

```
Level 1 → Recon          WHOIS · DNS · Subdomains · Google Dorks · crt.sh
Level 2 → Scanning       Nmap · Nikto · Gobuster · WhatWeb · Metasploitable2
Level 3 → Web Vulns      XSS · SQLi · IDOR · LFI · Auth Bypass
Level 4 → Exploitation   Burp Suite · sqlmap · Command Injection · Bug Chaining
Level 5 → Reporting      CVSS · Report Writing · Responsible Disclosure
              ↓
         Final Exam       Full simulation on Juice Shop — no hints
              ↓
         Real Bounty      Platforms · Target selection · Submission guide
```

---

## ✨ Features

- **25 guided tasks** across 5 levels — each with description, tool hint, and validator
- **Real lab targets** — DVWA, OWASP Juice Shop, WebGoat (Docker), Metasploitable2 (VM)
- **Offline cryptographic licensing** — keys verified locally, no server required
- **Machine-bound activation** — one license per device, HMAC-protected
- **Progress tracking** — JSON-backed, with badges and scoring
- **Professional report generator** — produces Markdown bug reports
- **Automation scripts** — subdomain enum, directory scan, Nuclei, full recon pipeline
- **Free preview** — Level 1 (Recon) is always free, no key needed
- **Ethics pledge** — mandatory on every launch

---

## 🖥️ Screenshots

> _Screenshots coming soon — run the trainer to see the full CLI experience._

```
  ██████╗ ██╗   ██╗ ██████╗     ██████╗  ██████╗ ██╗   ██╗███╗   ██╗████████╗██╗   ██╗
  ██╔══██╗██║   ██║██╔════╝     ██╔══██╗██╔═══██╗██║   ██║████╗  ██║╚══██╔══╝╚██╗ ██╔╝
  ██████╔╝██║   ██║██║  ███╗    ██████╔╝██║   ██║██║   ██║██╔██╗ ██║   ██║    ╚████╔╝
  ██╔══██╗██║   ██║██║   ██║    ██╔══██╗██║   ██║██║   ██║██║╚██╗██║   ██║     ╚██╔╝
  ██████╔╝╚██████╔╝╚██████╔╝    ██████╔╝╚██████╔╝╚██████╔╝██║ ╚████║   ██║      ██║
  ╚═════╝  ╚═════╝  ╚═════╝     ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝   ╚═╝      ╚═╝
```

---

## 🚀 Quick Start

### Requirements

| Requirement | Version |
|---|---|
| OS | Kali Linux (recommended) / Ubuntu / Debian |
| Python | 3.10+ |
| Docker | Any recent version |

### Install & Run

```bash
# 1. Clone the repository
git clone https://github.com/Ateebshaikh21/bugbountytrainer.git
cd bugbountytrainer

# 2. Run the installer (sets up tools, Docker lab, permissions)
bash install.sh

# 3. Start lab targets
docker-compose up -d

# 4. Launch the trainer
python3 trainer.py
```

On first launch you will see the **activation screen**.
Select **Free Preview** to start Level 1 immediately — no key needed.

---

## 🐳 Lab Targets

| Target | URL | Default Login |
|---|---|---|
| DVWA | http://127.0.0.1:8080 | admin / password |
| OWASP Juice Shop | http://127.0.0.1:3000 | register on first visit |
| WebGoat | http://127.0.0.1:8081/WebGoat | register on first visit |
| Metasploitable2 | 192.168.56.101 | msfadmin / msfadmin (VM only) |

> Full Docker setup instructions: **[SETUP.md](SETUP.md)**

---

## 📁 Project Structure

```
bugbountytrainer/
├── trainer.py                  ← entry point
├── config.py                   ← all constants
├── install.sh                  ← one-shot Kali installer
│
├── core/
│   ├── license.py              ← offline cryptographic license system
│   ├── ui.py                   ← terminal UI engine
│   ├── progress.py             ← JSON progress tracking + badges
│   ├── safety.py               ← ethics pledge banner
│   └── real_bounty_guide.py    ← post-exam real bounty guidance
│
├── levels/
│   ├── base_level.py           ← abstract Task + BaseLevel
│   ├── level_manager.py        ← level router with license gate
│   ├── level1_recon.py         ← 5 recon tasks
│   ├── level2_scanning.py      ← 5 scanning tasks
│   ├── level3_webvulns.py      ← 5 web vulnerability tasks
│   ├── level4_exploitation.py  ← 5 exploitation tasks
│   ├── level5_reporting.py     ← 5 reporting tasks
│   └── final_exam.py           ← 5-phase no-hint exam
│
├── reports/
│   └── report_generator.py     ← professional Markdown report builder
│
├── scripts/
│   ├── subdomain_enum.sh       ← passive + crt.sh subdomain enumeration
│   ├── dir_scan.sh             ← gobuster + sensitive path checks
│   ├── nuclei_scan.sh          ← template-based vulnerability scan
│   └── full_pipeline.sh        ← full recon pipeline + HTML report
│
├── docs/
│   └── setup_guide.py          ← interactive in-app setup guide
│
└── data/                       ← runtime only (gitignored)
```

---

## 🔐 Licensing

This is a **paid course**. Level 1 (Recon) is free — no key needed.
Full access requires a license key purchased via Dodo Payments.

👉 **[Buy Full Access](https://checkout.dodopayments.com/buy/pdt_0NeO8euWOWsLpvSZTH6f8?quantity=1)**

| Tier | Access |
|---|---|
| Free Preview | Level 1 — Recon (5 tasks) |
| Full License | All 5 levels + Final Exam + Bounty Guide + Automation Tools + Report Generator |

- License keys are cryptographically signed (HMAC-SHA256) and verified **fully offline**
- Each key is bound to **one device** on first activation
- No internet required after activation

---

## 🏅 Badges & Scoring

| Badge | Earned by |
|---|---|
| 🩸 First Blood | Complete your first task |
| 🔍 Recon Master | All Level 1 tasks done |
| 📡 Scanner Pro | All Level 2 tasks done |
| 🕸️ Web Hacker | All Level 3 tasks done |
| 💥 Exploiter | All Level 4 tasks done |
| 📝 Reporter | All Level 5 tasks done |
| 💰 Bounty Hunter | Pass the Final Exam |

---

## 🛠️ Tools You Will Use

`whois` · `dig` · `nslookup` · `subfinder` · `amass` · `nmap` · `nikto` · `gobuster`
`sqlmap` · `whatweb` · `Burp Suite` · `nuclei` · `curl` · `dnsrecon` · `theHarvester`

Install all tools at once:

```bash
sudo apt install -y nmap nikto gobuster dirb sqlmap whatweb whois dnsrecon burpsuite wordlists
```

---

## ⚠️ Legal & Ethical Notice

This tool is for **educational use on authorized local lab targets only**.

```
✅  DVWA, Juice Shop, WebGoat, Metasploitable2 — authorized local targets
✅  Bug bounty programs that explicitly list you in scope
❌  Never test real systems without explicit written permission
❌  Unauthorized access violates CFAA, Computer Misuse Act, IT Act, and local law
```

By launching the trainer you agree to the ethical hacking pledge displayed on startup.
The authors accept no liability for misuse.

---

## 👤 Author

**Ateeb Shaikh** — Senior Security Engineer  
Building practical security education for the next generation of bug hunters.

---

## 📄 License

© 2025 Bug Bounty Trainer. All rights reserved.  
This software is provided to licensed buyers only.  
Redistribution, resale, or public sharing of license keys is not permitted.

---

*Stay ethical. Stay curious. Happy hacking! 🎯*
