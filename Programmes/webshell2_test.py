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

if ligne_id == "GET / HTTP/1.1": # Premiere connexion du navigateur, création des fifo et du shell persistant
    id_session = os.getpid()

    # On envoie la réponse (formulaire) puis on forme le shell persistant

    print(f"""HTTP/1.1 200 
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
""")

    os.write(2, "donnée transmise\n".encode('utf-8'))

    os.mkfifo(f"/tmp/traitant{id_session}_to_shell")
    os.mkfifo(f"/tmp/shell_to_traitant{id_session}")

    os.write(2, "fifos créées\n".encode('utf-8'))
    # SHELL PERSISTANT
    traitant_shell = os.open(f"/tmp/traitant{id_session}_to_shell", os.O_RDWR)

    lecture_ShellTraitant = os.open(f"/tmp/shell_to_traitant{id_session}", os.O_RDONLY | os.O_NONBLOCK)
    ecriture_ShellTraitant = os.open(f"/tmp/shell_to_traitant{id_session}", os.O_WRONLY | os.O_NONBLOCK)

    os.write(2, "ouverts\n".encode('utf-8'))
    os.dup2(traitant_shell,3)

    os.dup2(ecriture_ShellTraitant,2)
    os.dup2(ecriture_ShellTraitant,1)

    os.dup2(lecture_ShellTraitant, 4)

    os.execvp("sh", ["sh", "-c", f"/tmp/traitant{id_session}_to_shell"])


else:
    id_session = ligne_id.split("?")[0][13:]
    saisie = ligne_id.split("=")[1].split("&")[0]
    saisie = escaped_utf8_to_utf8(saisie)
    saisie = saisie.replace("+", " ")

    if os.fork() == 0:
        ecriture_TraitantShell = os.open(f"/tmp/traitant{id_session}_to_shell", os.O_WRONLY | os.O_NONBLOCK)
        os.write(ecriture_TraitantShell, saisie)
        os.close(ecriture_TraitantShell)
        sys.exit(0)

    lecture_ShellTraitant = os.open(f"/tmp/shell_to_traitant{id_session}", os.O_RDONLY | os.O_NONBLOCK)
    resultat_commande = os.read(lecture_ShellTraitant, MAXBYTES)
    
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
