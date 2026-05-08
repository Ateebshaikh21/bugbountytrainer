"""
reports/report_generator.py — Professional bug bounty report generator.
Generates both terminal preview and Markdown file output.
"""

import os
import json
from datetime import datetime


class ReportGenerator:
    def __init__(self, ui):
        self.ui = ui
        self.output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "reports")
        os.makedirs(self.output_dir, exist_ok=True)

    def interactive(self):
        """Interactive report builder."""
        self.ui.clear()
        self.ui.section("📝  PROFESSIONAL BUG REPORT GENERATOR")
        self.ui.print_color("""
  Fill in each field. Press ENTER to skip optional fields.
  A Markdown report will be saved to data/reports/
""", "cyan")

        fields = self._collect_fields()
        if not fields:
            return

        self._preview_report(fields)

        save = self.ui.prompt("Save this report to file? (y/n)", default="y")
        if save and save.lower() == "y":
            path = self._save_report(fields)
            self.ui.success(f"Report saved to: {path}")

        self.ui.pause()

    def _collect_fields(self):
        data = {}

        self.ui.print_color("\n  === REPORT METADATA ===\n", "magenta")
        data["researcher"] = self.ui.prompt("Your handle/name", default="Anonymous Researcher")
        data["program"]    = self.ui.prompt("Target program name", default="Target Company")
        data["date"]       = datetime.now().strftime("%Y-%m-%d")

        self.ui.print_color("\n  === VULNERABILITY DETAILS ===\n", "magenta")
        data["title"]    = self.ui.prompt("Report Title (be specific)")
        if not data["title"]:
            self.ui.warn("Title is required.")
            return None

        self.ui.print_color("""
  SEVERITY OPTIONS:
    Critical (9.0-10.0) — RCE, full account takeover, mass data breach
    High     (7.0-8.9)  — SQLi, stored XSS, privilege escalation
    Medium   (4.0-6.9)  — Reflected XSS, IDOR, CSRF
    Low      (0.1-3.9)  — Info disclosure, minor misconfig
    Informational       — Best practice recommendation
""", "dim")
        data["severity"] = self.ui.prompt("Severity", default="Medium")
        data["cvss"]     = self.ui.prompt("CVSS Score (optional, e.g., 6.1)")
        data["cwe"]      = self.ui.prompt("CWE ID (optional, e.g., CWE-79 for XSS)")

        self.ui.print_color("\n  === VULNERABILITY DESCRIPTION ===\n", "magenta")
        data["summary"] = self.ui.prompt("Summary (2-3 sentences — what, where, why)")
        data["endpoint"] = self.ui.prompt("Affected endpoint/URL")
        data["parameter"] = self.ui.prompt("Affected parameter (if applicable)")

        self.ui.print_color("\n  === REPRODUCTION STEPS ===\n", "magenta")
        self.ui.info("Enter numbered steps. Type 'DONE' when finished.")
        steps = []
        i = 1
        while True:
            step = self.ui.prompt(f"  Step {i}")
            if not step or step.upper() == "DONE":
                break
            steps.append(step)
            i += 1
        data["steps"] = steps

        self.ui.print_color("\n  === PROOF OF CONCEPT ===\n", "magenta")
        data["request"]  = self.ui.prompt("HTTP Request (or 'see attachment')")
        data["response"] = self.ui.prompt("Server Response / Evidence")
        data["payload"]  = self.ui.prompt("Payload used")

        self.ui.print_color("\n  === IMPACT & REMEDIATION ===\n", "magenta")
        data["impact"]       = self.ui.prompt("Impact (what can attacker do?)")
        data["business_risk"] = self.ui.prompt("Business Risk (data breach? reputation?)")
        data["remediation"]  = self.ui.prompt("Remediation recommendation")
        data["references"]   = self.ui.prompt("References (OWASP link, CVE, etc.)")

        return data

    def generate_markdown(self, data: dict) -> str:
        """Generate professional Markdown report."""
        steps_md = "\n".join(f"{i+1}. {s}" for i, s in enumerate(data.get("steps", [])))
        if not steps_md:
            steps_md = "_Steps not provided_"

        cvss_line = f" | CVSS Score: **{data['cvss']}**" if data.get("cvss") else ""
        cwe_line  = f" | CWE: [{data['cwe']}](https://cwe.mitre.org/data/definitions/{data['cwe'].replace('CWE-','')}.html)" if data.get("cwe") else ""

        severity_emoji = {
            "critical": "🔴", "high": "🟠", "medium": "🟡",
            "low": "🟢", "informational": "ℹ️"
        }.get(data.get("severity", "medium").lower(), "⚪")

        return f"""# Bug Report: {data.get('title', 'Untitled')}

---

## Metadata

| Field | Value |
|-------|-------|
| **Researcher** | {data.get('researcher', 'Anonymous')} |
| **Program** | {data.get('program', 'Unknown')} |
| **Date** | {data.get('date', datetime.now().strftime('%Y-%m-%d'))} |
| **Severity** | {severity_emoji} **{data.get('severity', 'Medium')}**{cvss_line}{cwe_line} |

---

## Summary

{data.get('summary', '_No summary provided_')}

---

## Vulnerability Details

| Field | Value |
|-------|-------|
| **Affected Endpoint** | `{data.get('endpoint', 'N/A')}` |
| **Affected Parameter** | `{data.get('parameter', 'N/A')}` |
| **Vulnerability Type** | {data.get('title', 'Unknown').split()[0]} |

---

## Steps to Reproduce

{steps_md}

---

## Proof of Concept

### HTTP Request
```http
{data.get('request', 'See attached Burp Suite export')}
```

### Payload Used
```
{data.get('payload', 'N/A')}
```

### Server Response / Evidence
```
{data.get('response', 'See attached screenshot')}
```

---

## Impact

{data.get('impact', '_Impact not described_')}

### Business Risk

{data.get('business_risk', '_Business risk not described_')}

---

## Remediation

{data.get('remediation', '_Remediation not provided_')}

---

## References

{data.get('references', '- [OWASP Top 10](https://owasp.org/www-project-top-ten/)')}

---

_Report generated by Bug Bounty Trainer v1.0_
_Researcher: {data.get('researcher', 'Anonymous')} | Date: {data.get('date', '')} | Confidential_
"""

    def _preview_report(self, data):
        self.ui.clear()
        self.ui.section("📄  REPORT PREVIEW")
        md = self.generate_markdown(data)
        print(md[:3000])
        if len(md) > 3000:
            self.ui.info("... (truncated for preview — full report will be saved)")
        print()

    def _save_report(self, data):
        filename = (
            data.get("title", "report")
            .lower()
            .replace(" ", "_")
            .replace("/", "-")[:50]
        ) + f"_{data['date']}.md"

        path = os.path.join(self.output_dir, filename)
        with open(path, "w") as f:
            f.write(self.generate_markdown(data))

        # Also save JSON for programmatic access
        json_path = path.replace(".md", ".json")
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)

        return path

    def generate_from_exam(self, exam_data: dict) -> str:
        """Auto-generate report from final exam answers."""
        return self.generate_markdown({
            "researcher": "Trainee",
            "program":    "Juice Shop (Training Target)",
            "date":       datetime.now().strftime("%Y-%m-%d"),
            "title":      exam_data.get("title", "Vulnerability Found in Juice Shop"),
            "severity":   exam_data.get("severity", "Medium"),
            "summary":    exam_data.get("summary", ""),
            "endpoint":   "http://127.0.0.1:3000",
            "steps":      exam_data.get("steps", "").split("\n"),
            "impact":     exam_data.get("impact", ""),
            "remediation": exam_data.get("fix", ""),
            "request":    "Captured via Burp Suite",
            "response":   "See attached screenshot",
            "payload":    "See reproduction steps",
        })
