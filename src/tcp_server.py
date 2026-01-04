# TCP Server
import socket
import logging
import time
import random


logging.basicConfig(format = u'[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.NOTSET)

# un socket este o interfata software care permite comunicarea intre doua dispozitive prin retea
# e folosit pentru a trimite si a primi date intre un client si un server
# facem un nou socket
# socket.AF_INET specifica familia de adrese - IPv4 (adrese formate din 4 octeti, ex: 192.168.0.1)
# socket.SOCK_STREAM specifica tipul de socket - TCP
# proto=socket.IPPROTO_TCP specifica explicit protocolul folosit - TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)


port = 10000
adresa = '0.0.0.0' # accept conexiuni de pe toate ip-urile

adresaServer = (adresa, port)
# serverului i se asociaza socketul respectiv
sock.bind(adresaServer)

logging.info("Serverul a pornit pe %s si portnul portul %d", adresa, port)
sock.listen(5) # asculta, dar pe un numar maxim de 5 clienti/conexiuni

while True:
    logging.info('Asteptam conexiuni...')
    # la realizarea conexiunii se accepta din socket datele
    conexiune, address = sock.accept()
    logging.info("Handshake cu %s", address)
    
    while True:
        time.sleep(5)
        
        # datele primite prin TCP
        data = conexiune.recv(1024)
        logging.info('Content primit: "%s"', data.decode())
        
        numar = random.randint(100000, 999999)
        numar = str(numar).encode()
        conexiune.send(numar) # aici trimit un alt numar inapoi
        logging.info('Server a trimis: %s', numar.decode())
        
    # inchei conexiunea
    conexiune.close()

# inchid si socket
sock.close()
