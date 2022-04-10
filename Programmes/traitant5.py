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

if (ligne_id != "GET / HTTP/1.1") and (ligne_id[:19] != "GET /ajoute_session"): # Ni saisie ni get http
        os.write(2, "request not supported\n".encode('utf-8'))
        sys.exit(0)

if(ligne_id == "GET / HTTP/1.1"): # A la premiere connexion on attribue le pid du fils a l'identifiant de session
    id_session = os.getpid()
    saisie = ""
else:                             # Si ce n'est pas la premiere connexion (donc que la requete n'est pas un get http) on lui attribue la valeur de l'id session dans la requete
    id_session = ligne_id.split("?")[0][19:]

    saisie = ligne_id.split("=")[1].split("&")[0]
    saisie = escaped_latin1_to_utf8(saisie)
    saisie = saisie.replace("+", " ")

historique_lecture = os.open(f"/tmp/historique_session{id_session}.txt", os.O_RDONLY | os.O_CREAT)
historique_ecriture = os.open(f"/tmp/historique_session{id_session}.txt", os.O_WRONLY | os.O_APPEND)

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
    <form action="ajoute_session{id_session}" method="get">
        {contenu_historique} </br>
        <input type="text" name="saisie" placeholder="Tapez quelque chose" />
        <input type="submit" name="send" value="&#9166;">
    </form>
</body>
</html>
"""

os.close(historique_lecture)
os.close(historique_ecriture)

print(reponse) # Etant donné que le traitant hérite des descripteurs de fichier de son père, un print écrivant normalement sur 1 va écrire sur la socket, donc chez le client