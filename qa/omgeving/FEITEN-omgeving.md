# Feiten omgevingspagina's (Hotel Asteria, /omgeving-v2 en /omgeving-<cat>-v2)

Peildatum 11 nov 2026. Eigen teksten vanuit Venray; niets overgenomen van parkhotelhorst.nl, www.asteria.nl/omgeving, de
Effecty-staging of de gespiegelde `omgeving.html`. Feiten alleen uit de bronnen hieronder.

## Bronnen

- HC | `hotel-content.md` (repo): adres, wellness 300 m² op de Top Floor met vier sauna's, stoomcabine, dompelbad; brasserie met streekproducten; A73.
- CL | `CLAUDE.md` (repo, vaste feiten Stijn 14 okt 2026): ontbijt ma-vr 07.00-10.00, za-zo 08.00-10.30.
- UJ | `translations/uitje-*-nl.json` (deze tak + ~/projects/asteria-pages-omgeving): rijtijden `vk-auto`/`vk-fiets` (Venray-centrum 6/20, Oorlogsmuseum 9/25, ZooParc 11/35, Maasduinen 18/55, Mind Mystery 10, De Locht 14, Hertog Jan 23, Limburgs Museum 24, Venlo 24, Kasteeltuinen 25, Toverland 26, Roermond 40, Groote Peel 43).
- FV | `qa/uitje/FEITEN-venray-centrum.md`: weekmarkt maandag 11.00-16.00 op Henseniusplein en Schouwburgplein; koopzondag niet elke zondag.
- FO | `qa/uitje/FEITEN-oorlogsmuseum-overloon.md` en `translations/uitje-oorlogsmuseum-overloon-nl.json`: gevechten 1944, Britse oorlogsbegraafplaats Venray.
- GA | `translations/golfarrangement-nl.json` `_banen` (eigen Asteria-tekst): Geijsteren ca. 15 min, 13 holes tussen de bomen + 5 waterholes, bosrijk historisch landgoed; Bleijenbeek in Afferden ca. 25 min, glooiend, waterpartijen, bomenlanen, kasteelruïne; greenfee 18 holes in het arrangement.
- OA | `translations/oorlogsmuseum-arrangement-nl.json`: inhoud Oorlogsmuseum Arrangement (overnachting, entree, koffie of thee, drie-gangen diner, ontbijt).
- BD | `~/Documents/Asteria-omgevingsonderzoek/beslisdocument-inhoud.md` (kolom A/PH min): Toverland 25, Thermaalbad Arcen 23, Venlo 27, Roermond 40, Groote Peel 44 (gebruikt waar het uitje-JSON ontbreekt; bij verschil wint het uitje-JSON).
- KAL | `/api/arr-kalender?code=GOLF` live opgevraagd op 11 nov 2026: november deel 1 buiten bereik (verleden), 17-24 nov beschikbaar, december, maart en mei 2027 beschikbaar.

## Gebruikte feiten per pagina

- Overzicht: rijtijden Venray 6, Oorlogsmuseum 9, ZooParc 11 (UJ); ontbijttijden (CL); wellness (HC); arrangement Oorlogsmuseum (OA).
- Cultuur: 1944 (FO); Oorlogsmuseum 9 min, De Locht ca. een kwartier (UJ 14), Arcen ca. 25 min (UJ 23/25); arrangement (OA).
- Dagje uit: ZooParc 11, Mind Mystery 10 (UJ); Toverland en Thermaalbad "ongeveer een half uur" (UJ 26, BD 23-25).
- Natuur: Maasduinen 18 min auto, ca. 50 min fiets (UJ 55); Groote Peel "ruim drie kwartier" (UJ 43, BD 44).
- Shoppen & Steden: Venray 6 min auto, ca. 20 min fiets (UJ); weekmarkt (FV); Venlo ca. 25 min (UJ 24, BD 27); Roermond 40 min (UJ, BD).
- Golf: alles uit GA; vergelijkingstabel alleen rijen met bron (rijtijd, plaats, karakter, opvallend, greenfee in het arrangement).

## Nog nakijken

1. Parkeren bij het hotel (overzicht f2, m2): geen harde bron (alleen reviews en de foto `l26-waarom-parkeren`). Gratis staat bewust niet in de tekst.
2. Wandelkaarten bij de receptie en een plek voor de fiets (overzicht f3, natuur f2/f3/f6): wandelkaarten alleen in `route-wandelen-nl.json` (andere tak); fietsenstalling alleen uit een gastreview.
3. Tickets via de receptie: hotel-content.md noemt tickets voor Kasteeltuinen en Oorlogsmuseum; de tekst belooft alleen dat de receptie helpt.
4. Kasteeltuinen Arcen staat volgens de afgesproken indeling bij Cultuur; het uitje-JSON heeft hero-cat "Dagje uit".
5. Golf: aantal holes per baan (Bleijenbeek), par, niveau, oefenfaciliteiten, buggy's en starttijden: geen bron, dus niet op de pagina (geen tabelrij, geen chip). FAQ f4 (starttijd) verwijst naar de receptie.
6. "De wellness op de Top Floor is voor hotelgasten" (dagje uit f3): wellness is volgens HC ook extern te reserveren; tijden niet bekend.
7. Late aankomst melden bij de receptie (dagje uit f5) en aankopen in het hotel laten (shoppen f6): huisregel nakijken.
8. Natuur m1: "bezoekerscentrum van De Maasduinen in Well" (UJ kaart-naam), openingstijden niet genoemd.
9. Heidebloei eind augustus (natuur f5): algemeen bekend, geen bron in de repo.
10. Mind Mystery heeft in het uitje-JSON een hotelfoto als herofoto (`l26-waarom-hotel.webp`), zichtbaar op de kaart.
11. Golfarrangement GOLF: boekbaar vastgesteld via de kalender-API (KAL); de kalender toont prijzen (dat is de boekstap, niet de pagina).
