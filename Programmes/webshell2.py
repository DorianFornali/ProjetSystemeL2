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
ligne_id = requete_decoded.split("\r\n")[0].split()

if ligne_id[0] != "GET" or ligne_id[1] == "/favicon.ico" or ligne_id[-1] != "HTTP/1.1":
    os.write(2, "request not supported\n".encode('utf-8'))
    sys.exit(1)


if ligne_id[1] == "/":
    id_session = os.getpid()
    saisie = ''
    os.mkfifo(f"/tmp/traitant{id_session}_to_shell")
    os.mkfifo(f"/tmp/shell_to_traitant{id_session}")

    pid = os.fork()
    if pid == 0:
        os.execvp('bash', [
                  'bash', '-c', f"sh /tmp/traitant{id_session}_to_shell 3<> /tmp/traitant{id_session}_to_shell &> /tmp/shell_to_traitant{id_session} 4< /tmp/shell_to_traitant{id_session}"])
else:
    id_session = ligne_id[1].split("?")[0][9:]
    saisie = escaped_utf8_to_utf8(ligne_id[1].split(
        "=")[1].split("&")[0].replace('+', ' '))

    with open(f"/tmp/traitant{id_session}_to_shell", "w") as tvs:
        if saisie == "":
            tvs.write("echo \n")
        else:
            tvs.write(f"{saisie};echo \n")
    time.sleep(0.5)

    svt = os.open(f"/tmp/shell_to_traitant{id_session}", os.O_RDONLY)
    resultat_commande = os.read(svt, 100000).decode(
        "UTF-8").rstrip().replace("\n", "</br>")

historique_lecture = os.open(f"/tmp/historique_session{id_session}.txt", os.O_RDONLY | os.O_CREAT)
historique_ecriture = os.open(f"/tmp/historique_session{id_session}.txt", os.O_WRONLY | os.O_APPEND)

if ligne_id[1] != "/":
    os.write(historique_ecriture, f"{time.strftime('%H:%M:%S', time.localtime())} >>> {saisie}</br>{resultat_commande}</br>".encode('utf-8'))
    # On ajoute a l'historique une reproduction du prompt avec la commande saisie et son resultat

contenu_historique = os.read(historique_lecture, MAXBYTES).decode('utf-8')

reponse = f"""HTTP/1.1 200 
Content-Type: text/html; charset=utf-8
Connection: close
Content-Length: {str(sys.getsizeof(requete_decoded)+200).encode('utf-8')} 

<DOCTYPE html>
<html>
<head></head>
<body>
    <form action="commande{id_session}" method="get">
        {contenu_historique}
        {time.strftime('%H:%M:%S', time.localtime())} >>>
        <input type="text" name="saisie" placeholder="Entrez une commande shell" /> 
        <input type="submit" name="send" value="&#9166;">     
    </form>
</body>
</html>
"""

print(reponse)