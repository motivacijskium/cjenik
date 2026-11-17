# Strojno čitljiv cjenik — Motivacijski Um

## Gdje će se to vidjeti na tvojoj stranici

Nigdje posebno. Cjenik nije za ljude, nego za programe koji automatski skupljaju
cijene i za inspekciju. Tvoj landing page ostaje identičan.

Jedino vidljivo je **jedan link u podnožju stranice** na kojem piše „Cjenik". Klikom
se otvara popis datoteka. Posjetitelji ga neće otvarati.

Izgled popisa radi skripta sama (`index.html`) — najnoviji cjenik je prvi, ispod su
stariji, s datumom i vremenom objave. Boje i font su kao na tvojim stranicama.

## Besplatno rješenje bez ručnog rada

GitHub Actions generira novu datoteku svaki radni dan i objavljuje ju na GitHub
Pages. Ti ne radiš ništa. Besplatno je, bez ograničenja za ovu namjenu.

**Što ti treba napraviti — tri koraka:**

1. Otvori besplatan račun na `github.com` ako ga nemaš.
2. U claude.ai idi na Settings → Connectors i poveži GitHub.
3. Reci mi da je povezano.

Nakon toga ja napravim repozitorij, ubacim skriptu i raspored, uključim Pages i
dodam link u podnožje tvojih stranica. Ti više ne diraš ništa.

Ako to želiš sam, ručno:

1. Novi repozitorij na GitHubu, naziv `cjenik`, **Public**.
2. Upload `generiraj_cjenik.py` u korijen repozitorija.
3. Napravi mapu `.github/workflows/` i u nju upload `workflow-cjenik.yml`.
4. Settings → Pages → Source: `Deploy from a branch`, branch `main`, folder `/ (root)`.
5. Actions → „Objavi cjenik" → `Run workflow` da se prvi cjenik generira odmah.

Datoteke su tada na `https://TVOJ-KORISNIK.github.io/cjenik/cjenik/`.

### Raspored

Cron je postavljen na 05:10 UTC, radnim danima. To je 06:10 zimi, 07:10 ljeti —
namjerno rano, jer GitHub ponekad odgodi pokretanje, a propis traži objavu
**najkasnije do 8:00**. Ako primijetiš da kasni, pomakni cron na `40 4 * * 1-5`.

## Jedna stvar koju moraš znati prije nego se osloniš na ovo

Odluka kaže da trgovac cjenik objavljuje **na svojim mrežnim stranicama**. Kod ovog
besplatnog rješenja datoteka fizički stoji na `github.io`, a s tvoje stranice vodi
link na nju. Po mom čitanju to zadovoljava svrhu — cjenik je javno dostupan,
strojno čitljiv i dohvatljiv s tvoje stranice — ali **ne mogu ti garantirati da bi
inspektor to prihvatio** kao objavu na vlastitoj mrežnoj stranici.

Potpuno čisto bi bilo da datoteka stoji na tvojoj domeni. To nije skupo:

- Kupiš domenu, oko 10–15 € godišnje.
- Glavnu domenu usmjeriš na systeme.io kao do sada.
- Poddomenu `cjenik.tvojadomena.hr` usmjeriš na GitHub Pages — hosting ostaje
  besplatan, a adresa je tvoja.

Sve ostalo je identično. Ako odlučiš tako, reci i postavim DNS zapise.

Systeme.io ne može hostati datoteku ni u jednoj varijanti — File Manager nema API ni
raspored, pa bi svako jutro uploadao ručno.

## Odakle obveza

Odluka o objavi cjenika proizvoda i usluga kao mjera izravne kontrole cijena,
**NN 101/2026**, izmijenjena u **NN 110/2026**. Primjenjuje se **od 17. 11. 2026.**
Pravilnik o načinu objave cjenika proizvoda objavljen je 15. 11. 2026.

Obveza se odnosi na trgovce koji posluju s potrošačima i imaju mrežnu stranicu.
Ministarstvo je izričito pojasnilo da web shop traži **zasebnu** CSV ili XML
datoteku, neovisno o tome što su cijene već prikazane na stranicama.

## Rokovi i pravila

| | |
|---|---|
| Ažuriranje | jednom dnevno, najkasnije do 8:00 za tekući radni dan |
| Dostupnost | svaka objavljena datoteka ostaje dostupna 30 dana |
| Stare datoteke | ne brišu se i ne prepisuju — mora postojati povijest |
| Pristup | bez prijave, obrasca, CAPTCHA-e ili blokiranja botova |

Skripta drži arhivu 40 dana, deset dana zalihe iznad propisanog minimuma.

## Što je u datoteci

Sedam artikala. Kombinacije paketa nisu zasebni artikli — svaki dodatak ima svoju
cijenu, pa alat za usporedbu sam izračuna bilo koju kombinaciju.

| Artikl | Šifra | Cijena | Sidrena |
|---|---|---:|---:|
| Kod smirenosti — e-knjiga | MU-KS-EB | 24 € | 24 € |
| Kod smirenosti — audioknjiga | MU-KS-AUDIO | 6 € | 6 € |
| Prvih 60 sekundi — PDF | MU-KS-P60 | 7 € | 7 € |
| Psihološki dekoder — e-knjiga | MU-PD-EB | 24 € | 16 € |
| Psihološki dekoder — audioknjiga | MU-PD-AUDIO | 6 € | 6 € |
| Protokol odgovora — PDF | MU-PD-PROT | 7 € | 7 € |
| Paket obje e-knjige | MU-PAKET-2EB | 48 € | 40 € |

Dekoder ima ispunjeno polje posebnog oblika prodaje: „Akcija — ponuda za prve
čitatelje". U datoteci je time jasno da je 24 € akcijska, a 16 € sidrena cijena.

Barkod je prazan jer digitalni proizvodi nemaju EAN. Jedinica mjere je komad.

E-knjige sam tretirao kao **proizvode**, ne usluge. Za proizvode propis traži više
polja, pa je datoteka ispravna u svakom slučaju. Razlika je samo u učestalosti:
proizvodi svaki radni dan, usluge samo pri promjeni cijene.

## Naziv datoteke

Prema točki VI. Odluke sadrži oblik objekta, adresu, oznaku objekta, broj pohrane te
datum i vrijeme slanja:

```
webshop_Petrova Gora 62 Lobor_WEB_7_17.11.2026_06-10.csv
```

Broj pohrane skripta sama povećava i pamti u `cjenik/.broj_pohrane.json`. Dvotočje u
vremenu zamijenjeno je crticom jer dvotočje ne prolazi u URL-u; Odluka ne propisuje
razdjelnik.

## Kad mijenjaš cijene

Uredi blok `ARTIKLI` na vrhu skripte. **Sidrenu cijenu ne diraj** — ona je fiksna i
veže se na referentni dan: 10. 9. 2026. za Kod smirenosti i dodatke, 10. 11. 2026.
za Dekoder i paket.

Kad Dekoderu istekne popust i cijena ide na 32 €, promijeni samo:

```python
"maloprodajna_cijena": "32.00",
"posebni_oblik_prodaje": "NE",
"naziv_posebnog_oblika_prodaje": "",
```

Sidrena ostaje `16.00`.

## Napomena

Napravio sam datoteku prema tekstu Odluke i objavljenim pojašnjenjima Ministarstva.
Nisam pravnik. Provjeri sa knjigovođom primjenjuje li se obveza na tvoj obrt u punom
obliku i jesu li e-knjige u tvom slučaju proizvod ili usluga — to mijenja samo
učestalost ažuriranja, ne sadržaj datoteke.
