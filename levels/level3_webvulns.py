"""
levels/level3_webvulns.py — Level 3: Web Vulnerabilities
5 tasks: XSS, SQL Injection, IDOR, Directory Traversal, Authentication Bypass.
Primary target: DVWA (localhost:8080) and Juice Shop (localhost:3000).
"""

import re
from levels.base_level import BaseLevel, Task


class Level3WebVulns(BaseLevel):
    level_num = 3
    level_name = "Web Vulnerabilities"
    concept = """The OWASP Top 10 is your bible. These are the most common critical web bugs.

XSS (Cross-Site Scripting):
  Injecting JavaScript into a page that runs in another user's browser.
  • Reflected XSS: payload in URL, reflected immediately
  • Stored XSS:    payload saved to DB, hits every visitor
  • DOM XSS:       client-side JS processes untrusted data
  Classic payload: <script>alert(1)</script>

SQL INJECTION:
  Manipulating database queries via user input.
  Classic: ' OR '1'='1  |  ' OR 1=1--  |  '; DROP TABLE users;--
  Tool: sqlmap -u "http://target/page?id=1" --dbs

IDOR (Insecure Direct Object Reference):
  Accessing resources by changing an ID in the URL/body.
  Example: /api/users/1337 → change to /api/users/1 → see admin data

DIRECTORY TRAVERSAL / LFI:
  Reading files outside the web root.
  Payload: ../../../../etc/passwd

AUTHENTICATION BYPASS:
  Logging in without valid credentials.
  Techniques: default creds, SQLi login, JWT manipulation, forced browsing

In bug bounty, XSS + SQLi + IDOR are the most commonly rewarded in web programs."""

    tools = ["Burp Suite", "sqlmap", "curl", "browser DevTools", "OWASP ZAP", "Postman"]

    def _build_tasks(self):
        return [
            Task(
                task_id="L3_T1",
                title="Reflected XSS — DVWA",
                description=(
                    "In DVWA, set Security Level to LOW (DVWA Security menu).\n"
                    "Go to: XSS (Reflected) module.\n"
                    "Enter this payload in the 'What's your name?' field:\n"
                    "  <script>alert('XSS')</script>\n"
                    "Did a popup appear? Enter the payload you used."
                ),
                tool_suggestion="Browser — DVWA at http://127.0.0.1:8080/dvwa/vulnerabilities/xss_r/",
                expected_output="The XSS payload that triggered the alert",
                hint="Try: <script>alert(1)</script>  OR  <img src=x onerror=alert(1)>  "
                     "Make sure DVWA security is set to LOW.",
                validator=lambda a: any(w in a.lower() for w in
                    ["<script>", "alert", "onerror", "onload", "xss", "img src",
                     "javascript:", "svg", "prompt", "confirm"]),
                points=150,
            ),
            Task(
                task_id="L3_T2",
                title="SQL Injection — DVWA Login Bypass",
                description=(
                    "Go to DVWA → SQL Injection module (security: LOW).\n"
                    "In the 'User ID' field, enter: ' OR '1'='1\n"
                    "This should dump all user records.\n"
                    "Enter ONE username you found from the SQL injection output."
                ),
                tool_suggestion="DVWA at http://127.0.0.1:8080/dvwa/vulnerabilities/sqli/",
                expected_output="A username revealed by the SQLi (e.g., 'admin', 'gordonb')",
                hint="The payload: ' OR '1'='1  — Note the single quotes. "
                     "DVWA has users: admin, gordonb, 1337, pablo, smithy.",
                validator=lambda a: any(w in a.lower() for w in
                    ["admin", "gordonb", "1337", "pablo", "smithy", "user",
                     "root", "or 1=1", "or '1'='1", "sqli"]),
                points=200,
            ),
            Task(
                task_id="L3_T3",
                title="IDOR — Juice Shop User Profile",
                description=(
                    "In Juice Shop, register an account and log in.\n"
                    "Open DevTools → Network tab.\n"
                    "Go to your profile: http://127.0.0.1:3000/profile\n"
                    "Find the GET request to /api/Users/YOUR_ID\n"
                    "Change the ID to 1 in the URL and see if you get another user's data.\n"
                    "Enter: the HTTP status code you got OR the email in the response."
                ),
                tool_suggestion="Browser DevTools → Network tab, OR Burp Suite Intercept",
                expected_output="HTTP status code (200) or another user's email/data",
                hint="In Juice Shop, user IDs are integers. Try /api/Users/1, /api/Users/2. "
                     "A 200 response = IDOR confirmed. Look for admin@juice-sh.op.",
                validator=lambda a: any(w in a.lower() for w in
                    ["200", "admin", "juice", "idor", "user", "email",
                     "403", "found", "access", "@", "id"]),
                points=200,
            ),
            Task(
                task_id="L3_T4",
                title="Directory Traversal — DVWA File Inclusion",
                description=(
                    "In DVWA → File Inclusion module (security: LOW).\n"
                    "The URL looks like: ?page=include.php\n"
                    "Try replacing with: ?page=../../../../etc/passwd\n"
                    "Did you see the contents of /etc/passwd?\n"
                    "Enter the payload you used OR the first user in /etc/passwd."
                ),
                tool_suggestion="DVWA at http://127.0.0.1:8080/dvwa/vulnerabilities/fi/",
                expected_output="The traversal payload or 'root' (first line of /etc/passwd)",
                hint="URL: http://127.0.0.1:8080/dvwa/vulnerabilities/fi/?page=../../../../etc/passwd  "
                     "The first entry in /etc/passwd is always 'root'.",
                validator=lambda a: any(w in a.lower() for w in
                    ["root", "passwd", "etc", "../../../../", "traversal",
                     "lfi", "bin", "daemon", "/etc", "include"]),
                points=200,
            ),
            Task(
                task_id="L3_T5",
                title="Authentication Bypass — DVWA Login",
                description=(
                    "Try to bypass DVWA's login using SQL injection.\n"
                    "Go to http://127.0.0.1:8080/dvwa/login.php\n"
                    "Username: admin' #\n"
                    "Password: anything\n"
                    "OR try: Username: admin  Password: password\n"
                    "Did you log in? Enter what username you used to bypass auth."
                ),
                tool_suggestion="Browser → DVWA login page",
                expected_output="Username used (e.g., 'admin') or 'bypass' or the SQLi payload",
                hint="Default DVWA credentials: admin / password. "
                     "SQLi bypass: Username = admin'# (the # comments out password check).",
                validator=lambda a: any(w in a.lower() for w in
                    ["admin", "password", "bypass", "login", "sql", "#", "--",
                     "success", "dashboard", "logged"]),
                points=150,
            ),
        ]
