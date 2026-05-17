# Design Spec — wellness-arr-c pagina-structuur

**Datum:** 2026-05-17
**Pagina:** `/wellness-arr-c` op visit.asteria.nl
**Scope:** Welke blokken de pagina bevat, in welke volgorde, en de logica per blok. UI-details worden per blok in aparte sessies uitgewerkt.

---

## Huidige staat

De pagina bestaat al en bevat:
- NAV (sticky header)
- HERO (vol scherm, foto, headline, CTA, trust badges)
- Arrangement-blok "Wat is inbegrepen" (interactive split-layout — de `arr-c` component)
- FOOTER

---

## Definitieve pagina-opbouw

### 1. NAV — Klaar
Sticky header met logo, navigatiemenu en boek-knop.

---

### 2. HERO — Klaar
Vol scherm (100svh), grote sfeerfoto wellness, headline, CTA-knop, trust badges. Geen wijzigingen nodig.

---

### 3. STICKY CTA — Nieuw
Verschijnt zodra de hero-sectie uit beeld scrolt. Blijft zichtbaar door de rest van de pagina. Verdwijnt wanneer de footer in beeld komt.

**A/B test:** twee varianten bouwen, gelijkelijk getoond via JS (random split, geen externe tool nodig voor v1):

| Variant | Inhoud |
|---------|--------|
| A | Arrangementsnaam + prijs (€139,50 p.p.) + knop "Boek nu" |
| B | Knop met meer context: "Boek het arrangement" + subtekst "Incl. wellness, diner & ontbijt" — geen prijs zichtbaar |

Meetpunt: klikratio op de CTA-knop per variant. Implementatie zonder externe A/B tool — eenvoudige 50/50 Math.random() split, varianten gelogd als URL-parameter of via custom event naar analytics.

---

### 4. ARRANGEMENT — "Wat is inbegrepen" — Kleine aanpassing
Bestaande `arr-c` component blijft ongewijzigd qua structuur.
Toevoeging: een mini Google-rating (4,2 ★ · 2.219 reviews) zichtbaar in het contentpaneel, met een anchor-link naar de reviews-sectie (#reviews). Dit verankert vertrouwen vroeg in de pagina, direct na de "wat krijg ik"-informatie.

---

### 5. REVIEWS — Nieuw
**Bron:** Google Places API — live en actueel, geen statische teksten.
**Stijl:** Authentieke Google-kaarten. Elementen per review-kaart:
- Initiaal-avatar of profielfoto
- Voornaam + achternaam
- Datum (bijv. "14 augustus 2025")
- Google-G logo
- Sterrenscore (geel, 5 sterren)
- Reviewtekst (ingekort met "lees meer")

**Totaalscore** staat prominent boven de kaarten (groot getal, gemiddelde, totaal aantal reviews).
Doel: reviews voelen als een echte derde-partij bron, niet als iets dat de hotelbeheerder er zelf op heeft gezet.

**Technische noot:** Vereist Google Places API key + Cloudflare Function als proxy (key niet in frontend blootstellen).

---

### 6. WELLNESS — Top Floor — Nieuw
Foto-dominant blok. Tekst is ondergeschikt aan de beelden.

**Volledige faciliteiten (300m², Top Floor):**
- 4 unieke sauna's (o.a. infrarood en zoutsteen)
- Stoomcabine
- Dompelbad
- Kruidenbad
- Belevenisdouches
- 4 voetenbaden
- Relaxruimte

Structuur: één grote sfeerfoto + grid van de afzonderlijke faciliteiten. Elk element krijgt een foto + kort label, geen langere teksten. Foto's uit eigen fotobank.

---

### 7. KAMERTYPES — "Kies je kamer" — Nieuw
Ecommerce-stijl kaartjes, één per kamertype. Klik op een kaartje opent een popup met foto's, faciliteiten en een boek-knop.

**Structuur:**

| Kamer | Status | Upgrade-reden |
|-------|--------|---------------|
| Comfort Kamer | **Standaard** (inbegrepen in €139,50 p.p.) | — |
| Royale Kamer | Upgrade | Meer ruimte, keuze bad of douche |
| Deluxe Kamer | Upgrade + eigen sauna | Privé infraroodsauna op de kamer |
| Junior Suite | Upgrade | Kingsize bed, ruime zithoek, bad |
| Suite | Upgrade + eigen sauna | Kingsize bed + privé infraroodsauna |
| Bruidssuite | Upgrade premium | Vrijstaand bad, inloopdouche — meest romantisch |

Kaartjes met eigen infraroodsauna (Deluxe, Suite) krijgen een prominente badge.
Prijzen worden niet getoond per kamer (niet beschikbaar in content) — de CTA stuurt door naar de Mews booking engine.

**Popup bevat:** 2-3 kamerfoto's (slider of grid), faciliteiten-lijst, upgrade-reden als headline, CTA naar Mews.

---

### 8. RESTAURANT / DINER — Nieuw
Sfeerblok dat het 3-gangen diner — inbegrepen in het arrangement — concreet en aantrekkelijk maakt.
Foto-first: sfeershot van het restaurant of een bord.
Korte tekst: wat de gast kan verwachten, geen menu.

---

### 9. LOCATIE / OMGEVING — Optioneel
Venray, bereikbaarheid (bijv. 35 min van Eindhoven), "even weg"-gevoel versterken.
Kan later worden toegevoegd als de pagina verder volgroeit.

---

### 10. FAQ — Optioneel
Laatste bezwaren wegnemen. Onderwerpen: check-in/uit tijden, parkeren, annuleringsbeleid, extra personen.
Kan later worden toegevoegd.

---

### 11. FOOTER — Klaar
Contact, adres, copyright. Geen wijzigingen.

---

## Principes die gelden voor alle nieuwe blokken

1. **Foto eerst, tekst tweede.** Travel en hotel = visueel medium. Elke sectie heeft een dominante foto.
2. **Eigen fotobank.** Geen stockfoto's — 399 originelen beschikbaar in `~/Documents/Asteria Fotobank/`. Geselecteerde WebP's in `fotos/`.
3. **Authentiek vertrouwen.** Reviews komen van een derde partij (Google API), niet van de hotelbeheerder.
4. **Upsell met reden.** Elke kamerupgrade heeft een expliciete "waarom upgraden"-tekst, geen generieke naamgeving.
5. **CTA altijd bereikbaar.** Sticky CTA zorgt dat boeken op elk moment mogelijk is.

---

## Bouwvolgorde (aanbevolen)

Volgorde op basis van impact en afhankelijkheden:

1. **Sticky CTA** — klein, hoge impact, geen afhankelijkheden
2. **Rating toevoegen aan arr-c** — kleine aanpassing bestaand blok
3. **Reviews** — vereist Google Places API setup
4. **Wellness-blok** — fotoselectie + layout
5. **Kamertypes** — grootste component (kaartjes + popups)
6. **Restaurant/diner** — fotoselectie + layout
7. **Locatie / FAQ** — optioneel, later

---

## Openstaande beslissingen

- Google Places API key: nog aan te maken via Google Cloud Console
- Welke foto's per sauna-type worden geselecteerd: keuze uit fotobank in bouwsessie
- Kamerfoto's per kamertype: beschikbaarheid controleren in fotobank
