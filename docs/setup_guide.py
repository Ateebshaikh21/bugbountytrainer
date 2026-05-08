"""
docs/setup_guide.py — Complete lab setup guide with exact commands.
"""


def show_setup_guide(ui):
    while True:
        ui.clear()
        ui.section("🔧  LAB ENVIRONMENT SETUP GUIDE")
        ui.print_color("""
  This guide sets up your complete local hacking lab.
  All targets run in Docker — no VMs needed (except Metasploitable2).
""", "cyan")

        ui.menu([
            ("1", "Prerequisites — Docker & Tools"),
            ("2", "DVWA Setup"),
            ("3", "OWASP Juice Shop Setup"),
            ("4", "WebGoat Setup"),
            ("5", "Metasploitable2 — VM Setup"),
            ("6", "Full docker-compose.yml (all-in-one)"),
            ("7", "Burp Suite Setup Guide"),
            ("8", "Kali Linux Tools Installation"),
            ("0", "Back"),
        ])

        choice = ui.prompt("Select section")
        if choice == "0" or choice is None:
            return
        elif choice == "1":
            _prerequisites(ui)
        elif choice == "2":
            _dvwa_setup(ui)
        elif choice == "3":
            _juice_shop_setup(ui)
        elif choice == "4":
            _webgoat_setup(ui)
        elif choice == "5":
            _metasploitable_setup(ui)
        elif choice == "6":
            _full_compose(ui)
        elif choice == "7":
            _burp_setup(ui)
        elif choice == "8":
            _kali_tools(ui)


def _prerequisites(ui):
    ui.clear()
    ui.section("📦  PREREQUISITES")
    ui.print_color("""
  STEP 1: Update Kali Linux
  ─────────────────────────
  sudo apt update && sudo apt upgrade -y

  STEP 2: Install Docker
  ──────────────────────
  # Install Docker
  sudo apt install -y docker.io docker-compose

  # Start Docker service
  sudo systemctl start docker
  sudo systemctl enable docker

  # Add your user to docker group (no sudo needed)
  sudo usermod -aG docker $USER
  newgrp docker

  # Verify Docker works
  docker run hello-world

  STEP 3: Verify docker-compose
  ─────────────────────────────
  docker-compose --version
  # Should show: Docker Compose version 1.29.x or higher

  STEP 4: Create lab directory
  ─────────────────────────────
  mkdir -p ~/bugbounty-lab && cd ~/bugbounty-lab
""", "white")
    ui.pause()


def _dvwa_setup(ui):
    ui.clear()
    ui.section("🎯  DVWA — Damn Vulnerable Web Application")
    ui.print_color("""
  DVWA covers: XSS, SQLi, CSRF, File Upload, Command Injection, and more.
  Security levels: Low → Medium → High → Impossible

  OPTION A: Docker (Recommended)
  ──────────────────────────────
  docker run -d \\
    --name dvwa \\
    -p 8080:80 \\
    vulnerables/web-dvwa:latest

  # Access: http://127.0.0.1:8080
  # Default login: admin / password
  # After login: click "Create / Reset Database" button

  OPTION B: Docker with custom MySQL
  ────────────────────────────────────
  # Create docker-compose-dvwa.yml:
  cat > docker-compose-dvwa.yml << 'EOF'
  version: '3'
  services:
    dvwa:
      image: vulnerables/web-dvwa
      ports:
        - "8080:80"
      environment:
        - DB_SERVER=mysql
        - DB_PORT=3306
        - DB_DATABASE=dvwa
        - DB_USERNAME=dvwa
        - DB_PASSWORD=p@ssw0rd
      depends_on:
        - mysql
    mysql:
      image: mysql:5.7
      environment:
        - MYSQL_ROOT_PASSWORD=rootpassword
        - MYSQL_DATABASE=dvwa
        - MYSQL_USER=dvwa
        - MYSQL_PASSWORD=p@ssw0rd
      volumes:
        - dvwa_mysql:/var/lib/mysql
  volumes:
    dvwa_mysql:
  EOF

  docker-compose -f docker-compose-dvwa.yml up -d

  SETUP:
  ──────
  1. Open http://127.0.0.1:8080
  2. Login: admin / password
  3. Go to http://127.0.0.1:8080/dvwa/setup.php
  4. Click "Create / Reset Database"
  5. Login again
  6. Go to DVWA Security → Set to "Low"

  STOP/START:
  ────────────
  docker stop dvwa
  docker start dvwa
  docker logs dvwa   # view logs if issues
""", "white")
    ui.pause()


