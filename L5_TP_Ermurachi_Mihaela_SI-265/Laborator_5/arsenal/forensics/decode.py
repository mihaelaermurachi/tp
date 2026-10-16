# -*- coding: utf-8 -*-
"""
arsenal/forensics/decode.py

Decoder universal: primeste un sir sau un fisier, recunoaste stratul de
codare (base64, hex, url), il desface, repeta pentru straturi multiple
si, cand ajunge la un XOR cu cheie de un octet sau la un hash de parola,
il sparge singur.

Tehnici de programare - Laboratorul 5, Lucrarea A.
Student: Ermurachi Mihaela, gr. SI-265.
"""

import re
import os
import json
import base64
import hashlib
import argparse
from urllib.parse import unquote


# ---------------------------------------------------------------------------
# A1. Text si octeti: incalzirea
# ---------------------------------------------------------------------------
def demo_text_octeti():
    """Mica demonstratie a diferentei dintre text (str) si octeti (bytes)."""
    s = "Salut"
    b = s.encode()
    print(b, b[0])            # b"Salut" 83  -- b[0] e un NUMAR, nu o litera

    h = b.hex()
    print(h)                  # "53616c7574"
    inapoi = bytes.fromhex(h)
    print(inapoi)              # b"Salut"
    assert inapoi == b


# ---------------------------------------------------------------------------
# A2. Recunosti stratul dupa forma (nu decodeaza inca, doar clasifica)
# ---------------------------------------------------------------------------
_RE_URL = re.compile(r"%[0-9a-fA-F]{2}")
_RE_HEX = re.compile(r"^[0-9a-fA-F]+$")
_RE_B64 = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")


def ghici_strat(s: str) -> str:
    """Ghiceste tipul de codare al sirului s, uitandu-se doar la forma lui.

    Ordinea verificarilor conteaza: intai "%" (URL), apoi hexul (cel mai
    strict alfabet: doar 0-9a-f), apoi base64 (cel mai larg alfabet).
    """
    if _RE_URL.search(s):
        return "url"
    if _RE_HEX.match(s) and len(s) % 2 == 0:
        return "hex"
    if _RE_B64.match(s) and len(s) % 4 == 0:
        return "base64"
    return "necunoscut"


# ---------------------------------------------------------------------------
# A3. Desfaci stratul recunoscut
# ---------------------------------------------------------------------------
def desfa(s: str):
    """Decodeaza sirul s dupa stratul recunoscut de ghici_strat().

    Returneaza un tuplu (strat, rezultat_octeti).
    """
    strat = ghici_strat(s)
    if strat == "base64":
        return strat, base64.b64decode(s, validate=True)
    if strat == "hex":
        return strat, bytes.fromhex(s)
    if strat == "url":
        return strat, unquote(s).encode()
    return strat, s.encode()


# ---------------------------------------------------------------------------
# A4. Straturi multiple, intr-o bucla
# ---------------------------------------------------------------------------
def citibil(b: bytes) -> bool:
    """True daca b nu e gol si toti octetii lui sunt ASCII imprimabil (32..126)."""
    return len(b) > 0 and all(32 <= c < 127 for c in b)


def despica(val: str, max_pasi: int = 8):
    """Desface sirul val strat cu strat, cat timp fiecare forma noua e tot
    o codare recunoscuta. Se opreste cand ghici_strat() nu mai recunoaste
    niciun strat (am ajuns la text simplu) sau dupa max_pasi incercari, ca
    sa nu intram intr-o bucla infinita.

    Returneaza (lista_straturilor_parcurse, text_final_sau_None).
    """
    straturi = []
    for _ in range(max_pasi):
        strat = ghici_strat(val)
        straturi.append(strat)
        if strat == "necunoscut":
            # nu mai e nimic de desfacut: val e, probabil, textul final
            return straturi, (val if citibil(val.encode()) else None)
        try:
            _, b = desfa(val)
            val = b.decode()
        except (ValueError, UnicodeDecodeError):
            # stratul a fost recunoscut dupa forma, dar decodarea a esuat
            return straturi, None
    # am epuizat max_pasi fara sa ajungem la "necunoscut"
    return straturi, (val if citibil(val.encode()) else None)


