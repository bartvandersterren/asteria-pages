# Session Notes — 2026-05-22 (update 6)

## Gedaan in deze sessie (update 6) — Nav + Trust bar + vipStatus

Alle 3 aanpassingen aan `lander-google.html` uitgevoerd via subagent-driven development.

**Commits (gepusht naar main, nog niet live door Cloudflare-storing):**
- `098807e` fix: vipStatus Revinate form — Google Lander ipv Wellness nieuwsbrief
- `74e9700` feat: vereenvoudig nav — logo + boek-nu, geen menu of top-bar
- `e40419a` fix: verwijder dode taalwisselaar JS + orphaned nav CSS
- `c2c768e` feat: vervang hero trust badges door witte trust bar onderin hero
- `2f27e8f` fix: voeg hero__trust-bar toe aan prefers-reduced-motion selector

**Nav:** top-bar + menu-items weg, logo links + "Boek nu" rechts (desktop én mobile), hero padding-top 110→90px

**Trust bar:** `.hero__trust` badges + scroll-indicator weg → witte kaart-balk (`position: absolute; bottom: 24px`) met ★4,2 · 2.219 reviews + ✓ Gratis annuleren + ✓ Gratis parkeren + ✓ Laagste prijs

**vipStatus:** "Wellness nieuwsbrief" → "Google Lander"

## Open voor volgende sessie

### 1. Visuele verificatie op live URL
- Cloudflare-storing (2026-05-22 ~15:36 UTC) blokkeerde de deploy
- Zodra hersteld deployt het automatisch van commit `2f27e8f`
- Check: desktop 1280px + mobile 375px op visit.asteria.nl/lander-google
- Als overlap hero-content en trust bar op mobile: `padding-bottom: 60px` → `100px` in `@media (max-width: 600px)`

### 2. Asperge kaart
- Vervalt 24 juni 2026 — dan verbergen of vervangen

## Lokale preview
- Server: `wrangler pages dev . --port 8788` (PID was 16014, opnieuw starten als gestopt)
- URL: http://localhost:8788/lander-google

## Referentie
- Plan: docs/superpowers/plans/2026-05-22-lander-google-trust-nav.md
