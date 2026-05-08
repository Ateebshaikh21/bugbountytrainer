"""
levels/level_manager.py — Routes the user through all 5 training levels.
Enforces license gate: Level 1 free, Levels 2-5 require full license.
"""

from levels.level1_recon import Level1Recon
from levels.level2_scanning import Level2Scanning
from levels.level3_webvulns import Level3WebVulns
from levels.level4_exploitation import Level4Exploitation
from levels.level5_reporting import Level5Reporting
from core.license import check_level_access, is_preview_mode, DODO_PURCHASE_URL


class LevelManager:
    def __init__(self, tracker, ui, license_data=None):
        self.tracker = tracker
        self.ui = ui
        self.license_data = license_data or {"preview": True}
        self.preview = is_preview_mode(self.license_data)
        self.levels = {
            1: Level1Recon(tracker, ui),
            2: Level2Scanning(tracker, ui),
            3: Level3WebVulns(tracker, ui),
            4: Level4Exploitation(tracker, ui),
            5: Level5Reporting(tracker, ui),
        }

    def run(self):
        while True:
            self.ui.clear()
            profile = self.tracker.get_profile()
            current = profile["current_level"]

            self.ui.section("🎓  TRAINING LEVELS")

            # Show preview notice if applicable
            if self.preview:
                self.ui.print_color(
                    f"  ℹ️  FREE PREVIEW MODE — Level 1 free. "
                    f"Upgrade: {DODO_PURCHASE_URL}\n", "yellow"
                )

            level_info = [
                (1, "Recon",              "OSINT, DNS, subdomains, Google dorks"),
                (2, "Scanning",           "Nmap, Nikto, directory brute force"),
                (3, "Web Vulnerabilities","XSS, SQLi, IDOR, CSRF, LFI"),
                (4, "Exploitation",       "Burp Suite, auth bypass, chaining bugs"),
                (5, "Reporting",          "CVSS, templates, responsible disclosure"),
            ]

            headers = ["#", "Level", "Topics", "Status"]
            rows = []
            for num, name, topics in level_info:
                done = len([t for t in profile["completed_tasks"]
                            if t.startswith(f"L{num}_")])
                if self.preview and num > 1:
                    status = "🔒 Locked — Upgrade"
                elif done >= 5:
                    status = "✅ Done"
                elif num <= current:
                    status = "🔓 Open"
                else:
                    status = "🔒 Locked"
                rows.append([str(num), name, topics, status])
            self.ui.table(headers, rows)

            self.ui.menu([
                *[(str(i), f"Enter Level {i}") for i in range(1, 6)],
                ("0", "Back to Main Menu"),
            ])

            choice = self.ui.prompt("Select level")
            if choice == "0" or choice is None:
                return

            try:
                lvl_num = int(choice)
                if lvl_num < 1 or lvl_num > 5:
                    raise ValueError
            except ValueError:
                self.ui.warn("Enter a number 1–5.")
                self.ui.pause()
                continue

            # License gate check — blocks levels 2-5 in preview mode
            if not check_level_access(lvl_num, self.license_data, self.ui):
                continue

            # Progress gate check — must complete previous level first
            if lvl_num > current:
                self.ui.warn(f"Level {lvl_num} is locked. Complete Level {lvl_num - 1} first.")
                self.ui.pause()
                continue

            self.levels[lvl_num].run()
