#!/bin/bash
# ============================================================
# nuclei_scan.sh — Template-based vulnerability scanner
# Usage: ./nuclei_scan.sh <url> [severity] [output_dir]
# Example: ./nuclei_scan.sh http://127.0.0.1:8080 medium,high
# ============================================================

set -euo pipefail

TARGET="${1:-}"
SEVERITY="${2:-low,medium,high,critical}"
OUTPUT_DIR="${3:-/tmp/nuclei_$(date +%Y%m%d_%H%M%S)}"

if [[ -z "$TARGET" ]]; then
    echo "Usage: $0 <url> [severity] [output_dir]"
    echo "Example: $0 http://127.0.0.1:8080 medium,high"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
RESULTS="$OUTPUT_DIR/nuclei_findings.txt"
JSON_OUT="$OUTPUT_DIR/nuclei_findings.jsonl"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  NUCLEI VULNERABILITY SCAN"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Target:   $TARGET"
echo "║  Severity: $SEVERITY"
echo "║  Output:   $OUTPUT_DIR"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check nuclei is installed
if ! command -v nuclei &>/dev/null; then
    echo "⚠  nuclei not installed."
    echo ""
    echo "  Install with Go:"
    echo "    go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
    echo "    export PATH=\$PATH:\$HOME/go/bin"
    echo ""
    echo "  Or download binary:"
    echo "    wget https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip"
    echo "    unzip nuclei_linux_amd64.zip && sudo mv nuclei /usr/local/bin/"
    echo ""
    echo "  Update templates after install:"
    echo "    nuclei -update-templates"
    exit 1
fi

# Update templates if older than 7 days
TEMPLATES_DIR="$HOME/nuclei-templates"
if [[ ! -d "$TEMPLATES_DIR" ]]; then
    echo "[*] Downloading nuclei templates for first time..."
    nuclei -update-templates -silent 2>/dev/null || true
elif [[ $(find "$TEMPLATES_DIR" -maxdepth 0 -mtime +7 2>/dev/null) ]]; then
    echo "[*] Templates older than 7 days — updating..."
    nuclei -update-templates -silent 2>/dev/null || true
fi

echo "[*] Starting Nuclei scan..."
echo ""

# ── PHASE 1: Exposures (fast, low noise) ─────────────────────
echo "━━━ PHASE 1/5: Exposure Templates ━━━━━━━━━━━━━━━━━━━━━━━"
nuclei \
    -u "$TARGET" \
    -t exposures/ \
    -severity "$SEVERITY" \
    -stats \
    -o "$OUTPUT_DIR/phase1_exposures.txt" \
    -json-export "$OUTPUT_DIR/phase1_exposures.jsonl" \
    2>/dev/null | grep -E "\[|\]" | tee -a "$RESULTS" || true

# ── PHASE 2: Misconfigurations ────────────────────────────────
echo ""
echo "━━━ PHASE 2/5: Misconfiguration Templates ━━━━━━━━━━━━━━━"
nuclei \
    -u "$TARGET" \
    -t misconfiguration/ \
    -severity "$SEVERITY" \
    -stats \
    -o "$OUTPUT_DIR/phase2_misconfig.txt" \
    -json-export "$OUTPUT_DIR/phase2_misconfig.jsonl" \
    2>/dev/null | grep -E "\[|\]" | tee -a "$RESULTS" || true

# ── PHASE 3: Default logins ───────────────────────────────────
echo ""
echo "━━━ PHASE 3/5: Default Login Templates ━━━━━━━━━━━━━━━━━━"
nuclei \
    -u "$TARGET" \
    -t default-logins/ \
    -severity "$SEVERITY" \
    -stats \
    -o "$OUTPUT_DIR/phase3_default_logins.txt" \
    -json-export "$OUTPUT_DIR/phase3_default_logins.jsonl" \
    2>/dev/null | grep -E "\[|\]" | tee -a "$RESULTS" || true

# ── PHASE 4: CVE templates ────────────────────────────────────
echo ""
echo "━━━ PHASE 4/5: CVE Templates (known vulnerabilities) ━━━━"
nuclei \
    -u "$TARGET" \
    -t cves/ \
    -severity "$SEVERITY" \
    -stats \
    -timeout 10 \
    -o "$OUTPUT_DIR/phase4_cves.txt" \
    -json-export "$OUTPUT_DIR/phase4_cves.jsonl" \
    2>/dev/null | grep -E "\[|\]" | tee -a "$RESULTS" || true

# ── PHASE 5: Technologies fingerprint ────────────────────────
echo ""
echo "━━━ PHASE 5/5: Technology Detection ━━━━━━━━━━━━━━━━━━━━━"
nuclei \
    -u "$TARGET" \
    -t technologies/ \
    -stats \
    -o "$OUTPUT_DIR/phase5_technologies.txt" \
    2>/dev/null | grep -E "\[|\]" | tee -a "$RESULTS" || true

# ── SUMMARY REPORT ───────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  NUCLEI SCAN COMPLETE"
echo "╠══════════════════════════════════════════════════════════╣"

TOTAL=$(wc -l < "$RESULTS" 2>/dev/null || echo 0)
CRITICAL=$(grep -c "\[critical\]" "$RESULTS" 2>/dev/null || echo 0)
HIGH=$(grep -c "\[high\]" "$RESULTS" 2>/dev/null || echo 0)
MEDIUM=$(grep -c "\[medium\]" "$RESULTS" 2>/dev/null || echo 0)
LOW=$(grep -c "\[low\]" "$RESULTS" 2>/dev/null || echo 0)
INFO=$(grep -c "\[info\]" "$RESULTS" 2>/dev/null || echo 0)

echo "║  Total Findings: $TOTAL"
echo "║  Critical: $CRITICAL  |  High: $HIGH  |  Medium: $MEDIUM  |  Low: $LOW  |  Info: $INFO"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Results saved to: $OUTPUT_DIR"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

if [[ $TOTAL -gt 0 ]]; then
    echo "  TOP FINDINGS:"
    echo ""
    grep -E "\[critical\]|\[high\]" "$RESULTS" 2>/dev/null | head -10 \
        | sed 's/^/    /' || echo "    (none at critical/high)"
fi
