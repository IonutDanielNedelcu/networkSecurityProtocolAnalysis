import socket
import sys  #pentru citirea argumentelor din linia de comanda
import requests  #pentru apelul api de geolocatie
import time  # pentru masurarea RTT

#fisierul unde salvam rutele
fisierRute = open('rute_traceroute.txt', 'a')

#lista globala pentru plotare (lat, lon) - pun Bucuresti ca start ca sa avem cum sa stim de unde plecam
listaHopuri = [(44.4268,26.1025)]

# socket de UDP pentru trimiterea probelor
udp_send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
# socket RAW de citire a răspunsurilor ICMP
icmp_recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
# setam timout in cazul in care socketul ICMP la apelul recvfrom nu primeste nimic in buffer
icmp_recv_socket.settimeout(5) #era 3

#ipDestinatie: adresa IP sau hostname tinta
#portDestinatie: port UDP de start 
def traceroute(ipDestinatie, portDestinatie, impRecvSocket):
    # setam TTL in headerul de IP pentru socketul de UDP
    ttlCurent = 1
    maxHops = 64  #numarul maxim de hop-uri

    while ttlCurent <= maxHops:
        udp_send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttlCurent)

        #pregatim lista pentru timpi RTT si variabila ip
        timpiRTT = []
        adresaHop = None #vom retine IP-ul primului router care raspunde la probe, iar daca niciunul nu raspunde ramane None 
        tipICMP = codICMP = None #vom folosi aceste variabile pentru a stoca tipul si codul ICMP din raspuns

        # Trimitem 3 probe pe acelasi TTL
        for indexProbe in range(3):
            #crestem valoarea portului la fiecare pachet pentru a evita confundarea raspunsurilor
            #Routerele intermediare trimit inapoi pachetul original in mesajul ICMP, inclusiv portul care este flosit de traceroute ca "id" 
            portCurent = portDestinatie + indexProbe  
            start = time.time()  # retinem momentul trimiterii
            udp_send_sock.sendto(b'', (ipDestinatie, portCurent))  #trimitem pachetul UDP

            try:
                #asteptam raspuns ICMP
                date, infoAdresa = icmp_recv_socket.recvfrom(65535)
                durata = (time.time() - start) * 1000  #calculam RTT in ms
                timpiRTT.append(durata)
                ipHop = infoAdresa[0]
                #vom salva IP-ul primului raspuns
                if adresaHop is None:
                    adresaHop = ipHop

                #facem fallback dupa ip (daca ip-ul hopului este egal cu ip-ul destinatiei)
                if ipHop == ipDestinatie:
                    break

                
            except socket.timeout:
                #nu s-a primit raspuns in timp
                timpiRTT.append(None)


        # asteapta un mesaj ICMP de tipul ICMP TTL exceeded messages
        # in cazul nostru nu verificăm tipul de mesaj ICMP
        # puteti verifica daca primul byte are valoarea Type == 11
        # https://tools.ietf.org/html/rfc792#page-5
        # https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol#Header
        if adresaHop:
            text = f"{ttlCurent:2d}   {adresaHop:>15}"
        else:
            text = f"{ttlCurent:2d}   {'timeout':>15}"
        print(text, end=' ')
        fisierRute.write(text)

        #afisam timpii RTT pentru toate probele
        for rtt in timpiRTT:
            if rtt is None:
                text = f"    timeout"
            else:
                text = f"    {rtt:7.2f} ms"
            print(text, end=' ')
            fisierRute.write(text)
        fisierRute.write("\n")

        #apelez api pentru geolocatie   -  ex 2
        if adresaHop:
            try:
                raspuns = requests.get(f"http://ip-api.com/json/{adresaHop}", timeout=1) #era 5
                info = raspuns.json()
                if info.get("status") == "success":
                    oras   = info.get("city", "-")
                    regiune = info.get("regionName", "-")
                    tara   = info.get("country", "-")
                    lat = info.get("lat")
                    lon = info.get("lon")
                    print(f"      => {oras}, {regiune}, {tara}")
                    fisierRute.write(f"      => {oras}, {regiune}, {tara}\n")
                else:
                    #in caz de fail preluam mesajul de eroare
                    print(f"      => nu se poate obtine locatia: {info.get('message')}")
                    fisierRute.write(f"      => nu se poate obtine locatia: {info.get('message')}\n")
                    oras = regiune = tara = f"({info.get('message')})"
                    lat = lon = None
                #adaugam datele in listaHopuri pentru plotare
                listaHopuri.append((lat, lon))
            except Exception as e:
                print("      => eroare obtinere locatie:", e)
                fisierRute.write(f"      => eroare obtinere locatie: {e}\n")

        # Daca am gasit destinatia afisam si iesim
        if adresaHop == ipDestinatie:
            ok = 1
            final = "Ajuns la destinatie!\n\n"
            print(final)
            fisierRute.write(final)
            break

        ttlCurent += 1


