# Laborator: functii, metode si importuri pe web
# Student: Ermurachi Mihaela
#
# webtools.py -- modulul propriu: toate functiile reutilizabile ale
# laboratorului, stranse intr-un singur loc, asa cum cere Partea 5.

import csv
import hashlib
import json
import re
import socket
import ssl
import datetime
import urllib.parse
from html.parser import HTMLParser

import requests

TIMEOUT = 10  # secunde

# --- Exercitiul 47: Constante de modul --------------------------------------
DEFAULT_HEADERS = {"User-Agent": "WebLab-Ermurachi-Mihaela"}


ANTETE_SECURITATE = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]


# --- Exercitiul 21/23: fetch --------------------------------------------------
def fetch(url, timeout=TIMEOUT):
    """Descarca URL-ul dat (cu DEFAULT_HEADERS) si returneaza obiectul raspuns."""
    return requests.get(url, timeout=timeout, headers=DEFAULT_HEADERS)


# --- Exercitiul 22/26: get_status ---------------------------------------------
def get_status(url: str) -> int:
    """Returneaza codul de stare HTTP al adresei url."""
    return fetch(url).status_code


# --- Exercitiul 25: get_title -------------------------------------------------
def get_title(html: str) -> str:
    """Returneaza textul dintre <title> si </title> dintr-un sir HTML.

    Parametri:
        html (str): codul sursa HTML al unei pagini.

    Returneaza:
        str: titlul paginii, fara spatii la capete. Sir gol daca nu exista
        niciun tag <title> in html.
    """
    start_tag = html.find("<title>")
    if start_tag == -1:
        return ""
    start = start_tag + len("<title>")
    end = html.find("</title>", start)
    if end == -1:
        return ""
    return html[start:end].strip()


# --- Exercitiul 27: page_exists -----------------------------------------------
def page_exists(url: str) -> bool:
    """Returneaza True daca URL-ul raspunde, False la orice eroare de retea."""
    try:
        fetch(url)
        return True
    except requests.RequestException:
        return False


# --- Exercitiul 28: check_paths -----------------------------------------------
def check_paths(base: str, paths) -> dict:
    """Returneaza un dictionar {path: status_code} pentru fiecare cale din paths."""
    import time

    rezultat = {}
    for cale in paths:
        rezultat[cale] = get_status(base + cale)
        time.sleep(1)
    return rezultat


# --- Exercitiul 29: get_header ------------------------------------------------
def get_header(url: str, name: str, default: str = "lipseste") -> str:
    """Returneaza valoarea unui singur antet HTTP, sau default daca nu exista."""
    return fetch(url).headers.get(name, default)


# --- Exercitiul 30: security_headers -------------------------------------------
def security_headers(url: str) -> dict:
    """Verifica prezenta a cinci antete de securitate si returneaza {antet: True/False}."""
    raspuns = fetch(url)
    return {antet: antet in raspuns.headers for antet in ANTETE_SECURITATE}


# --- Exercitiul 31: score_headers ----------------------------------------------
def score_headers(results: dict) -> str:
    """Primeste dictionarul din security_headers si returneaza un scor 'n/total'."""
    obtinute = sum(1 for prezent in results.values() if prezent)
    return f"{obtinute}/{len(results)}"


# --- Exercitiul 32: fetch_robots / disallowed_paths -----------------------------
def fetch_robots(base: str):
    """Returneaza textul fisierului /robots.txt, sau None daca lipseste."""
    raspuns = fetch(base + "/robots.txt")
    if raspuns.status_code != 200:
        return None
    return raspuns.text


def disallowed_paths(robots_text):
    """Returneaza lista cailor interzise (Disallow:) dintr-un text robots.txt."""
    if robots_text is None:
        return []
    cai = []
    for linie in robots_text.splitlines():
        linie = linie.strip()
        if linie.lower().startswith("disallow:"):
            cale = linie.split(":", 1)[1].strip()
            if cale:
                cai.append(cale)
    return cai


# --- Exercitiul 33: response_times -----------------------------------------------
def response_times(*urls) -> dict:
    """Returneaza un dictionar {url: secunde} cu timpul de raspuns al fiecarui URL."""
    import time

    rezultat = {}
    for url in urls:
        raspuns = fetch(url)
        rezultat[url] = raspuns.elapsed.total_seconds()
        time.sleep(1)
    return rezultat


# --- Exercitiul 34: log -------------------------------------------------------------
def log(message, **details):
    """Afiseaza un mesaj urmat de fiecare detaliu primit ca argument cu nume."""
    bucati = [message] + [f"{cheie}={valoare}" for cheie, valoare in details.items()]
    print(" | ".join(bucati))


# --- Exercitiul 37/38: extract_links / split_links -----------------------------------
def extract_links(html: str) -> list:
    """Returneaza legaturile href gasite in html, fara duplicate, in ordinea aparitiei."""
    gasite = re.findall(r'href="([^"]+)"', html)
    unice = []
    for legatura in gasite:
        if legatura not in unice:
            unice.append(legatura)
    return unice


