#!/bin/bash
# ============================================================
# full_pipeline.sh — Complete Bug Bounty Recon Pipeline
# Usage: ./full_pipeline.sh <domain> [output_base_dir]
# Example: ./full_pipeline.sh testphp.vulnweb.com
#
# Pipeline stages:
#   1. Subdomain enumeration (passive + crt.sh)
#   2. Live host resolution
#   3. Port scanning (nmap)
#   4. HTTP probing (httpx)
#   5. Directory brute force (gobuster)
#   6. Nuclei vulnerability scan
#   7. Generate HTML summary report
# ============================================================

set -uo pipefail

TARGET="${1:-}"
BASE_DIR="${2:-$HOME/recon_results}"

if [[ -z "$TARGET" ]]; then
    echo "Usage: $0 <domain> [output_base_dir]"
    echo "Example: $0 testphp.vulnweb.com"
    exit 1
fi

# Create timestamped output directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="$BASE_DIR/${TARGET}_${TIMESTAMP}"
mkdir -p "$OUTPUT"/{subdomains,ports,dirs,vulns,screenshots}

LOG="$OUTPUT/pipeline.log"

# ── Logging helper ───────────────────────────────────────────
log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }
ok()  { echo -e "\033[92m[✓] $*\033[0m" | tee -a "$LOG"; }
warn(){ echo -e "\033[93m[!] $*\033[0m" | tee -a "$LOG"; }
err() { echo -e "\033[91m[✗] $*\033[0m" | tee -a "$LOG"; }

# ── Banner ───────────────────────────────────────────────────
clear
cat << EOF
╔══════════════════════════════════════════════════════════════╗
║          FULL BUG BOUNTY RECON PIPELINE                      ║
╠══════════════════════════════════════════════════════════════╣
║  Target:    $TARGET
║  Output:    $OUTPUT
║  Started:   $(date)
╚══════════════════════════════════════════════════════════════╝
EOF
echo ""

# ── STAGE 1: Subdomain Enumeration ──────────────────────────
echo "━━━ STAGE 1/7: SUBDOMAIN ENUMERATION ━━━━━━━━━━━━━━━━━━━━"
log "Starting subdomain enumeration for $TARGET"

SUB_FILE="$OUTPUT/subdomains/all_subdomains.txt"
> "$SUB_FILE"

# subfinder
if command -v subfinder &>/dev/null; then
    log "Running subfinder..."
    subfinder -d "$TARGET" -silent -timeout 30 2>/dev/null >> "$SUB_FILE" || true
    ok "subfinder done — $(wc -l < "$SUB_FILE") results"
else
    warn "subfinder not installed — skipping"
fi

# amass passive
if command -v amass &>/dev/null; then
    log "Running amass passive..."
    amass enum -passive -d "$TARGET" -timeout 3 2>/dev/null >> "$SUB_FILE" || true
    ok "amass done"
else
    warn "amass not installed — skipping"
fi

# crt.sh
log "Querying crt.sh..."
curl -s --max-time 20 "https://crt.sh/?q=%25.$TARGET&output=json" 2>/dev/null \
| python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    subs = set()
    for e in data:
        for n in e.get('name_value','').split('\n'):
            n = n.strip().lstrip('*.')
            if n.endswith('$TARGET') and n != '$TARGET':
                subs.add(n)
    [print(s) for s in sorted(subs)]
except: pass
" >> "$SUB_FILE" 2>/dev/null || warn "crt.sh unavailable"

# Deduplicate
sort -u "$SUB_FILE" -o "$SUB_FILE"
TOTAL_SUBS=$(wc -l < "$SUB_FILE")
ok "Stage 1 complete — $TOTAL_SUBS unique subdomains"
echo ""

# ── STAGE 2: Live Host Resolution ───────────────────────────
echo "━━━ STAGE 2/7: LIVE HOST RESOLUTION ━━━━━━━━━━━━━━━━━━━━━"
log "Resolving live hosts..."

LIVE_FILE="$OUTPUT/subdomains/live_hosts.txt"
> "$LIVE_FILE"

if command -v httpx &>/dev/null; then
    cat "$SUB_FILE" | httpx -silent -timeout 10 -threads 50 2>/dev/null \
        | tee "$LIVE_FILE" | head -20
    ok "httpx: $(wc -l < "$LIVE_FILE") live HTTP hosts"
