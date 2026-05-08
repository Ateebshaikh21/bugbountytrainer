"""
core/progress.py — JSON-backed progress tracker for the Bug Bounty Trainer.
"""

import json
import os
from datetime import datetime

PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "progress.json")

DEFAULT_PROFILE = {
    "username": "trainee",
    "current_level": 1,
    "score": 0,
    "completed_tasks": [],
    "level_scores": {
        "1": 0, "2": 0, "3": 0, "4": 0, "5": 0
    },
    "badges": [],
    "exam_passed": False,
    "started_at": None,
    "last_active": None,
    "history": []
}

LEVEL_NAMES = {
    1: "Recon",
    2: "Scanning",
    3: "Web Vulnerabilities",
    4: "Exploitation",
    5: "Reporting",
}

BADGES = {
    "first_blood":    ("🩸 First Blood",    "Completed your very first task"),
    "recon_master":   ("🔍 Recon Master",   "Completed all Level 1 tasks"),
    "scanner_pro":    ("📡 Scanner Pro",    "Completed all Level 2 tasks"),
    "web_hacker":     ("🕸️  Web Hacker",    "Completed all Level 3 tasks"),
    "exploiter":      ("💥 Exploiter",      "Completed all Level 4 tasks"),
    "reporter":       ("📝 Reporter",       "Completed all Level 5 tasks"),
    "bounty_hunter":  ("💰 Bounty Hunter",  "Passed the Final Exam"),
}

TASKS_PER_LEVEL = 5


class ProgressTracker:
    def __init__(self):
        os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
        self.profile = self._load()

    def _load(self):
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE) as f:
                    data = json.load(f)
                # merge missing keys from default
                for k, v in DEFAULT_PROFILE.items():
                    if k not in data:
                        data[k] = v
                return data
            except Exception:
                pass
        profile = DEFAULT_PROFILE.copy()
        profile["started_at"] = datetime.now().isoformat()
        self._save(profile)
        return profile

    def _save(self, profile=None):
        if profile is None:
            profile = self.profile
        profile["last_active"] = datetime.now().isoformat()
        with open(PROGRESS_FILE, "w") as f:
            json.dump(profile, f, indent=2)

    def get_profile(self):
        return self.profile

    def set_username(self, name):
        self.profile["username"] = name
        self._save()

    def complete_task(self, task_id: str, level: int, points: int):
        if task_id in self.profile["completed_tasks"]:
            return False  # already done

        self.profile["completed_tasks"].append(task_id)
        self.profile["score"] += points
        self.profile["level_scores"][str(level)] = \
            self.profile["level_scores"].get(str(level), 0) + points
        self.profile["history"].append({
            "task": task_id,
            "level": level,
            "points": points,
            "time": datetime.now().isoformat()
        })

        # Badge: first task ever
        if len(self.profile["completed_tasks"]) == 1:
            self._award_badge("first_blood")

        # Badge: level completion
        level_tasks = [t for t in self.profile["completed_tasks"]
                       if t.startswith(f"L{level}_")]
        if len(level_tasks) >= TASKS_PER_LEVEL:
            badge_map = {1: "recon_master", 2: "scanner_pro",
                         3: "web_hacker", 4: "exploiter", 5: "reporter"}
            self._award_badge(badge_map.get(level, ""))
            # Unlock next level
            if level < 5 and self.profile["current_level"] == level:
                self.profile["current_level"] = level + 1

        self._save()
        return True

    def is_task_done(self, task_id: str):
        return task_id in self.profile["completed_tasks"]

    def all_levels_complete(self):
        for lvl in range(1, 6):
            done = [t for t in self.profile["completed_tasks"]
                    if t.startswith(f"L{lvl}_")]
            if len(done) < TASKS_PER_LEVEL:
                return False
        return True

    def pass_exam(self):
        self.profile["exam_passed"] = True
        self._award_badge("bounty_hunter")
        self._save()

    def _award_badge(self, badge_key):
        if badge_key and badge_key not in self.profile["badges"]:
            self.profile["badges"].append(badge_key)

    def display_progress(self, ui):
        ui.clear()
        ui.section(f"📊  PROGRESS REPORT — {self.profile['username'].upper()}")

        # Overall bar
        total_tasks = 5 * 5
        done = len(self.profile["completed_tasks"])
        ui.progress_bar(done, total_tasks, "Overall Progress")
        print()

        # Per-level table
        headers = ["Level", "Name", "Tasks Done", "Score", "Status"]
        rows = []
        for lvl in range(1, 6):
            done_count = len([t for t in self.profile["completed_tasks"]
                              if t.startswith(f"L{lvl}_")])
            status = "✅ Complete" if done_count >= 5 else (
                "🔓 Unlocked" if lvl <= self.profile["current_level"] else "🔒 Locked")
            rows.append([
                f"Level {lvl}",
                LEVEL_NAMES[lvl],
                f"{done_count}/5",
                self.profile["level_scores"].get(str(lvl), 0),
                status,
            ])
        ui.table(headers, rows)

        # Badges
        ui.print_color("  🏅  BADGES EARNED:", "yellow")
        if self.profile["badges"]:
            for b in self.profile["badges"]:
                info = BADGES.get(b, (b, ""))
                print(f"    {info[0]}  —  {info[1]}")
        else:
            ui.info("No badges yet. Complete your first task!")

        print()
        ui.print_color(f"  💰  TOTAL SCORE: {self.profile['score']} pts", "green")
        ui.print_color(f"  🎯  EXAM PASSED: {'Yes ✅' if self.profile['exam_passed'] else 'No ❌'}", "cyan")
        print()
        ui.pause()
