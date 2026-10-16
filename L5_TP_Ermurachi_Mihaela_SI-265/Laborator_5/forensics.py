# -*- coding: utf-8 -*-
"""
forensics.py

Forensics pe fisiere: semnatura reala (magic bytes), text citibil scos
dintr-un binar (strings), metadate EXIF/GPS dintr-o poza si extragerea
unui fisier ascuns la coada (file carving).

Tehnici de programare - Laboratorul 5, Lucrarea B (B1-B4).
Student: Ermurachi Mihaela, gr. SI-265.
"""

import os
import re
import zipfile

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


# ---------------------------------------------------------------------------
# B1. Magic bytes: tipul real, nu extensia
# ---------------------------------------------------------------------------
_SEMNATURI = {
    b"%PDF": "pdf",
    b"\x89PNG": "png",
    b"\xff\xd8": "jpeg",
    b"PK\x03\x04": "zip/docx",
}


def tip_real(cale: str) -> str:
    """Citeste primii octeti ai fisierului de la cale si ii compara cu
    semnaturile cunoscute. Returneaza numele tipului gasit, sau hexul
    capului de fisier daca nicio semnatura nu se potriveste.
    """
    with open(cale, "rb") as f:
        cap = f.read(8)
    for semnatura, nume in _SEMNATURI.items():
        if cap.startswith(semnatura):
            return nume
    return cap.hex()


# ---------------------------------------------------------------------------
# B2. strings: textul citibil dintr-un binar
# ---------------------------------------------------------------------------
_RE_STRINGS = re.compile(rb"[ -~]{4,}")


def strings(cale: str, lungime_minima: int = 4):
    """Scoate toate secventele de caractere ASCII imprimabile, de cel putin
    lungime_minima octeti, dintr-un fisier binar. Returneaza o lista de
    siruri de text.
    """
    with open(cale, "rb") as f:
        date = f.read()
    tipar = re.compile(rb"[ -~]{%d,}" % lungime_minima)
    return [m.decode() for m in tipar.findall(date)]


# ---------------------------------------------------------------------------
# B3. Metadate EXIF si GPS dintr-o poza
# ---------------------------------------------------------------------------
def _grade_zecimale(valoare, emisfera):
    """Converteste un tuplu (grade, minute, secunde) + emisfera (N/S/E/V)
    intr-un singur numar, in grade zecimale (pozitiv N/E, negativ S/V).
    """
    grade, minute, secunde = valoare
    zecimal = float(grade) + float(minute) / 60 + float(secunde) / 3600
    if emisfera in ("S", "W"):
        zecimal = -zecimal
    return zecimal


def citeste_exif(cale: str) -> dict:
    """Returneaza un dictionar {nume_tag: valoare} cu toate etichetele EXIF
    lizibile ale pozei de la cale.
    """
    exif = Image.open(cale).getexif() or {}
    rezultat = {}
    for id_tag, val in exif.items():
        rezultat[TAGS.get(id_tag, id_tag)] = val
    return rezultat


def citeste_gps(cale: str):
    """Extrage blocul GPS (tag 34853) din EXIF si returneaza (lat, lon) in
    grade zecimale, sau None daca poza nu are date GPS.
    """
    exif = Image.open(cale).getexif()
    bloc_gps = exif.get_ifd(0x8825) if exif else None
    if not bloc_gps:
        return None

    gps = {GPSTAGS.get(k, k): v for k, v in bloc_gps.items()}
    if "GPSLatitude" not in gps or "GPSLongitude" not in gps:
        return None

    lat = _grade_zecimale(gps["GPSLatitude"], gps.get("GPSLatitudeRef", "N"))
    lon = _grade_zecimale(gps["GPSLongitude"], gps.get("GPSLongitudeRef", "E"))
    return lat, lon


# ---------------------------------------------------------------------------
# B4. File carving: scoti fisierul ascuns
# ---------------------------------------------------------------------------
def extrage_zip_ascuns(cale_sursa: str, cale_destinatie: str = "gasit.zip"):
    """Cauta semnatura unei arhive ZIP (PK\\x03\\x04) in interiorul
    fisierului de la cale_sursa si, daca o gaseste, salveaza totul de la
    acel octet inainte intr-un fisier .zip separat.

    Returneaza octetul de inceput al arhivei, sau None daca nu s-a gasit.
    """
    with open(cale_sursa, "rb") as f:
        date = f.read()

    i = date.find(b"PK\x03\x04")
    if i == -1:
        return None

    with open(cale_destinatie, "wb") as f:
        f.write(date[i:])
    return i


def listeaza_continut_zip(cale_zip: str):
    """Returneaza lista numelor fisierelor dintr-o arhiva ZIP, si continutul
    fiecarui fisier text din ea (decodat utf-8)."""
    continut = {}
    with zipfile.ZipFile(cale_zip) as z:
        for nume in z.namelist():
            try:
                continut[nume] = z.read(nume).decode("utf-8")
            except UnicodeDecodeError:
                continut[nume] = "<continut binar>"
    return continut


# ---------------------------------------------------------------------------
# Script: ruleaza B1-B4, in ordine, pe fisierele din probe/
# ---------------------------------------------------------------------------
def main():
    aici = os.path.dirname(os.path.abspath(__file__))
    probe = os.path.join(aici, "probe")

    print("=== B1. Magic bytes ===")
    for nume_fisier in ("foto.jpg", "ascuns.png", "xor.bin"):
        cale = os.path.join(probe, nume_fisier)
        print(f"{nume_fisier}: {tip_real(cale)}")

    print("\n=== B2. strings pe ascuns.png ===")
    for s in strings(os.path.join(probe, "ascuns.png")):
        print(" ", s)

    print("\n=== B3. EXIF si GPS din foto.jpg ===")
    cale_foto = os.path.join(probe, "foto.jpg")
    for nume_tag, val in citeste_exif(cale_foto).items():
        print(f"  {nume_tag} = {val}")
    gps = citeste_gps(cale_foto)
    if gps:
        lat, lon = gps
        print(f"  Latitudine = {lat:.6f}")
        print(f"  Longitudine = {lon:.6f}")
        print(f"  Harta: https://www.openstreetmap.org/?mlat={lat:.6f}&mlon={lon:.6f}&zoom=14")
    else:
        print("  (fara date GPS)")

    print("\n=== B4. File carving din ascuns.png ===")
    cale_ascuns = os.path.join(probe, "ascuns.png")
    cale_zip = os.path.join(aici, "gasit.zip")
    pozitie = extrage_zip_ascuns(cale_ascuns, cale_zip)
    if pozitie is None:
        print("  nicio arhiva ZIP gasita")
    else:
        print(f"  arhiva extrasa de la octetul {pozitie} -> {cale_zip}")
        for nume, text in listeaza_continut_zip(cale_zip).items():
            print(f"  continut [{nume}]: {text!r}")


if __name__ == "__main__":
    main()
