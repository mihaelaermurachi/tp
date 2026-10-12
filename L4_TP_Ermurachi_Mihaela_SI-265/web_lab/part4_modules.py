# Laborator: functii, metode si importuri pe web
# Student: Ermurachi Mihaela

import time
import re
import json
import socket
import ssl
import hashlib
import datetime
import urllib.parse
from html.parser import HTMLParser

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# --- Exercitiul 35: Descompunerea unui URL -------------------------------------
bucati = urllib.parse.urlparse("https://cybercor.org/path?x=1#top")
print("scheme:", bucati.scheme)
print("netloc:", bucati.netloc)
print("path:", bucati.path)
print("query:", bucati.query)
print("fragment:", bucati.fragment)


# --- Exercitiul 36: Compunerea URL-urilor ----------------------------------------
for legatura in ("/about", "contact.html", "../index.html"):
    print(legatura, "->", urllib.parse.urljoin(BASE_URL, legatura))


# --- Exercitiul 37: Extragerea legaturilor ---------------------------------------
def extract_links(html):
    """Returneaza legaturile href gasite in html, fara duplicate, in ordinea aparitiei."""
    gasite = re.findall(r'href="([^"]+)"', html)
    unice = []
    for legatura in gasite:
        if legatura not in unice:
            unice.append(legatura)
    return unice


raspuns = requests.get(BASE_URL, timeout=TIMEOUT)
legaturi = extract_links(raspuns.text)
print(legaturi)

time.sleep(1)


# --- Exercitiul 38: Interne sau externe? ------------------------------------------
def split_links(links, domain):
    """Imparte legaturile in interne (acelasi domeniu) si externe."""
    interne, externe = [], []
    for legatura in links:
        completa = urllib.parse.urljoin(BASE_URL, legatura)
        netloc = urllib.parse.urlparse(completa).netloc
        if netloc == domain:
            interne.append(completa)
        else:
            externe.append(completa)
    return interne, externe


domeniu = urllib.parse.urlparse(BASE_URL).netloc
interne, externe = split_links(legaturi, domeniu)
print("Interne:", interne)
print("Externe:", externe)


# --- Exercitiul 39: Propriile metode ------------------------------------------------
class ImageFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "img":
            src = dict(attrs).get("src")
            if src:
                self.images.append(src)


# Testez mai intai parserul pe un fragment HTML scris de mine, pentru care
# stiu dinainte rezultatul corect:
test_html = """
<html><body>
<img src="/logo.png" alt="Logo">
<IMG SRC="poza.jpg">
<img alt="imagine fara src">
<img src="https://cdn.example.com/banner.webp" />
<a href="/despre">Aceasta nu este o imagine</a>
</body></html>
"""
finder = ImageFinder()
finder.feed(test_html)
print(finder.images)
assert finder.images == [
    "/logo.png",
    "poza.jpg",
    "https://cdn.example.com/banner.webp",
], "Parserul nu a gasit exact imaginile asteptate"
print("Testul a trecut!")

# Abia acum rulez parserul pe pagina reala:
finder_real = ImageFinder()
finder_real.feed(raspuns.text)
print(len(finder_real.images), "imagini gasite")
for src in finder_real.images:
    print(src)

# Verific rezultatul si in al doilea mod indicat in cerinta:
print("numar aproximativ de tag-uri <img:",
      raspuns.text.lower().count("<img"))

# Verificati-va: handle_starttag() este apelata automat de catre
# HTMLParser, din interiorul metodei .feed(); noi nu o apelam niciodata
# direct. De fiecare data cand parserul intalneste, in textul dat lui
# .feed(), un tag de deschidere, el insusi cheama handle_starttag() cu
# numele si atributele acelui tag.


# --- Exercitiul 40: Amprenta paginii -------------------------------------------------
def page_fingerprint(url):
    """Returneaza amprenta SHA-256 a continutului paginii de la url."""
    raspuns = requests.get(url, timeout=TIMEOUT)
    return hashlib.sha256(raspuns.content).hexdigest()


amprenta1 = page_fingerprint(BASE_URL)
time.sleep(1)
amprenta2 = page_fingerprint(BASE_URL)
print(amprenta1)
print(amprenta2)
print("identice:", amprenta1 == amprenta2)
# Ar fi diferite daca pagina s-ar schimba intre cele doua cereri (continut
# actualizat de administratorul site-ului) sau daca pagina ar include ceva
# generat diferit la fiecare incarcare (de exemplu data si ora curenta, un
# numar aleator sau un token unic de sesiune, scrise direct in codul HTML).


# --- Exercitiul 41: Salvarea in JSON ----------------------------------------------------
with open("headers.json", "w", encoding="utf-8") as fisier:
    json.dump(dict(raspuns.headers), fisier, indent=2)

with open("headers.json", "r", encoding="utf-8") as fisier:
    antete_incarcate = json.load(fisier)

print("Content-Type din fisier:", antete_incarcate.get("Content-Type"))


# --- Exercitiul 42: Interogare DNS -------------------------------------------------------
def resolve(hostname):
    """Returneaza adresa IP a unui hostname."""
    return socket.gethostbyname(hostname)


print("Adresa IP cybercor.org:", resolve("cybercor.org"))


# --- Exercitiul 43: Expirarea certificatului ----------------------------------------------
def cert_days_left(hostname):
    """Returneaza numarul de zile ramase pana la expirarea certificatului TLS."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
            certificat = tls_sock.getpeercert()
    expira_la_secunde = ssl.cert_time_to_seconds(certificat["notAfter"])
    expira_la = datetime.datetime.fromtimestamp(expira_la_secunde)
    ramase = expira_la - datetime.datetime.now()
    return ramase.days


print("Zile ramase pana la expirarea certificatului:", cert_days_left("cybercor.org"))
