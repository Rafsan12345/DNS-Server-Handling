import threading
import socket
from tkinter import *
from tkinter import messagebox
from dnslib import RR, A, QTYPE, RCODE
from dnslib.server import DNSServer

DNS_TABLE = {
    "www.eslab.com.": "10.10.10.56"
}

dns_server = None
dns_thread = None

# ================= GUI =================

root = Tk()
root.title("Python DNS Server GUI")
root.geometry("520x420")

forward_google = BooleanVar(value=False)

# ================= DNS LOGIC =================

class MyDNS:
    def resolve(self, request, handler):
        reply = request.reply()
        qname = str(request.q.qname).lower()
        qtype = QTYPE[request.q.qtype]

        print("Query:", qname, qtype)

        if qtype == "A" and qname in DNS_TABLE:
            ip = DNS_TABLE[qname]
            reply.add_answer(RR(qname, QTYPE.A, rdata=A(ip), ttl=120))
            print("→ LOCAL:", ip)

        else:
            if forward_google.get():
                try:
                    real_ip = socket.gethostbyname(qname.rstrip("."))
                    reply.add_answer(RR(qname, QTYPE.A, rdata=A(real_ip), ttl=60))
                    print("→ FORWARDED:", real_ip)
                except:
                    reply.header.rcode = RCODE.NXDOMAIN
            else:
                reply.header.rcode = RCODE.NXDOMAIN
                print("→ BLOCKED")

        return reply


def start_dns():
    global dns_server, dns_thread
    if dns_server:
        messagebox.showinfo("Info", "DNS already running")
        return

    dns_server = DNSServer(MyDNS(), port=53, address="0.0.0.0")
    dns_thread = threading.Thread(target=dns_server.start)
    dns_thread.daemon = True
    dns_thread.start()

    messagebox.showinfo("DNS", "DNS Server Started on port 53")


def stop_dns():
    global dns_server
    if dns_server:
        dns_server.stop()
        dns_server = None
        messagebox.showinfo("DNS", "DNS Server Stopped")
    else:
        messagebox.showinfo("Info", "DNS not running")


def add_entry():
    domain = domain_entry.get().strip().lower()
    ip = ip_entry.get().strip()

    if not domain.endswith("."):
        domain += "."

    if domain and ip:
        DNS_TABLE[domain] = ip
        refresh_list()
        domain_entry.delete(0, END)
        ip_entry.delete(0, END)
    else:
        messagebox.showerror("Error", "Domain & IP required")


def delete_entry():
    try:
        selected = listbox.get(listbox.curselection())
        del DNS_TABLE[selected.split(" → ")[0]]
        refresh_list()
    except:
        pass


def refresh_list():
    listbox.delete(0, END)
    for d, i in DNS_TABLE.items():
        listbox.insert(END, f"{d} → {i}")

Label(root, text="Domain").pack()
domain_entry = Entry(root, width=40)
domain_entry.pack()

Label(root, text="IP Address").pack()
ip_entry = Entry(root, width=40)
ip_entry.pack()

Button(root, text="Add Entry", command=add_entry).pack(pady=5)
Button(root, text="Delete Selected", command=delete_entry).pack(pady=5)

listbox = Listbox(root, width=60)
listbox.pack(pady=10)

Checkbutton(
    root,
    text="Bypass unknown domains via Google DNS (8.8.8.8)",
    variable=forward_google
).pack()

Button(root, text="▶ Start DNS Server", bg="green", fg="white",
       command=start_dns).pack(pady=5)

Button(root, text="⏹ Stop DNS Server", bg="red", fg="white",
       command=stop_dns).pack(pady=5)

refresh_list()
root.mainloop()
