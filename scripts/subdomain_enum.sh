#!/bin/bash
# ============================================================
# subdomain_enum.sh — Passive + Active Subdomain Enumeration
# Usage: ./subdomain_enum.sh <domain> [output_dir]
# Example: ./subdomain_enum.sh example.com /tmp/recon
# ============================================================

set -euo pipefail

TARGET="${1:-}"
OUTPUT_DIR="${2:-/tmp/recon_$(date +%Y%m%d_%H%M%S)}"

if [[ -z "$TARGET" ]]; then
    echo "Usage: $0 <domain> [output_dir]"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
RESULTS="$OUTPUT_DIR/subdomains_${TARGET}.txt"
> "$RESULTS"   # clear file

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  SUBDOMAIN ENUMERATION — $TARGET"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── METHOD 1: subfinder ──────────────────────────────────────
echo "[1/5] subfinder (passive DNS aggregation)..."
if command -v subfinder &>/dev/null; then
    subfinder -d "$TARGET" -silent 2>/dev/null | tee -a "$RESULTS"
    COUNT=$(wc -l < "$RESULTS")
    echo "      → subfinder found $COUNT subdomains"
else
    echo "      ⚠ subfinder not installed. Run: go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
fi

# ── METHOD 2: amass passive ──────────────────────────────────
echo ""
echo "[2/5] amass (passive mode)..."
if command -v amass &>/dev/null; then
    amass enum -passive -d "$TARGET" 2>/dev/null | tee -a "$RESULTS"
else
    echo "      ⚠ amass not installed. Run: sudo apt install amass"
fi

# ── METHOD 3: theHarvester ───────────────────────────────────
echo ""
echo "[3/5] theHarvester (OSINT sources)..."
if command -v theHarvester &>/dev/null; then
    theHarvester -d "$TARGET" -b bing,google,yahoo,dnsdumpster 2>/dev/null \
        | grep -E "^\[?\*" | grep "\.$TARGET" | tee -a "$RESULTS" || true
else
    echo "      ⚠ theHarvester not installed. Run: sudo apt install theharvester"
fi

# ── METHOD 4: crt.sh Certificate Transparency ────────────────
echo ""
echo "[4/5] crt.sh (certificate transparency logs)..."
if command -v curl &>/dev/null; then
    curl -s --max-time 15 "https://crt.sh/?q=%25.$TARGET&output=json" 2>/dev/null \
    | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    subs = set()
    for entry in data:
        for name in entry.get('name_value', '').split('\n'):
            name = name.strip().lstrip('*.')
            if name.endswith('$TARGET') and name != '$TARGET':
                subs.add(name)
    for s in sorted(subs):
        print(s)
    import sys; print(f'      → crt.sh found {len(subs)} unique subdomains', file=sys.stderr)
except Exception as e:
    print(f'      ⚠ crt.sh error: {e}', file=sys.stderr)
" 2>&1 | tee -a "$RESULTS"
else
    echo "      ⚠ curl not installed"
fi

# ── METHOD 5: DNS brute force ─────────────────────────────────
echo ""
echo "[5/5] DNS brute force with wordlist..."
WORDLIST="/usr/share/wordlists/dns/subdomains-top1million-5000.txt"
if [[ ! -f "$WORDLIST" ]]; then
    WORDLIST="/usr/share/wordlists/dirb/common.txt"
fi

if command -v dnsrecon &>/dev/null && [[ -f "$WORDLIST" ]]; then
    dnsrecon -d "$TARGET" -t brt -D "$WORDLIST" 2>/dev/null \
        | grep -oP '[A-Za-z0-9.-]+\.'$TARGET | sort -u | tee -a "$RESULTS"
elif command -v ffuf &>/dev/null && [[ -f "$WORDLIST" ]]; then
    ffuf -u "http://FUZZ.$TARGET" -w "$WORDLIST" -mc 200,301,302 \
        -t 50 -silent 2>/dev/null | tee -a "$RESULTS"
else
    echo "      ⚠ dnsrecon/ffuf not installed"
fi

# ── FINAL DEDUP + SORT ───────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════════"
sort -u "$RESULTS" -o "$RESULTS"
TOTAL=$(wc -l < "$RESULTS")
echo "✅ COMPLETE — $TOTAL unique subdomains saved to: $RESULTS"
echo ""
echo "Preview (first 20):"
head -20 "$RESULTS"
echo "══════════════════════════════════════════════════════════"
