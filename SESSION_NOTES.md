# Session Notes — 2026-05-22 (update 5)

## Gedaan in deze sessie (update 5) — Arrangementen blok

### Arrangementen blok — lander-google.html (LIVE)

Nieuw blok gebouwd via brainstorming + visuele companion (tier-mockup).

**Positie:** na `#kamertypes`, vóór `#sfeer`

**3 arrangementen:**
- Weekend Aanbieding (€166,– p.p. · 2 nachten) → vouchercode WEEKEND
- Wellnessarrangement (€139,50 p.p. · 1 nacht) → WELLNESS — featured, "Meest gekozen" badge
- Asperge Arrangement (€138,– p.p. · 1 nacht) → ASPERGE — seizoensbadge "t/m 24 juni"

**Desktop:** 3-koloms grid, `align-items: stretch`, foto 220px (gelijk), `margin-top: auto` op CTA. Wellness popt via rode box-shadow + badge.

**Mobile:** verticale stack, foto 170px, grote kaarten.

**Popup:** `data-arr` attribuut → JS IIFE rendert dynamisch uit `ARR_DATA` object. Sluit via ×, Escape, of klik op overlay.

**Mews deeplinks:** `https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556?mewsVoucherCode=WEEKEND/WELLNESS/ASPERGE`

**Spec:** `docs/superpowers/specs/2026-05-22-arrangementen-blok-design.md`

---

## Open voor volgende sessie

### 1. Nav vereenvoudigen
- Verwijder menu-items (Kamers, Hotel, Restaurant, etc.) + top-bar (e-mail, telefoon, taalschakelaar)
- Houd: logo (links) + "Boek nu" knop (rechts)
- Pas hero padding-top aan als nav smaller wordt

### 2. Trust bar in hero
- Witte kaart-balk onderin de hero, volledig BINNEN de 100svh
- Inhoud: Google-score (★ 4,2 · 2.219 reviews) + ✓ Gratis annuleren · ✓ Gratis parkeren · ✓ Laagste prijs
- Hero blijft 100svh

### 3. vipStatus fix
- Revinate hidden form: value="Wellness nieuwsbrief" → "Google Lander"

### 4. Asperge kaart
- Vervalt 24 juni 2026 — dan vervangen of verbergen
- Geen asperge-specifieke foto beschikbaar, nu `restaurant-sfeer.webp`

## Wat NIET aanpassen
- Sticky card: niet aanraken
- Hero hoogte: 100svh

## Referentie
- Plan: docs/superpowers/plans/2026-05-22-lander-google-trust-nav.md
