# Laborator: functii, metode si importuri pe web
# Student: Ermurachi Mihaela
#
# main.py -- programul care importa modulul propriu webtools.

import argparse

# --- Exercitiul 44: importarea intregului modul ---------------------------
import webtools

# --- Exercitiul 45: importarea anumitor nume -------------------------------
from webtools import get_title, security_headers, check_paths, save_report_csv
# Daca main.py ar avea si o functie proprie numita get_title, ea ar
# "acoperi" (shadow) numele importat din webtools: ultima definitie a
# numelui get_title din acest fisier ar fi cea folosita mai departe, iar
# get_title importat din webtools nu ar mai fi accesibil direct sub acel
# nume (ar trebui apelat ca webtools.get_title(), nu doar get_title()).


def main():
    # --- Exercitiul 48: argument din linia de comanda ---------------------
    parser = argparse.ArgumentParser(
        description="Genereaza un raport despre un site web."
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="https://cybercor.org",
        help="adresa site-ului de analizat (implicit: https://cybercor.org)",
    )
    argumente = parser.parse_args()
    url = argumente.url

    # --- Exercitiul 44: folosirea modulului importat intreg ---------------
    raspuns_initial = webtools.fetch(url)
    print("Titlu (prin webtools.fetch + webtools.get_title):",
          webtools.get_title(raspuns_initial.text))

    # --- Exercitiul 45: folosirea numelor importate direct -----------------
    print("Titlu (import direct get_title):", get_title(raspuns_initial.text))

    # --- Exercitiul 47: constanta de modul ----------------------------------
    print("DEFAULT_HEADERS:", webtools.DEFAULT_HEADERS)

    # --- Exercitiul 30: scorul antetelor de securitate, pentru control -------
    print("Antete de securitate:", security_headers(url))

    # --- Exercitiul 49: raport CSV --------------------------------------------
    rezultate_cai = check_paths(url, ["/", "/robots.txt", "/sitemap.xml"])
    save_report_csv(rezultate_cai, path="report.csv")
    print("Salvat in report.csv")

    # --- Exercitiul 50: raportul final, complet -------------------------------
    webtools.site_report(url)


if __name__ == "__main__":
    main()

# Explicatie pentru exercitiul 46 (blocul "if __name__ == '__main__':" este
# in webtools.py): acel bloc contine un autotest care ruleaza DOAR cand
# webtools.py este executat direct (python webtools.py), pentru ca atunci
# Python seteaza __name__ pe "__main__" in interiorul lui webtools.py.
# Cand webtools este doar importat (ca aici, in main.py, cu "import
# webtools"), __name__ din interiorul lui webtools.py devine "webtools" (numele
# modulului), nu "__main__", asa ca blocul de autotest nu se executa --
# ruleaza doar functiile pe care chiar le apelam noi, explicit, din main.py.
