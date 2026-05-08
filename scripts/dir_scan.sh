#!/bin/bash
# ============================================================
# dir_scan.sh — Directory & File Brute Force Scanner
# Usage: ./dir_scan.sh <url> [wordlist] [output_dir]
# Example: ./dir_scan.sh http://127.0.0.1:8080
# ============================================================

set -euo pipefail

TARGET="${1:-}"
WORDLIST="${2:-/usr/share/wordlists/dirb/common.txt}"
OUTPUT_DIR="${3:-/tmp/dirscan_$(date +%Y%m%d_%H%M%S)}"

if [[ -z "$TARGET" ]]; then
    echo "Usage: $0 <url> [wordlist] [output_dir]"
    echo "Example: $0 http://127.0.0.1:8080"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
RESULTS="$OUTPUT_DIR/dirs.txt"
DOMAIN=$(echo "$TARGET" | sed 's|https\?://||' | cut -d/ -f1 | tr ':' '_')

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  DIRECTORY SCAN — $TARGET"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Wordlist: $WORDLIST"
echo "║  Output:   $OUTPUT_DIR"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check wordlist exists
if [[ ! -f "$WORDLIST" ]]; then
    echo "⚠ Wordlist not found: $WORDLIST"
    echo "  Trying fallback: /usr/share/wordlists/dirb/small.txt"
    WORDLIST="/usr/share/wordlists/dirb/small.txt"
    if [[ ! -f "$WORDLIST" ]]; then
        echo "  No wordlist found. Install: sudo apt install wordlists"
        exit 1
    fi
fi

# ── METHOD 1: gobuster (fastest) ─────────────────────────────
echo "[1/4] GOBUSTER — Fast parallel directory brute force"
echo "      Status codes: 200, 204, 301, 302, 307, 401, 403"
if command -v gobuster &>/dev/null; then
    gobuster dir \
        --url "$TARGET" \
        --wordlist "$WORDLIST" \
        --threads 50 \
        --timeout 10s \
        --status-codes "200,204,301,302,307,401,403" \
        --no-error \
        --quiet \
        --output "$OUTPUT_DIR/gobuster_raw.txt" 2>/dev/null || true

    # Pretty print with colors
    if [[ -f "$OUTPUT_DIR/gobuster_raw.txt" ]]; then
        echo ""
        echo "  Results:"
        grep -E "Status: (200|301|302|401|403)" "$OUTPUT_DIR/gobuster_raw.txt" | \
            awk '{
                if ($2 == "(Status: 200)") color="\033[92m";
                else if ($2 ~ /301|302/) color="\033[93m";
                else if ($2 ~ /401|403/) color="\033[91m";
                else color="\033[0m";
                print "  " color $0 "\033[0m"
            }' || cat "$OUTPUT_DIR/gobuster_raw.txt"
    fi
    echo ""
    FOUND=$(wc -l < "$OUTPUT_DIR/gobuster_raw.txt" 2>/dev/null || echo 0)
    echo "  → gobuster found $FOUND paths"
else
    echo "  ⚠ gobuster not installed. Run: sudo apt install gobuster"
fi

# ── METHOD 2: dirb (classic) ─────────────────────────────────
echo ""
echo "[2/4] DIRB — Classic web content scanner"
if command -v dirb &>/dev/null; then
    dirb "$TARGET" "$WORDLIST" \
        -o "$OUTPUT_DIR/dirb_raw.txt" \
        -r -S -N 404 2>/dev/null | grep -E "^\+" | tee -a "$RESULTS" || true
    echo "  → dirb results appended to results"
else
    echo "  ⚠ dirb not installed. Run: sudo apt install dirb"
fi

# ── METHOD 3: Look for common sensitive paths ─────────────────
echo ""
echo "[3/4] MANUAL CHECKS — Common sensitive endpoints"
SENSITIVE_PATHS=(
    "/.git/config"
    "/.env"
    "/admin"
    "/admin/login"
    "/administrator"
    "/wp-admin"
    "/wp-login.php"
    "/phpmyadmin"
    "/phpinfo.php"
    "/config.php"
    "/backup.zip"
    "/backup.tar.gz"
    "/db.sql"
    "/robots.txt"
    "/sitemap.xml"
    "/.well-known/security.txt"
    "/api"
    "/api/v1"
    "/api/v2"
    "/swagger"
    "/swagger-ui.html"
    "/actuator"
    "/actuator/env"
    "/server-status"
    "/server-info"
    "/.htaccess"
    "/crossdomain.xml"
    "/clientaccesspolicy.xml"
    "/WEB-INF/web.xml"
    "/META-INF/MANIFEST.MF"
)

echo ""
for path in "${SENSITIVE_PATHS[@]}"; do
    url="$TARGET$path"
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "ERR")
    if [[ "$status" == "200" ]]; then
        echo -e "  \033[92m[200 OK]  $url\033[0m"
        echo "$url [200]" >> "$RESULTS"
    elif [[ "$status" == "403" ]]; then
        echo -e "  \033[91m[403 FRB] $url\033[0m"
        echo "$url [403]" >> "$RESULTS"
    elif [[ "$status" == "301" || "$status" == "302" ]]; then
        echo -e "  \033[93m[$status RDR] $url\033[0m"
    fi
done

# ── METHOD 4: File extension fuzzing ─────────────────────────
echo ""
echo "[4/4] FILE EXTENSION SCAN — .bak .old .php .txt .sql"
EXTENSIONS=("bak" "old" "php~" "php.bak" "txt" "sql" "conf" "log" "zip" "tar.gz")
BASE_PATHS=("/index" "/config" "/backup" "/database" "/admin" "/setup" "/install")

for base in "${BASE_PATHS[@]}"; do
    for ext in "${EXTENSIONS[@]}"; do
        url="$TARGET${base}.${ext}"
        status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "$url" 2>/dev/null || echo "ERR")
        if [[ "$status" == "200" ]]; then
            echo -e "  \033[92m[FOUND] $url\033[0m"
            echo "$url [200 - $ext file]" >> "$RESULTS"
        fi
    done
done

# ── SUMMARY ──────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════════"
TOTAL=$(sort -u "$RESULTS" 2>/dev/null | wc -l || echo 0)
echo "✅ COMPLETE — $TOTAL findings saved to: $RESULTS"
echo ""
echo "All results:"
sort -u "$RESULTS" 2>/dev/null || echo "(none)"
echo "══════════════════════════════════════════════════════════"
