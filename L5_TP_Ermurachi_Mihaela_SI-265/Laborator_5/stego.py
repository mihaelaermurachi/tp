# -*- coding: utf-8 -*-
"""
stego.py

Steganografie LSB: ascunde un mesaj in ultimul bit al fiecarui canal de
culoare al unei imagini (rosu, verde, albastru), apoi il dezvaluie
inapoi, citind aceiasi biti in aceeasi ordine.

Tehnici de programare - Laboratorul 5, Lucrarea B (B5-B6).
Student: Ermurachi Mihaela, gr. SI-265.
"""

import argparse
from PIL import Image

TERMINATOR = b"\x00"  # un octet nul marcheaza finalul mesajului ascuns


# ---------------------------------------------------------------------------
# B5. Ascunzi un mesaj prin LSB
# ---------------------------------------------------------------------------
def ascunde_lsb(cale_imagine: str, mesaj: bytes, cale_iesire: str):
    """Scrie mesaj (octeti) in ultimul bit al fiecarui canal R/G/B al
    imaginii de la cale_imagine si salveaza rezultatul, fara pierdere,
    in cale_iesire (trebuie sa fie .png).

    Adauga automat un octet 0x00 la finalul mesajului, ca sa stim unde
    se opreste la dezvaluire.
    """
    img = Image.open(cale_imagine).convert("RGB")
    px = list(img.getdata())

    date = mesaj + TERMINATOR
    biti = "".join(f"{octet:08b}" for octet in date)

    capacitate = len(px) * 3
    if len(biti) > capacitate:
        raise ValueError(
            f"Mesajul are nevoie de {len(biti)} biti, dar imaginea are loc "
            f"doar pentru {capacitate} (prea mic)."
        )

    px_nou = []
    indice_bit = 0
    for (r, g, b) in px:
        canale = [r, g, b]
        for i in range(3):
            if indice_bit < len(biti):
                bit = int(biti[indice_bit])
                canale[i] = (canale[i] & ~1) | bit
                indice_bit += 1
        px_nou.append(tuple(canale))

    img.putdata(px_nou)
    img.save(cale_iesire)  # .png: fara pierdere, biții rămân neatinși
    return len(date)


# ---------------------------------------------------------------------------
# B6. Dezvalui mesajul inapoi
# ---------------------------------------------------------------------------
def dezvaluie_lsb(cale_imagine: str) -> bytes:
    """Citeste ultimul bit al fiecarui canal R/G/B din cale_imagine, ii
    regrupeaza cate 8 si reconstituie mesajul, oprindu-se la primul octet
    nul (terminatorul pus de ascunde_lsb).
    """
    px = list(Image.open(cale_imagine).convert("RGB").getdata())

    biti = []
    for (r, g, b) in px:
        biti.append(r & 1)
        biti.append(g & 1)
        biti.append(b & 1)

    octeti = bytearray()
    for i in range(0, len(biti) - 7, 8):
        bucata = biti[i:i + 8]
        valoare = int("".join(str(bit) for bit in bucata), 2)
        if valoare == 0:
            break
        octeti.append(valoare)

    return bytes(octeti)


def main():
    parser = argparse.ArgumentParser(description="Steganografie LSB: ascunde/dezvaluie un mesaj intr-o imagine.")
    sub = parser.add_subparsers(dest="comanda", required=True)

    p_ascunde = sub.add_parser("ascunde", help="ascunde un mesaj intr-o imagine")
    p_ascunde.add_argument("imagine", help="imaginea gazda (orice format citit de Pillow)")
    p_ascunde.add_argument("mesaj", help="textul de ascuns")
    p_ascunde.add_argument("iesire", nargs="?", default="stego.png", help="unde se salveaza (implicit stego.png)")

    p_dezvaluie = sub.add_parser("dezvaluie", help="citeste mesajul ascuns dintr-o imagine")
    p_dezvaluie.add_argument("imagine", help="imaginea stego (de obicei stego.png)")

    a = parser.parse_args()

    if a.comanda == "ascunde":
        n = ascunde_lsb(a.imagine, a.mesaj.encode(), a.iesire)
        print(f"Ascuns {n} octeti (cu terminator) in {a.iesire}")
    else:
        mesaj = dezvaluie_lsb(a.imagine)
        print(mesaj.decode(errors="replace"))


if __name__ == "__main__":
    main()
