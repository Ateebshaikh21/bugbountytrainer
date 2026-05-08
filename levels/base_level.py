"""
levels/base_level.py — Abstract base class for all training levels.
Each level defines its concept text, tool list, and list of Task objects.
"""

from abc import ABC, abstractmethod
from core.safety import safety_reminder


class Task:
    """Represents one hands-on challenge within a level."""

    def __init__(self, task_id, title, description, tool_suggestion,
                 expected_output, hint, validator, points=100):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.tool_suggestion = tool_suggestion
        self.expected_output = expected_output
        self.hint = hint
        self.validator = validator   # callable(answer: str) -> bool
        self.points = points


class BaseLevel(ABC):
    level_num = 0
    level_name = "Base"
    concept = ""
    tools = []

    def __init__(self, tracker, ui):
        self.tracker = tracker
        self.ui = ui
        self.tasks = self._build_tasks()

    @abstractmethod
    def _build_tasks(self) -> list:
        """Return list of Task objects."""
        ...

    def run(self):
        while True:
            self.ui.clear()
            self.ui.section(f"LEVEL {self.level_num} — {self.level_name.upper()}")

            # Show concept
            self.ui.print_color("  📖  CONCEPT\n", "magenta")
            for para in self.concept.strip().split("\n\n"):
                self.ui.typewrite("  " + para.strip(), delay=0.008, color="white")
                print()

            print(print(safety_reminder()))

            # Show task list
            self._show_task_menu()

            choice = self.ui.prompt("Select task (0 = back)")
            if choice == "0" or choice is None:
                return

            try:
                idx = int(choice) - 1
                if idx < 0 or idx >= len(self.tasks):
                    raise ValueError
            except ValueError:
                self.ui.warn("Enter a valid task number.")
                self.ui.pause()
                continue

            self._run_task(self.tasks[idx])

    def _show_task_menu(self):
        self.ui.print_color(f"\n  🛠️  TOOLS FOR THIS LEVEL: {', '.join(self.tools)}\n", "yellow")
        headers = ["#", "Task", "Points", "Status"]
        rows = []
        for i, t in enumerate(self.tasks, 1):
            status = "✅" if self.tracker.is_task_done(t.task_id) else "○"
            rows.append([str(i), t.title, str(t.points), status])
        self.ui.table(headers, rows)
        print("  [0] Back\n")

    def _run_task(self, task: Task):
        self.ui.clear()
        self.ui.section(f"TASK: {task.title}")

        if self.tracker.is_task_done(task.task_id):
            self.ui.success("You already completed this task!")
            self.ui.pause()
            return

        # Task description
        self.ui.task_box("📋  DESCRIPTION", task.description)
        self.ui.task_box("🔧  SUGGESTED TOOL", task.tool_suggestion, color="yellow")
        self.ui.task_box("🎯  EXPECTED OUTPUT", task.expected_output, color="green")

        show_hint = self.ui.prompt("Show hint? (y/n)", default="n")
        if show_hint and show_hint.lower() == "y":
            self.ui.hint_box(task.hint)

        self.ui.print_color("  ⚡  Perform the task, then enter your answer below.", "cyan")
        print()

        attempts = 0
        while attempts < 3:
            answer = self.ui.prompt(f"Your answer (attempt {attempts+1}/3)")
            if not answer:
                self.ui.warn("No answer entered.")
                attempts += 1
                continue

            if task.validator(answer):
                earned = self.tracker.complete_task(task.task_id, self.level_num, task.points)
                if earned:
                    self.ui.success(f"✅ Correct! +{task.points} points earned!")
                else:
                    self.ui.success("Already completed — nice review!")
                self.ui.pause()
                return
            else:
                attempts += 1
                if attempts < 3:
                    self.ui.error("Not quite right. Try again.")
                    hint_again = self.ui.prompt("Show hint? (y/n)", default="n")
                    if hint_again and hint_again.lower() == "y":
                        self.ui.hint_box(task.hint)

        self.ui.warn("3 attempts used. Task not completed — study the hint and retry later.")
        self.ui.pause()
