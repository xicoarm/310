# Parcel CH767815507214 — research notes (collected before network access)

Status: the cloud environment blocks all outbound hosts (api.geo.ag.ch, apps.geo.ag.ch,
geo.admin.ch, municipality sites, even PyPI). Everything parcel-specific below is still
**unknown** until `fetch_parcel.py` can run. Figures marked *(web search, unverified)* come
from search-engine summaries, not from the source documents themselves.

## Location
- Link coordinates LV95 E 2'670'029.8 / N 1'246'145.6 ≈ 47.3624 N, 8.3657 E (own conversion).
- That is the Mutschellen area, Bezirk Bremgarten AG: most likely **Widen** (PLZ 8967), close
  to the border with Berikon (8965). The ÖREB extract will confirm municipality, parcel
  number and land-register area.

## Zoning context (to be replaced by the ÖREB extract, which lists the BNO in force)
- Widen BNO "Stand Juni 2014" on widen.ch *(web search, unverified)*:
  - Dorfkernzone D: AZ 0.55, Grenzabstand 5 m, giebelseitige Fassadenhöhe max. 12.50 m
  - WG3: AZ 0.60, up to 0.85 with an Arealüberbauung
  - W2 AZ 0.45 and W3 AZ 0.55 are mentioned; W1 AZ 0.40. Number of storeys in the
    summary was garbled, so check the table in the PDF.
  - A current listing in Widen describes a 525 m² W1 plot as "2 Vollgeschosse + Attika, AZ 0.45",
    which suggests the BNO has been revised since 2014 (needs checking).
- Berikon: Gesamtrevision in force retroactively since 1.1.2016; Attika and basement living
  space no longer count toward AZ *(web search)*.

## Market benchmarks *(web search, unverified)*
| Item | Value | Source |
|---|---|---|
| Land price Widen, average | ~CHF 1'090 / m² | immobilienindex.ch |
| Land price Berikon, average | ~CHF 1'130 / m² | immobilienindex.ch |
| Apartment sale price Widen | ~CHF 7'300–9'400 / m² (sources disagree) | immobilienindex.ch, realadvisor.ch |
| House sale price Widen | ~CHF 7'900–10'100 / m² | same |
| Berikon, all objects | ~CHF 8'100–11'200 / m² | immobilienindex.ch, neho.ch |
| Rent, apartments Widen | ~CHF 293 / m² / year | realadvisor.ch |
| Rent examples Widen | 3 rooms ~CHF 2'040, 4 rooms ~CHF 2'510, 5 rooms ~CHF 3'260 / month | realadvisor.ch |

Plots currently advertised in Widen/Berikon (search snippets): 880 m², 1'094 m², 1'631 m²
(view plot), 525 m² W1; Berikon Unterdorfstrasse 922 m² + 70 m² transferable floor area,
village-centre zone AZ 0.55. A homegate ad "Papillon – Ein besonderer Ort – BA1,
Dorfstrasse 60, CHF 2'500'000" also showed up.

## Costs, taxes, financing *(web search, unverified)*
- Construction cost BKP 2: simple CHF 600–750 / m³, mid CHF 750–950 / m³ (SIA 416);
  rental apartment blocks without underground garage ~CHF 680 / m³, condo blocks CHF 900–950 / m³.
  Ancillary costs, site works, fees add 25–40 %.
- Aargau: **no Handänderungssteuer**; Grundbuchabgabe 0.4 % of purchase price.
- Aargau Grundstückgewinnsteuer: 40 % in year 1, −2 pp per year up to year 11, then −1 pp
  per year, minimum 5 % after 25 years. Short holding (build-and-sell) is heavily taxed.
- SNB policy rate 0.00 %; 10-year fixed mortgages ~1.5–2.1 %; SARON mortgages ~0.7–1.3 %.

## Sources
- https://www.widen.ch/public/upload/assets/261/BNO_2014.pdf
- https://www.widen.ch/public/upload/assets/148/BNO_20110712.pdf
- https://www.aargauerzeitung.ch/aargau/freiamt/raumplanungsgesetz-wirbelte-zeitplan-durcheinander-ld.1744192
- https://www.immobilienindex.ch/AG/Widen/ · https://www.immobilienindex.ch/AG/Berikon/
- https://realadvisor.ch/de/immobilienpreise-pro-m2/8967-widen · https://realadvisor.ch/de/mieten/8967-widen/wohnung
- https://neho.ch/de/quadratmeterpreis-berikon
- https://www.homegate.ch/buy/plot/city-widen/matching-list · https://www.homegate.ch/kaufen/4002267270
- https://neho.ch/de/blog/baukosten-schweiz-pro-m3 · https://timberfinance.ch/wp-content/uploads/2025/07/202504-Abschlussbericht_Holzbaukennzahlen_Wust-Partner.pdf
- https://www.ag.ch/de/themen/planen-bauen/grundbuch-vermessung/grundbuch/grundbuchabgaben-und-gebuehren
- https://realadvisor.ch/de/blog/grundstueckgewinnsteuer-im-kanton-aargau
- https://www.moneypark.ch/ch/mp/de/home/hypotheken/hypothekar-zinsentwicklung.html
