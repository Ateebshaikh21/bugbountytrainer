"""
core/safety.py — Mandatory ethical/legal safety banner.
Displayed on every launch. Non-negotiable.
"""

import time

SAFETY_BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║                    ⚠️   ETHICAL HACKING PLEDGE  ⚠️                    ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  By using this trainer, you AGREE to:                                ║
║                                                                      ║
║  ✔  ONLY test systems you have WRITTEN PERMISSION to test            ║
║  ✔  NEVER attack production systems without explicit scope           ║
║  ✔  ALWAYS follow responsible disclosure timelines                   ║
║  ✔  REPORT vulnerabilities to the vendor FIRST (not public)          ║
║  ✔  NEVER destroy, alter, or exfiltrate real user data               ║
║  ✔  STOP immediately if you go out of scope                          ║
║                                                                      ║
║  ❌  This tool is for EDUCATION on LOCAL labs only                   ║
║  ❌  Using this on real systems without permission = CRIME            ║
║  ❌  Unauthorized access violates CFAA, IT Act, and local laws        ║
║                                                                      ║
║  LEGAL TARGETS IN THIS TRAINER:                                      ║
║    • DVWA         (http://localhost:8080)                             ║
║    • Juice Shop   (http://localhost:3000)                             ║
║    • WebGoat      (http://localhost:8081/WebGoat)                    ║
║    • Metasploitable2 (192.168.56.101 — isolated VM only)             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

RULES = [
    "Only test authorized targets",
    "Never attack real systems without permission",
    "Follow responsible disclosure",
    "Document everything before reporting",
    "Never cause damage — proof of concept only",
    "Respect scope boundaries at all times",
]


def display_safety_banner():
    """Show safety banner and force acknowledgement."""
    print("\033[93m" + SAFETY_BANNER + "\033[0m")
    time.sleep(0.5)
    try:
        ack = input("\033[91m  Type 'I AGREE' to continue: \033[0m").strip()
        if ack.upper() != "I AGREE":
            print("\033[91m\n  You must agree to the ethical pledge. Exiting.\n\033[0m")
            import sys
            sys.exit(0)
    except (KeyboardInterrupt, EOFError):
        import sys
        sys.exit(0)
    print("\033[92m\n  ✅  Pledge accepted. Welcome to Bug Bounty Trainer!\n\033[0m")
    time.sleep(1)


def safety_reminder():
    """Short inline reminder for display during tasks."""
    return "\033[93m  ⚠️  Remember: Only test authorized targets!\033[0m"
