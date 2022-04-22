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

if ligne_id == "GET / HTTP/1.1": # Premiere connexion, on crée le shell persistant
    id_session = os.getpid()

    os.mkfifo(f"/tmp/traitant{id_session}_to_shell")
    os.mkfifo(f"/tmp/shell_to_traitant{id_session}")
    os.write(2, "debug".encode('utf-8'))

    commande = f"sh /tmp/traitant{id_session}_to_shell 3<> /tmp/traitant{id_session}_to_shell &> /tmp/shell_to_traitant{id_session} 4> /tmp/traitant{id_session}_to_shell 5< /tmp/shell_to_traitant{id_session}"
    #os.system(f"sh -c 'sh /tmp/traitant{id_session}_to_shell 3< /tmp/traitant{id_session}_to_shell &> /tmp/shell_to_traitant{id_session} 4> /tmp/traitant{id_session}_to_shell 5< /tmp/shell_to_traitant{id_session}'")
    if os.fork() == 0:
        os.execvp("sh", ['sh', '-c', commande])
else:
    id_session = ligne_id.split("?")[0][13:]
    saisie = ligne_id.split("=")[1].split("&")[0]
    saisie = escaped_utf8_to_utf8(saisie)
    saisie = saisie.replace("+", " ")

    os.write(2, saisie.encode('utf-8')) #debug
    os.write(2, "\n".encode('utf-8')) #debug
    os.write(2, id_session.encode('utf-8')) #debug
    try:
        tvs = os.open(f"/tmp/traitant{id_session}_to_shell", os.O_WRONLY)
        os.write(tvs, saisie.encode('utf-8'))
        os.close(tvs)
        
        svt = os.open(f"/tmp/shell_to_traitant{id_session}", os.O_RDONLY)
        resultat_commande = os.read(svt, MAXBYTES).decode('utf-8')
        os.close(svt)

        os.write(2, resultat_commande.encode('utf-8')) #debug
    except:
        resultat_commande = "null"

reponse = f"""HTTP/1.1 200 
Content-Type: text/html; charset=utf-8
Connection: close
Content-Length: {str(sys.getsizeof(requete_decoded)+200).encode('utf-8')} 

<DOCTYPE html>
<html>
<head></head>
<body>
    <form action="commande{id_session}" method="get">
        {time.strftime('%H:%M:%S', time.localtime())}
        <input type="text" name="saisie" placeholder="Entrez une commande shell" /> 
        <input type="submit" name="send" value="&#9166;"> </br>
        {resultat_commande}
    </form>
</body>
</html>
"""

print(reponse)
