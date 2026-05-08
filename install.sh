#!/bin/bash
# ============================================================
# install.sh — One-shot installer for Bug Bounty Trainer
# Run as normal user (will sudo when needed)
# Usage: bash install.sh
# ============================================================

set -euo pipefail

GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
CYAN='\033[96m'
RESET='\033[0m'

ok()   { echo -e "${GREEN}[✓]${RESET} $*"; }
warn() { echo -e "${YELLOW}[!]${RESET} $*"; }
err()  { echo -e "${RED}[✗]${RESET} $*"; }
info() { echo -e "${CYAN}[*]${RESET} $*"; }

TRAINER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}"
cat << 'BANNER'
╔══════════════════════════════════════════════════════════════╗
║       BUG BOUNTY TRAINER — INSTALLER                         ║
║       Setting up your complete hacking lab                   ║
╚══════════════════════════════════════════════════════════════╝
BANNER
echo -e "${RESET}"

# ── Step 1: Check OS ─────────────────────────────────────────
info "Checking system..."
if grep -qi "kali" /etc/os-release 2>/dev/null; then
    ok "Kali Linux detected"
elif grep -qi "ubuntu\|debian" /etc/os-release 2>/dev/null; then
    warn "Ubuntu/Debian detected — most steps will work"
else
    warn "Unknown OS — some package names may differ"
fi

# ── Step 2: Python check ─────────────────────────────────────
info "Checking Python 3..."
if command -v python3 &>/dev/null; then
    PYVER=$(python3 --version)
    ok "Found: $PYVER"
else
    err "Python 3 not found. Install: sudo apt install python3"
    exit 1
fi

# ── Step 3: Docker check ─────────────────────────────────────
info "Checking Docker..."
if command -v docker &>/dev/null; then
    ok "Docker found: $(docker --version)"
else
    warn "Docker not installed. Installing..."
    sudo apt update -qq
    sudo apt install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker "$USER"
    ok "Docker installed"
fi

# ── Step 4: docker-compose check ─────────────────────────────
info "Checking docker-compose..."
if command -v docker-compose &>/dev/null; then
    ok "docker-compose found"
else
    warn "docker-compose not found. Installing..."
    sudo apt install -y docker-compose
    ok "docker-compose installed"
fi

# ── Step 5: Create data directories ──────────────────────────
info "Creating data directories..."
mkdir -p "$TRAINER_DIR/data/reports"
mkdir -p "$TRAINER_DIR/data"
ok "Directories created"

# ── Step 6: Make scripts executable ──────────────────────────
info "Setting script permissions..."
chmod +x "$TRAINER_DIR/trainer.py"
chmod +x "$TRAINER_DIR/scripts/"*.sh
ok "Permissions set"

# ── Step 7: Check optional security tools ────────────────────
info "Checking security tools..."

TOOLS=("nmap" "nikto" "gobuster" "dirb" "sqlmap" "whatweb" "whois" "dig" "curl" "wget")
MISSING=()

for tool in "${TOOLS[@]}"; do
    if command -v "$tool" &>/dev/null; then
        ok "  $tool ✓"
    else
        warn "  $tool — not found"
        MISSING+=("$tool")
    fi
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo ""
    warn "Missing tools: ${MISSING[*]}"
    read -rp "  Install missing tools? (y/n): " INSTALL_TOOLS
    if [[ "$INSTALL_TOOLS" == "y" || "$INSTALL_TOOLS" == "Y" ]]; then
        sudo apt update -qq
        for tool in "${MISSING[@]}"; do
            info "Installing $tool..."
            sudo apt install -y "$tool" 2>/dev/null && ok "$tool installed" || warn "Could not install $tool"
        done
    fi
fi

# ── Step 8: Optional — start lab containers ──────────────────
echo ""
info "Docker Lab Setup"
read -rp "  Start DVWA + Juice Shop + WebGoat now? (y/n): " START_LAB

if [[ "$START_LAB" == "y" || "$START_LAB" == "Y" ]]; then
    info "Pulling Docker images (this may take a few minutes)..."
    cd "$TRAINER_DIR"

    docker-compose pull 2>/dev/null || warn "Some images failed to pull"
    docker-compose up -d 2>/dev/null || warn "Failed to start some containers"

    echo ""
    ok "Lab containers started!"
    echo ""
    echo "  Access your targets:"
    echo "  ┌─────────────────────────────────────────────────────┐"
    echo "  │  DVWA       → http://127.0.0.1:8080                 │"
    echo "  │  Juice Shop → http://127.0.0.1:3000                 │"
    echo "  │  WebGoat    → http://127.0.0.1:8081/WebGoat         │"
    echo "  └─────────────────────────────────────────────────────┘"
    echo ""
    echo "  DVWA setup: Login at http://127.0.0.1:8080"
    echo "  Username: admin  |  Password: password"
    echo "  Then go to Setup page and click 'Create/Reset Database'"
fi

# ── Step 9: Create launcher shortcut ─────────────────────────
info "Creating launcher shortcut..."
LAUNCHER="$HOME/.local/bin/bbt"
mkdir -p "$HOME/.local/bin"
cat > "$LAUNCHER" << LAUNCHEOF
#!/bin/bash
cd "$TRAINER_DIR"
python3 trainer.py
LAUNCHEOF
chmod +x "$LAUNCHER"

if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    warn "Added ~/.local/bin to PATH — run: source ~/.bashrc"
fi
ok "Launcher created: bbt (just type 'bbt' to start)"

# ── Done ─────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}"
cat << 'DONE'
╔══════════════════════════════════════════════════════════════╗
║  ✅  INSTALLATION COMPLETE!                                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Start the trainer:                                          ║
║    cd bugbounty-trainer && python3 trainer.py                ║
║    OR: bbt  (if PATH is updated)                             ║
║                                                              ║
║  Lab targets (if started):                                   ║
║    DVWA       → http://127.0.0.1:8080                        ║
║    Juice Shop → http://127.0.0.1:3000                        ║
║    WebGoat    → http://127.0.0.1:8081/WebGoat                ║
║                                                              ║
║  ⚠️  Remember: Only test authorized targets!                  ║
╚══════════════════════════════════════════════════════════════╝
DONE
echo -e "${RESET}"
