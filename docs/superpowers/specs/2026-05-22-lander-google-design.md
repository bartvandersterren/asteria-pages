# Design Spec — lander-google.html

**Datum:** 2026-05-22
**Status:** Goedgekeurd, klaar voor implementatie

## Doel

Algemene Google Ads landingspagina voor Hotel Asteria Venray. Niet arrangement-specifiek. Gericht op brand searches ("Hotel Asteria Venray") en generic hotel searches ("hotel Venray", "hotel Limburg").

**Primaire conversiedoelstelling:** directe kamerboeking via booking popup → Mews.

**URL:** `visit.asteria.nl/lander-google`
**Bestandsnaam:** `lander-google.html`
**Taal:** NL alleen (vertalingen later, buiten scope)

## Basis

Directe fork van `wellness-arr-c.html`. Geen template/build.py systeem.

## Paginastructuur

| Volgorde | Blok | Herkomst |
|----------|------|----------|
| 1 | Hero | Behouden, copy aanpassen |
| 2 | USP-blok | Nieuw bouwen |
| 3 | Sfeerblok | Nieuw bouwen |
| 4 | Kamertypes | Behouden, copy aanpassen |
| 5 | Booking popup | Behouden, aanpassen |
| 6 | Email capture | Behouden, copy aanpassen |
| 7 | Footer | Behouden, copy aanpassen |

## Wat eruit gaat (Sessie 1 — Strippen)

- Wellness-arrangement-blok (arr-c kaart met prijs, features, foto-carousel)
- Wellness plattegrond + hotspot-blok
- Diner-blok
- Wellness-specifieke hero-copy en hero-foto (placeholder — wordt sessie 2)
- Voucher code (WELLNESSARRA / WELLNESS124) uit booking popup
- A/B price test logica (track() IIFE mag blijven, A/B split eruit)
- Alle verwijzingen naar "wellness arrangement" in trust badges en CTAs

Na sessie 1 is de pagina kaal maar functioneel: hero + kamertypes + booking popup + email capture + footer.

## Blok-voor-blok aanpak

### Sessie 1 — Strippen
Kopieer `wellness-arr-c.html` → `lander-google.html`. Verwijder alle wellness-arrangement-specifieke secties. Pagina is daarna kaal maar live-ready.

### Sessie 2 — Hero aanpassen
- Nieuwe hero-foto (exterieur of sfeer-foto, geen wellness-specifiek)
- Nieuwe headline en subline: hotel-first, geen arrangement-verwijzing
- Trust badges aanpassen (geen "wellness arrangement" — generieke hotel USPs)
- Sticky CTA tekst aanpassen

### Sessie 3 — USP-blok bouwen (nieuw)
Nieuw blok direct onder hero. Antwoordt op "waarom Hotel Asteria?":
- Locatie (bosrijke omgeving Venray, Noord-Limburg)
- Faciliteiten (wellness, restaurant, kamers)
- Service / sfeer
Visueel: icon-grid of 3-koloms tekst-blok, passend bij design-dna.md

### Sessie 4 — Sfeerblok bouwen (nieuw)
Beleving-georiënteerd blok. Drie thema's:
1. Het hotel zelf (interieur, sfeer, comfort)
2. Wellness — licht aangestipt (sauna's, ontspanning)
3. Omgeving & restaurant (natuur, Limburg, brasserie)
Visueel: foto-gedreven, niet tekst-zwaar. Referentie: design-dna.md + foto-index.md voor fotoselectie.

### Sessie 5 — Kamertypes aanpassen
Het bestaande kamertypes-blok is al grotendeels generiek. Aanpassingen:
- Verwijder arrangement-koppeling in CTAs ("Boek dit arrangement" → "Bekijk kamer")
- Controleer delta-framing t.o.v. Comfort — blijft intact
- Popup-copy aanpassen waar arrangement-taal staat

### Sessie 6 — Booking popup aanpassen
- Voucher code verwijderen (geen WELLNESSARRA, geen WELLNESS124)
- Deeplink zonder mewsVoucherCode param
- Stap-titels en copy generiek maken
- "Boek uw verblijf" als standaard CTA-tekst

### Sessie 7 — Email capture + footer aanpassen
- Email capture: offer blijft wellness-gefocust (intentioneel — werkt ook als upsell op algemene bezoekers)
- Footer: controleer op wellness-verwijzingen, schoonmaken

### Sessie 8 — Polish
- Copy-review volledige pagina (u/uw, geen em dashes, geen superlatieven)
- SEO meta (title, description, canonical)
- Analytics/tracking controleren
- Mobile check via Playwright

## Technische uitgangspunten

- Alle bewezen JS-IIFEs blijven intact: datepicker, booking popup, kamertypes, email capture
- Geen externe dependencies toevoegen
- Geen voucher code
- Geen A/B price split (track() IIFE mag blijven voor analytics)
- Foto's uit `fotos/` — bij sessie 2 en 4 foto-index.md raadplegen

## Buiten scope

- Vertalingen (NL/EN/DE) — later
- Template/build.py systeem — niet van toepassing
- A/B testing op prijs
- Nieuwe JS-functionaliteit
