"""
levels/level2_scanning.py — Level 2: Scanning & Enumeration
5 tasks covering Nmap, Nikto, Gobuster, service detection.
Target: DVWA at localhost:8080 and local network lab.
"""

from levels.base_level import BaseLevel, Task


class Level2Scanning(BaseLevel):
    level_num = 2
    level_name = "Scanning & Enumeration"
    concept = """After recon, we move to active scanning — directly probing the target.

PORT SCANNING with Nmap:
Nmap is the Swiss Army knife of scanning. It finds open ports, services, and OS versions.
  • nmap -sV target       — Service version detection
  • nmap -sC target       — Default scripts (safe)
  • nmap -A target        — Aggressive (OS, version, scripts, traceroute)
  • nmap -p- target       — All 65535 ports

WEB SCANNING with Nikto:
Nikto checks web servers for misconfigurations, default files, and known vulnerabilities.
  • nikto -h http://target

DIRECTORY BRUTE FORCE with Gobuster/Dirsearch:
Hidden directories often contain admin panels, backups, config files.
  • gobuster dir -u http://target -w /usr/share/wordlists/dirb/common.txt
  • dirsearch -u http://target

In bug bounty, always enumerate EVERYTHING. Hidden endpoints = hidden bugs.

⚠️  WARNING: Only scan your LOCAL lab targets (DVWA, Juice Shop, Metasploitable2)."""

    tools = ["nmap", "nikto", "gobuster", "dirsearch", "whatweb", "wapiti"]

    def _build_tasks(self):
        return [
            Task(
                task_id="L2_T1",
                title="Nmap — Port Scan DVWA",
                description=(
                    "Run Nmap against your DVWA Docker container at 127.0.0.1 port 8080. "
                    "Command: nmap -sV -p 8080 127.0.0.1\n"
                    "What service/version is running on port 8080?"
                ),
                tool_suggestion="nmap -sV -p 8080 127.0.0.1",
                expected_output="Service name running on 8080 (e.g., 'Apache httpd', 'nginx')",
                hint="Look for the 'SERVICE' and 'VERSION' columns in nmap output.",
                validator=lambda a: any(w in a.lower() for w in
                    ["apache", "nginx", "http", "php", "open", "80", "web", "lighttpd"]),
                points=100,
            ),
            Task(
                task_id="L2_T2",
                title="Nikto — Web Vulnerability Scan",
                description=(
                    "Run Nikto against DVWA to find web misconfigurations. "
                    "Command: nikto -h http://127.0.0.1:8080\n"
                    "What is ONE finding Nikto reported? (e.g., X-Frame-Options missing)"
                ),
                tool_suggestion="nikto -h http://127.0.0.1:8080",
                expected_output="One Nikto finding (e.g., 'X-Frame-Options header missing')",
                hint="Nikto lists findings with '+' prefix. Look for header issues, default files, or known CVEs.",
                validator=lambda a: any(w in a.lower() for w in
                    ["x-frame", "header", "cookie", "clickjack", "csrf", "php", "osvdb",
                     "server", "index", "login", "default", "nikto", "found", "missing",
                     "content-security", "cross", "options"]),
                points=150,
            ),
            Task(
                task_id="L2_T3",
                title="Directory Brute Force — Gobuster",
                description=(
                    "Find hidden directories on DVWA using Gobuster. "
                    "Command: gobuster dir -u http://127.0.0.1:8080 -w /usr/share/wordlists/dirb/common.txt\n"
                    "Enter ONE directory you found (e.g., /admin, /dvwa, /login)"
                ),
                tool_suggestion="gobuster dir -u http://127.0.0.1:8080 -w /usr/share/wordlists/dirb/common.txt",
                expected_output="A directory path found (e.g., '/dvwa' or '/setup')",
                hint="Status 200 or 301 means the directory exists. Look for /dvwa, /docs, /config, /setup.",
                validator=lambda a: (
                    a.strip().startswith("/") or
                    any(w in a.lower() for w in
                        ["dvwa", "admin", "login", "setup", "config", "docs",
                         "php", "test", "install", "includes", "external"])
                ),
                points=150,
            ),
            Task(
                task_id="L2_T4",
                title="Service Fingerprinting — WhatWeb",
                description=(
                    "Use WhatWeb to fingerprint the Juice Shop technology stack. "
                    "Command: whatweb http://127.0.0.1:3000\n"
                    "What JavaScript framework does Juice Shop use?"
                ),
                tool_suggestion="whatweb http://127.0.0.1:3000",
                expected_output="Framework name (e.g., 'Angular', 'React', 'Express')",
                hint="OWASP Juice Shop is built on Angular + Node.js + Express. WhatWeb should detect these.",
                validator=lambda a: any(w in a.lower() for w in
                    ["angular", "node", "express", "javascript", "js", "react",
                     "bootstrap", "jquery", "typescript", "ionic", "spa"]),
                points=100,
            ),
            Task(
                task_id="L2_T5",
                title="Full Port Scan — Metasploitable2",
                description=(
                    "Scan Metasploitable2 (usually 192.168.56.101) for ALL open ports. "
                    "Command: nmap -sV --open 192.168.56.101\n"
                    "How many open ports did you find? (enter the count OR a port number)"
                ),
                tool_suggestion="nmap -sV --open 192.168.56.101",
                expected_output="Number of open ports (e.g., '23') or a specific port like '21'",
                hint="Metasploitable2 is intentionally vulnerable — it has MANY open ports (20+). "
                     "If it's not reachable, answer with how many ports a typical Metasploitable2 has.",
                validator=lambda a: (
                    a.strip().isdigit() or
                    any(w in a.lower() for w in
                        ["21", "22", "23", "25", "80", "139", "445", "3306",
                         "ftp", "ssh", "telnet", "smtp", "http", "smb", "mysql"])
                ),
                points=200,
            ),
        ]
