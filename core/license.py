"""
core/license.py — Offline Cryptographic License System v4.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Features:
  • Fully offline — zero network calls, zero hosting
  • Keys are HMAC-SHA256 signed tokens — unforgeable without HMAC_SECRET
  • verify_license_key() validates signature locally in microseconds
  • Email is embedded in the key payload — no separate DB needed
  • Machine binding — SHA-256 hash of MAC + machine-id + hostname
  • HMAC-SHA256 tamper detection on license.json
  • Offline after first activation (which is also offline)
  • Free preview mode — Level 1 free, Levels 2-5 locked
  • Max 3 failed attempts then forced exit
  • Compatible with Dodo automatic key delivery (Dodo emails the key)
"""

import os
import sys
import json
import uuid
import hmac
import hashlib
import base64
import time
from datetime import datetime

# ── Constants (sourced from config.py so only one place to edit) ─────────────

# Add project root to path so config.py is always findable
_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config import (                          # noqa: E402
    DODO_PURCHASE_URL,
    HMAC_SECRET             as _INTEGRITY_SECRET,
    MAX_ACTIVATION_ATTEMPTS as MAX_ATTEMPTS,
)

# License storage — hidden dot-file, chmod 600
_LICENSE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "data", ".license.json"
)


# ── Machine Fingerprinting ────────────────────────────────────────────────────

def get_machine_id() -> str:
    """
    Build a stable, unique device fingerprint.
    Combines MAC address + /etc/machine-id + hostname, then SHA-256 hashes it.
    Raw hardware values are never stored — only the hash is saved.
    Stable across reboots; changes only on major hardware replacement.
    """
    components = []

    # 1. MAC address (primary NIC)
    try:
        mac = uuid.getnode()
        # Real MACs have bit-40 = 0 (locally administered bit)
        if (mac >> 40) % 2 == 0:
            components.append(str(mac))
    except Exception:
        pass

    # 2. Linux machine-id (most reliable on Kali/Ubuntu)
    for path in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        try:
            if os.path.exists(path):
                with open(path) as f:
                    val = f.read().strip()
                if val:
                    components.append(val)
                    break
        except Exception:
            pass

    # 3. Windows MachineGUID fallback
    if len(components) < 2:
        try:
            import subprocess
            out = subprocess.run(
                ["wmic", "csproduct", "get", "UUID"],
                capture_output=True, text=True, timeout=5
            ).stdout
            for line in out.splitlines():
                line = line.strip()
                if line and line.upper() != "UUID":
                    components.append(line)
                    break
        except Exception:
            pass

    # 4. Hostname as supplemental factor
    try:
        import socket
        components.append(socket.gethostname())
    except Exception:
        pass

    # 5. Safety fallback so we always return something
    if not components:
        components = ["bbt_fallback_no_hardware"]

    raw = "|".join(components)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ── HMAC Tamper Protection ─────────────────────────────────────────────────────

