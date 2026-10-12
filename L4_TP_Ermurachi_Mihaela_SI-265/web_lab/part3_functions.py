# Laborator: functii, metode si importuri pe web
# Student: Ermurachi Mihaela

import time
import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# --- Exercitiul 21: Prima functie --------------------------------------------
def fetch(url, timeout=10):
    """Descarca URL-ul dat si returneaza obiectul raspuns."""
    return requests.get(url, timeout=timeout)


raspuns = fetch(BASE_URL)
print("Cod de stare:", raspuns.status_code)

time.sleep(1)


# --- Exercitiul 22: Returnarea unei singure valori ---------------------------
def get_status(url):
    """Returneaza doar codul de stare HTTP al adresei url."""
    return requests.get(url, timeout=TIMEOUT).status_code


for cale in ("/", "/robots.txt", "/sitemap.xml"):
    print(cale, "->", get_status(BASE_URL + cale))
    time.sleep(1)


# --- Exercitiul 23: Parametri impliciti --------------------------------------
# (fetch de la exercitiul 21 are deja timeout=10 ca valoare implicita)
raspuns_implicit = fetch(BASE_URL)           # foloseste timeout implicit = 10
raspuns_scurt = fetch(BASE_URL, timeout=3)   # timeout explicit = 3
print("Status (timeout implicit):", raspuns_implicit.status_code)
print("Status (timeout=3):", raspuns_scurt.status_code)

time.sleep(1)


# --- Exercitiul 24: O singura sarcina pe functie ------------------------------
def get_title(html):
    start = html.find("<title>") + len("<title>")
    end = html.find("</title>")
    return html[start:end].strip()


print("Titlu (fara nicio cerere noua):", get_title(raspuns_implicit.text))
# get_title nu face nicio operatie de retea: primeste un text HTML deja
# descarcat si doar il analizeaza. Descarcarea (fetch) si analiza
# (get_title) sunt acum doua sarcini separate, fiecare in functia ei.


# --- Exercitiul 25: Docstring-uri ---------------------------------------------
def get_title(html):
    """Returneaza textul dintre <title> si </title> dintr-un sir HTML.

    Parametri:
        html (str): codul sursa HTML al unei pagini.

    Returneaza:
        str: titlul paginii, fara spatii la capete.
    """
    start = html.find("<title>") + len("<title>")
    end = html.find("</title>")
    return html[start:end].strip()


help(get_title)


# --- Exercitiul 26: Adnotari de tip --------------------------------------------
def get_status(url: str) -> int:
    """Returneaza codul de stare HTTP al adresei url."""
    return requests.get(url, timeout=TIMEOUT).status_code


try:
    print(get_status(123))
except Exception as eroare:
    print("Rezultat:", type(eroare).__name__, "-", eroare)
# Adnotarile de tip (type hints) NU opresc executia. Sunt doar informative,
# pentru programator si pentru unelte externe (de exemplu mypy); Python nu
# le verifica la rulare. Din acest motiv get_status(123) este acceptat de
# interpretor si esueaza abia in interiorul functiei, cand requests.get()
# primeste un numar intreg in loc de un text si nu stie sa il foloseasca
# ca URL.


# --- Exercitiul 27: Fara opriri neasteptate ------------------------------------
def page_exists(url):
    """Returneaza True daca URL-ul raspunde, False la orice eroare de retea."""
    try:
        requests.get(url, timeout=TIMEOUT)
        return True
    except requests.RequestException:
        return False


print("cybercor.org exista:", page_exists(BASE_URL))
print("domeniu inexistent:", page_exists("https://this-domain-does-not-exist.invalid"))

time.sleep(1)


# --- Exercitiul 28: Returnarea unui dictionar ----------------------------------
def check_paths(base, paths):
    """Returneaza un dictionar {path: status_code} pentru fiecare cale din paths."""
    rezultat = {}
    for cale in paths:
        rezultat[cale] = get_status(base + cale)
        time.sleep(1)
    return rezultat


print(check_paths(BASE_URL, ["/", "/robots.txt", "/sitemap.xml"]))


# --- Exercitiul 29: Argumente cu nume --------------------------------------------
def get_header(url, name, default="lipseste"):
    """Returneaza valoarea unui singur antet HTTP, sau default daca nu exista."""
    return requests.get(url, timeout=TIMEOUT).headers.get(name, default)


print(get_header(BASE_URL, name="Server"))

time.sleep(1)


# --- Exercitiul 30: Antete de securitate -----------------------------------------
def security_headers(url):
    """Verifica prezenta a cinci antete de securitate si returneaza {antet: True/False}."""
    antete_de_verificat = [
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Referrer-Policy",
    ]
    raspuns = requests.get(url, timeout=TIMEOUT)
    return {antet: antet in raspuns.headers for antet in antete_de_verificat}


rezultate_securitate = security_headers(BASE_URL)
print(rezultate_securitate)

time.sleep(1)


# --- Exercitiul 31: Functii care apeleaza functii --------------------------------
def score_headers(results):
    """Primeste dictionarul din security_headers si returneaza un scor 'n/total'."""
    obtinute = sum(1 for prezent in results.values() if prezent)
    return f"{obtinute}/{len(results)}"


print(score_headers(security_headers(BASE_URL)))

time.sleep(1)


# --- Exercitiul 32: Doua functii, o sarcina ---------------------------------------
def fetch_robots(base):
    """Returneaza textul fisierului /robots.txt, sau None daca lipseste."""
    raspuns = requests.get(base + "/robots.txt", timeout=TIMEOUT)
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


text_robots = fetch_robots(BASE_URL)
print(disallowed_paths(text_robots))
print(disallowed_paths(None))  # trebuie sa functioneze si aici, returnand []

time.sleep(1)


# --- Exercitiul 33: Oricate argumente ------------------------------------------------
def response_times(*urls):
    """Returneaza un dictionar {url: secunde} cu timpul de raspuns al fiecarui URL."""
    rezultat = {}
    for url in urls:
        raspuns = requests.get(url, timeout=TIMEOUT)
        rezultat[url] = raspuns.elapsed.total_seconds()
        time.sleep(1)
    return rezultat


print(response_times(BASE_URL, BASE_URL + "/robots.txt"))


# --- Exercitiul 34: Argumente cu nume colectate ---------------------------------------
def log(message, **details):
    """Afiseaza un mesaj urmat de fiecare detaliu primit ca argument cu nume."""
    bucati = [message] + [f"{cheie}={valoare}" for cheie, valoare in details.items()]
    print(" | ".join(bucati))


log("verificat", url=BASE_URL, status=200)

# Verificati-va: print() doar AFISEAZA o valoare pe ecran, pentru ca o
# persoana sa o vada, dar functia nu da nimic inapoi codului care a
# apelat-o (rezultatul este None). return TRIMITE valoarea inapoi catre
# codul apelant, ca aceasta sa poata fi folosita mai departe (salvata
# intr-o variabila, transmisa altei functii etc.). O functie poate folosi
# si print() si return in acelasi timp, dar scopul lor ramane diferit.
