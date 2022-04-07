#!/usr/bin/env python3
import os, sys

MAXBYTES = 100000

requete = os.read(0, MAXBYTES)

requete_decoded = requete.decode("utf-8")
ligne_id = requete_decoded.split("\r\n")[0] 

if ligne_id != "GET / HTTP/1.1":
    os.write(2, "request not supported".encode('utf-8'))

os.write(2, requete)
