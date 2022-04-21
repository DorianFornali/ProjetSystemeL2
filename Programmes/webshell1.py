#!/usr/bin/env python3

import os, sys, time
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


resultat_commande = ''

requete = os.read(0, MAXBYTES)
requete_decoded = requete.decode("utf-8")
ligne_id = requete_decoded.split("\r\n")[0]


if ligne_id != "GET / HTTP/1.1" and ligne_id[:13] != "GET /commande":
    os.write(2, "request not supported\n".encode('utf-8'))
    sys.exit(0)

if ligne_id[:13] == "GET /commande":
    pere, fils = os.pipe()

    saisie = ligne_id.split("=")[1].split("&")[0]
    saisie = escaped_utf8_to_utf8(saisie)
    saisie = saisie.replace("+", " ")

    if os.fork() == 0:
        os.close(pere)
        os.dup2(fils, 1)
        os.dup2(fils, 2)

        os.execvp('sh', ['sh', '-c', saisie])

    os.close(fils)
    pere = os.fdopen(pere, 'r')
    resultat_commande = pere.read(MAXBYTES)
    resultat_commande = resultat_commande.replace("\n", "</br>")

reponse = f"""HTTP/1.1 200 
Content-Type: text/html; charset=utf-8
Connection: close
Content-Length: {str(sys.getsizeof(requete_decoded)+200).encode('utf-8')} 

<DOCTYPE html>
<html>
<head></head>
<body>
    <form action="commande" method="get">
        {time.strftime('%H:%M:%S', time.localtime())}
        <input type="text" name="saisie" placeholder="Entrez une commande shell" />
        <input type="submit" name="send" value="&#9166;"> </br>
        {resultat_commande} 
    </form>
</body>
</html>
"""

print(reponse)
