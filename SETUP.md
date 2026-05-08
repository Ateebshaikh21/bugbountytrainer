# 🔐 Bug Bounty Trainer — Setup Guide

> Complete this guide in order. Takes about 10 minutes.

---

## Requirements

| Requirement | Version | Check |
|---|---|---|
| OS | Kali Linux (recommended) | `uname -a` |
| Python | 3.10+ | `python3 --version` |
| Docker | Any recent | `docker --version` |
| Internet | Required for first activation | `ping google.com` |

---

## Step 1 — Clone the repo

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/bugbounty-trainer.git
cd bugbounty-trainer
```

---

## Step 2 — Install Docker (if not installed)

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker
```

---

## Step 3 — Start lab targets

```bash
docker-compose up -d
```

This starts:

| Target | URL | Login |
|---|---|---|
| DVWA | http://127.0.0.1:8080 | admin / password |
| Juice Shop | http://127.0.0.1:3000 | register on first visit |
| WebGoat | http://127.0.0.1:8081/WebGoat | register on first visit |

**DVWA first-time setup:**
```bash
# Wait 10 seconds for containers to start, then:
curl -s -c /tmp/d.txt -d "username=admin&password=password&Login=Login" \
  http://127.0.0.1:8080/dvwa/login.php > /dev/null
curl -s -b /tmp/d.txt \
  "http://127.0.0.1:8080/dvwa/setup.php?setupdb=true" > /dev/null
echo "DVWA ready!"
```

---

## Step 4 — Launch the trainer

```bash
python3 trainer.py
```

On first run you'll see the **activation screen**.

---

## Step 5 — Activate your license

1. Get your license key from your **Gumroad receipt email**
2. Select option `[1] Activate full course`
3. Enter your **email** (used on Gumroad)
4. Enter your **license key** (from receipt)
5. You'll see: `🎉 ACTIVATION SUCCESSFUL! Welcome, [Your Name]`

> **Free preview:** Select option `[2]` to access Level 1 (Recon) for free.

---

## Step 6 — Install security tools (for hands-on tasks)

```bash
sudo apt install -y nmap nikto gobuster dirb sqlmap whatweb whois dnsrecon burpsuite wordlists
sudo gzip -d /usr/share/wordlists/rockyou.txt.gz
```

---

## Troubleshooting

### "Unable to connect" on activation
→ You need internet on first activation. Fix your connection and retry.

### "Device mismatch" error  
→ Your license is bound to another device. Contact support to reset.

### DVWA not loading  
→ Wait 15 seconds after `docker-compose up -d`, then try again.

### Nikto "Unable to connect"  
→ Make sure DVWA is running: `docker ps | grep dvwa`

### Port conflict on 8080
→ Burp Suite also uses 8080. Change Burp's proxy port to 8082 in Burp settings.

---

## Stop / restart lab

```bash
docker-compose down      # stop
docker-compose up -d     # start again
docker-compose down -v   # stop and delete all data (full reset)
```

---

## ⚠️ Legal reminder

This trainer is for **authorized testing on local lab targets only**.  
Never attack real systems without explicit written permission.

---

*Bug Bounty Trainer v2.0 — Stay ethical. Stay legal. Happy hacking! 🎯*
