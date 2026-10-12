# Laborator: functii, metode si importuri pe web
# Student: Ermurachi Mihaela

import time
import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# --- Exercitiul 9: Elementele de baza ale raspunsului ------------------------
response = requests.get(BASE_URL, timeout=TIMEOUT)
print("status_code:", response.status_code)   # atribut
print("ok:", response.ok)                     # atribut
print("url:", response.url)                   # atribut
print("encoding:", response.encoding)         # atribut
# (toate patru sunt ATRIBUTE: valori deja calculate de requests, pe care le
# citim fara paranteze)

time.sleep(1)


# --- Exercitiul 10: Tratarea erorilor cu o metoda ----------------------------
response.raise_for_status()  # metoda; nu arunca nimic, pentru ca status e 2xx

try:
    raspuns_lipsa = requests.get(BASE_URL + "/this-page-does-not-exist", timeout=TIMEOUT)
    raspuns_lipsa.raise_for_status()
except requests.HTTPError:
    print("Pagina ceruta nu a putut fi gasita pe server.")

time.sleep(1)


# --- Exercitiul 11: Toate antetele -------------------------------------------
for nume, valoare in response.headers.items():
    print(f"{nume}: {valoare}")


# --- Exercitiul 12: Metode de dictionar ---------------------------------------
print("Server:", response.headers.get("Server", "lipseste"))
print("Content-Type:", response.headers.get("Content-Type", "lipseste"))
print("content-type (litere mici):", response.headers.get("content-type", "lipseste"))
# Observatie: rezultatul este identic in ambele cazuri. response.headers nu
# este un dictionar obisnuit, ci unul "case-insensitive" (nu tine cont de
# majuscule/minuscule) -- pentru ca protocolul HTTP insusi nu face diferenta
# intre "Content-Type" si "content-type", iar requests respecta acest lucru.


# --- Exercitiul 13: Inlantuirea metodelor de sir ------------------------------
numar_aparitii = response.text.lower().count("cyber")
print("Cuvantul 'cyber' apare de", numar_aparitii, "ori")
# Pot inlantui .lower() si .count() pentru ca .lower() returneaza un sir nou
# de caractere (tot de tip str), iar .count() este si ea o metoda a tipului
# str. Rezultatul unei metode poate fi folosit imediat ca "obiect" pentru
# urmatoarea metoda, atata timp cat tipul rezultat are metoda ceruta.


# --- Exercitiul 14: Gasirea titlului ------------------------------------------
html = response.text
start = html.find("<title>") + len("<title>")
end = html.find("</title>")
titlu = html[start:end].strip()
print("Titlu:", titlu)


# --- Exercitiul 15: Numararea liniilor -----------------------------------------
linii = html.splitlines()
print("Numar de linii:", len(linii))
cea_mai_lunga = max(linii, key=len)
print("Lungimea celei mai lungi linii:", len(cea_mai_lunga))


# --- Exercitiul 16: Verificarea HTTPS ------------------------------------------
if response.url.startswith("https://"):
    print("Conexiune securizata")
else:
    print("Conexiune nesecurizata")

time.sleep(1)


# --- Exercitiul 17: Urmarirea redirectionarilor --------------------------------
raspuns_http = requests.get("http://cybercor.org", timeout=TIMEOUT)
for pas in raspuns_http.history:
    print(pas.status_code, "->", pas.url)
print("URL final:", raspuns_http.url)

time.sleep(1)


# --- Exercitiul 18: HEAD versus GET ---------------------------------------------
raspuns_head = requests.head(BASE_URL, timeout=TIMEOUT)
time.sleep(1)
raspuns_get = requests.get(BASE_URL, timeout=TIMEOUT)
print("Lungime continut HEAD:", len(raspuns_head.content))
print("Lungime continut GET:", len(raspuns_get.content))
# HEAD cere serverului aceleasi antete ca si GET, dar fara corpul paginii,
# deci raspuns_head.content este gol (lungime 0); GET descarca si corpul
# efectiv al paginii, deci are o lungime mult mai mare. HEAD e util cand
# vrei doar sa verifici ceva (de exemplu daca pagina exista) fara sa
# consumi trafic pentru tot continutul.


# --- Exercitiul 19: Cookie-uri ----------------------------------------------------
if len(raspuns_get.cookies) == 0:
    print("Niciun cookie setat")
else:
    for cookie in raspuns_get.cookies:
        print(cookie.name, cookie.secure)


# --- Exercitiul 20: Sesiuni -------------------------------------------------------
session = requests.Session()
session.headers.update({"User-Agent": "WebLab-Ermurachi-Mihaela"})
time.sleep(1)
raspuns_echo = session.get(ECHO_URL + "/headers", timeout=TIMEOUT)
print(raspuns_echo.json())
# Verificati in rezultatul de mai sus ca "User-Agent" apare, in sectiunea
# "headers" a raspunsului JSON, cu valoarea "WebLab-Ermurachi-Mihaela".

# Verificati-va: response.text este un ATRIBUT, pentru ca textul e deja
# stocat pe obiect, gata de citit, fara nicio prelucrare suplimentara.
# response.json() este o METODA pentru ca, de fiecare data cand o apelam,
# Python trebuie sa analizeze (parse) textul ca JSON si sa construiasca pe
# loc un dictionar sau o lista noua -- este o actiune, nu doar o valoare
# gata existenta, de aceea are paranteze.
