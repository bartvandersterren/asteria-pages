# Session Notes — 2026-05-22 (update 4)

## Eerder gedaan (update 3)
- Sectievolgorde lander-google: Reviews → Waarom Asteria → Kamertypes → Omgeving
- Mosaic leesbaarheid verbeterd
- USP mobile A/B test live

## Gedaan in deze sessie (update 4)
- Content gaps lander-google geanalyseerd
- Subagent-driven poging gedaan (nav, trust signals, vipStatus) — volledig teruggedraaid
- Revert commit: 6b69146 — pagina staat terug op fa00c55

## Open voor volgende sessie

### 1. Nav vereenvoudigen
- Verwijder menu-items (Kamers, Hotel, Restaurant, etc.) + top-bar (e-mail, telefoon, taalschakelaar)
- Houd: logo (links) + "Boek nu" knop (rechts)
- Pas hero padding-top aan als nav smaller wordt

### 2. Trust bar in hero (vervangt huidige .hero__trust badges)
- Witte kaart-balk onderin de hero, volledig BINNEN de 100svh
- Inhoud: Google-score (★ 4,2 · 2.219 reviews) + ✓ Gratis annuleren · ✓ Gratis parkeren · ✓ Laagste prijs
- Stijl: wit, schaduw, border-radius — zie screenshot in sessie (hero-v2 stijl)
- Hero blijft 100svh

### 3. vipStatus fix (klein)
- Revinate hidden form: value="Wellness nieuwsbrief" → "Google Lander"

## Wat NIET aanpassen
- Sticky card: niet aanraken
- Hero hoogte: 100svh

## Referentie
- Plan: docs/superpowers/plans/2026-05-22-lander-google-trust-nav.md
