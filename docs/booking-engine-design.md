# Asteria Booking Engine — Design Document
*Versie 1.0 · 2026-05-10*

---

## Doel

Custom booking engine als alternatief voor de Mews standaard widget. Kernreden: pre-selected extras via deeplinks vanuit landingspagina's zijn niet mogelijk in de standaard Mews widget.

---

## Flow — 5 stappen

| Stap | Pagina | Inhoud |
|------|--------|--------|
| 1 | Arrangement | Kies arrangement (Logies & Ontbijt / Culinair Weekend / Wellness Weekend) |
| 2 | Datum | Kalender met check-in + check-out, personen |
| 3 | Kamer & Extra's | Kamer upgrade (optioneel) + extra's (optioneel) — gecombineerd |
| 4 | Gegevens | Naam, e-mail, telefoon, occasionkeuze |
| 5 | Betaling | Samenvatting + betalingsformulier |

**Waarom 5 i.p.v. 6:** Stap "Kamer" is te simpel voor een eigen pagina (3 opties, één al geselecteerd). Samenvoegen met Extra's verlaagt de perceived complexity en elimineert een onnodige drempel.

---

## Design principles

- **Premium, geen druk** — Geen scarcity strips, geen emoji's, geen countdown timers. Exclusiviteit via toon, niet via urgentie.
- **Één beslissing per stap** — Elke stap heeft één duidelijk doel. Geen concurrerende keuzelagen.
- **Mobile-first** — 375px als uitgangspunt bij elke layoutkeuze.
- **Brand-consistent** — Electrolize (headings), Montserrat (body), #c23435 rood, #dcbe1f goud, #292929 charcoal.

---

## Brand

| Token | Waarde |
|-------|--------|
| Rood (CTA, actief) | `#c23435` |
| Charcoal (nav, tekst) | `#292929` |
| Goud (sterren, accenten) | `#dcbe1f` |
| Font heading | Electrolize, uppercase |
| Font body | Montserrat 300/400/700 |
| Logo | `https://www.asteria.nl/images/logo-hotel-asteria.png` |

---

## Arrangementen

| Arrangement | Prijs | Basis |
|-------------|-------|-------|
| Wellness Weekend | €139 p.p. / €278 per stel | 2 nachten, ontbijt, sauna & zwembad, parkeren |
| Culinair Weekend | €119 p.p. / €238 per stel | 1 nacht, ontbijt, 3-gangen diner, parkeren |
| Logies & Ontbijt | €89 p.p. / €178 per stel | 1 nacht, ontbijt, parkeren |

---

## Mews API

- **configId:** `9fc01bd9-bc04-49f2-83cf-b44400835224`
- **enterpriseId:** `65a522c9-4828-413d-9ad8-af1d00ffb83f`
- **serviceId:** `755424cc-3077-4320-b069-af1d00ffbe47`
- **Basis URL:** `https://api.mews.com/api/bookingEngine/v1/`
- **Reservering endpoint:** `https://api.mews.com/api/distributor/v1/reservationGroups/create`
- **Dag-grens:** 22:00 UTC = middernacht CEST
- **Client string:** `"Asteria Booking 1.0.0"` — nog niet geregistreerd bij Mews (mail verstuurd)
- **Sessie:** handmatig injecteren via `/api/session` (zie server.js)

---

## MVP status

| Onderdeel | Status |
|-----------|--------|
| Stap 1 — Arrangement | ✅ Gebouwd (`boeken-stap1.html`) |
| Stap 2 — Datum | ✅ Gebouwd (`boeken-stap2.html`) |
| Stap 3 — Kamer & Extra's | 🔨 In uitvoering |
| Stap 4 — Gegevens | ⏳ Nog te bouwen |
| Stap 5 — Betaling | ⏳ Nog te bouwen |
| Proxy server | ✅ Werkend (`server.js`, port 3334) |
| Mews API stap 1-3 | ✅ Werkend |
| Mews API reservering (stap 5) | ⏳ Wacht op client-registratie |

---

## Analyse-bevindingen (multi-agent review 2026-05-10)

### Wat goed werkt in de MVP
- Prijzen per dag in de kalender — stuurt gedrag zonder uitleg
- Post-purchase upsell timing (na bevestiging = buyer's high)
- Progress bar oriënteert de gebruiker
- Stap 3 (kamer) anchoring: suite legitimeert de superior als middenweg

### Wat verbeterd is in de nieuwe versie
- Geen scarcity strip met 🔥 emoji
- Geen bundle-popup direct na arrangement-klik
- Geen countdown timer op betalingsstap
- Scarcity beperkt tot één subtiel signaal (roze border op kalender)
- SVG iconen in plaats van emoji's
- 5 stappen i.p.v. 6 (kamer + extras samengevoegd)
- Geen dark pattern decline-knoppen

### Openstaande aandachtspunten
- Browser back-button verliest state — oplossen met URL params of sessionStorage
- Betalingsvelden stap 5 moeten expliciete mobile breakpoint krijgen
- Countdown interval clearen bij terugnavigeren
- Exit intent werkt niet op touch — weglaten of vervangen
