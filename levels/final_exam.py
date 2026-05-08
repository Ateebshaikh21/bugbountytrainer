"""
levels/final_exam.py — Final Exam: Full Bug Bounty Simulation
No hints. Real workflow. Must find, exploit, and report a vulnerability.
Target: Juice Shop (http://127.0.0.1:3000)
"""

import time


class FinalExam:
    def __init__(self, tracker, ui):
        self.tracker = tracker
        self.ui = ui

    def run(self):
        self.ui.clear()
        self.ui.section("🏁  FINAL EXAM — BUG BOUNTY SIMULATION")

        self.ui.print_color("""
  This is your FINAL EXAM. No hints. No guidance.
  You must complete a full bug bounty workflow from scratch.

  TARGET: OWASP Juice Shop — http://127.0.0.1:3000
  
  Treat this like a real bug bounty scope.
  You have permission to test Juice Shop locally only.
""", "cyan")

        self.ui.print_color("  ⚠️  RULES:\n", "yellow")
        rules = [
            "No hints will be given",
            "You must complete ALL 5 phases",
            "Each phase requires a real answer based on your testing",
            "Passing score: 4 out of 5 phases correct",
            "Your report will be evaluated at the end",
        ]
        for r in rules:
            print(self.ui.color(f"    • {r}", "white"))

        print()
        proceed = self.ui.prompt("Type 'START EXAM' to begin", default="")
        if not proceed or proceed.upper() != "START EXAM":
            self.ui.warn("Exam cancelled.")
            self.ui.pause()
            return

        scores = []

        # Phase 1: Recon
        scores.append(self._phase_recon())
        # Phase 2: Scanning
        scores.append(self._phase_scanning())
        # Phase 3: Vulnerability Discovery
        scores.append(self._phase_vuln_discovery())
        # Phase 4: Exploitation
        scores.append(self._phase_exploitation())
        # Phase 5: Report Writing
        scores.append(self._phase_report())

        # Results
        passed = sum(scores)
        self._show_results(passed, scores)

    def _phase_recon(self):
        self.ui.clear()
        self.ui.section("PHASE 1 / 5 — RECONNAISSANCE")
        self.ui.print_color("""
  Target: http://127.0.0.1:3000 (Juice Shop)
  
  Tasks:
    1. What JavaScript framework does Juice Shop use? (run: whatweb http://127.0.0.1:3000)
    2. Find at least one API endpoint by browsing the app and watching DevTools Network tab.
    3. Check if a robots.txt exists at http://127.0.0.1:3000/robots.txt
""", "white")

        print(self.ui.color("  Answer the following questions:\n", "cyan"))

        q1 = self.ui.prompt("Q1: What JS framework does Juice Shop use?")
        q2 = self.ui.prompt("Q2: One API endpoint you found (e.g., /api/Products)")
        q3 = self.ui.prompt("Q3: Does robots.txt exist? What does it say?")

        score = 0
        if q1 and any(w in q1.lower() for w in ["angular", "node", "react", "js", "express"]):
            score += 1
            self.ui.success("Q1 correct!")
        else:
            self.ui.error("Q1: Juice Shop uses Angular + Node.js.")

        if q2 and ("/" in q2 or "api" in q2.lower()):
            score += 1
            self.ui.success("Q2 correct!")
        else:
            self.ui.error("Q2: Try /api/Products or /rest/user/login")

        if q3 and len(q3) > 3:
            score += 1
            self.ui.success("Q3 answered!")

        time.sleep(1)
        return 1 if score >= 2 else 0

    def _phase_scanning(self):
        self.ui.clear()
        self.ui.section("PHASE 2 / 5 — SCANNING")
        self.ui.print_color("""
  Run a directory brute force against Juice Shop to find hidden paths.
  
  Commands (choose one):
    gobuster dir -u http://127.0.0.1:3000 -w /usr/share/wordlists/dirb/common.txt
    dirsearch -u http://127.0.0.1:3000
    
  Also try: whatweb http://127.0.0.1:3000
  And check: http://127.0.0.1:3000/ftp  (Juice Shop has an exposed FTP directory)
""", "white")

        q1 = self.ui.prompt("Q1: Name ONE hidden path you discovered")
        q2 = self.ui.prompt("Q2: What interesting file/folder did you find at /ftp?")

        score = 0
        if q1 and any(w in q1.lower() for w in
                      ["/ftp", "/api", "/rest", "/administration", "/score-board",
                       "/#/", "hidden", "found", "path", "admin", "login"]):
            score += 1
            self.ui.success("Q1 correct!")

        if q2 and any(w in q2.lower() for w in
                      ["ftp", "file", "pdf", ".md", "acquisitions", "legal",
                       "package", "found", "directory", "list"]):
            score += 1
            self.ui.success("Q2 correct! The /ftp directory is a common Juice Shop finding.")

        time.sleep(1)
        return 1 if score >= 1 else 0

    def _phase_vuln_discovery(self):
        self.ui.clear()
        self.ui.section("PHASE 3 / 5 — VULNERABILITY DISCOVERY")
        self.ui.print_color("""
  Find a vulnerability in Juice Shop. Candidates:
  
    A) XSS: Try payload in search box: <iframe src="javascript:alert(`xss`)">
    B) SQLi: Try login with: ' OR 1=1-- (email field)
    C) IDOR: GET /api/Users/1 with your JWT token
    D) Sensitive data: Check /api/Products for admin-only data leaks
    E) DOM XSS: Check challenge at /#/search?q=<script>alert(1)</script>
  
  Use browser DevTools → Network to observe API calls.
""", "white")

        vuln_type = self.ui.prompt("Q1: What type of vulnerability did you find?")
        endpoint  = self.ui.prompt("Q2: What endpoint/URL was vulnerable?")
        payload   = self.ui.prompt("Q3: What payload or method did you use?")

        score = 0
        valid_vulns = ["xss", "sqli", "sql", "idor", "injection", "traversal",
                       "csrf", "disclosure", "leak", "bypass", "access"]
        if vuln_type and any(w in vuln_type.lower() for w in valid_vulns):
            score += 1

        if endpoint and ("/" in endpoint or "http" in endpoint.lower() or "api" in endpoint.lower()):
            score += 1

        if payload and len(payload) > 3:
            score += 1

        self.ui.success(f"Phase 3: {score}/3 sub-questions answered correctly.")
        time.sleep(1)
        return 1 if score >= 2 else 0

    def _phase_exploitation(self):
        self.ui.clear()
        self.ui.section("PHASE 4 / 5 — EXPLOITATION (PROOF OF CONCEPT)")
        self.ui.print_color("""
  Now PROVE the vulnerability is exploitable.
  
  For the vulnerability you found in Phase 3:
    • Capture the full HTTP request (use Burp Suite or DevTools)
    • Record the server's response
    • Screenshot the successful exploit
  
  Answer these questions based on your PoC:
""", "white")

        http_method = self.ui.prompt("Q1: What HTTP method was used? (GET/POST/PUT/DELETE)")
        response    = self.ui.prompt("Q2: What did the server respond with? (status code or key data)")
        impact      = self.ui.prompt("Q3: In one sentence, what can an attacker do with this?")

        score = 0
        if http_method and any(m in http_method.upper() for m in ["GET", "POST", "PUT", "DELETE", "PATCH"]):
            score += 1
            self.ui.success("Q1 correct!")

        if response and (response.strip().isdigit() or len(response) > 5):
            score += 1
            self.ui.success("Q2 answered!")

        if impact and len(impact) > 15:
            score += 1
            self.ui.success("Q3 answered!")

        time.sleep(1)
        return 1 if score >= 2 else 0

    def _phase_report(self):
        self.ui.clear()
        self.ui.section("PHASE 5 / 5 — WRITE YOUR BUG REPORT")
        self.ui.print_color("""
  Write a professional bug report for the vulnerability you found.
  Answer each field. This will be evaluated for clarity and completeness.
""", "white")

        title    = self.ui.prompt("TITLE: (one clear sentence)")
        summary  = self.ui.prompt("SUMMARY: (2-3 sentences — what, where, why it matters)")
        steps    = self.ui.prompt("STEPS: (brief numbered steps to reproduce)")
        impact   = self.ui.prompt("IMPACT: (what damage could an attacker cause?)")
        severity = self.ui.prompt("SEVERITY: (Critical/High/Medium/Low + reason)")
        fix      = self.ui.prompt("REMEDIATION: (how to fix it)")

        score = 0
        if title and len(title) > 15:
            score += 1
        if summary and len(summary) > 30:
            score += 1
        if steps and len(steps) > 20:
            score += 1
        if impact and len(impact) > 15:
            score += 1
        if severity and any(w in severity.lower() for w in ["critical", "high", "medium", "low"]):
            score += 1
        if fix and len(fix) > 10:
            score += 1

        # Save the report draft
        self._save_exam_report({
            "title": title, "summary": summary, "steps": steps,
            "impact": impact, "severity": severity, "fix": fix
        })

        self.ui.success(f"Report evaluation: {score}/6 fields complete.")
        time.sleep(1)
        return 1 if score >= 4 else 0

    def _save_exam_report(self, data):
        import json, os
        path = os.path.join(os.path.dirname(__file__), "..", "data", "exam_report.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _show_results(self, passed, scores):
        self.ui.clear()
        self.ui.section("🏆  FINAL EXAM RESULTS")

        phases = ["Recon", "Scanning", "Vuln Discovery", "Exploitation", "Report Writing"]
        self.ui.table(
            ["Phase", "Name", "Result"],
            [[str(i+1), phases[i], "✅ PASS" if scores[i] else "❌ FAIL"]
             for i in range(len(scores))]
        )

        self.ui.progress_bar(passed, 5, "Final Score")
        print()

        if passed >= 4:
            self.tracker.pass_exam()
            self.ui.print_color("""
  ╔══════════════════════════════════════════════════════════╗
  ║  🎉  CONGRATULATIONS! YOU PASSED THE FINAL EXAM!        ║
  ║                                                          ║
  ║  You've earned the 💰 Bounty Hunter badge!               ║
  ║  Real Bug Bounty Guidance is now UNLOCKED.               ║
  ║  Go to Main Menu → Real Bug Bounty to start hunting!     ║
  ╚══════════════════════════════════════════════════════════╝
""", "green")
        else:
            self.ui.print_color(f"""
  ╔══════════════════════════════════════════════════════════╗
  ║  ❌  You scored {passed}/5. Need 4/5 to pass.              ║
  ║                                                          ║
  ║  Review the failed phases and try again.                 ║
  ║  Go back to the training levels for more practice.       ║
  ╚══════════════════════════════════════════════════════════╝
""", "red")

        self.ui.pause()
