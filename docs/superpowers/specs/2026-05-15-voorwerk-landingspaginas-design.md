# Design: Voorwerk Asteria Landingspagina's

**Datum:** 2026-05-15
**Status:** Goedgekeurd

## Probleem

Het bouwen van Asteria landingspagina's kost te veel voorbereiding per sessie:
- Hotelfeiten (kamers, prijzen, arrangementen, USPs) moeten telkens opnieuw worden aangeleverd
- De fotocatalogus (697 foto's) is niet toegankelijk als context
- Design-feedback komt halverwege het bouwen in plaats van vooraf
- De `asteria-lander` skill en CLAUDE.md bevatten hetzelfde proces (duplicaat)

## Oplossing: Twee sporen parallel

### Spoor 1 — Kennisbank

**`hotel-content.md`** (repo root)
Gescrapet van asteria.nl. Bevat:
- Kamertypes: naam, kenmerken, prijs
- Arrangementen: naam, inhoud, prijs, boekingslink
- Vaste USPs (gratis parkeren, ontbijt, locatie, etc.)
- Echte review-quotes met naam en sterrenscore
- Contactinfo, adres, openingstijden
- Mews booking deeplinks

**`foto-index.md`** (repo root)
Gerichte selectie uit de catalogus (`~/Documents/Asteria Fotobank/catalogus.md`), georganiseerd per use case:
- Hero (buitenkant, lobby — breed, licht)
- Sfeerblok (brasserie met gasten, restaurant diner)
- Kamers (per type: comfort, superior, suite)
- Wellness (sauna, spa)
- Natuur/omgeving
- Zaal/vergadering

Bestandspaden zijn absoluut naar de lokale fotobank. De 17 geoptimaliseerde foto's in `fotos/` blijven de standaard voor live pagina's; de index geeft aan welke raw foto's beschikbaar zijn voor nieuwe selecties.

### Spoor 2 — Workflow

**`asteria-lander` skill — volledig herschreven**

Nieuw: verplichte **Stap 0** vóór de bestaande stappen:

> **Stap 0 — Design brief**
> 1. Superpowers brainstorm: pagina-doel, doelgroep, verkeersbron
> 2. ui-ux-pro-max: moodboard/stijlkeuze, layout-variant per blok, typografische hiërarchie, foto-strategie
> Output: goedgekeurd visueel plan voordat er code wordt geschreven

Stap 4 (Grafisch) wordt uitgebreid: expliciete keuzes per blok op basis van Stap 0 output — welke foto, welke layout-variant, welke sfeer.

Stappen 1–3 en 5–7 blijven ongewijzigd.

**CLAUDE.md — opgeschoond**

De uitgebreide stappenlijst (huidige stappen 1–7) wordt verwijderd uit CLAUDE.md. In de plaats komt één zin:

> "Gebruik de `asteria-lander` skill bij het bouwen van een pagina."

De projectcontext (repo, hosting, brand, booking engine, foto's) blijft in CLAUDE.md.

## Volgorde van uitvoering

1. Scrape asteria.nl → schrijf `hotel-content.md`
2. Stel foto-index samen uit catalogus → schrijf `foto-index.md`
3. Herschrijf `asteria-lander` skill met Stap 0
4. Schoon CLAUDE.md op
5. Commit alles naar `main`

## Verwacht resultaat

- Elke volgende pagina-sessie start met volledige hotelkennis beschikbaar
- Design wordt vooraf vastgelegd (visueel + strategisch), niet bijgestuurd halverwege
- Één bron van waarheid voor het bouwproces (skill), CLAUDE.md blijft licht