else
    warn "httpx not installed — using basic DNS check"
    while IFS= read -r sub; do
        if host "$sub" &>/dev/null 2>&1; then
            echo "$sub" >> "$LIVE_FILE"
        fi
    done < "$SUB_FILE"
    ok "DNS check: $(wc -l < "$LIVE_FILE") resolving hosts"
fi
echo ""

# ── STAGE 3: Port Scanning ───────────────────────────────────
echo "━━━ STAGE 3/7: PORT SCANNING ━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Port scanning $TARGET..."

NMAP_OUT="$OUTPUT/ports/nmap_$TARGET.txt"
COMMON_PORTS="21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5432,5900,6379,8080,8443,8888,9200,27017"

if command -v nmap &>/dev/null; then
    nmap -sV -sC \
        -p "$COMMON_PORTS" \
        --open \
        -T4 \
        -oN "$NMAP_OUT" \
        "$TARGET" 2>/dev/null | tee -a "$LOG" | tail -30
    ok "nmap scan complete → $NMAP_OUT"
else
    err "nmap not installed — run: sudo apt install nmap"
fi
echo ""

# ── STAGE 4: HTTP Service Discovery ─────────────────────────
echo "━━━ STAGE 4/7: HTTP PROBING ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Probing web services..."

HTTP_URLS="$OUTPUT/subdomains/http_urls.txt"
{
    echo "http://$TARGET"
    echo "https://$TARGET"
    cat "$LIVE_FILE" 2>/dev/null
} | sort -u > "$HTTP_URLS"

# whatweb fingerprint
if command -v whatweb &>/dev/null; then
    WHATWEB_OUT="$OUTPUT/ports/whatweb.txt"
    log "Running whatweb fingerprint..."
    while IFS= read -r url; do
        whatweb "$url" --color=never 2>/dev/null >> "$WHATWEB_OUT" || true
    done < <(head -5 "$HTTP_URLS")
    ok "whatweb done → $WHATWEB_OUT"
fi
echo ""

# ── STAGE 5: Directory Brute Force ──────────────────────────
echo "━━━ STAGE 5/7: DIRECTORY BRUTE FORCE ━━━━━━━━━━━━━━━━━━━━"
log "Directory scanning main target..."

DIR_OUT="$OUTPUT/dirs/gobuster_${TARGET}.txt"
WORDLIST="/usr/share/wordlists/dirb/common.txt"

if [[ ! -f "$WORDLIST" ]]; then
    WORDLIST="/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt"
fi

if command -v gobuster &>/dev/null && [[ -f "$WORDLIST" ]]; then
    gobuster dir \
        -u "http://$TARGET" \
        -w "$WORDLIST" \
        -t 40 \
        -timeout 10s \
        -status-codes "200,204,301,302,307,401,403" \
        -no-error \
        -q \
        -o "$DIR_OUT" 2>/dev/null || true
    ok "gobuster: $(wc -l < "$DIR_OUT" 2>/dev/null || echo 0) paths found"
    cat "$DIR_OUT" 2>/dev/null | head -20
else
    warn "gobuster not installed or wordlist missing"
    err "Install: sudo apt install gobuster wordlists"
fi
echo ""

# ── STAGE 6: Nuclei Vulnerability Scan ──────────────────────
echo "━━━ STAGE 6/7: NUCLEI VULNERABILITY SCAN ━━━━━━━━━━━━━━━━"
log "Running nuclei templates..."

NUCLEI_OUT="$OUTPUT/vulns/nuclei_findings.txt"
NUCLEI_JSON="$OUTPUT/vulns/nuclei_findings.jsonl"

if command -v nuclei &>/dev/null; then
    nuclei \
        -u "http://$TARGET" \
        -t exposures/ \
        -t misconfiguration/ \
        -t default-logins/ \
        -t cves/ \
        -severity low,medium,high,critical \
        -stats \
        -silent \
        -o "$NUCLEI_OUT" \
        -json-export "$NUCLEI_JSON" \
        2>/dev/null | tee -a "$LOG" || true
    ok "nuclei: $(wc -l < "$NUCLEI_OUT" 2>/dev/null || echo 0) findings"
else
    warn "nuclei not installed"
    log "Install: go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
fi
echo ""

# ── STAGE 7: HTML Summary Report ─────────────────────────────
echo "━━━ STAGE 7/7: GENERATING SUMMARY REPORT ━━━━━━━━━━━━━━━━"
log "Building HTML report..."

