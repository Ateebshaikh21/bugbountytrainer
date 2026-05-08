#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          BUG BOUNTY TRAINER — by Senior Security Engineer    ║
║          Train → Practice → Hack → Report → Earn             ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ui import UI
from core.progress import ProgressTracker
from core.safety import display_safety_banner
from core.license import authenticate, is_preview_mode, check_level_access, DODO_PURCHASE_URL
from levels.level_manager import LevelManager
from levels.final_exam import FinalExam
from reports.report_generator import ReportGenerator
from core.real_bounty_guide import RealBountyGuide


def main():
    ui = UI()
    ui.clear()

    # ── Step 1: License gate — runs before everything else ───────────────────
    license_data = authenticate(ui)
    preview = is_preview_mode(license_data)

    # ── Step 2: Ethics banner ─────────────────────────────────────────────────
    display_safety_banner()

    # ── Step 3: Init core systems ─────────────────────────────────────────────
    tracker      = ProgressTracker()
    level_manager = LevelManager(tracker, ui, license_data)
    final_exam   = FinalExam(tracker, ui)
    report_gen   = ReportGenerator(ui)
    bounty_guide = RealBountyGuide(ui)

    # ── Step 4: Main loop ─────────────────────────────────────────────────────
    while True:
        ui.clear()
        ui.banner()

        profile = tracker.get_profile()

        # Show license mode in status bar
        license_badge = "🔓 FREE PREVIEW" if preview else f"✅ Licensed: {license_data.get('name', '')}"
        ui.print_status(
            f"Level: {profile['current_level']} | "
            f"Score: {profile['score']} pts | "
            f"Tasks Done: {len(profile['completed_tasks'])} | "
            f"{license_badge}"
        )

        # Build menu — locked items shown differently in preview mode
        lock = "🔒" if preview else "  "
        ui.menu([
            ("1", "Training Levels       (Recon → Report)"),
            ("2", "View My Progress"),
            ("3", f"{lock} Final Exam            (All levels complete)"),
            ("4", f"{lock} Real Bug Bounty       (Post-exam guidance)"),
            ("5", f"{lock} Generate Report       (Professional template)"),
            ("6", "Setup Guide           (Lab environment)"),
            ("7", f"{lock} Automation Tools      (Recon scripts)"),
            ("8", "Upgrade to Full Version" if preview else "License Info"),
            ("0", "Exit"),
        ])

        choice = ui.prompt("Select option")

        if choice == "1":
            level_manager.run()

        elif choice == "2":
            tracker.display_progress(ui)

        elif choice == "3":
            if preview:
                _show_upgrade_prompt(ui, "Final Exam")
            elif profile["current_level"] >= 5 and tracker.all_levels_complete():
                final_exam.run()
            else:
                ui.warn("Complete all 5 levels first before taking the Final Exam.")
                ui.pause()

        elif choice == "4":
            if preview:
                _show_upgrade_prompt(ui, "Real Bug Bounty Guidance")
            elif profile.get("exam_passed"):
                bounty_guide.run()
            else:
                ui.warn("Pass the Final Exam first to unlock Real Bug Bounty Guidance.")
                ui.pause()

        elif choice == "5":
            if preview:
                _show_upgrade_prompt(ui, "Report Generator")
            else:
                report_gen.interactive()

        elif choice == "6":
            from docs.setup_guide import show_setup_guide
            show_setup_guide(ui)

        elif choice == "7":
            if preview:
                _show_upgrade_prompt(ui, "Automation Tools")
            else:
                from scripts.automation_menu import AutomationMenu
                AutomationMenu(ui).run()

        elif choice == "8":
            if preview:
                _show_upgrade_prompt(ui, "full course")
            else:
                _show_license_info(ui, license_data)

        elif choice == "0":
            ui.print_color("\n[*] Stay ethical. Stay curious. Happy hacking!\n", "cyan")
            sys.exit(0)

        else:
            ui.warn("Invalid option. Try again.")
            ui.pause()


def _show_upgrade_prompt(ui, feature_name: str) -> None:
    """Show upgrade prompt when preview user tries to access locked feature."""
    ui.clear()
    ui.print_color(f"""
  ╔══════════════════════════════════════════════════════════════╗
  ║  🔒  {feature_name.upper() + ' IS LOCKED':<57}║
  ╠══════════════════════════════════════════════════════════════╣
  ║                                                              ║
  ║  This feature requires the full version.                     ║
  ║  You're currently in FREE PREVIEW (Level 1 only).            ║
  ║                                                              ║
  ║  Get full access — all 5 levels, exam, bounty guide:         ║""", "yellow")
    ui.print_color(f"  ║  👉  {DODO_PURCHASE_URL:<57}║", "cyan")
    ui.print_color("""  ║                                                              ║
  ║  After purchase → restart trainer → enter license key        ║
  ╚══════════════════════════════════════════════════════════════╝
""", "yellow")
    ui.pause()


def _show_license_info(ui, license_data: dict) -> None:
    """Show current license details for fully licensed users."""
    ui.clear()
    ui.section("🔐  LICENSE INFORMATION")
    ui.print_color(f"""
  Status:       ✅ Active — Full Version
  Name:         {license_data.get('name', 'N/A')}
  Email:        {license_data.get('email', 'N/A')}
  Activated:    {license_data.get('activated_at', 'N/A')[:10]}
  Device:       Bound to this machine ✅
  Version:      {license_data.get('version', '1.0')}
""", "green")
    ui.pause()


if __name__ == "__main__":
    main()