def _juice_shop_setup(ui):
    ui.clear()
    ui.section("🧃  OWASP Juice Shop")
    ui.print_color("""
  Juice Shop is the most modern vulnerable web app.
  Built with Angular + Node.js. Has 100+ challenges.

  DOCKER INSTALL:
  ───────────────
  docker run -d \\
    --name juice-shop \\
    -p 3000:3000 \\
    bkimminich/juice-shop:latest

  # Access: http://127.0.0.1:3000
  # No login needed to browse; register for challenges

  VERIFY IT'S RUNNING:
  ─────────────────────
  docker ps | grep juice-shop
  curl -s http://127.0.0.1:3000 | grep -i juice

  SCORE BOARD (cheat sheet):
  ───────────────────────────
  # Juice Shop has a hidden score board
  http://127.0.0.1:3000/#/score-board

  USEFUL JUICE SHOP CHALLENGES FOR TRAINING:
  ────────────────────────────────────────────
  ⭐    DOM XSS                    → Search for <iframe src="javascript:alert(`xss`)">
  ⭐    Login Admin                → admin@juice-sh.op'-- (SQL injection login bypass)
  ⭐    View Basket                → Change your basket ID to another user's
  ⭐⭐   Admin Registration         → Register with role "admin" in JSON body
  ⭐⭐   IDOR                       → Access /api/Users/1 with your JWT token
  ⭐⭐   Forged Coupon              → Manipulate coupon JWT
  ⭐⭐⭐  NoSQL Injection            → Find the admin panel password

  STOP/START:
  ────────────
  docker stop juice-shop
  docker start juice-shop
""", "white")
    ui.pause()


def _webgoat_setup(ui):
    ui.clear()
    ui.section("🐐  WebGoat — OWASP")
    ui.print_color("""
  WebGoat teaches web security through interactive lessons with explanations.
  Great for learning WHY vulnerabilities work, not just HOW.

  DOCKER INSTALL:
  ───────────────
  docker run -d \\
    --name webgoat \\
    -p 8081:8080 \\
    -p 9090:9090 \\
    -e TZ=America/New_York \\
    webgoat/goat-and-wolf

  # Access WebGoat:  http://127.0.0.1:8081/WebGoat
  # Access WebWolf:  http://127.0.0.1:9090/WebWolf

  FIRST-TIME SETUP:
  ──────────────────
  1. Go to http://127.0.0.1:8081/WebGoat
  2. Click "Register new user"
  3. Create your account
  4. Start lessons from the menu

  KEY LESSONS TO COMPLETE:
  ─────────────────────────
  • (A1) SQL Injection       — Hands-on SQLi practice
  • (A2) Broken Auth         — Session management attacks
  • (A3) XSS                 — All three types with exercises
  • (A5) Broken Access       — IDOR and authorization bypass
  • (A8) Insecure Deserialization
  • (A10) Server-Side Request Forgery (SSRF)

  WEBWOLF (attacker server):
  ───────────────────────────
  WebWolf acts as your attacker-controlled server.
  Used for: stolen cookies, SSRF callbacks, file upload tests.
  Access: http://127.0.0.1:9090/WebWolf

  STOP/START:
  ────────────
  docker stop webgoat
  docker start webgoat
""", "white")
    ui.pause()


