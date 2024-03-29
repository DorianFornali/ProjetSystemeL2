#!/usr/bin/env python3
import os, sys

MAXBYTES = 100000

def escaped_utf8_to_utf8(s):
    res = b'' ; i = 0
    while i < len(s):
        if s[i] == '%':
            res += int(s[i+1:i+3], base=16).to_bytes(1, byteorder='big')
            i += 3
        else :
            res += s[i].encode('utf-8')
            i += 1
    return res.decode('utf-8')

requete = os.read(0, MAXBYTES)
requete_decoded = requete.decode("utf-8")
ligne_id = requete_decoded.split("\r\n")[0]  # Premiere ligne, censée comporter le type de requete et sa version HTTP

requete_decoded = requete_decoded.replace("\r\n", "</br>")

historique_lecture = os.open("/tmp/historique.txt", os.O_RDONLY | os.O_CREAT)
historique_ecriture = os.open("/tmp/historique.txt", os.O_WRONLY | os.O_APPEND)



if (ligne_id != "GET / HTTP/1.1") and (ligne_id[:18] != "GET /ajoute?saisie"): # Ni saisie ni get http
        os.write(2, "request not supported\n".encode('utf-8'))
        sys.exit(0)

if ligne_id == "GET / HTTP/1.1":
    saisie = ""
else:
    saisie = ligne_id[19:].split("&")[0]
    saisie = escaped_utf8_to_utf8(saisie)
    saisie = saisie.replace("+", " ")

if len(saisie) != 0:
    os.write(historique_ecriture, f"{saisie}</br>".encode('utf-8'))


contenu_historique = os.read(historique_lecture, MAXBYTES).decode('utf-8')


reponse = f"""HTTP/1.1 200 
Content-Type: text/html; charset=utf-8
Connection: close
Content-Length: {str(sys.getsizeof(requete_decoded)+200).encode('utf-8')} 

<DOCTYPE html>
<html>
<head></head>
<body>
    <form action="ajoute" method="get">
        {contenu_historique}
        <input type="text" name="saisie" placeholder="Tapez quelque chose" />
        <input type="submit" name="send" value="&#9166;">
    </form>
</body>
</html>
"""

os.close(historique_lecture)
os.close(historique_ecriture)

print(reponse) # Etant donné que le traitant hérite des descripteurs de fichier de son père, un print écrivant normalement sur 1 va écrire sur la socket, donc chez le client