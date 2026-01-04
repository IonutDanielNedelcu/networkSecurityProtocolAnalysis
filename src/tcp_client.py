# TCP client
import socket
import logging
import time
import sys
import random

logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

# un socket este o interfata software care permite comunicarea intre doua dispozitive prin retea
# e folosit pentru a trimite si a primi date intre un client si un server
# facem un nou socket
# socket.AF_INET specifica familia de adrese - IPv4 (adrese formate din 4 octeti, ex: 192.168.0.1)
# socket.SOCK_STREAM specifica tipul de socket - TCP
# proto=socket.IPPROTO_TCP specifica explicit protocolul folosit - TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)

# portul si adresa serverului in subreteaua in care se afla
port = 10000
adresa = '198.7.0.2'

adresaServer = (adresa, port)

try:
    logging.info('Handshake cu %s', str(adresaServer))
    
    # clientul se conecteaza la server - are nevoie de IP si de port
    sock.connect(adresaServer)
    logging.info('Handshake a fost stabilit')
    time.sleep(3)
    
    # o bucla infinita in care trimite si primeste mesaje
    while True:
        numar = random.randint(100000, 999999)
        numar = str(numar).encode()
        
        # trimite numarul codificat in biti
        sock.send(numar)
        logging.info('Client a trimis: %s', numar.decode())
        
        # primeste date de la server
        data = sock.recv(1024)
        logging.info('Client a primit: %s', data.decode())
        
        time.sleep(5)
finally:
    logging.info('inchidere socket')
    sock.close()
