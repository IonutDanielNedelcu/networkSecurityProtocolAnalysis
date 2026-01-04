import socket, struct, sys
from datetime import datetime

upstreamDns = ('8.8.8.8', 53)    #serverul DNS la care forwardam cererile neblocate
fisierBlacklist = 'blacklist.txt'    #fisierul cu domeniile care trebuie blocate
adresaAscultare = '0.0.0.0'          #ascultam pe toate interfetele
portAscultare = 53                #port DNS standard pe care ascultam

#incarcam lista de domenii de blocat intr-un set pentru verificare rapida
with open(fisierBlacklist, 'r') as f:
    domeniiBlocate = set()
    for linie in f:
        linie = linie.strip().lower()
        if not linie or linie.startswith('#'):
            continue
        parts = linie.split() #fiecare linie incepe cu 0.0.0.0 si abia dupa e domeniul
        domeniu = parts[1]
        domeniiBlocate.add(domeniu)

#deschidem fisierul in care vom scrie toate blocarile
fisierBlocari = open('/app/blocked.txt', 'a')

#cream socketul UDP si il legam pe portul 53
socketUdp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketUdp.bind((adresaAscultare, portAscultare))

#functie pentru citirea domeniului din cererea DNS
def parseDomeniu(dateCerere):
    #dateCerere repr continului pachetului in bytes
    pozitie = 12  #pentru ca header dns are 12 bytes
    etichete = [] #pentru componentele domeniului
    #separare componente
    while True:
        lungime = dateCerere[pozitie]
        if lungime == 0: #atunci este sfarsitul sirului de etichete
            pozitie = pozitie + 1
            break
        pozitie = pozitie + 1 #nu ne intereseaza octetul de lungime si saim peste el 
        etichete.append(dateCerere[pozitie:pozitie+lungime].decode())
        pozitie += lungime #trecem la urmatoarea componenta
    return '.'.join(etichete), pozitie #pozitia este practic pozitia din buffer dupa ultimul byte

#functie in care construim raspunsul pentru dom blocat
def constrRaspBlocat(dateCerere, domeniuOffset):
    #extragem din headerul initial datele urmatoare
    idTranzactie, flags, qdcount = struct.unpack('!HHH', dateCerere[:6])
    #setam QR=1 (marcam pachetul cu raspuns) si RA=1 (recursion available)
    flagsRaspuns = 0x8000 | 0x0100

    #header nou cu un singur raspuns
    headerRaspuns = struct.pack(
        '!HHHHHH',
        idTranzactie, #originaluk
        flagsRaspuns, #cele schimbate
        qdcount, #nemodificat
        1,  #un raspuns in sectiunea Answer (ancount)
        0, #nscount
        0 #arcount
    )

    #pastram sectiunea querry nemodificata
    sectiuneQuestion = dateCerere[12:domeniuOffset+4]

    #construim recordul A (0.0.0.0)
    recordRaspuns = (
        b'\xc0\x0c'                  #pointer la offset 12
        + struct.pack('!H', 1)        #type=A
        + struct.pack('!H', 1)        #class=in
        + struct.pack('!I', 60)       #TTL=60 s
        + struct.pack('!H', 4)        #lungime 4 octeti
        + socket.inet_aton('0.0.0.0') # ip
    )
    #returnam modificarile
    return headerRaspuns + sectiuneQuestion + recordRaspuns

#functie care trimite cererea la server si intoarce raspunsul
def trimitereLaUpstream(dateCerere):
    #facem un socket udp temporar pentru comuncarea cu serverul
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socketUpstream:
        socketUpstream.settimeout(3)
        socketUpstream.sendto(dateCerere, upstreamDns)
        #asteptam raspunsul serverului upstream
        try:
            dataUpstream, _ = socketUpstream.recvfrom(4096) #numarul maxim de bytes
            return dataUpstream
        except socket.timeout:
            return None

#procesam cererile DNS
while True:
    try:
        #primim pachetul DNS si adresa clientului (IP, port)
        pachetCerere, adresaClient = socketUdp.recvfrom(4096)

        #extragem domeniul si pozitia dupa qname
        numeDomeniu, pozOffset = parseDomeniu(pachetCerere)
        numeLower = numeDomeniu.lower()

        # verificam daca domeniul este in lista de blocat 
        if numeLower in domeniiBlocate:
            # locam domeniul
            timp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            mesajLog = f"{timp} BLOCKED {numeDomeniu}\n"
            # afisam in consola si salvam in fisier cu append+flush
            print(mesajLog, end='')
            fisierBlocari.write(mesajLog)
            #construim raspunsul DNS in formatul cerut
            raspuns = constrRaspBlocat(pachetCerere, pozOffset)
        else:
            #trimitem cererea la DNS-ul upstream
            raspUp = trimitereLaUpstream(pachetCerere)
            if raspUp is None:
                #daca upstream nu raspunde, intoarcem NXDOMAIN
                idTran, flagsInit, qdcount = struct.unpack('!HHH', pachetCerere[:6])
                flagsInit = flagsInit | 0x0003  # setam rcode = 3
                #construim headerul fara raspunsuri
                headerNx = struct.pack('!HHHHHH', idTran, flagsInit, qdcount, 0, 0, 0)
                raspuns = headerNx + pachetCerere[12:pozOffset+4]
            else:
                #primim raspunsul normal de la upstream
                raspuns = raspUp
        #trimitem raspunsul inapoi clientului
        socketUdp.sendto(raspuns, adresaClient)

    except KeyboardInterrupt:
        print("\n DNS blocker oprit")
        break
    except Exception as err:
        # orice alta eroare este afisata in consola
        print(f"Eroare: {err}")

fisierBlocari.close()
socketUdp.close()