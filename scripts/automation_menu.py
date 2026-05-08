"""
scripts/automation_menu.py — Menu for recon automation scripts.
"""

import subprocess
import os
import sys


class AutomationMenu:
    def __init__(self, ui):
        self.ui = ui

    def run(self):
        while True:
            self.ui.clear()
            self.ui.section("⚙️  AUTOMATION SCRIPTS")
            self.ui.print_color("  ⚠️  Only use these against LOCAL lab targets or authorized programs!\n", "yellow")

            self.ui.menu([
                ("1", "Subdomain Enumeration  (subfinder/amass wrapper)"),
                ("2", "Directory Scan          (gobuster wrapper)"),
                ("3", "Nuclei Scan             (template-based vuln scan)"),
                ("4", "Full Recon Pipeline     (auto: subdomains + dirs + nuclei)"),
                ("5", "View Script Source Code"),
                ("0", "Back"),
            ])

            choice = self.ui.prompt("Select")
            if choice == "0" or choice is None:
                return
            elif choice == "1":
                self._subdomain_enum()
            elif choice == "2":
                self._directory_scan()
            elif choice == "3":
                self._nuclei_scan()
            elif choice == "4":
                self._full_pipeline()
            elif choice == "5":
                self._show_source()

    def _subdomain_enum(self):
        self.ui.clear()
        self.ui.section("🔍  SUBDOMAIN ENUMERATION")
        target = self.ui.prompt("Target domain (e.g., testphp.vulnweb.com)")
        if not target:
            return

        self.ui.print_color(f"\n  Running subdomain enum on: {target}\n", "cyan")
        self.ui.print_color("  Commands that will run:\n", "dim")

        script = f"""
# --- Subdomain Enumeration Script ---
# Target: {target}

echo "[*] Starting subdomain enumeration for {target}"
echo "[*] Method 1: subfinder"
subfinder -d {target} -silent 2>/dev/null || echo "subfinder not installed"

echo ""
echo "[*] Method 2: amass (passive only)"
amass enum -passive -d {target} 2>/dev/null || echo "amass not installed"

echo ""
echo "[*] Method 3: DNS brute force with dnsrecon"
dnsrecon -d {target} -t brt 2>/dev/null | grep -E "\\[\\*\\]|\\[\\+\\]" || echo "dnsrecon not installed"

echo ""
echo "[*] Method 4: Certificate transparency (crt.sh)"
curl -s "https://crt.sh/?q=%25.{target}&output=json" 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    subs = set()
    for entry in data:
        name = entry.get('name_value', '')
        for sub in name.split('\\n'):
            sub = sub.strip().lstrip('*.')
            if sub.endswith('{target}'):
                subs.add(sub)
    for s in sorted(subs):
        print(f'  {{s}}')
    print(f'[+] Found {{len(subs)}} unique subdomains via crt.sh')
except:
    print('Could not parse crt.sh response')
" || echo "Failed to query crt.sh"
"""
        print(self.ui.color(script, "dim"))
        run = self.ui.prompt("Run now? (y/n)", default="n")
        if run and run.lower() == "y":
            self._execute_script(script)
        self.ui.pause()

    def _directory_scan(self):
        self.ui.clear()
        self.ui.section("📂  DIRECTORY SCAN")
        target = self.ui.prompt("Target URL (e.g., http://127.0.0.1:8080)")
        if not target:
            return
        wordlist = self.ui.prompt(
            "Wordlist path",
            default="/usr/share/wordlists/dirb/common.txt"
        )

        script = f"""
# --- Directory Scan Script ---
echo "[*] Scanning {target} for directories"

echo ""
echo "[*] Method 1: gobuster"
gobuster dir \\
  -u {target} \\
  -w {wordlist} \\
  -t 50 \\
  --status-codes 200,301,302,403 \\
  -q 2>/dev/null || echo "gobuster not installed"

echo ""
echo "[*] Method 2: dirb (fallback)"
dirb {target} {wordlist} -S -r 2>/dev/null | grep -E "CODE|DIRECTORY" || echo "dirb not installed"
"""
        print(self.ui.color(script, "dim"))
        run = self.ui.prompt("Run now? (y/n)", default="n")
        if run and run.lower() == "y":
            self._execute_script(script)
        self.ui.pause()

    def _nuclei_scan(self):
        self.ui.clear()
        self.ui.section("☢️  NUCLEI SCAN")
        target = self.ui.prompt("Target URL (e.g., http://127.0.0.1:8080)")
        if not target:
            return

        script = f"""
# --- Nuclei Scan Script ---
# Templates: CVEs, misconfigs, exposures, default-logins
echo "[*] Running Nuclei against {target}"
echo "[*] Using templates: cves, misconfiguration, exposures, default-logins"

nuclei \\
  -u {target} \\
  -t cves/ \\
  -t misconfiguration/ \\
  -t exposures/ \\
  -t default-logins/ \\
  -severity low,medium,high,critical \\
  -stats \\
  -silent 2>/dev/null || echo "nuclei not installed — install: go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
"""
        print(self.ui.color(script, "dim"))
        run = self.ui.prompt("Run now? (y/n)", default="n")
        if run and run.lower() == "y":
            self._execute_script(script)
        self.ui.pause()

    def _full_pipeline(self):
        self.ui.clear()
        self.ui.section("🚀  FULL RECON PIPELINE")
        domain = self.ui.prompt("Target domain (e.g., testphp.vulnweb.com)")
        if not domain:
            return

        output_dir = f"/tmp/recon_{domain.replace('.', '_')}"
        script = f"""
#!/bin/bash
# --- Full Recon Pipeline ---
TARGET="{domain}"
OUTPUT="{output_dir}"
mkdir -p $OUTPUT

echo "╔══════════════════════════════════════╗"
echo "║   FULL RECON PIPELINE — $TARGET"
echo "╚══════════════════════════════════════╝"
echo ""

# 1. Subdomain enum
echo "[1/5] Subdomain Enumeration..."
subfinder -d $TARGET -silent -o $OUTPUT/subdomains.txt 2>/dev/null
echo "      → Saved to $OUTPUT/subdomains.txt"
cat $OUTPUT/subdomains.txt 2>/dev/null | head -20

# 2. DNS resolution
echo ""
echo "[2/5] Resolving live hosts..."
cat $OUTPUT/subdomains.txt 2>/dev/null | while read sub; do
  if host $sub &>/dev/null; then echo $sub; fi
done > $OUTPUT/live_hosts.txt
echo "      → Live hosts: $(wc -l < $OUTPUT/live_hosts.txt)"

# 3. Port scan on main domain
echo ""
echo "[3/5] Port Scanning..."
nmap -sV --open -p 80,443,8080,8443,3000,8000 $TARGET -oN $OUTPUT/ports.txt 2>/dev/null | tail -20
echo "      → Saved to $OUTPUT/ports.txt"

# 4. Directory scan
echo ""
echo "[4/5] Directory Enumeration on main domain..."
gobuster dir -u http://$TARGET -w /usr/share/wordlists/dirb/common.txt -q -t 30 2>/dev/null \\
  | tee $OUTPUT/dirs.txt | head -20
echo "      → Saved to $OUTPUT/dirs.txt"

# 5. Nuclei scan
echo ""
echo "[5/5] Nuclei vulnerability scan..."
nuclei -u http://$TARGET -t exposures/ -t misconfiguration/ -silent 2>/dev/null \\
  | tee $OUTPUT/nuclei.txt | head -20
echo "      → Saved to $OUTPUT/nuclei.txt"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   RECON COMPLETE! Results in: $OUTPUT"
echo "╚══════════════════════════════════════╝"
"""
        print(self.ui.color(script, "dim"))
        run = self.ui.prompt("Run now? (y/n)", default="n")
        if run and run.lower() == "y":
            self._execute_script(script)
        self.ui.pause()

    def _show_source(self):
        """Show the standalone script files."""
        self.ui.clear()
        self.ui.section("📁  AUTOMATION SCRIPT FILES")
        scripts_dir = os.path.join(os.path.dirname(__file__))
        self.ui.info(f"Scripts location: {scripts_dir}")
        self.ui.info("Files:")
        for f in ["subdomain_enum.sh", "dir_scan.sh", "nuclei_scan.sh", "full_pipeline.sh"]:
            path = os.path.join(scripts_dir, f)
            status = "✅ exists" if os.path.exists(path) else "○ not yet generated"
            print(f"    {f}  —  {status}")
        print()
        self.ui.info("Run the scripts above once to auto-generate .sh files.")
        self.ui.pause()

    def _execute_script(self, script):
        """Execute a shell script and stream output."""
        import tempfile
        self.ui.print_color("\n  [*] Executing...\n", "cyan")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
            f.write(script)
            tmppath = f.name
        os.chmod(tmppath, 0o755)
        try:
            result = subprocess.run(
                ["bash", tmppath],
                capture_output=False,
                text=True,
                timeout=120
            )
        except subprocess.TimeoutExpired:
            self.ui.warn("Script timed out after 120 seconds.")
        except FileNotFoundError:
            self.ui.error("bash not found.")
        finally:
            os.unlink(tmppath)
