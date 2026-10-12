# Laborator: functii, metode si importuri pe web
# Student: Ermurachi Mihaela

import time

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# --- Exercitiul 1: Primul import --------------------------------------------
import requests
print("Versiunea requests:", requests.__version__)

import urllib.request
# requests a avut nevoie de "pip install requests" pentru ca NU face parte
# din biblioteca standard a Python: e un pachet extern, scris de altcineva
# si publicat pe PyPI, asa ca trebuie instalat separat, o singura data, pe
# fiecare calculator pe care vrem sa il folosim.
# urllib.request, in schimb, vine deja cu orice instalare de Python (face
# parte din biblioteca standard), deci poate fi importat direct, fara pip.


# --- Exercitiul 2: Doua stiluri de import -----------------------------------
response = requests.get(BASE_URL, timeout=TIMEOUT)
print("Cod de stare (import requests):", response.status_code)

time.sleep(1)

from requests import get
response2 = get(BASE_URL, timeout=TIMEOUT)
print("Cod de stare (from requests import get):", response2.status_code)
# import requests: trebuie sa scriu requests.get(), dar e clar, oriunde in
#   fisier, din ce modul vine get() -- usor de citit in fisiere mari, cu
#   multe importuri.
# from requests import get: scriu doar get(), cod mai scurt de tastat, dar
#   daca fisierul are mai multe importuri de genul asta, nu mai e clar, la
#   prima vedere, din ce modul vine fiecare functie folosita.

time.sleep(1)


# --- Exercitiul 3: Alias-uri -------------------------------------------------
import requests as rq
response3 = rq.get(BASE_URL, timeout=TIMEOUT)
print("Cod de stare (alias rq):", response3.status_code)
# Un alias ajuta cand numele original e lung sau cand exista deja o
# conventie cunoscuta (de exemplu import numpy as np) -- codul devine mai
# scurt, iar cititorul recunoaste imediat conventia. Devine mai greu de
# citit cand alias-ul e ales la intamplare (de exemplu import requests as
# r2) sau cand fiecare fisier din proiect foloseste alt alias pentru acelasi
# modul, pentru ca atunci cititorul trebuie sa caute inapoi ce inseamna
# prescurtarea.

time.sleep(1)


# --- Exercitiul 4: Doar biblioteca standard ----------------------------------
import urllib.request as urlreq

with urlreq.urlopen(BASE_URL, timeout=TIMEOUT) as raspuns:
    continut = raspuns.read()  # .read() returneaza octeti (bytes)
    print("Status (urllib):", raspuns.status)
    print("Primele 200 caractere:", continut.decode("utf-8")[:200])


# --- Exercitiul 5: Priviti in interiorul unui modul --------------------------
print(dir(requests))
# Trei nume alese din rezultat, cu tipul lor:
#   get        -> functie   (o apelam direct: requests.get(url))
#   Session    -> clasa     (cream obiecte noi cu requests.Session())
#   exceptions -> modul     (contine toate clasele de exceptii ale
#                            pachetului, de exemplu requests.exceptions.HTTPError)


# --- Exercitiul 6: Cititi documentatia ---------------------------------------
help(requests.get)
# Parametrul cautat este "timeout". Il folosim asa:
response4 = requests.get(BASE_URL, timeout=TIMEOUT)
print("Cod de stare cu timeout explicit:", response4.status_code)

time.sleep(1)


# --- Exercitiul 7: Cronometrarea unei cereri ---------------------------------
inceput = time.perf_counter()
response5 = requests.get(BASE_URL, timeout=TIMEOUT)
sfarsit = time.perf_counter()
print("Durata masurata manual:", sfarsit - inceput, "secunde")
print("response.elapsed:", response5.elapsed.total_seconds(), "secunde")
# response.elapsed masoara DOAR timpul dintre trimiterea cererii si primirea
# raspunsului de la server. Masuratoarea noastra manuala include si pasii
# din jur (de exemplu apelul in sine al functiei requests.get), deci e de
# obicei putin mai mare, dar foarte apropiata ca valoare.


# --- Exercitiul 8: Cand un import esueaza ------------------------------------
try:
    import bs4
except ImportError:
    print("Instalati modulul cu: pip install beautifulsoup4")

# Verificati-va: un MODUL este un singur fisier .py; un PACHET este un
# director cu mai multe module, grupate sub un singur nume (are un fisier
# __init__.py care marcheaza directorul ca fiind importabil); o BIBLIOTECA
# este un termen mai general, pentru cod gata scris pe care il poti
# refolosi -- poate fi un singur modul sau un pachet intreg (de exemplu,
# "biblioteca requests" este de fapt un pachet cu mai multe module).
