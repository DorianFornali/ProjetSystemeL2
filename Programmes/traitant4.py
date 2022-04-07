#!/usr/bin/env python3
import os, sys

MAXBYTES = 100000

def escaped_latin1_to_utf8(s):
    res = '' ; i = 0
    while i < len(s):
        if s[i] == '%':
            res += chr(int(s[i+1:i+3], base=16))
            i += 3
        else :
            res += s[i]
            i += 1
    return res

requete = os.read(0, MAXBYTES)
requete_decoded = requete.decode("utf-8")
ligne_id = requete_decoded.split("\r\n")[0]  # Premiere ligne, censée comporter le type de requete et sa version HTTP

requete_decoded = requete_decoded.replace("\r\n", "</br>")

historique = os.open("./historique.txt", os.O_RDWR | os.O_CREAT | os.O_APPEND)

if (ligne_id != "GET / HTTP/1.1") and (ligne_id[:18] != "GET /ajoute?saisie"): # Ni saisie ni get http
        os.write(2, "request not supported\n".encode('utf-8'))
        sys.exit(0)


saisie = ligne_id[19:].split("&")[0]
saisie = escaped_latin1_to_utf8(saisie)
saisie = saisie.replace("+", " ")

if len(saisie) != 0:
    os.write(historique, f"{saisie}</br>".encode('utf-8'))

contenu_historique = os.read(historique, MAXBYTES).decode('utf-8')


reponse = f"""HTTP/1.1 200 
Content-Type: text/html; charset=utf-8
Connection: close
Content-Length: {str(sys.getsizeof(requete_decoded)+200).encode('utf-8')} 

<DOCTYPE html>
<html>
<head></head>
<body>
    <form action="ajoute" method="get">
        {contenu_historique} </br>
        <input type="text" name="saisie" placeholder="Tapez quelque chose" />
        <input type="submit" name="send" value="&#9166;">
    </form>
</body>
</html>
"""

os.close(historique)
print(reponse) # Etant donné que le traitant hérite des descripteurs de fichier de son père, un print écrivant normalement sur 1 va écrire sur la socket, donc chez le client