#citim argumentele din linia de comanda
if len(sys.argv) < 2:
    print(f"Utilizare: {sys.argv[0]} <host> [port]")
    sys.exit(1)

destinatie = sys.argv[1]  #hostname sau IP tinta
portStart = int(sys.argv[2]) if len(sys.argv) > 2 else 33434  #portul initial

#Rezolvam hostname in IP
try:
    ipRezolvat = socket.gethostbyname(destinatie)
except socket.gaierror:
    print(f"Nu se poate rezolva destinatia: {destinatie}")
    sys.exit(1)
#gaierror este  ridicata de modulul socket cand operatiunea de rezolvare a unui hostname in adresa ip da fail
# „gai” vine de la getaddrinfo (functie din libc care cauta informatii despre adresa)

print(f"Incepem traceroute catre {destinatie} [{ipRezolvat}]\n")
fisierRute.write(f"Incepem traceroute catre {destinatie} [{ipRezolvat}]\n")


# Apelare functiei traceroute
traceroute(ipRezolvat, portStart, icmp_recv_socket)

#inchidem socketii 
udp_send_sock.close()
icmp_recv_socket.close()

fisierRute.close()





#generam harta si o salvam ca png
from datetime import datetime  #pentru timestamp
import matplotlib.pyplot as plt #pentru desenare
import cartopy.crs as ccrs #pentru proiectii geografice


# Pregatim liste de coordonate valide
lats = [lat for lat, lon in listaHopuri if lat is not None and lon is not None]
lons = [lon for lat, lon in listaHopuri if lat is not None and lon is not None]

#cream figura si axa ca harta plana
fig = plt.figure(figsize=(10, 5)) #dimensiunea figurii in inch
ax = plt.axes(projection=ccrs.PlateCarree())  #proiectia geografica
ax.coastlines() #deseneaza linia de coasta
ax.set_global()  #seteaza extinderea globala

#plotam traseul (linie rosie)
ax.plot(lons, lats, linewidth=1.5, marker='o', transform=ccrs.Geodetic())
#transform=ccrs.Geodetic() asigura desenarea corecta pe suprafata pamantului

#adaugam un titlu
plt.title(f"Traceroute pe harta: {destinatie}")

    #generam un nume de fisier unic in functie de timestamp, incluzand domeniul 
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # timestamp curent
    #inlocuim punctele din destinatie cu _
destinatieUnderscore = destinatie.replace('.', '_')
png = f"tracerouteMap{destinatieUnderscore}_{timestamp}.png" 
plt.savefig(png, dpi=150, bbox_inches='tight')
print(f"Harta a fost salvata in '{png}'")





'''
 Exercitiu hackney carriage (optional)!
    e posibil ca ipinfo sa raspunda cu status code 429 Too Many Requests
    cititi despre campul X-Forwarded-For din antetul HTTP
        https://www.nginx.com/resources/wiki/start/topics/examples/forwarded/
    si setati-l o valoare in asa fel incat
    sa puteti trece peste sistemul care limiteaza numarul de cereri/zi

    Alternativ, puteti folosi ip-api (documentatie: https://ip-api.com/docs/api:json).
    Acesta permite trimiterea a 45 de query-uri de geolocare pe minut.
'''

# # exemplu de request la IP info pentru a
# # obtine informatii despre localizarea unui IP
# fake_HTTP_header = {
#                     'referer': 'https://ipinfo.io/',
#                     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
#                    }
# # informatiile despre ip-ul 193.226.51.6 pe ipinfo.io
# # https://ipinfo.io/193.226.51.6 e echivalent cu
# raspuns = requests.get('https://ipinfo.io/widget/193.226.51.6', headers=fake_HTTP_header)
# print (raspuns.json())

# # pentru un IP rezervat retelei locale da bogon=True
# raspuns = requests.get('https://ipinfo.io/widget/10.0.0.1', headers=fake_HTTP_header)
# print (raspuns.json())