def _metasploitable_setup(ui):
    ui.clear()
    ui.section("💀  Metasploitable2 — VM Setup")
    ui.print_color("""
  Metasploitable2 is an intentionally vulnerable Linux VM.
  It has network services with known CVEs — great for Metasploit practice.

  ⚠️  CRITICAL: Run Metasploitable2 in a HOST-ONLY network adapter.
      NEVER expose it to the internet or public network.

  DOWNLOAD:
  ──────────
  # Direct download (SourceForge):
  wget -c "https://sourceforge.net/projects/metasploitable/files/Metasploitable2/metasploitable-linux-2.0.0.zip"

  # Extract
  unzip metasploitable-linux-2.0.0.zip
  cd metasploitable-linux-2.0.0/

  VIRTUALBOX SETUP (Recommended):
  ─────────────────────────────────
  sudo apt install -y virtualbox

  # Import VM
  # In VirtualBox → File → Import Appliance
  # Select Metasploitable2.vmdk

  # CRITICAL: Network settings:
  # Settings → Network → Adapter 1:
  #   Attached to: Host-Only Adapter
  #   Name: vboxnet0

  # Default credentials: msfadmin / msfadmin

  VMWARE SETUP (Alternative):
  ─────────────────────────────
  # Open VMware Player → Open Virtual Machine
  # Select Metasploitable2.vmx
  # Network: Host-only

  VERIFY NETWORK:
  ────────────────
  # After booting Metasploitable2, check its IP:
  # (inside Metasploitable) ip addr show
  # Typically: 192.168.56.101 on vboxnet0

  # From Kali, verify connectivity:
  ping 192.168.56.101
  nmap -sV 192.168.56.101

  COMMON METASPLOITABLE2 VULNERABILITIES:
  ─────────────────────────────────────────
  Port 21  — vsftpd 2.3.4 backdoor     (CVE-2011-2523)
  Port 22  — OpenSSH weak creds
  Port 23  — Telnet (unencrypted)
  Port 25  — Postfix SMTP open relay
  Port 80  — DVWA, Tikiwiki, phpMyAdmin
  Port 445  — Samba "username map script" (CVE-2007-2447)
  Port 3306 — MySQL no root password
  Port 5432 — PostgreSQL default creds
  Port 8180 — Apache Tomcat default creds

  METASPLOIT QUICK START:
  ────────────────────────
  # On Kali:
  msfconsole
  msf6 > search vsftpd
  msf6 > use exploit/unix/ftp/vsftpd_234_backdoor
  msf6 exploit > set RHOSTS 192.168.56.101
  msf6 exploit > run
""", "white")
    ui.pause()


def _full_compose(ui):
    ui.clear()
    ui.section("🐳  Full docker-compose.yml — All-In-One Lab")
    ui.print_color("""
  Save this as ~/bugbounty-lab/docker-compose.yml
  Then run: docker-compose up -d
  All three targets start together.

  ──────────────────────────────────────────────────────────
""", "cyan")

    compose = """
version: '3.8'

services:
  # ═══════════════════════════════════════
  # DVWA — Damn Vulnerable Web Application
  # Access: http://127.0.0.1:8080
  # Login: admin / password
  # ═══════════════════════════════════════
  dvwa:
    image: vulnerables/web-dvwa:latest
    container_name: dvwa
    ports:
      - "8080:80"
    environment:
      - DB_SERVER=dvwa-mysql
      - DB_PORT=3306
      - DB_DATABASE=dvwa
      - DB_USERNAME=dvwa
      - DB_PASSWORD=p@ssw0rd
    depends_on:
      - dvwa-mysql
    networks:
      - lab-network
    restart: unless-stopped

  dvwa-mysql:
    image: mysql:5.7
    container_name: dvwa-mysql
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=dvwa
      - MYSQL_USER=dvwa
      - MYSQL_PASSWORD=p@ssw0rd
    volumes:
      - dvwa_mysql_data:/var/lib/mysql
    networks:
      - lab-network
    restart: unless-stopped

  # ═══════════════════════════════════════
  # OWASP Juice Shop
  # Access: http://127.0.0.1:3000
  # No login needed to start
  # ═══════════════════════════════════════
  juice-shop:
    image: bkimminich/juice-shop:latest
    container_name: juice-shop
    ports:
      - "3000:3000"
    networks:
      - lab-network
    restart: unless-stopped

  # ═══════════════════════════════════════
  # WebGoat + WebWolf
  # WebGoat: http://127.0.0.1:8081/WebGoat
  # WebWolf: http://127.0.0.1:9090/WebWolf
  # Register new user on first access
  # ═══════════════════════════════════════
  webgoat:
    image: webgoat/goat-and-wolf:latest
    container_name: webgoat
    ports:
      - "8081:8080"
      - "9090:9090"
    environment:
      - TZ=UTC
      - WEBGOAT_PORT=8080
      - WEBWOLF_PORT=9090
    networks:
      - lab-network
    restart: unless-stopped

networks:
  lab-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  dvwa_mysql_data:
"""
    print(compose)

    ui.print_color("""
  USAGE COMMANDS:
  ────────────────
  # Start all labs
  cd ~/bugbounty-lab && docker-compose up -d

  # Check all running
  docker-compose ps

  # View logs
  docker-compose logs -f juice-shop

  # Stop all labs
  docker-compose down

  # Stop and delete all data
  docker-compose down -v

  DVWA POST-SETUP:
  ─────────────────
  # After containers start, initialize DVWA database:
  sleep 5
  curl -s -c /tmp/dvwa_cookies.txt -b "security=low" \\
    -d "username=admin&password=password&Login=Login" \\
    http://127.0.0.1:8080/dvwa/login.php

  curl -s -b /tmp/dvwa_cookies.txt \\
    "http://127.0.0.1:8080/dvwa/setup.php?setupdb=true"
  echo "DVWA database initialized!"
""", "white")
    ui.pause()


