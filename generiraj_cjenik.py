#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator strojno čitljivog cjenika — Motivacijski Um
Odluka o objavi cjenika proizvoda i usluga (NN 101/2026, izmjene NN 110/2026),
primjena od 17. studenoga 2026.

Pokretanje:  python3 generiraj_cjenik.py
Rezultat:    jedna .csv i jedna .xml datoteka u mapi ./cjenik/

Datoteku treba objaviti na mrežnoj stranici svaki radni dan najkasnije do 8:00
i držati je dostupnom 30 dana (stare datoteke se NE brišu i NE prepisuju).
"""

import csv
import datetime
import json
import os
import re
import urllib.parse
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ──────────────────────────────────────────────────────────────────────────────
# 1. PODACI O OBJEKTU  — ovo ispuni jednom i više ne diraj
# ──────────────────────────────────────────────────────────────────────────────

OBLIK_OBJEKTA = "webshop"                      # oblik prodajnog objekta
ADRESA_OBJEKTA = "motivacijskium"            # ide u naziv datoteke
OZNAKA_OBJEKTA = "WEB"                         # oznaku objekta određuješ sam
NAZIV_TRGOVCA = "Motivacijski Um"

IZLAZNA_MAPA = "docs"
BROJAC_DATOTEKA = "docs/.broj_pohrane.json"   # pamti broj pohrane između pokretanja
DANA_ARHIVE = 40                                # propis traži 30; držimo zalihu

# ──────────────────────────────────────────────────────────────────────────────
# 2. KATALOG  — ovdje mijenjaš cijene kad se promijene
#
#    bazna_cijena = cijena koja je vrijedila na referentni dan
#      • Kod smirenosti i dodaci  → 10. 9. 2026.
#      • Psihološki dekoder, paket → 10. 11. 2026. (prva prodaja)
#    Bazna se cijena NE mijenja kad promijeniš maloprodajnu cijenu.
# ──────────────────────────────────────────────────────────────────────────────

ARTIKLI = [
    {
        "sifra": "MU-KS-EB",
        "naziv": "Kod smirenosti — e-knjiga (PDF)",
        "maloprodajna_cijena": "24.00",
        "bazna_cijena": "24.00",
        "posebni_oblik_prodaje": "NE",
        "naziv_posebnog_oblika_prodaje": "",
    },
    {
        "sifra": "MU-KS-AUDIO",
        "naziv": "Kod smirenosti — audioknjiga",
        "maloprodajna_cijena": "6.00",
        "bazna_cijena": "6.00",
        "posebni_oblik_prodaje": "NE",
        "naziv_posebnog_oblika_prodaje": "",
    },
    {
        "sifra": "MU-KS-P60",
        "naziv": "Prvih 60 sekundi — PDF dodatak",
        "maloprodajna_cijena": "7.00",
        "bazna_cijena": "7.00",
        "posebni_oblik_prodaje": "NE",
        "naziv_posebnog_oblika_prodaje": "",
    },
    {
        "sifra": "MU-PD-EB",
        "naziv": "Psihološki dekoder — e-knjiga (PDF)",
        "maloprodajna_cijena": "24.00",
        "bazna_cijena": "16.00",
        "posebni_oblik_prodaje": "DA",
        "naziv_posebnog_oblika_prodaje": "Akcija — ponuda za prve čitatelje",
    },
    {
        "sifra": "MU-PD-AUDIO",
        "naziv": "Psihološki dekoder — audioknjiga",
        "maloprodajna_cijena": "6.00",
        "bazna_cijena": "6.00",
        "posebni_oblik_prodaje": "NE",
        "naziv_posebnog_oblika_prodaje": "",
    },
    {
        "sifra": "MU-PD-PROT",
        "naziv": "Protokol odgovora — PDF dodatak",
        "maloprodajna_cijena": "7.00",
        "bazna_cijena": "7.00",
        "posebni_oblik_prodaje": "NE",
        "naziv_posebnog_oblika_prodaje": "",
    },
    {
        "sifra": "MU-PAKET-2EB",
        "naziv": "Paket — Kod smirenosti i Psihološki dekoder, obje e-knjige (PDF)",
        "maloprodajna_cijena": "40.00",
        "bazna_cijena": "40.00",
        "posebni_oblik_prodaje": "NE",
        "naziv_posebnog_oblika_prodaje": "",
    },
]

# Polja koja Odluka traži za svaki proizvod. Barkod je prazan jer digitalni
# proizvodi nemaju EAN. Jedinica mjere je komad, pa je cijena za jedinicu mjere
# jednaka maloprodajnoj cijeni.
STUPCI = [
    "naziv",
    "sifra",
    "marka",
    "jedinica_mjere",
    "cijena_za_jedinicu_mjere",
    "maloprodajna_cijena",
    "posebni_oblik_prodaje",
    "naziv_posebnog_oblika_prodaje",
    "bazna_cijena",
    "barkod",
    "dostupnost",
]


def red_za_artikl(a):
    return {
        "naziv": a["naziv"],
        "sifra": a["sifra"],
        "marka": NAZIV_TRGOVCA,
        "jedinica_mjere": "kom",
        "cijena_za_jedinicu_mjere": a["maloprodajna_cijena"],
        "maloprodajna_cijena": a["maloprodajna_cijena"],
        "posebni_oblik_prodaje": a["posebni_oblik_prodaje"],
        "naziv_posebnog_oblika_prodaje": a["naziv_posebnog_oblika_prodaje"],
        "bazna_cijena": a["bazna_cijena"],
        "barkod": "",
        "dostupnost": "dostupno",
    }


def sljedeci_broj_pohrane():
    broj = 0
    if os.path.exists(BROJAC_DATOTEKA):
        try:
            with open(BROJAC_DATOTEKA, encoding="utf-8") as f:
                broj = int(json.load(f).get("broj_pohrane", 0))
        except (ValueError, OSError, json.JSONDecodeError):
            broj = 0
    broj += 1
    with open(BROJAC_DATOTEKA, "w", encoding="utf-8") as f:
        json.dump({"broj_pohrane": broj}, f)
    return broj


def osnovno_ime(sada, broj_pohrane):
    # Odluka, točka VI.: oblik objekta, adresa objekta, oznaka objekta,
    # broj pohrane, datum i vrijeme slanja datoteke.
    # Dvotočje se u nazivu zamjenjuje crticom jer nije dopušteno u URL-u
    # i na dijelu datotečnih sustava. Odluka ne propisuje razdjelnik.
    return "{}_{}_{}_{}_{}".format(
        OBLIK_OBJEKTA,
        ADRESA_OBJEKTA,
        OZNAKA_OBJEKTA,
        broj_pohrane,
        sada.strftime("%d.%m.%Y_%H-%M"),
    )


def zapisi_csv(putanja, redovi):
    with open(putanja, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=STUPCI, delimiter=";")
        w.writeheader()
        w.writerows(redovi)


def zapisi_xml(putanja, redovi, sada, broj_pohrane):
    korijen = ET.Element("Cjenik")
    korijen.set("trgovac", NAZIV_TRGOVCA)
    korijen.set("oblikObjekta", OBLIK_OBJEKTA)
    korijen.set("oznakaObjekta", OZNAKA_OBJEKTA)
    korijen.set("brojPohrane", str(broj_pohrane))
    korijen.set("datumVrijeme", sada.strftime("%Y-%m-%dT%H:%M:%S"))
    korijen.set("valuta", "EUR")

    for r in redovi:
        p = ET.SubElement(korijen, "Proizvod")
        for stupac in STUPCI:
            ET.SubElement(p, stupac).text = r[stupac]

    sirovi = ET.tostring(korijen, encoding="utf-8")
    lijepi = minidom.parseString(sirovi).toprettyxml(indent="  ", encoding="utf-8")
    with open(putanja, "wb") as f:
        f.write(lijepi)


_UZORAK_VREMENA = re.compile(r"_(\d{2})\.(\d{2})\.(\d{4})_(\d{2})-(\d{2})\.(?:csv|xml)$", re.I)


def vrijeme_datoteke(naziv):
    """Vrijeme cjenika iz njegovog imena, a ne iz mtime.

    Mtime nije pouzdan: git checkout, rebase ili ponovno kloniranje repozitorija
    ga resetiraju na trenutak operacije. Time bi popis pokazivao pogrešno vrijeme,
    a brisanje iz arhive bi krivo računalo 30-dnevni rok iz propisa. Ime datoteke
    nosi stvarni datum i vrijeme objave i ne mijenja se.
    """
    m = _UZORAK_VREMENA.search(naziv)
    if m:
        dan, mjesec, godina, sat, minuta = (int(x) for x in m.groups())
        try:
            return datetime.datetime(godina, mjesec, dan, sat, minuta)
        except ValueError:
            pass
    return datetime.datetime.fromtimestamp(
        os.path.getmtime(os.path.join(IZLAZNA_MAPA, naziv))
    )


def ocisti_arhivu(sada):
    """Briše datoteke starije od DANA_ARHIVE. Propis traži 30 dana dostupnosti."""
    granica = sada - datetime.timedelta(days=DANA_ARHIVE)
    obrisano = 0
    for naziv in os.listdir(IZLAZNA_MAPA):
        if not naziv.lower().endswith((".csv", ".xml")):
            continue
        if vrijeme_datoteke(naziv) < granica:
            os.remove(os.path.join(IZLAZNA_MAPA, naziv))
            obrisano += 1
    return obrisano


def zapisi_index():
    """Stranica s direktnim linkovima na sve objavljene cjenike, najnoviji prvi."""
    datoteke = sorted(
        (n for n in os.listdir(IZLAZNA_MAPA) if n.lower().endswith((".csv", ".xml"))),
        key=vrijeme_datoteke,
        reverse=True,
    )

    redovi_html = []
    for n in datoteke:
        vrijeme = vrijeme_datoteke(n)
        redovi_html.append(
            '<li><a href="{0}">{1}</a> <span>{2}</span></li>'.format(
                urllib.parse.quote(n),
                n.replace("&", "&amp;").replace("<", "&lt;"),
                vrijeme.strftime("%d.%m.%Y. u %H:%M"),
            )
        )

    html = """<!DOCTYPE html>
