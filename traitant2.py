#!/usr/bin/env python3
import os, sys, time

MAXBYTES = 100000

requete = os.read(0, MAXBYTES)

requete_decoded = requete.decode("utf-8")
ligne_id = requete_decoded.split("\r\n")[0]  # Premiere ligne, censée comporter le type de requete et sa version HTTP

requete_decoded = requete_decoded.replace("\r\n", "</br>")

if ligne_id != "GET / HTTP/1.1":
    os.write(2, "request not supported\n".encode('utf-8'))
    sys.exit(0)

reponse = f"""HTTP/1.1 200 
Content-Type: text/html; charset=utf-8
Connection: close
Content-Length: {str(sys.getsizeof(requete_decoded)+100).encode('utf-8')} 

<DOCTYPE html>
<html>
<head><p>{requete_decoded}</p></head>
</html>
"""
# reponse est le paquet http qu'on envoie en réponse, il est consituté du header d'un dans lequel on spécifie la taille du payload notamment
# et ensuite le payload sous forme HTML avec un simple paragraphe dans lequel on réécrit la requête reçue

print(reponse) # Etant donné que le traitant hérite des descripteurs de fichier de son père, un print écrivant normalement sur 1 va écrire sur la socket, donc chez le client
