# Laboratorul 5 — Informații invizibile: forensics și steganografie

**Student:** Ermurachi Mihaela, gr. SI-265
**Disciplina:** Tehnici de programare

---

## Lucrarea A — Decoderul universal (`arsenal/forensics/decode.py`)

### Ce ascundea `probe/mesaj.txt`

Șirul din `mesaj.txt` este codat în trei straturi succesive. Rulat prin
`despica()`, decoderul le-a desfăcut automat, în ordine:

| Pas | Strat recunoscut |
|----:|-------------------|
| 1   | base64            |
| 2   | base64            |
| 3   | hex               |
| 4   | necunoscut (text simplu — s-a oprit aici) |

**Mesajul ascuns era:** `FLAG{straturi_de_encoding}`

Comanda folosită:

```
python arsenal/forensics/decode.py "$(cat probe/mesaj.txt)"
```

### Cheia XOR găsită în `probe/xor.bin`

Brute-force pe toate cele 256 de chei posibile (`sparge_xor`) a găsit o
singură cheie care produce text imprimabil:

- **Cheia XOR:** `128` (`0x80`)
- **Textul clar:** `Un singur octet tine tot secretul... gaseste-l! FLAG{xor_un_octet}`

Comanda folosită:

```
python arsenal/forensics/decode.py probe/xor.bin --fisier
```

### Parola spartă din `probe/hashuri.txt`

Toate cele 5 hash-uri din fișier sunt MD5 (32 de caractere hex) și au fost
sparte prin căutare în `probe/wordlist.txt`:

| Hash (MD5)                        | Parolă     |
|------------------------------------|------------|
| `5f4dcc3b5aa765d61d8327deb882cf99` | `password` |
| `8621ffdbc5698829397d97767ac13db3` | `dragon`   |
| `d8578edf8458ce06fbc5bb76a58c5ca4` | `qwerty`   |
| `0d107d09f5bbe40cade3de5c71e9e9b7` | `letmein`  |
| `d0763edaa9d9bd2a9516280e9044d885` | `monkey`   |

### Bonus — `probe/challenge.bin` (pentru vârful sălii)

Fișierul combină un strat de base64 peste un XOR cu cheie de un octet,
exact cum descrie `challenge_hint.txt`. Pașii parcurși manual, cu aceleași
funcții din `decode.py`:

1. `base64.b64decode(...)` pe conținutul fișierului → octeți criptați XOR.
2. `sparge_xor(...)` pe acei octeți → cheia `128` (`0x80`), ca și la `xor.bin`.
3. Textul clar obținut: `FLAG{lant_complet_despicat}`
4. Verificare: `md5("FLAG{lant_complet_despicat}")` = `8c4eb02d9dcef7d0ff91d8e4c7fea91b`,
   identic cu hash-ul din `challenge_hint.txt`. ✅

### Teste

`teste/test_decode.py` conține 9 teste (recunoașterea fiecărui strat,
desfacerea lui, straturi multiple înlănțuite, spargerea XOR și spargerea
unui hash prin dicționar). Toate trec:

```
python -m pytest teste/
```

---

## Lucrarea B — Forensics pe fișiere și mesaj ascuns

### Tipul real al fișierelor (magic bytes)

| Fișier            | Extensie | Tip real (după semnătură) |
|--------------------|----------|----------------------------|
| `probe/foto.jpg`   | .jpg     | `jpeg` ✅ (corespunde)      |
| `probe/ascuns.png` | .png     | `png` ✅ (corespunde)       |
| `probe/xor.bin`    | .bin     | niciuna recunoscută — date criptate, fără semnătură de format |

### `strings` pe `probe/ascuns.png`

Printre secvențele de caractere imprimabile extrase din fișier apar
clar structurile PNG obișnuite (`IHDR`, `IDATx`, `IEND`), dar și
indiciul căutat, chiar la coada fișierului:

```
secret.txtFLAG{ascuns_prin_carving}
```

Acesta este, de fapt, numele fișierului și conținutul lui din interiorul
arhivei ZIP lipite la coada imaginii — vizibile direct, fără să mai fie
nevoie de dezarhivare, pentru că arhiva nu e comprimată puternic.

### Metadate EXIF și GPS din `probe/foto.jpg`

| Etichetă | Valoare |
|----------|---------|
| Make     | Apple |
| Model    | iPhone 13 |
| DateTime | 2026:09:14 10:30:00 |

**Coordonate GPS**, convertite din (grade, minute, secunde) în grade
zecimale:

- **Latitudine:** 47.016667° N
- **Longitudine:** 28.857500° E
- Pe hartă: <https://www.openstreetmap.org/?mlat=47.016667&mlon=28.857500&zoom=14>

Coordonatele indică **Chișinău** — exact genul de informație pe care o
fotografie o poate scurge fără voia celui care o publică, dacă nu i se
șterge EXIF-ul înainte.

### Arhiva ascunsă în `probe/ascuns.png` (file carving)

Semnătura unei arhive ZIP (`PK\x03\x04`) a fost găsită lipită la coada
fișierului PNG, începând de la **octetul 781**. Extrasă separat, în
`gasit.zip`, arhiva conține un singur fișier:

- `secret.txt` → `FLAG{ascuns_prin_carving}`

### Mesajul ascuns prin steganografie LSB

Mesajul `FLAG{ascuns_in_pixeli}` a fost ascuns în ultimul bit al
canalelor R/G/B din `probe/foto.jpg`, salvat fără pierdere în `stego.png`
(imaginea arată identică cu originalul — doar biții cei mai puțin
semnificativi ai pixelilor s-au schimbat).

Dezvăluit înapoi, citind aceiași biți în aceeași ordine, până la octetul
terminator (`0x00`):

```
python stego.py dezvaluie stego.png
FLAG{ascuns_in_pixeli}
```

Mesajul recuperat este identic cu cel ascuns inițial. ✅

---

## Concluzie

Toate cele șapte fișiere din `probe/` au fost analizate cu succes:
mesajul pe straturi, cheia XOR și parolele au fost sparte automat de
`decode.py`; tipul real, textul ascuns, GPS-ul și arhiva ascunsă au fost
scoase din fișiere cu `forensics.py`; iar `stego.py` a demonstrat, pe un
ciclu complet, cum un mesaj poate fi ascuns și apoi recuperat dintr-o
imagine fără nicio schimbare vizibilă. Bonusul `challenge.bin` a
confirmat că aceleași unelte de bază (decodare + XOR + verificare prin
hash) se pot înlănțui pentru a despica un caz mai complex.
