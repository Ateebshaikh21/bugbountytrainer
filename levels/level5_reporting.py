"""
levels/level5_reporting.py — Level 5: Vulnerability Reporting
5 tasks: CVSS scoring, report writing, disclosure, severity rating, PoC quality.
"""

from levels.base_level import BaseLevel, Task


class Level5Reporting(BaseLevel):
    level_num = 5
    level_name = "Reporting & Disclosure"
    concept = """A great hack with a bad report = $0. A decent bug with a great report = $500+.

REPORT ANATOMY:
  1. Title       — Clear, specific, one-line description
  2. Summary     — What is the bug? Why does it matter?
  3. Severity    — CVSS score + business impact
  4. Steps       — Numbered, reproducible steps (with screenshots)
  5. Impact      — What can an attacker DO with this?
  6. PoC         — Actual payload/request/video
  7. Remediation — How to fix it

CVSS v3.1 SCORING:
  Critical: 9.0–10.0 | High: 7.0–8.9 | Medium: 4.0–6.9 | Low: 0.1–3.9
  Calculator: https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator

RESPONSIBLE DISCLOSURE PROCESS:
  1. Find bug → document everything
  2. Report to vendor FIRST (not Twitter, not GitHub)
  3. Give vendor 90 days to fix (Google Project Zero standard)
  4. If no response in 90 days → limited public disclosure
  5. NEVER sell 0-days to gray-market brokers

WRITING TIPS:
  • Assume the triager is NOT a security expert
  • Be specific: "I accessed admin@company.com's order history" not "I found an IDOR"
  • Always include: endpoint, request, response, impact
  • One report per vulnerability
  • Be professional — no bragging, no threats

Platforms pay more for: clear PoC, accurate CVSS, actionable remediation."""

    tools = ["CVSS Calculator", "Burp Suite", "Markdown editor", "ScreenCapture", "HackerOne platform"]

    def _build_tasks(self):
        return [
            Task(
                task_id="L5_T1",
                title="CVSS Scoring — Rate an XSS Bug",
                description=(
                    "Score this bug using CVSS v3.1:\n"
                    "  Bug: Reflected XSS in search box, no auth required,\n"
                    "  requires user to click a crafted link, steals session cookie.\n\n"
                    "Use: https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator\n"
                    "What is the CVSS Base Score? (or enter Medium/High/Critical)"
                ),
                tool_suggestion="https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator",
                expected_output="CVSS score (e.g., '6.1') or severity (Medium/High)",
                hint="Reflected XSS is typically Medium (6.1) — CVSS vector: "
                     "AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
                validator=lambda a: any(w in a.lower() for w in
                    ["6", "7", "8", "medium", "high", "cvss", "score",
                     "critical", "low", "4", "5", "3"]),
                points=150,
            ),
            Task(
                task_id="L5_T2",
                title="Write a Bug Report Title",
                description=(
                    "Write a professional bug report TITLE for this vulnerability:\n"
                    "  You found that changing the 'id' parameter in\n"
                    "  GET /api/v1/orders?id=1234 to another user's ID\n"
                    "  exposes their full order history including payment info.\n\n"
                    "A good title is: [Type] in [Endpoint] allows [Impact].\n"
                    "Enter your bug report title."
                ),
                tool_suggestion="Text editor / your brain",
                expected_output="A clear bug title mentioning IDOR, endpoint, and impact",
                hint="Example format: 'IDOR in /api/v1/orders allows unauthenticated access to "
                     "other users order history and payment information'",
                validator=lambda a: (
                    len(a) > 20 and
                    any(w in a.lower() for w in
                        ["idor", "order", "api", "access", "user", "payment",
                         "insecure", "parameter", "id", "expose", "unauthorized"])
                ),
                points=150,
            ),
            Task(
                task_id="L5_T3",
                title="Impact Statement — Business Risk",
                description=(
                    "Write a 2-sentence impact statement for a Stored XSS bug\n"
                    "in a banking application's transaction notes field.\n\n"
                    "Consider: Who is affected? What can an attacker do?\n"
                    "Enter your 2-sentence impact statement."
                ),
                tool_suggestion="Text editor",
                expected_output="2 sentences explaining who is affected and attacker capability",
                hint="Think: attacker can steal session cookies → account takeover. "
                     "ALL users who view the infected transaction are at risk.",
                validator=lambda a: (
                    len(a) > 30 and
                    any(w in a.lower() for w in
                        ["user", "attacker", "session", "cookie", "account",
                         "steal", "takeover", "execute", "javascript", "victim",
                         "banking", "impact", "financial"])
                ),
                points=150,
            ),
            Task(
                task_id="L5_T4",
                title="Remediation Advice — SQL Injection",
                description=(
                    "A developer asks: 'How do we fix SQL injection in our login page?'\n"
                    "Provide ONE specific, technical remediation recommendation.\n"
                    "Enter your fix recommendation."
                ),
                tool_suggestion="Your security knowledge",
                expected_output="Technical fix recommendation (e.g., 'Use prepared statements')",
                hint="The correct fix is parameterized queries / prepared statements. "
                     "WAFs are NOT a fix — they're a band-aid.",
                validator=lambda a: any(w in a.lower() for w in
                    ["prepared statement", "parameterized", "parameterised", "orm",
                     "bind", "placeholder", "pdo", "stored procedure", "escap",
                     "input validation", "whitelist"]),
                points=150,
            ),
            Task(
                task_id="L5_T5",
                title="Responsible Disclosure Timeline",
                description=(
                    "You found a critical SQL injection on a company's website.\n"
                    "They don't have a bug bounty program or security.txt.\n"
                    "What is the correct first action?\n\n"
                    "Options:\n"
                    "  A) Post on Twitter immediately\n"
                    "  B) Email security@company.com or their contact email\n"
                    "  C) Sell it on exploit marketplaces\n"
                    "  D) Report to CERT/national authority first\n"
                    "Enter the letter of the correct answer."
                ),
                tool_suggestion="Your ethics and legal knowledge",
                expected_output="Letter B (or explanation of responsible disclosure)",
                hint="ALWAYS contact the vendor first. If no security contact, try: "
                     "security@, admin@, or check security.txt at /.well-known/security.txt",
                validator=lambda a: (
                    "b" in a.lower() or
                    any(w in a.lower() for w in
                        ["email", "contact", "vendor", "company", "security@",
                         "responsible", "disclosure", "first", "report to"])
                ),
                points=200,
            ),
        ]
