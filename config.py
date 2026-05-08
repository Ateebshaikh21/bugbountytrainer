"""
config.py — Bug Bounty Trainer · Production Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All constants live here. Edit only this file — nothing else.
"""

import os as _os

# ── Dodo Payments ─────────────────────────────────────────────────────────────

DODO_PRODUCT_NAME = "Bug Bounty Trainer"
DODO_PURCHASE_URL = "https://dodopayments.com"  # replace with your Dodo payment link

# ── License Security ──────────────────────────────────────────────────────────

# Strong 256-bit HMAC secret — used to sign and verify license keys locally.
# Do not change after first release — invalidates all existing keys.
# Do NOT ship this value publicly. Keep it in your build environment only.
HMAC_SECRET = "64da185248ae05a4df6d9fe571b9b0f83d013e4082f7dff6def5255d8169eba9"

# Maximum failed activation attempts before the program exits.
MAX_ACTIVATION_ATTEMPTS = 3

# ── Trainer Metadata ──────────────────────────────────────────────────────────

TRAINER_VERSION = "2.0"
TRAINER_NAME    = "Bug Bounty Trainer"

# ── Lab Targets ───────────────────────────────────────────────────────────────

LAB_TARGETS = {
    "dvwa":      "http://127.0.0.1:8080",
    "juiceshop": "http://127.0.0.1:3000",
    "webgoat":   "http://127.0.0.1:8081/WebGoat",
}
