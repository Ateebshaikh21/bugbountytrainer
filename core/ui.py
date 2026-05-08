"""
core/ui.py — Terminal UI engine with colors, menus, and formatting.
"""

import os
import time
import textwrap


COLORS = {
    "red":     "\033[91m",
    "green":   "\033[92m",
    "yellow":  "\033[93m",
    "blue":    "\033[94m",
    "magenta": "\033[95m",
    "cyan":    "\033[96m",
    "white":   "\033[97m",
    "bold":    "\033[1m",
    "dim":     "\033[2m",
    "reset":   "\033[0m",
}

BANNER_ART = r"""
  ██████╗ ██╗   ██╗ ██████╗     ██████╗  ██████╗ ██╗   ██╗███╗   ██╗████████╗██╗   ██╗
  ██╔══██╗██║   ██║██╔════╝     ██╔══██╗██╔═══██╗██║   ██║████╗  ██║╚══██╔══╝╚██╗ ██╔╝
  ██████╔╝██║   ██║██║  ███╗    ██████╔╝██║   ██║██║   ██║██╔██╗ ██║   ██║    ╚████╔╝ 
  ██╔══██╗██║   ██║██║   ██║    ██╔══██╗██║   ██║██║   ██║██║╚██╗██║   ██║     ╚██╔╝  
  ██████╔╝╚██████╔╝╚██████╔╝    ██████╔╝╚██████╔╝╚██████╔╝██║ ╚████║   ██║      ██║   
  ╚═════╝  ╚═════╝  ╚═════╝     ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝   ╚═╝      ╚═╝  
  ████████╗██████╗  █████╗ ██╗███╗   ██╗███████╗██████╗                                
  ╚══██╔══╝██╔══██╗██╔══██╗██║████╗  ██║██╔════╝██╔══██╗                               
     ██║   ██████╔╝███████║██║██╔██╗ ██║█████╗  ██████╔╝                               
     ██║   ██╔══██╗██╔══██║██║██║╚██╗██║██╔══╝  ██╔══██╗                               
     ██║   ██║  ██║██║  ██║██║██║ ╚████║███████╗██║  ██║                               
     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝  v1.0 by Senior SecEng
"""


class UI:
    def clear(self):
        os.system("clear" if os.name == "posix" else "cls")

    def color(self, text, color="white"):
        return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"

    def print_color(self, text, color="white"):
        print(self.color(text, color))

    def banner(self):
        print(self.color(BANNER_ART, "cyan"))

    def print_status(self, text):
        bar = "─" * 70
        print(self.color(bar, "blue"))
        print(self.color(f"  ▶  {text}", "yellow"))
        print(self.color(bar, "blue"))
        print()

    def menu(self, options):
        print(self.color("┌─── MAIN MENU " + "─" * 55, "blue"))
        for key, label in options:
            if key == "0":
                print(self.color(f"│  [{key}] {label}", "dim"))
            else:
                print(self.color(f"│  [{key}] ", "cyan") + self.color(label, "white"))
        print(self.color("└" + "─" * 68, "blue"))
        print()

    def section(self, title):
        print()
        print(self.color("═" * 70, "magenta"))
        print(self.color(f"  {title}", "magenta"))
        print(self.color("═" * 70, "magenta"))
        print()

    def task_box(self, title, content, color="cyan"):
        width = 68
        print(self.color("┌" + "─" * width + "┐", color))
        print(self.color(f"│  {title:<{width-2}}│", color))
        print(self.color("├" + "─" * width + "┤", color))
        for line in textwrap.wrap(content, width - 4):
            print(self.color(f"│  {line:<{width-2}}│", "white"))
        print(self.color("└" + "─" * width + "┘", color))
        print()

    def hint_box(self, hint):
        print(self.color("  💡 HINT: ", "yellow") + self.color(hint, "dim"))
        print()

    def success(self, msg):
        print(self.color(f"\n  ✅  {msg}", "green"))
        time.sleep(0.5)

    def warn(self, msg):
        print(self.color(f"\n  ⚠️   {msg}", "yellow"))

    def error(self, msg):
        print(self.color(f"\n  ❌  {msg}", "red"))

    def info(self, msg):
        print(self.color(f"  ℹ️   {msg}", "cyan"))

    def prompt(self, label="Input", default=None):
        suffix = f" [{default}]" if default else ""
        try:
            val = input(self.color(f"\n  ▶ {label}{suffix}: ", "green")).strip()
            return val if val else default
        except (KeyboardInterrupt, EOFError):
            print()
            return None

    def pause(self):
        try:
            input(self.color("\n  Press ENTER to continue...", "dim"))
        except (KeyboardInterrupt, EOFError):
            pass

    def typewrite(self, text, delay=0.018, color="white"):
        """Typewriter effect for immersive explanations."""
        import sys
        for ch in self.color(text, color):
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    def progress_bar(self, current, total, label="Progress"):
        filled = int((current / total) * 30)
        bar = "█" * filled + "░" * (30 - filled)
        pct = int((current / total) * 100)
        print(self.color(f"  {label}: [{bar}] {pct}% ({current}/{total})", "cyan"))

    def table(self, headers, rows, col_color="cyan"):
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        def fmt_row(cells, c):
            parts = [self.color(str(cells[i]).ljust(col_widths[i]), c) for i in range(len(cells))]
            return "  │ " + " │ ".join(parts) + " │"

        sep = "  ├─" + "─┼─".join("─" * w for w in col_widths) + "─┤"
        top = "  ┌─" + "─┬─".join("─" * w for w in col_widths) + "─┐"
        bot = "  └─" + "─┴─".join("─" * w for w in col_widths) + "─┘"

        print(self.color(top, col_color))
        print(fmt_row(headers, col_color))
        print(self.color(sep, col_color))
        for row in rows:
            print(fmt_row(row, "white"))
        print(self.color(bot, col_color))
        print()