def _burp_setup(ui):
    ui.clear()
    ui.section("🔫  Burp Suite Setup Guide")
    ui.print_color("""
  Burp Suite is your PRIMARY tool. Set it up before doing any web testing.

  INSTALL (Kali already has Community Edition):
  ──────────────────────────────────────────────
  which burpsuite      # check if installed
  sudo apt install -y burpsuite   # install if missing

  START BURP:
  ────────────
  burpsuite &   # runs in background

  BROWSER PROXY SETUP:
  ─────────────────────
  Firefox (Recommended):
    1. Install FoxyProxy addon: https://addons.mozilla.org/en-US/firefox/addon/foxyproxy-standard/
    2. Add proxy: 127.0.0.1 : 8080 (name it "Burp")
    3. Toggle on/off with one click

  Manual browser proxy:
    Firefox → Settings → Network Settings → Manual Proxy:
    HTTP Proxy: 127.0.0.1  Port: 8080

  IMPORT BURP CA CERTIFICATE (CRITICAL for HTTPS):
  ──────────────────────────────────────────────────
  1. With Burp proxy ON, visit: http://burp
  2. Click "CA Certificate" to download cacert.der
  3. Firefox → Settings → Privacy → Certificates → Import
  4. Import cacert.der → trust for websites

  Or via terminal:
  # Export cert from Burp
  curl -s http://127.0.0.1:8080/cert -o burp_cert.der

  # Import to Firefox (Kali)
  certutil -d sql:$HOME/.mozilla/firefox/*.default-esr -A \\
    -t "CT,," -n BurpSuiteCA -i burp_cert.der

  KEY BURP FEATURES:
  ───────────────────
  • Proxy → Intercept   — Toggle to catch/modify requests
  • Proxy → HTTP History — See ALL traffic
  • Repeater (Ctrl+R)   — Replay & modify any request
  • Intruder (Ctrl+I)   — Automated fuzzing/brute force
  • Decoder             — Base64/URL/HTML encode/decode
  • Comparer            — Diff two responses
  • Scanner (Pro only)  — Automated vuln scanner

  BURP TIPS:
  ───────────
  • Right-click any request → Send to Repeater
  • In Repeater: change params, headers, body → click Send
  • Use Proxy → Match & Replace to auto-modify requests
""", "white")
    ui.pause()


def _kali_tools(ui):
    ui.clear()
    ui.section("🐉  Kali Linux Tools Installation")
    ui.print_color("""
  Install all tools needed for this training:

  # Update first
  sudo apt update

  # RECON TOOLS
  sudo apt install -y \\
    whois \\
    dnsrecon \\
    dnsenum \\
    amass \\
    theharvester \\
    nmap \\
    masscan

  # Install subfinder (Go-based)
  go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
  # Or: sudo apt install -y subfinder

  # WEB SCANNING
  sudo apt install -y \\
    nikto \\
    gobuster \\
    dirb \\
    dirsearch \\
    wapiti \\
    whatweb \\
    sqlmap

  # EXPLOITATION
  sudo apt install -y \\
    burpsuite \\
    metasploit-framework \\
    hydra \\
    john \\
    hashcat

  # NUCLEI (template-based scanner)
  go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
  nuclei -update-templates

  # WORDLISTS
  sudo apt install -y wordlists
  sudo gzip -d /usr/share/wordlists/rockyou.txt.gz   # decompress

  # ADDITIONAL
  sudo apt install -y \\
    curl \\
    wget \\
    jq \\
    python3-pip \\
    git \\
    tmux \\
    net-tools

  # Python security libraries
  pip3 install requests beautifulsoup4 dnspython

  # VERIFY KEY TOOLS:
  nmap --version
  sqlmap --version
  gobuster version
  nikto -Version

  # Optional: Install OWASP ZAP
  sudo apt install -y zaproxy
""", "white")
    ui.pause()
