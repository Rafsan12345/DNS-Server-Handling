from dnslib import DNSRecord, RR, A, QTYPE
from dnslib.server import DNSServer
import socket

# === Custom DNS Table (local + external) ===
DNS_TABLE = {
    # Local custom domains
    "myserver.local.": "192.168.0.102",   # 8080 port server
    "iot.local.":      "192.168.1.20",
    "server.local.":   "192.168.1.30",

    # Professional / external info domains
    "google.com.":     "8.8.8.8",        # Example Google DNS
    "chat.openai.com.": "104.18.22.174"  # Example ChatGPT IP (Cloudflare)
}

class MyDNS:
    def resolve(self, request, handler):
        reply = request.reply()
        qname = str(request.q.qname).lower()
        print("Query:", qname)

        if qname in DNS_TABLE:
            ip = DNS_TABLE[qname]
            reply.add_answer(RR(qname, QTYPE.A, rdata=A(ip), ttl=60))
            print("→ Returned:", ip)
        else:
            # Forward other queries to real DNS server
            try:
                real_ip = socket.gethostbyname(qname.rstrip('.'))
                reply.add_answer(RR(qname, QTYPE.A, rdata=A(real_ip), ttl=60))
                print("→ Forwarded and returned:", real_ip)
            except Exception as e:
                print("→ Cannot resolve:", qname, e)
        return reply

server = DNSServer(MyDNS(), port=53, address="0.0.0.0")
print("DNS Server Running on port 53...")
server.start_thread()

while True:
    pass