<html lang="hr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cjenik — {trgovac}</title>
<style>
body{{font:16px/1.6 Arial,Helvetica,sans-serif;color:#25231f;background:#f5f0e7;
margin:0;padding:clamp(20px,5vw,56px)}}
main{{max-width:760px;margin:0 auto}}
h1{{font:500 clamp(26px,4vw,38px)/1.2 Georgia,serif;margin:0 0 6px}}
p.uvod{{color:#514b42;margin:0 0 28px}}
ul{{list-style:none;padding:0;margin:0}}
li{{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;
padding:10px 0;border-bottom:1px solid #dfd5c6}}
a{{color:#7b2d2a;word-break:break-all}}
li span{{color:#70695f;font-size:13px;white-space:nowrap}}
footer{{margin-top:32px;font-size:13px;color:#70695f}}
</style>
</head>
<body>
<main>
<h1>Cjenik proizvoda</h1>
<p class="uvod">{trgovac}. Cjenici su objavljeni u strojno čitljivom
CSV i XML formatu u skladu s Odlukom o objavi cjenika proizvoda i usluga
(NN 101/2026, NN 110/2026). Najnoviji cjenik je prvi na popisu.</p>
<ul>
{redovi}
</ul>
<footer>Cijene su u eurima. Bazna cijena je cijena koja je vrijedila na
referentni dan: 10. 9. 2026. za Kod smirenosti i njegove dodatke,
10. 11. 2026. za Psihološki dekoder i paket.</footer>
</main>
</body>
</html>
""".format(
        trgovac=NAZIV_TRGOVCA,
        redovi="\n".join(redovi_html) if redovi_html else "<li>Nema objavljenih cjenika.</li>",
    )

    with open(os.path.join(IZLAZNA_MAPA, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return len(datoteke)


def main():
    os.makedirs(IZLAZNA_MAPA, exist_ok=True)
    sada = datetime.datetime.now()
    broj_pohrane = sljedeci_broj_pohrane()
    redovi = [red_za_artikl(a) for a in ARTIKLI]
    ime = osnovno_ime(sada, broj_pohrane)

    csv_putanja = os.path.join(IZLAZNA_MAPA, ime + ".csv")
    xml_putanja = os.path.join(IZLAZNA_MAPA, ime + ".xml")
    zapisi_csv(csv_putanja, redovi)
    zapisi_xml(xml_putanja, redovi, sada, broj_pohrane)

    obrisano = ocisti_arhivu(sada)
    u_arhivi = zapisi_index()

    print("Generirano {} artikala, broj pohrane {}.".format(len(redovi), broj_pohrane))
    print("{}".format(csv_putanja))
    print("{}".format(xml_putanja))
    print("U arhivi: {} datoteka. Obrisano starih: {}.".format(u_arhivi, obrisano))


if __name__ == "__main__":
    main()
