"""
core/real_bounty_guide.py — Real Bug Bounty Guidance (unlocked after final exam).
Covers platforms, target selection, pre-test checklist, and first submission advice.
"""


class RealBountyGuide:
    def __init__(self, ui):
        self.ui = ui

    def run(self):
        while True:
            self.ui.clear()
            self.ui.section("💰  REAL BUG BOUNTY GUIDANCE")
            self.ui.print_color("""
  Congratulations on completing the training! You're now ready to hunt real bugs.
  This section gives you a structured path to your FIRST successful submission.
""", "cyan")

            self.ui.menu([
                ("1", "Platforms — HackerOne & Bugcrowd"),
                ("2", "Target Selection Strategy"),
                ("3", "Pre-Test Checklist"),
                ("4", "First Target Types"),
                ("5", "Submission Best Practices"),
                ("0", "Back"),
            ])

            choice = self.ui.prompt("Select section")
            if choice == "0" or choice is None:
                return
            elif choice == "1":
                self._platforms()
            elif choice == "2":
                self._target_selection()
            elif choice == "3":
                self._pretesting_checklist()
            elif choice == "4":
                self._first_target_types()
            elif choice == "5":
                self._submission_tips()

    def _platforms(self):
        self.ui.clear()
        self.ui.section("🌐  BUG BOUNTY PLATFORMS")
        self.ui.print_color("""
  ┌─── HACKERONE (hackerone.com) ─────────────────────────────────────┐
  │                                                                    │
  │  • Largest bug bounty platform (2000+ programs)                    │
  │  • Has both PUBLIC (anyone can join) and PRIVATE (invite-only)     │
  │  • Reputation system: higher rep = more private program invites    │
  │  • Beginner tip: Filter by "Bounty" + "Accepting" + "Web"         │
  │  • Programs to start with: look for programs with "All Assets"     │
  │    scope or small SaaS companies                                   │
  │  • URL: https://hackerone.com/programs                             │
  │                                                                    │
  └────────────────────────────────────────────────────────────────────┘

  ┌─── BUGCROWD (bugcrowd.com) ────────────────────────────────────────┐
  │                                                                    │
  │  • Strong for vulnerability disclosure programs                    │
  │  • Beginner-friendly UI and triage support                         │
  │  • VRT (Vulnerability Rating Taxonomy) helps you rate bugs        │
  │  • Many managed programs with active triagers                      │
  │  • URL: https://bugcrowd.com/programs                              │
  │                                                                    │
  └────────────────────────────────────────────────────────────────────┘

  ┌─── OTHER PLATFORMS ────────────────────────────────────────────────┐
  │                                                                    │
  │  • Intigriti (intigriti.com)    — Europe-focused, growing fast    │
  │  • Synack (synack.com)          — Vetted, pays well, competitive  │
  │  • YesWeHack (yeswehack.com)    — Europe + global                 │
  │  • Open Bug Bounty              — Free responsible disclosure      │
  │  • Self-run programs            — Company's own security page      │
  │                                                                    │
  └────────────────────────────────────────────────────────────────────┘
""", "white")
        self.ui.pause()

    def _target_selection(self):
        self.ui.clear()
        self.ui.section("🎯  TARGET SELECTION STRATEGY")
        self.ui.print_color("""
  FILTER CRITERIA FOR BEGINNERS:
  ══════════════════════════════

  1. PROGRAM AGE: Choose newer programs (launched < 6 months ago)
     → Less tested = more low-hanging fruit
     → HackerOne shows launch date on each program

  2. RESPONSE EFFICIENCY: Filter for programs with:
     → "Response Efficiency: 80%+" 
     → "Time to First Response: < 1 week"
     → Nobody wants to wait months for triage

  3. SCOPE TYPE: Prefer "Web" and "API" scope
     → Avoid mobile-only programs until you're experienced
     → "*.company.com" wide scopes = more attack surface

  4. BOUNTY RANGE: Don't just chase max bounty
     → Programs with $50–$500 range have less competition
     → Volume matters when starting out

  5. TECHNOLOGY STACK: Match your skills
     → You know PHP? Find PHP-based programs
     → You know JavaScript? Find Node/React apps

  COMPETITION ASSESSMENT:
  ═══════════════════════

  LOW competition indicators:
    ✓ Program launched recently
    ✓ Small company / startup
    ✓ Non-English primary market (localized apps)
    ✓ Niche B2B SaaS (not consumer apps)
    ✓ API-first companies (often miss API security)

  HIGH competition (avoid at first):
    ✗ Google, Apple, Meta, Microsoft programs
    ✗ Programs with 1000+ reports already submitted
    ✗ Crypto/blockchain programs (very crowded)
""", "white")
        self.ui.pause()

    def _pretesting_checklist(self):
        self.ui.clear()
        self.ui.section("✅  PRE-TESTING CHECKLIST")
        self.ui.print_color("""
  BEFORE SENDING A SINGLE REQUEST — RUN THIS CHECKLIST:
  ══════════════════════════════════════════════════════

  SCOPE REVIEW:
  ☐ Read the ENTIRE program policy page (not just the scope table)
  ☐ Identify in-scope domains/IPs/apps explicitly listed
  ☐ Note out-of-scope items (3rd-party services, payment pages, etc.)
  ☐ Check if subdomains are included ("*.company.com" means all subs)
  ☐ Confirm testing type allowed (black-box only? authenticated?)

  RULES OF ENGAGEMENT:
  ☐ No automated scanning unless explicitly allowed
  ☐ No DDoS / load testing
  ☐ No social engineering employees
  ☐ No physical attacks
  ☐ No accessing real user data (use test accounts)
  ☐ No modifying or deleting any data
  ☐ Create a dedicated test account (not your real account)

  DOCUMENTATION:
  ☐ Set up screen recording (OBS Studio / SimpleScreenRecorder)
  ☐ Configure Burp Suite to save request/response logs
  ☐ Create a folder for this target (screenshots, notes, requests)
  ☐ Note the date/time you start testing

  LEGAL:
  ☐ Program is currently ACTIVE (not paused)
  ☐ You meet age requirements (18+ for most programs)
  ☐ Your country is not in the restricted list
  ☐ You agree to the platform's terms of service

  TOOLS READY:
  ☐ Burp Suite running with browser proxied
  ☐ Wordlists available (/usr/share/wordlists/dirb/common.txt)
  ☐ Notes file open and ready
""", "white")
        self.ui.pause()

    def _first_target_types(self):
        self.ui.clear()
        self.ui.section("🎯  IDEAL FIRST TARGET TYPES")
        self.ui.print_color("""
  THE BEST FIRST TARGETS FOR BEGINNERS:
  ═══════════════════════════════════════

  1. SMALL SaaS PLATFORMS (BEST FOR BEGINNERS)
     ─────────────────────────────────────────
     • B2B tools: project management, HR systems, CRM software
     • Often built by small teams with limited security budget
     • Typical vulns: IDOR in user/account IDs, XSS in rich text editors,
       missing authorization on API endpoints
     • Why: Less researcher competition, faster triage, friendlier teams

  2. STAGING / DEMO ENVIRONMENTS
     ─────────────────────────────────────────
     • Some programs explicitly allow testing staging.company.com
     • Less monitored = safer to test more actively
     • Often have the same code as production
     • Check scope carefully — it must be explicitly listed

  3. REST / GraphQL APIs
     ─────────────────────────────────────────
     • Many web apps have public APIs with poor access control
     • Look for: IDOR, mass assignment, missing auth on endpoints
     • Use Postman or Burp to manually test every API endpoint
     • GraphQL introspection leaks full API schema — try it!
     • Target: /api/v1/*, /rest/*, /graphql

  4. MOBILE APP BACKENDS (WEB PORTION)
     ─────────────────────────────────────────
     • Mobile apps call REST APIs — test those APIs, not the app itself
     • Decompile APK (jadx) to find hardcoded API endpoints
     • Often miss server-side validation

  5. OPEN SOURCE PRODUCTS
     ─────────────────────────────────────────
     • Read the source code (GitHub)
     • Find vuln patterns in code → test them on the target instance
     • Example: WordPress plugins, open-source CMS, Joomla extensions

  WHAT TO LOOK FOR FIRST:
  ========================
  ✓ IDOR          — Change ID numbers in API calls
  ✓ Auth bypass   — Access pages without login (forced browsing)
  ✓ XSS           — Text fields, URL params, JSON responses
  ✓ Info disclosure — Error messages, verbose stack traces, debug endpoints
  ✓ Default creds  — admin/admin, admin/password on admin panels
""", "white")
        self.ui.pause()

    def _submission_tips(self):
        self.ui.clear()
        self.ui.section("📤  SUBMISSION BEST PRACTICES")
        self.ui.print_color("""
  HOW TO SUBMIT A WINNING REPORT:
  ════════════════════════════════

  BEFORE SUBMITTING:
  ☐ Test the bug THREE times to ensure it's reproducible
  ☐ Test in an incognito/private window with a fresh test account
  ☐ Have screenshots/screen recording of the entire exploit
  ☐ Copy the full HTTP request and response from Burp

  TITLE FORMULA:
  [Vulnerability Type] in [Endpoint/Feature] allows [Impact]
  
  Example: "IDOR in /api/v1/invoices/{id} allows any authenticated user
            to read other users' invoices"

  REPORT QUALITY TIPS:
  ✓ Number your reproduction steps clearly (1, 2, 3...)
  ✓ Include the exact payload or request
  ✓ Show BEFORE and AFTER screenshots
  ✓ Explain the BUSINESS impact, not just the technical bug
  ✓ Suggest a fix (shows professionalism)
  ✓ One vulnerability per report

  SEVERITY CALIBRATION:
  Don't over-inflate severity — triagers hate that and it damages your rep.
    Critical: RCE, Auth bypass to admin, Mass account takeover
    High:     SQLi with data dump, Stored XSS, Privilege escalation
    Medium:   Reflected XSS, IDOR (limited data), CSRF
    Low:      Info disclosure (non-sensitive), Self-XSS
    Info:     Best practice issues, missing headers (minor)

  AFTER SUBMITTING:
  ☐ Be patient — triage takes 1–30 days typically
  ☐ Respond quickly to triager questions
  ☐ If marked "Informative" or "N/A", ask politely for clarification
  ☐ Never threaten or harass — it gets you banned
  ☐ Keep a spreadsheet of all your submitted reports
""", "white")
        self.ui.pause()