def _compute_hmac(data: dict) -> str:
    """HMAC-SHA256 over all license fields except 'signature'."""
    fields  = {k: v for k, v in sorted(data.items()) if k != "signature"}
    payload = json.dumps(fields, sort_keys=True, separators=(",", ":"))
    return hmac.new(
        _INTEGRITY_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def _sign(data: dict) -> dict:
    """Attach HMAC signature to license dict. Mutates and returns."""
    data["signature"] = _compute_hmac(data)
    return data


def _verify_integrity(data: dict) -> bool:
    """Return True only if the license dict is unmodified since signing."""
    if "signature" not in data:
        return False
    expected = _compute_hmac(data)
    stored   = data.get("signature", "")
    return hmac.compare_digest(expected, stored)  # constant-time compare


# ── License File I/O ──────────────────────────────────────────────────────────

def save_license(
    email: str,
    license_key: str,
    name: str,
    machine_id: str,
    uses_count: int = 1,
) -> None:
    """
    Write license.json with HMAC signature.
    File is chmod 600 so only the owner can read it.
    """
    os.makedirs(os.path.dirname(_LICENSE_PATH), exist_ok=True)
    data = {
        "email":        email.lower().strip(),
        "license_key":  license_key.strip().upper(),
        "name":         name,
        "machine_id":   machine_id,
        "uses_count":   uses_count,
        "activated_at": datetime.now().isoformat(),
        "version":      "2.0",
    }
    _sign(data)
    with open(_LICENSE_PATH, "w") as f:
        json.dump(data, f, indent=2)
    try:
        os.chmod(_LICENSE_PATH, 0o600)
    except Exception:
        pass


def load_license() -> dict | None:
    """
    Read and verify license.json.
    Returns None if:
      - File doesn't exist
      - JSON is corrupt
      - HMAC check fails (tampered)
    """
    if not os.path.exists(_LICENSE_PATH):
        return None
    try:
        with open(_LICENSE_PATH) as f:
            data = json.load(f)
        return data if _verify_integrity(data) else None
    except Exception:
        return None


def _delete_license() -> None:
    """Remove license file so user can re-activate cleanly."""
    try:
        os.remove(_LICENSE_PATH)
    except Exception:
        pass


# ── Cryptographic License Key Verification ───────────────────────────────────
#
# Key format (generated by keygen.py, seller-only):
#
#   BBT-<B32_PAYLOAD>-<B32_SIG8>
#
#   PAYLOAD = base32( JSON({"e": email, "n": name, "v": 1}) )
#   SIG     = HMAC-SHA256(HMAC_SECRET, PAYLOAD)[:8 bytes] → base32
#
# Verification steps (all local, no network):
#   1. Split key into PAYLOAD + SIG parts
#   2. Recompute HMAC over PAYLOAD using embedded HMAC_SECRET
#   3. Compare first 8 bytes of digest with SIG (constant-time)
#   4. Decode PAYLOAD → extract email, name
#   5. Check supplied email matches embedded email
#
# Security properties:
#   - Cannot forge a key without HMAC_SECRET
#   - Truncated 8-byte sig = 64-bit security (sufficient for offline use)
#   - Email is bound inside the key — no external DB needed
#   - Machine binding happens in license.json (HMAC-protected separately)

def verify_license_key(license_key: str, email: str) -> dict:
    """
    Verify a signed license key entirely offline.

    Args:
        license_key: Key from purchase receipt (BBT-... format)
        email:       Email used at checkout

    Returns:
        {
          "valid":      bool,
          "name":       str,
          "uses_count": int,   always 1 on success
          "error":      str,
          "error_code": str,   INVALID_KEY | EMAIL_MISMATCH
        }
    """
    result = {
        "valid":      False,
        "name":       "",
        "uses_count": 0,
        "error":      "",
        "error_code": "",
    }

    key = license_key.strip().upper().replace(" ", "")

    # ── Split into parts ──────────────────────────────────────────────────────
    # Expected: BBT-<PAYLOAD>-<SIG8>
    parts = key.split("-")
    if len(parts) < 3 or parts[0] != "BBT":
        result["error"]      = "Invalid key format. Keys start with BBT-"
        result["error_code"] = "INVALID_KEY"
        return result

    # Last segment is the signature, everything between BBT- and sig is payload
    sig_b32   = parts[-1]
    payload_b32 = "-".join(parts[1:-1])

    # ── Recompute signature ───────────────────────────────────────────────────
    try:
        expected_full = hmac.new(
            _INTEGRITY_SECRET.encode("utf-8"),
            payload_b32.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        # Truncate to 8 bytes → 64-bit, encode as base32, strip padding
        expected_sig = base64.b32encode(expected_full[:8]).decode("utf-8").rstrip("=")
    except Exception:
        result["error"]      = "Key verification failed internally."
        result["error_code"] = "INVALID_KEY"
        return result

    # ── Constant-time signature comparison ───────────────────────────────────
    if not hmac.compare_digest(expected_sig, sig_b32):
        result["error"]      = "License key is invalid or has been tampered with."
        result["error_code"] = "INVALID_KEY"
        return result

    # ── Decode payload ────────────────────────────────────────────────────────
    try:
        # Re-add base32 padding
        padded = payload_b32 + "=" * ((8 - len(payload_b32) % 8) % 8)
        payload_json = base64.b32decode(padded).decode("utf-8")
        payload = json.loads(payload_json)
    except Exception:
        result["error"]      = "License key payload is corrupt."
        result["error_code"] = "INVALID_KEY"
        return result

    # ── Email match ───────────────────────────────────────────────────────────
    key_email = payload.get("e", "").lower().strip()
    if key_email != email.lower().strip():
        result["error"] = (
            f"Email does not match this license key. "
            f"Use the email from your purchase receipt."
        )
        result["error_code"] = "EMAIL_MISMATCH"
        return result

    # ── All checks passed ─────────────────────────────────────────────────────
    result["valid"]      = True
    result["name"]       = payload.get("n", "").strip() or email.split("@")[0].title()
    result["uses_count"] = 1
    return result


# ── Authentication Gate ────────────────────────────────────────────────────────

def authenticate(ui) -> dict:
    """
    Main auth entry point — called once at startup before anything else runs.

    Flow:
      1. Same machine + valid license  → silent auto-login
      2. Different machine             → hard block + exit
      3. Tampered license.json         → delete file + re-activate
      4. No license                    → activation flow (max 3 attempts)

    Returns a license dict on success.
    Calls sys.exit() on unrecoverable failures.
    """
    machine_id = get_machine_id()
    stored     = load_license()

    # ── Case 1: Returning user, same device ───────────────────────────────────
    if stored and stored.get("machine_id") == machine_id:
        _welcome_back(ui, stored["name"], stored["email"])
        return stored

    # ── Case 2: License from a different device ────────────────────────────────
    if stored and stored.get("machine_id") != machine_id:
        _show_device_mismatch(ui)
        sys.exit(1)

    # ── Case 3: File exists but integrity check failed (tampered) ─────────────
    if os.path.exists(_LICENSE_PATH) and stored is None:
        _show_tamper_warning(ui)
        _delete_license()
        time.sleep(1.5)
        # fall through to activation

    # ── Case 4: No license → activation screen ────────────────────────────────
    return _run_activation_flow(ui, machine_id)


def _run_activation_flow(ui, machine_id: str) -> dict:
    """
    Interactive activation loop with attempt counter.
    Exits program after MAX_ATTEMPTS failed verifications.
    """
    failed = 0

    while True:
        _draw_activation_screen(ui, failed)
        choice = ui.prompt("Select option")

        if choice == "0" or choice is None:
            ui.print_color("\n  Goodbye!\n", "dim")
            sys.exit(0)

        elif choice == "2":
            _draw_preview_screen(ui)
            return {"preview": True, "name": "Guest", "email": ""}

        elif choice == "1":
            outcome = _collect_and_verify(ui, machine_id)

            # None = bad input format → don't count as attempt
            if outcome is None:
                continue

            # "FAILED" = server returned invalid → count as attempt
            if outcome == "FAILED":
                failed += 1
                remaining = MAX_ATTEMPTS - failed
                if remaining <= 0:
                    _show_lockout(ui)
                    sys.exit(1)
                ui.print_color(
                    f"\n  ⚠️  {remaining} attempt(s) left before lockout.\n",
                    "yellow"
                )
                ui.pause()
                continue

            # outcome is a valid license dict
            return outcome

        else:
            ui.warn("Invalid choice. Enter 1, 2, or 0.")
            ui.pause()


def _collect_and_verify(ui, machine_id: str) -> "dict | str | None":
    """
    Collect email + license key, verify cryptographically (offline), save on success.

    Returns:
        dict     — valid license (success)
        "FAILED" — invalid key or email mismatch (counts as attempt)
        None     — bad input format (no attempt counted)
    """
    ui.clear()
    ui.print_color("\n  🔐  ENTER YOUR LICENSE DETAILS\n", "cyan")
    ui.print_color(
        "  Use the email and license key from your purchase receipt.\n",
        "dim"
    )

    # Email
    email = ui.prompt("  📧  Email (used at checkout)")
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        ui.error("Invalid email. Enter the email you used to purchase.")
        ui.pause()
        return None

    # License key
    key = ui.prompt("  🔑  License key (from your receipt)")
    if not key or len(key.strip()) < 6:
        ui.error("License key too short. Copy it directly from your receipt.")
        ui.pause()
        return None

    ui.print_color("\n  ⏳  Verifying...\n", "yellow")
    time.sleep(0.4)

    result = verify_license_key(key, email)

    # Invalid key or tampered — counts as attempt
    if not result["valid"]:
        reason = result["error"]
        if len(reason) > 53:
            reason = reason[:50] + "..."
        ui.clear()
        ui.print_color(f"""
  ╔══════════════════════════════════════════════════════════════╗
  ║  ❌  ACCESS DENIED                                           ║
  ╠══════════════════════════════════════════════════════════════╣
  ║                                                              ║
  ║  Reason: {reason:<53}║
  ║                                                              ║
  ║  Troubleshooting tips:                                       ║
  ║    • Use the exact email from your purchase receipt          ║
  ║    • Copy the license key carefully — no extra spaces        ║
  ║    • Check spam folder for your receipt email                ║
  ║                                                              ║
  ║  Don't have a license yet?                                   ║
  ║  🔒  Buy here: {DODO_PURCHASE_URL:<47}║
  ╚══════════════════════════════════════════════════════════════╝
""", "red")
        ui.pause()
        return "FAILED"

    # ── Valid — save and return ───────────────────────────────────────────────
    save_license(email, key, result["name"], machine_id, result["uses_count"])
    stored = load_license()

    _draw_success_screen(ui, result["name"])
    return stored


# ── Screen Renderers ──────────────────────────────────────────────────────────

def _draw_activation_screen(ui, failed: int) -> None:
    ui.clear()
    attempt_warn = ""
    if failed > 0:
        rem = MAX_ATTEMPTS - failed
        attempt_warn = f"  ║  ⚠️  {rem} attempt(s) remaining before lockout{' ' * 13}║\n"

    ui.print_color(f"""
  ╔══════════════════════════════════════════════════════════════╗
  ║          🔐  BUG BOUNTY TRAINER — ACTIVATION                 ║
  ╠══════════════════════════════════════════════════════════════╣
  ║                                                              ║
  ║  This is a paid course. Enter your license key to access     ║
  ║  all 5 levels, the final exam, and real bounty guidance.     ║
  ║                                                              ║
  ║  Don't have a license?                                       ║
  ║  🛒  Buy here: {DODO_PURCHASE_URL:<47}║
  ║                                                              ║
  ║  ✅  FREE PREVIEW: Level 1 — Recon (5 tasks) is free         ║
  ║                                                              ║
{attempt_warn}  ╚══════════════════════════════════════════════════════════════╝
""", "cyan")

    ui.menu([
        ("1", "Activate full course  (Enter license key)"),
        ("2", "Free preview         (Level 1 only — no key needed)"),
        ("0", "Exit"),
    ])


def _draw_success_screen(ui, name: str) -> None:
    display = (name[:50] + "...") if len(name) > 50 else name
    ui.clear()
    ui.print_color(f"""
  ╔══════════════════════════════════════════════════════════════╗
  ║  🎉  ACTIVATION SUCCESSFUL!                                  ║
  ╠══════════════════════════════════════════════════════════════╣
  ║                                                              ║
  ║  Welcome, {display:<53}║
  ║                                                              ║
  ║  ✅  All 5 training levels unlocked                          ║
  ║  ✅  Final exam unlocked                                     ║
  ║  ✅  Real bug bounty guidance unlocked                       ║
  ║  ✅  Automation tools unlocked                               ║
  ║  ✅  Report generator unlocked                               ║
  ║  ✅  License bound to this device                            ║
  ║                                                              ║
  ║  Happy Hacking! 🎯  Stay ethical. Stay legal.               ║
  ╚══════════════════════════════════════════════════════════════╝
""", "green")
    time.sleep(2.5)


def _draw_preview_screen(ui) -> None:
    ui.clear()
    ui.print_color(f"""
  ╔══════════════════════════════════════════════════════════════╗
  ║  ℹ️   FREE PREVIEW MODE                                       ║
  ╠══════════════════════════════════════════════════════════════╣
  ║                                                              ║
  ║  ✅  Level 1 — Recon           5 tasks    FREE               ║
  ║  🔒  Level 2 — Scanning        5 tasks    Locked             ║
  ║  🔒  Level 3 — Web Vulns       5 tasks    Locked             ║
  ║  🔒  Level 4 — Exploitation    5 tasks    Locked             ║
  ║  🔒  Level 5 — Reporting       5 tasks    Locked             ║
  ║  🔒  Final Exam                           Locked             ║
  ║  🔒  Real Bug Bounty Guide                Locked             ║
  ║  🔒  Automation Tools                     Locked             ║
  ║  🔒  Report Generator                     Locked             ║
  ║                                                              ║
  ║  Upgrade anytime — restart and enter your license key.       ║
  ║  🛒  {DODO_PURCHASE_URL:<58}║
  ╚══════════════════════════════════════════════════════════════╝
""", "yellow")
    time.sleep(1)
    ui.pause()


def _welcome_back(ui, name: str, email: str) -> None:
    ui.print_color(f"\n  ✅  Welcome back, {name}! ({email})\n", "green")
    time.sleep(0.7)


def _show_device_mismatch(ui) -> None:
    ui.clear()
    ui.print_color(f"""
  ╔══════════════════════════════════════════════════════════════╗
  ║  ⚠️   DEVICE MISMATCH — ACCESS BLOCKED                       ║
  ╠══════════════════════════════════════════════════════════════╣
  ║                                                              ║
  ║  This license is already activated on another device.        ║
  ║  Each license is valid for ONE device only.                  ║
  ║                                                              ║
  ║  Changed hardware or reinstalled OS? Contact support.        ║
  ║                                                              ║
  ║  Need a new license for this device:                         ║
  ║  🛒  {DODO_PURCHASE_URL:<58}║
  ╚══════════════════════════════════════════════════════════════╝
""", "yellow")


def _show_tamper_warning(ui) -> None:
    ui.clear()
    ui.print_color("""
  ╔══════════════════════════════════════════════════════════════╗
  ║  ❌  LICENSE FILE TAMPERED — DELETED                         ║
  ╠══════════════════════════════════════════════════════════════╣
  ║                                                              ║
  ║  The license file was manually edited and is invalid.        ║
  ║  It has been deleted. Re-enter your license key below.       ║
  ║                                                              ║
  ╚══════════════════════════════════════════════════════════════╝
""", "red")
    time.sleep(1.5)


def _show_lockout(ui) -> None:
    ui.clear()
    ui.print_color(f"""
  ╔══════════════════════════════════════════════════════════════╗
  ║  🚫  TOO MANY FAILED ATTEMPTS                                ║
  ╠══════════════════════════════════════════════════════════════╣
  ║                                                              ║
  ║  {MAX_ATTEMPTS} failed attempts. Program locked for security.             ║
  ║                                                              ║
  ║  Restart the trainer to try again with valid credentials.    ║
  ║                                                              ║
  ║  Purchase a valid license:                                   ║
  ║  🔒  {DODO_PURCHASE_URL:<58}║
  ╚══════════════════════════════════════════════════════════════╝
""", "red")
    time.sleep(1)


# ── Public Guards ─────────────────────────────────────────────────────────────

def is_preview_mode(license_data: dict) -> bool:
    """True if running in free preview (no paid license)."""
    return bool(license_data.get("preview", False))


def check_level_access(level_num: int, license_data: dict, ui) -> bool:
    """
    Returns True if user may enter this level.
    Level 1 is always free.
    Levels 2-5 require a paid license — shows buy prompt if blocked.
    """
    if level_num == 1:
        return True

    if is_preview_mode(license_data):
        ui.clear()
        ui.print_color(f"""
  ╔══════════════════════════════════════════════════════════════╗
  ║  🔒  LEVEL {level_num} IS LOCKED — UPGRADE REQUIRED                    ║
  ╠══════════════════════════════════════════════════════════════╣
  ║                                                              ║
  ║  You're in FREE PREVIEW — only Level 1 (Recon) is free.     ║
  ║                                                              ║
  ║  Unlock everything with a full license:                      ║
  ║  🛒  Buy here: {DODO_PURCHASE_URL:<47}║
  ║                                                              ║
  ║  After purchase:                                             ║
  ║    1. Restart the trainer                                    ║
  ║    2. Select "Activate full course"                          ║
  ║    3. Enter your email + license key from your receipt       ║
  ║                                                              ║
  ╚══════════════════════════════════════════════════════════════╝
""", "yellow")
        ui.pause()
        return False

    return True
