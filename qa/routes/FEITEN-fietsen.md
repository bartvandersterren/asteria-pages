# Feiten: Fietsen rond Venray (Hotel Asteria), /fietsen-rond-venray-v2

Opgehaald op 11 nov 2026 met `python3 scripts/routes_os.py` uit het Asteria OS (os.asteria.nl, omgevingsscherm, alleen lezen:
login + `GET /api/omgevingsscherm/instellingen` voor het schermtoken + `GET /api/omgeving/<token>/routes`). Hotelpunt 51.5478, 5.9972.

## Routes (content/routes/fiets.json)

| nr | route (pagina) | OS-slug | bron | km | duur | start | reistijd | rondje | klasse |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Rondje Venray | asteria-rondje-venray | Fietsknoop 31960088 | 24,5 | 1 u 30 | Oostrum (Maasheseweg) | 11 min fietsen | ja | kort |
| 2 | Rondje over het pontje | asteria-rondje-over-het-pontje | Fietsknoop 31960100 | 30,4 | 1 u 55 | Oostrum | 6 min fietsen | ja | gemiddeld |
| 3 | Fietsroute langs de Maas | asteria-langs-de-maas | Fietsknoop 31960090 | 41,1 | 2 u 35 | Oostrum (Spurkterdijk 16) | 5 min fietsen | ja | gemiddeld |
| 4 | Van Venray naar De Peel | asteria-van-venray-naar-de-peel | Fietsknoop 31960089 | 42 | 2 u 40 | Oostrum | 5 min fietsen | nee (eindigt centrum Venray) | gemiddeld |
| 5 | Rondje Horst aan de Maas | asteria-rondje-horst-aan-de-maas | Fietsknoop 31960098 | 49,4 | 3 u 05 | Oostrum | 5 min fietsen | nee (eindigt centrum Venray) | gemiddeld |
| 6 | Maasduinen en Arcen | asteria-maasduinen-en-arcen | Fietsknoop 31960094 | 52,4 | 3 u 15 | Oostrum | 5 min fietsen | ja | lang |
| 7 | Ballonzuilbossen en Overloon | asteria-ballonzuilbossen-en-overloon | Fietsknoop 31960092 | 51,5 | 3 u 15 | Venray (Kerkpad 1, Grote Kerk) | 13 min fietsen | ja | lang |
| 8 | Rondje Venray via Vierlingsbeek | rondje-venray (routiq 115051, OS-naam "Rondje Venray") | routiq | 33,72 | 1 u 58 | Overloon (Vierlingsbeekseweg) | 8 min rijden | ja | gemiddeld |
| 9 | Meterik, Venray, Horst | meterik-venray-horst (routiq 185810) | routiq | 54,94 | 3 u 13 | Meterik (Lollebeekweg) | 12 min rijden | ja | lang |
| 10 | Door de Peel bij Horst | peel-bij-horst (routiq 133681, OS-naam "Op de fiets door de Peel bij Horst") | routiq | 58,8 | 3 u 27 | Meterik (Lollebeekweg) | 12 min rijden | ja | lang |

- Selectie en volgorde: besluit Stijn 11 nov 2026 (plan wondrous-foraging-mccarthy). De 8 andere OS-fietsroutes (Kasteeltuinenroute,
  Cultuurhistorische route Horst, Melderslo-Lomm, Blauwe bessenroute, Meerlo-Wanssum, Roermond, Broekhuizen, De Peelstreek) vervallen.
- Reistijd: Fietsknoop-routes met een fietstijd tot 15 min tonen de fietstijd, de rest de autotijd (beide uit het OS, OSRM).
- Lengteklassen: de Parkhotel-grenzen tot 30 / 30-50 / vanaf 50 km (besluit coordinator 11 nov: aanhouden, ook al heeft Kort maar een route).
- Startplaatsen: de OS-velden `start_adres` zijn per route naar een plaatsnaam vertaald in `scripts/routes_os.py` (FIETS); Overloon
  voor 115051 komt uit de OS-omschrijving ("We starten deze route in Overloon"), Meterik voor 185810/133681 uit de coordinaat
  (51.48219, 6.01079, Lollebeekweg). Nakijken: of "Meterik" de plaats is die de receptie gebruikt.
- Knooppuntenreeks per Fietsknoop-route: uit de NL-omschrijving in het OS ("Knooppunten: 65, 15, ..."), gelijk aan
  parkhotel-os scripts/data/fietsknoop-asteria.json (tak routes-aanuit).
- Lijnen: OS-lijn (260 punten) met Douglas-Peucker naar hoogstens 120 punten, 5 decimalen. Kaart en lus-kaartjes:
  `python3 scripts/route_kaartfoto.py` (zelfde kaart-getekend.js, ondergrond content/kaart/getekend.json; die dekt Venray, Overloon,
  de Maas, Arcen, Horst, de Peel tot Helenaveen en Bergen: alle routes vallen binnen beeld).

## Teksten per route (eigen woorden, bron = OS-omschrijving)

