from dnslib import DNSRecord, RR, QTYPE, A
from dnslib.server import DNSServer, BaseResolver
from datetime import datetime  # <-- add this

# Custom DNS table
DNS_TABLE = {
    "chatgpt.com.": "172.64.155.209",
    "ab.chatgpt.com.": "172.64.155.209",
    "auth.openai.com.": "104.18.41.241",
    "cdn.oaistatic.com.": "104.18.41.158",
    "www.google.com.": "216.239.38.120",
}

# Color codes
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

# Specify the IP you want to monitor
MONITOR_IP = "172.64.155.209"

class MyDNS(BaseResolver):
    def resolve(self, request, handler):
        reply = request.reply()
        qname = str(request.q.qname).lower()
        client_ip = handler.client_address[0]

        ip = DNS_TABLE.get(qname)
        if ip:
            reply.add_answer(RR(qname, QTYPE.A, rdata=A(ip), ttl=60))
            
            # Print colorful log
            print(f"{GREEN}requested:{RESET} {YELLOW}{qname}{RESET} -> {GREEN}{ip}{RESET}")
            
            # If IP matches MONITOR_IP, write a note to file with date & time
            if ip == MONITOR_IP:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open("dns_monitor_log.txt", "a") as f:
                    f.write(f"[{now}] {client_ip} requested {qname} -> {ip}\n")
        return reply

# Disable dnslib internal logs completely
server = DNSServer(MyDNS(), port=53, address="0.0.0.0", logger=None)
server.start_thread()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("DNS server stopped.")