def split_links(links, base: str, domain: str):
    """Imparte legaturile in interne (acelasi domeniu) si externe."""
    interne, externe = [], []
    for legatura in links:
        completa = urllib.parse.urljoin(base, legatura)
        netloc = urllib.parse.urlparse(completa).netloc
        if netloc == domain:
            interne.append(completa)
        else:
            externe.append(completa)
    return interne, externe


# --- Exercitiul 39: ImageFinder ------------------------------------------------------
class ImageFinder(HTMLParser):
    """Parser HTML care colecteaza atributul src al fiecarui tag <img>."""

    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "img":
            src = dict(attrs).get("src")
            if src:
                self.images.append(src)


# --- Exercitiul 40: page_fingerprint -------------------------------------------------
def page_fingerprint(url: str) -> str:
    """Returneaza amprenta SHA-256 a continutului paginii de la url."""
    raspuns = fetch(url)
    return hashlib.sha256(raspuns.content).hexdigest()


# --- Exercitiul 42: resolve -----------------------------------------------------------
def resolve(hostname: str) -> str:
    """Returneaza adresa IP a unui hostname."""
    return socket.gethostbyname(hostname)


# --- Exercitiul 43: cert_days_left -----------------------------------------------------
def cert_days_left(hostname: str) -> int:
    """Returneaza numarul de zile ramase pana la expirarea certificatului TLS."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
            certificat = tls_sock.getpeercert()
    expira_la_secunde = ssl.cert_time_to_seconds(certificat["notAfter"])
    expira_la = datetime.datetime.fromtimestamp(expira_la_secunde)
    ramase = expira_la - datetime.datetime.now()
    return ramase.days


# --- Exercitiul 49: salvarea unui raport CSV ---------------------------------------------
def save_report_csv(path_status: dict, path="report.csv"):
    """Salveaza rezultatul check_paths() in path, cu coloanele path, status, checked_at."""
    acum = datetime.datetime.now().isoformat()
    with open(path, "w", newline="", encoding="utf-8") as fisier:
        writer = csv.writer(fisier)
        writer.writerow(["path", "status", "checked_at"])
        for cale, status in path_status.items():
            writer.writerow([cale, status, acum])


# --- Exercitiul 50: raportul final al site-ului ------------------------------------------
def site_report(url: str) -> dict:
    """Colecteaza un raport complet despre site-ul de la url, il afiseaza si il
    salveaza in report.json.

    Foloseste toate functiile de mai sus: codul de stare, titlul, adresa IP,
    lantul de redirectionari, scorul antetelor de securitate, zilele ramase
    pana la expirarea certificatului, legaturile interne/externe si caile
    interzise din robots.txt.
    """
    raspuns = fetch(url)
    raspuns.raise_for_status()

    domeniu = urllib.parse.urlparse(raspuns.url).netloc
    hostname = domeniu.split(":")[0]

    titlu = get_title(raspuns.text)
    adresa_ip = resolve(hostname)

    url_http = "http://" + hostname
    raspuns_http = fetch(url_http)
    redirectionari = [
        {"status": pas.status_code, "url": pas.url} for pas in raspuns_http.history
    ]

    scor_securitate = score_headers(security_headers(url))
    zile_certificat = cert_days_left(hostname)

    legaturi = extract_links(raspuns.text)
    interne, externe = split_links(legaturi, raspuns.url, domeniu)

    robots_text = fetch_robots(f"{raspuns.url.rstrip('/')}")
    cai_interzise = disallowed_paths(robots_text)

    raport = {
        "url": raspuns.url,
        "status_code": raspuns.status_code,
        "titlu": titlu,
        "adresa_ip": adresa_ip,
        "redirectionari": redirectionari,
        "scor_securitate": scor_securitate,
        "zile_pana_la_expirarea_certificatului": zile_certificat,
        "legaturi_interne": len(interne),
        "legaturi_externe": len(externe),
        "cai_interzise": cai_interzise,
    }

    print(f"=== Raport site: {raport['url']} ===")
    print("Cod de stare:", raport["status_code"])
    print("Titlu:", raport["titlu"])
    print("Adresa IP:", raport["adresa_ip"])
    if redirectionari:
        for pas in redirectionari:
            print(f"Redirectionare: {pas['status']} -> {pas['url']}")
    else:
        print("Redirectionari: niciuna")
    print("Scor securitate:", raport["scor_securitate"])
    print("Certificat:", raport["zile_pana_la_expirarea_certificatului"], "de zile ramase")
    print(f"Legaturi: {raport['legaturi_interne']} interne, {raport['legaturi_externe']} externe")
    print("Cai interzise:", ", ".join(cai_interzise) if cai_interzise else "niciuna")

    with open("report.json", "w", encoding="utf-8") as fisier:
        json.dump(raport, fisier, indent=2, ensure_ascii=False)
    print("Salvat in report.json")

    return raport


# --- Exercitiul 46: blocul main -----------------------------------------------------------
if __name__ == "__main__":
    print("Autotest:", get_status("https://cybercor.org"))