- Rondje Venray: Annapark (park van het vroegere Sint Anna), buurtschap Weverslo, Weverslose Berg 38,6 m = hoogste punt Noord-Limburg
  met uitzichtpunt, doorsteek centrum bij knooppunt 23.
- Rondje over het pontje: Maashees met De Watervogel, Reindersmeer (NP De Maasduinen), tuinen bij Kasteel Well (waterburcht), pontje
  over de Maas, terug via Geijsteren. Vaartijden van dit pontje staan niet in het OS: tekst zegt "kijk vooraf even of het pontje vaart".
- Langs de Maas: Oostrum, Parc de Witte Vennen, Meerlo met Sint-Goarkapel (1662) en Slothoeve 't Kasteelke, Tante Jet aan de Maas,
  voet- en fietsveer 1 april t/m 14 oktober, terug via Geijsteren.
- Van Venray naar De Peel: Weverslose Berg, Rouwvennen, Duitse oorlogsbegraafplaats Ysselsteyn (knooppunt 25, bezoekerscentrum),
  Heere Peel, Schadijkse bossen, eindigt centrum Venray op 3 km van het hotel.
- Rondje Horst aan de Maas: Tienray (Klein Lourdes, kerk, kapelletjes, ijssalon Clevers), Schuitwater, Kasteelse Bossen, eindigt centrum Venray.
- Maasduinen en Arcen: Geijsteren, NP De Maasduinen, uitkijktoren Wellerlooi, Kasteeltuinen, vestingstadje, Hertog Jan Brouwerij met
  proeflokaal; fietsveer knooppunt 14-15 vaart 10 april t/m 14 oktober.
- Ballonzuilbossen en Overloon: start Grote Kerk Venray (3 km van het hotel), Annapark, Smakt met Sint-Jozefkapel (1699), Overloonse
  Duinen, Overloon met Brits oorlogskerkhof, Liberty Park en ZooParc, terug door de Ballonzuilbossen.
- Rondje Venray via Vierlingsbeek: start Overloon, Overloonse Duinen, Maashees, boomkwekerijen, Willibrorduskapel (landgoed Geijsteren),
  centrum Venray, Merselo. De naam "via Vierlingsbeek" is een paginanaam (start aan de Vierlingsbeekseweg) om de dubbele naam met
  route 1 te vermijden; het OS houdt "Rondje Venray". Nakijken: de route loopt niet aantoonbaar door het dorp Vierlingsbeek.
- Meterik, Venray, Horst: bossen, uiterwaarden van de Maas, Landgoed Geijsteren (ruim twee eeuwen dezelfde familie), Oostrumse Beek.
- Door de Peel bij Horst: Castenray, Veulen, De Paardekop met de Duitse militaire begraafplaats, Toon Kortoomspark, Griendtsveen en
  Helenaveen (veenkolonies), Deurnsche Peel en Mariapeel.

## Voorzieningen (bevestigd door Stijn, 11 nov 2026; alleen deze genoemd)

Afgesloten, overdekte fietsenstalling; e-bikes opladen; fietsverhuur aan de receptie (fiets en e-bike, geen prijzen, geen aantallen);
lunchpakket voor onderweg; reparatieset en pomp; gratis fiets- en wandelroutes bij de receptie; knooppuntennetwerk vlak bij het hotel.
Niet genoemd: keurmerken, e-chopper, Knapzakken-tour, Pieterpad-ophaalservice, bagagevervoer, prijzen.
Aannames in de tekst (nakijken): "Laat het bij het boeken of bij aankomst weten, dan zetten we hem voor je klaar" (verhuur);
"De receptie wijst je waar" (laden); fietspomp en reparatieset "lenen".

## Arrangementblok (7b)

Limburg Arrangement, bron translations/limburg-arrangement-nl.json en /limburg-arrangement: 3 nachten met ontbijt, elke avond een
3-gangenmenu, 3 dagen een elektrische fiets (vierde punt koffie en vlaai bij aankomst staat niet in de drie vinkjes). Geen prijs.
Knoppen: Bekijk het arrangement = /limburg-arrangement (ook op DE/EN: er is geen -de/-en-versie), Boek het arrangement = Mews met
`mewsVoucherCode=LIMBURG` en `data-voucher="LIMBURG"` (alleen deze knop draagt een code). Let op: de vaste 3 nachten dwingt alleen
de prijskalender op /limburg-arrangement af, niet deze knop.

## Foto's

Kaartfoto's: eigen beelden (Fotobank/contentshoot) en Commons-foto's met naamsvermelding (fotocredit onderaan de pagina en in de
pop-up). Repo-Commons-foto's: credits uit translations/hotel-venray-v2-nl.json `_bronnen.fotos`, overgenomen in `_credits` van
route-fietsen-nl.json. OS-foto's met credit: gedownload als fotos/l26-route-os-<id>.webp (de OS-foto's zonder credit, routiq- of
hotelfoto's, worden niet gebruikt).