HTML_REPORT="$OUTPUT/RECON_REPORT_${TARGET}.html"
SUBS_COUNT=$(wc -l < "$SUB_FILE" 2>/dev/null || echo 0)
LIVE_COUNT=$(wc -l < "$LIVE_FILE" 2>/dev/null || echo 0)
DIR_COUNT=$(wc -l < "$DIR_OUT" 2>/dev/null || echo 0)
VULN_COUNT=$(wc -l < "$NUCLEI_OUT" 2>/dev/null || echo 0)

SUBDOMAINS_LIST=$(head -50 "$SUB_FILE" 2>/dev/null | sed 's/^/<li>/' | sed 's/$/<\/li>/' | tr '\n' ' ')
DIRS_LIST=$(head -50 "$DIR_OUT" 2>/dev/null | sed 's/^/<li><code>/' | sed 's/$/<\/code><\/li>/' | tr '\n' ' ')
VULN_LIST=$(head -50 "$NUCLEI_OUT" 2>/dev/null | sed 's/&/\&amp;/g;s/</\&lt;/g;s/>/\&gt;/g' | sed 's/^/<li>/' | sed 's/$/<\/li>/' | tr '\n' ' ')
NMAP_CONTENT=$(cat "$NMAP_OUT" 2>/dev/null | sed 's/&/\&amp;/g;s/</\&lt;/g;s/>/\&gt;/g' | head -60 | tr '\n' '<br>')

cat > "$HTML_REPORT" << HTMLEOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Recon Report — $TARGET</title>
<style>
  body { font-family: 'Courier New', monospace; background: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; }
  h1 { color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
  h2 { color: #3fb950; margin-top: 30px; }
  .meta { background: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
  .stat { display: inline-block; background: #1f6feb; color: white; padding: 6px 14px; border-radius: 20px; margin: 4px; font-size: 13px; }
  .stat.red { background: #da3633; }
  .stat.orange { background: #d29922; }
  .stat.green { background: #238636; }
  ul { background: #161b22; border: 1px solid #30363d; padding: 15px 15px 15px 35px; border-radius: 6px; }
  li { padding: 2px 0; color: #8b949e; }
  pre { background: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 6px; overflow-x: auto; font-size: 12px; white-space: pre-wrap; }
  .warn { color: #f0883e; }
  footer { margin-top: 40px; color: #484f58; font-size: 12px; border-top: 1px solid #30363d; padding-top: 10px; }
</style>
</head>
<body>
<h1>🔍 Recon Report: $TARGET</h1>

<div class="meta">
  <strong>Target:</strong> $TARGET<br>
  <strong>Date:</strong> $(date)<br>
  <strong>Pipeline:</strong> Bug Bounty Trainer v1.0
</div>

<h2>📊 Summary Statistics</h2>
<span class="stat">Subdomains: $SUBS_COUNT</span>
<span class="stat green">Live Hosts: $LIVE_COUNT</span>
<span class="stat">Directories: $DIR_COUNT</span>
<span class="stat $([ "$VULN_COUNT" -gt 0 ] && echo red || echo green)">Findings: $VULN_COUNT</span>

<h2>🌐 Subdomains Found ($SUBS_COUNT)</h2>
<ul>$SUBDOMAINS_LIST</ul>

<h2>📂 Directories Discovered ($DIR_COUNT)</h2>
<ul>$DIRS_LIST</ul>

<h2>🔓 Port Scan Results</h2>
<pre>$NMAP_CONTENT</pre>

<h2>⚠️ Nuclei Findings ($VULN_COUNT)</h2>
$([ "$VULN_COUNT" -gt 0 ] && echo "<ul class='warn'>$VULN_LIST</ul>" || echo "<p style='color:#3fb950'>✅ No nuclei findings</p>")

<footer>Generated by Bug Bounty Trainer v1.0 — For authorized testing only</footer>
</body>
</html>
HTMLEOF

ok "HTML report → $HTML_REPORT"
echo ""

# ── FINAL SUMMARY ────────────────────────────────────────────
cat << EOF
╔══════════════════════════════════════════════════════════════╗
║  ✅  RECON PIPELINE COMPLETE
╠══════════════════════════════════════════════════════════════╣
║  Target:       $TARGET
║  Subdomains:   $SUBS_COUNT
║  Live Hosts:   $LIVE_COUNT
║  Directories:  $DIR_COUNT
║  Findings:     $VULN_COUNT
╠══════════════════════════════════════════════════════════════╣
║  Output dir:   $OUTPUT
║  HTML Report:  $HTML_REPORT
╚══════════════════════════════════════════════════════════════╝
EOF
