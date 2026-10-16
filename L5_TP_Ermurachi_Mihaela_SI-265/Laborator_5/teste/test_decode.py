# -*- coding: utf-8 -*-
"""teste/test_decode.py - teste scurte pentru arsenal/forensics/decode.py.

Se ruleaza din radacina Laborator_5/ cu:
    python -m pytest teste/
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arsenal.forensics.decode import (
    ghici_strat,
    desfa,
    citibil,
    despica,
    sparge_xor,
    sparge_hash,
)


def test_base64():
    strat, b = desfa("U2FsdXQ=")
    assert strat == "base64"
    assert b == b"Salut"


def test_ghici_strat_hex():
    assert ghici_strat("48656c6c6f") == "hex"


def test_ghici_strat_url():
    assert ghici_strat("%2Fetc") == "url"


def test_desfa_hex():
    strat, b = desfa("48656c6c6f")
    assert strat == "hex"
    assert b == b"Hello"


def test_desfa_url():
    strat, b = desfa("salut%20lume")
    assert strat == "url"
    assert b == b"salut lume"


def test_citibil():
    assert citibil(b"text normal") is True
    assert citibil(bytes([0, 1, 2, 255])) is False
    assert citibil(b"") is False


def test_despica_straturi_multiple():
    # "FLAG{ok}" -> hex -> base64 -> base64, exact ca in probe/mesaj.txt
    import base64

    clar = b"FLAG{ok}"
    pas1 = clar.hex().encode()
    pas2 = base64.b64encode(pas1)
    pas3 = base64.b64encode(pas2).decode()

    straturi, text = despica(pas3)
    assert text == "FLAG{ok}"
    assert straturi == ["base64", "base64", "hex", "necunoscut"]


def test_sparge_xor():
    # Cheia 0x80 e aleasa ca in probe/xor.bin: flip-uieste doar bitul cel
    # mai semnificativ. Textul original e ASCII standard (toti octetii sub
    # 128), deci dupa XOR cu 0x80 toti octetii criptati au bitul 7 pe 1
    # (nu mai sunt imprimabili); orice alta cheie gresita pastreaza acel
    # bit pe 1 la randul ei si tot nu da text imprimabil, deci 0x80 este
    # singura cheie posibila -- spre deosebire de o cheie oarecare, unde
    # pot aparea coincidente.
    secret = b"Un mesaj suficient de lung incat brute-force-ul sa fie clar!"
    cheie_corecta = 0x80
    date = bytes(b ^ cheie_corecta for b in secret)

    cheie, text = sparge_xor(date)
    assert cheie == cheie_corecta
    assert text == secret.decode()


def test_sparge_hash(tmp_path):
    import hashlib

    wordlist = tmp_path / "wordlist.txt"
    wordlist.write_text("alfa\nparola123\nbeta\n")
    tinta = hashlib.md5(b"parola123").hexdigest()

    algoritm, parola = sparge_hash(tinta, str(wordlist))
    assert algoritm == "md5"
    assert parola == "parola123"