# ---------------------------------------------------------------------------
# A5. Spargi un XOR cu cheie de un octet
# ---------------------------------------------------------------------------
def sparge_xor(date: bytes):
    """Incearca toate cele 256 de chei XOR de un octet pe date si pastreaza
    prima cheie al carei rezultat arata a text (toti octetii imprimabili).

    Returneaza (cheie, text_clar) sau (None, None) daca nicio cheie nu merge.
    """
    for k in range(256):
        clar = bytes(b ^ k for b in date)
        if citibil(clar):
            return k, clar.decode()
    return None, None


# ---------------------------------------------------------------------------
# A6. Spargi un hash prin dictionar
# ---------------------------------------------------------------------------
_ALGORITM_DUPA_LUNGIME = {32: "md5", 40: "sha1", 64: "sha256"}


def sparge_hash(tinta: str, cale_wordlist: str):
    """Identifica algoritmul de hash dupa lungimea lui tinta (32 -> md5,
    40 -> sha1, 64 -> sha256), apoi cauta in wordlist cuvantul al carui
    hash se potriveste.

    Returneaza (algoritm, parola_sau_None). Returneaza (None, None) daca
    lungimea nu corespunde niciunui algoritm cunoscut.
    """
    tinta = tinta.strip().lower()
    algoritm = _ALGORITM_DUPA_LUNGIME.get(len(tinta))
    if algoritm is None:
        return None, None
    functie = getattr(hashlib, algoritm)
    with open(cale_wordlist, encoding="latin1") as f:
        for linie in f:
            cuv = linie.strip()
            if not cuv:
                continue
            if functie(cuv.encode()).hexdigest() == tinta:
                return algoritm, cuv
    return algoritm, None


def sparge_toate_hashurile(cale_hashuri: str, cale_wordlist: str):
    """Aplica sparge_hash() pe fiecare linie din cale_hashuri.

    Returneaza o lista de dictionare {hash, algoritm, parola}.
    """
    rezultate = []
    with open(cale_hashuri) as f:
        for linie in f:
            tinta = linie.strip()
            if not tinta:
                continue
            algoritm, parola = sparge_hash(tinta, cale_wordlist)
            rezultate.append({"hash": tinta, "algoritm": algoritm, "parola": parola})
    return rezultate


# ---------------------------------------------------------------------------
# A7. argparse + fisa JSON
# ---------------------------------------------------------------------------
def ruleaza(intrare: str, este_fisier: bool):
    """Proceseaza 'intrare' si returneaza un dictionar gata de salvat in
    fisa.json.

    Pentru un fisier (--fisier): citeste octetii bruti si incearca sa
    sparga un XOR cu cheie de un octet (asta e analiza utila pentru un
    binar necunoscut, de tipul probe/xor.bin).

    Pentru un sir (fara --fisier): aplica despica() si desface straturile
    de codare (base64 / hex / url) pana la text simplu.
    """
    if este_fisier:
        date = open(intrare, "rb").read()
        cheie, text = sparge_xor(date)
        if text is not None:
            return {
                "intrare": intrare,
                "tip": "xor",
                "cheie_xor": cheie,
                "cheie_xor_hex": hex(cheie),
                "rezultat": text,
            }
        return {
            "intrare": intrare,
            "tip": "binar_nedescifrat",
            "lungime_octeti": len(date),
        }

    straturi, text = despica(intrare)
    return {
        "intrare": intrare,
        "straturi": straturi,
        "rezultat": text,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Decoder universal: recunoaste si desface straturi de "
                     "codare (base64/hex/url), sparge un XOR pe un octet "
                     "si salveaza rezultatul intr-o fisa JSON."
    )
    parser.add_argument("intrare", help="sirul de decodat, sau calea unui fisier")
    parser.add_argument(
        "--fisier", action="store_true",
        help="trateaza 'intrare' ca o cale de fisier binar (de ex. probe/xor.bin)",
    )
    implicit_iesire = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fisa.json")
    parser.add_argument(
        "--iesire", default=implicit_iesire,
        help="unde se salveaza fisa JSON (implicit: arsenal/forensics/fisa.json)",
    )
    a = parser.parse_args()

    rezultat = ruleaza(a.intrare, a.fisier)
    print(json.dumps(rezultat, indent=2, ensure_ascii=False))

    with open(a.iesire, "w", encoding="utf-8") as f:
        json.dump(rezultat, f, indent=2, ensure_ascii=False)
    print("Salvat in", a.iesire)


if __name__ == "__main__":
    main()
