"""
levels/level1_recon.py — Level 1: Reconnaissance
5 tasks covering OSINT, DNS, subdomains, Google dorks, Whois.
"""

from levels.base_level import BaseLevel, Task


class Level1Recon(BaseLevel):
    level_num = 1
    level_name = "Reconnaissance"
    concept = """Reconnaissance (recon) is the FIRST phase of any security assessment.
Before you touch a single tool, you gather intelligence. The more you know about the target,
the more precisely you can look for weaknesses.

There are two types:
• PASSIVE recon — You gather info WITHOUT touching the target's servers.
  Examples: WHOIS, Google dorks, Shodan, DNS lookups, certificate transparency logs.

• ACTIVE recon — You interact directly with the target.
  Examples: port scanning, directory brute force, banner grabbing.

In bug bounty, PASSIVE recon keeps you legally safe while scoping the target.
Always do passive recon first. Know the scope before you send a single packet.

Key tools: whois, nslookup, dig, subfinder, amass, theHarvester, shodan, crt.sh"""

    tools = ["whois", "dig", "nslookup", "subfinder", "amass", "theHarvester", "crt.sh"]

    def _build_tasks(self):
        return [
            Task(
                task_id="L1_T1",
                title="WHOIS Lookup",
                description=(
                    "Perform a WHOIS lookup on 'hackerone.com'. "
                    "Find the registrar name from the WHOIS output. "
                    "Command: whois hackerone.com"
                ),
                tool_suggestion="whois hackerone.com",
                expected_output="Name of the domain registrar (e.g., 'MarkMonitor')",
                hint="Look for 'Registrar:' line in the whois output.",
                validator=lambda a: any(w in a.lower() for w in
                    ["markmonitor", "registrar", "godaddy", "namecheap", "network solutions",
                     "cloudflare", "enom", "tucows", "pdr"]),
                points=100,
            ),
            Task(
                task_id="L1_T2",
                title="DNS Enumeration",
                description=(
                    "Use 'dig' to find the MX (mail) records of 'hackerone.com'. "
                    "What mail server handles email for this domain? "
                    "Command: dig MX hackerone.com"
                ),
                tool_suggestion="dig MX hackerone.com",
                expected_output="Mail exchange hostname (e.g., 'aspmx.l.google.com')",
                hint="Look for lines with 'MX' in the ANSWER SECTION of dig output.",
                validator=lambda a: any(w in a.lower() for w in
                    ["mx", "mail", "google", "aspmx", "smtp", "exchange",
                     "mailgun", "sendgrid", "protection.outlook"]),
                points=100,
            ),
            Task(
                task_id="L1_T3",
                title="Subdomain Discovery",
                description=(
                    "Use subfinder or amass to enumerate subdomains of 'testphp.vulnweb.com'. "
                    "How many subdomains did you discover? "
                    "Command: subfinder -d testphp.vulnweb.com  OR  amass enum -d testphp.vulnweb.com"
                ),
                tool_suggestion="subfinder -d testphp.vulnweb.com",
                expected_output="Number of subdomains found (e.g., '3') or a subdomain name",
                hint="Count the lines in the subfinder output. Even finding 0–2 is a valid answer.",
                validator=lambda a: (
                    a.strip().isdigit() or
                    "vulnweb" in a.lower() or
                    "subdomain" in a.lower() or
                    "found" in a.lower() or
                    len(a.strip()) > 2
                ),
                points=150,
            ),
            Task(
                task_id="L1_T4",
                title="Google Dork — Directory Listing",
                description=(
                    "Use Google to find open directory listings. "
                    "Search Google for: site:testphp.vulnweb.com intitle:\"index of\"\n"
                    "OR try the dork: inurl:admin site:vulnweb.com\n"
                    "Enter the Google dork you used."
                ),
                tool_suggestion="Google Search / DuckDuckGo",
                expected_output="The Google dork query you entered",
                hint="Google dorks use operators like site:, intitle:, inurl:, filetype:, ext:",
                validator=lambda a: any(op in a.lower() for op in
                    ["site:", "intitle:", "inurl:", "filetype:", "ext:",
                     "index of", "admin", "vulnweb"]),
                points=100,
            ),
            Task(
                task_id="L1_T5",
                title="Certificate Transparency — crt.sh",
                description=(
                    "Visit https://crt.sh/?q=hackerone.com in your browser. "
                    "Certificate transparency logs expose ALL subdomains with SSL certs. "
                    "Find one subdomain of hackerone.com from crt.sh results."
                ),
                tool_suggestion="Browser → https://crt.sh/?q=hackerone.com",
                expected_output="A subdomain of hackerone.com (e.g., 'api.hackerone.com')",
                hint="Look at the 'Name Value' column in the crt.sh table for *.hackerone.com entries.",
                validator=lambda a: "hackerone.com" in a.lower() and "." in a,
                points=150,
            ),
        ]
