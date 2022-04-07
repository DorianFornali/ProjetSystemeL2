#!/usr/bin/env python3

import os, sys, signal, socket, select, atexit, random, time, json

def handler_ctrlC(_sig, _frame):
    # A la reception du signal CTRL C :
    if os.getpid() not in liste_fils: # Père
        for i in liste_fils:
            try:
                os.kill(i, signal.SIGINT)
            except:
                pass
        for _ in liste_fils:
            try:
                os.wait()
            except:
                pass
        
        clientsocket.close()
        print('\nFermeture du serveur')

        sys.exit(0)
    else: # Fils
        serversocket.close()
        sys.exit(0)


signal.signal(signal.SIGINT, handler_ctrlC)


def usage():
    taille_arg = len(sys.argv)
    if taille_arg != 3:
        print("Usage: ./serveur.py ./traitant.py port")
        sys.exit(0)
    if not(sys.argv[2].isnumeric()):
        print('Usage: ./serveur.py ./traitant.py port\nLe port doit être un entier supérieur à 2000')
        sys.exit(0)
    if int(sys.argv[2]) <= 2000:
        print('Usage: ./serveur.py ./traitant.py port\nLe port doit être un entier supérieur à 2000')
        sys.exit(0)


def limitation(): # Fonction permettant de numérer le nombre de connexions encore en cours
    for s in liste_socket:
        if s.fileno() == -1 and s not in liste_socket_fermee:
                liste_socket_fermee.append(s)
        else: # Socket ouverte
            pass
    return (len(liste_socket) - len(liste_socket_fermee)) >= 4 

if __name__ == '__main__':

    usage() # Vérifie la bonne utilisation du serveur en ligne de commande

# ________________________________________________________________________________________________________________________ #


    HOST = 'localhost'
    PORT = int(sys.argv[2])
    traitant = sys.argv[1]

    MAXBYTES = 100000
    liste_fils = []
    liste_socket = []
    liste_socket_fermee = []

    print("PID actuel :", os.getpid())
    print("En attente d'une connexion ...")

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((HOST, PORT))
    serversocket.listen()

    while True:

        (clientsocket, (addr, port)) = serversocket.accept()
        liste_socket.append(clientsocket)

        if (limitation()):
            print(f"Tentative de connexion depuis {addr}\n4 connexions simultanées, suspension du client en attendant la terminaison de l'une d'elles.")
            clientsocket.send("Trop de connexions déjà en cours, veuillez patienter quelques instants le temps que l'une d'elles se termine ...".encode('utf-8'))
            os.wait()
            clientsocket.send('\nConnexion établie -- \n'.encode('utf-8'))

        pid = os.fork()
        if pid == 0:
            liste_fils.append(pid)

            fd_socket = clientsocket.fileno()
            os.dup2(fd_socket, 0)
            os.dup2(fd_socket, 1)

            serversocket.close()
            os.execvp(traitant, [traitant])
        
        else:
            liste_fils.append(pid)
            clientsocket.close()
