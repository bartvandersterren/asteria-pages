# Kamertypes Blok — Design Spec

**Pagina:** `wellness-arr-c.html`
**Positie:** tussen wellness plattegrond-blok en diner-blok
**Doel:** Overzichtelijk tonen welke kamertypes beschikbaar zijn en wat de upgrade-voordelen zijn t.o.v. de standaard Comfort Kamer. Primair conversie, secundair upsell.

---

## Informatiestructuur

Delta-framing: altijd t.o.v. Comfort. Geen lineaire hiërarchie (Deluxe → Junior Suite verliest sauna), dus elke kamer toont alleen zijn eigen pluspunten vs Comfort.

| Kamer | Badge | Delta's t.o.v. Comfort |
|-------|-------|------------------------|
| Comfort | Standaard inbegrepen | ~22 m2 · tweepersoons bed · douche · zithoek · airco · WiFi |
| Royale | Upgrade | + meer ruimte · + ligbad |
| Deluxe | + Sauna | + meer ruimte · + prive infraroodsauna |
| Junior Suite | Upgrade | + kingsize bed · + ruime zithoek · + ligbad · + koelkast |
| Suite | + Sauna | + kingsize bed · + prive infraroodsauna · + ruime zithoek · + koelkast |
| Bruidssuite | Premium | + kingsize bed · + vrijstaand bad · + inloopdouche · + koelkast |

**Badge-kleuren:**
- Standaard: `#f1f5f9` bg, `#64748b` tekst
- Upgrade: `#fff7ed` bg, `#c2450a` tekst, `#fed7aa` border
- + Sauna: `#c23435` bg, `#fff` tekst
- Premium: `#1e1e1e` bg, `#fff` tekst

Geen prijzen tonen (wisselen per seizoen, verwarrend als ze niet kloppen).

---

## Desktop Layout (>768px)

OTA room list — verticale lijst, Booking.com-stijl.

### Sectie-header
- Eyebrow: "KIES JE KAMER" (Electrolize, 10px, `#c23435`)
- Titel: "WELKE KAMER PAST BIJ JOU?" (Electrolize, clamp 22-36px)
- Subtitel: "Upgrade voor meer comfort of privacy" (Montserrat 300, 13px, `#64748b`)

### Comfort = baseline blok
- Achtergrond `#f8f7f5`, border-radius 12px, 1px border `#e8e5e0`
- Badge "Standaard inbegrepen" + naam + alle features als tekstregel
- Foto links (200px breed, aspect-ratio 4:3) — optioneel, als het past

### 5 upgrade-kaarten
- Witte kaart, border-radius 12px, 1px border `#f1f5f9`
- Foto links: 200px breed, aspect-ratio 4:3, object-fit cover, border-radius 12px 0 0 12px
- Midden: badge + naam (Electrolize uppercase) + delta-features ("Alles van Comfort + ...")
- Rechts: chevron `›` als tap-target
- Hover: subtiele box-shadow + translateY(-1px)

### Sectie-container
- `max-width: 1100px`, `margin: 0 auto`
- Padding: 80px 40px
- Achtergrond: `#fff`
- Gap tussen kaarten: 12px

---

## Mobile Layout (<768px)

Twee varianten als A/B test.

### Variant A — Compact Text (geen foto's)
- Comfort als baseline-kaart: `#f8f7f5` achtergrond, border-radius 12px, features als tekstregel
- Upgrades als compacte rijen: badge links (flex-shrink 0) + naam + delta's op 1 regel + chevron `›` rechts
- Geen foto's in de lijst zelf
- Tap op rij → popup met foto + details + CTA
- Padding sectie: 56px 20px

### Variant B — Mini Thumbnail
- Comfort met grote foto (140px hoog, border-radius 12px) als baseline + features eronder
- Upgrades als rijen met mini thumbnail (72×56px, border-radius 8px) links + naam + badge + delta's rechts + chevron
- Tap op rij → popup met foto + details + CTA
- Padding sectie: 56px 20px

### A/B Mechanisme
- URL param `?rooms=compact` of `?rooms=thumb` forceert variant
- Zonder param: random 50/50
- Keuze opgeslagen in `sessionStorage` zodat herlaad consistent is
- Implementatie: CSS class op `.rooms` sectie (`.rooms--compact` vs `.rooms--thumb`), JS wisselt bij load

---

## Popup (gedeeld, beide varianten)

Hergebruikt voor alle kamertypes, zowel desktop als mobile.

- `position: fixed`, overlay `rgba(0,0,0,0.6)`, z-index 1100
- Popup: `#fff`, border-radius 16px, max-width 640px, max-height 90vh, overflow-y auto
- Foto bovenaan (240px hoog desktop, 180px mobile)
- Body: close-button (×) + badge + naam (Electrolize 20px) + beschrijving (Montserrat 300, 13px) + features-lijst (checkmarks) + CTA-knop (rood, full-width)
- Sluiten: ×-knop, Escape-toets, klik op overlay
- `body overflow: hidden` wanneer open
- Animatie: fade-in overlay + translateY(20px→0) popup

### Popup content per kamer

**Comfort:**
- Beschrijving: "Alles wat je nodig hebt voor een ontspannen wellness-avond."
- Features: ~22 m2, 2 personen, Douche, Zithoek, Koffiezetapparaat, Airco, LCD-tv, Gratis WiFi

**Royale:**
- Beschrijving: "Meer ruimte om te ademen — en de keuze voor een bad als je na de wellness ook op de kamer wil ontspannen."
- Features: Ruimer dan Comfort, Bad of douche, Zithoek, Koffiezetapparaat, Airco

**Deluxe:**
- Beschrijving: "Een prive infraroodsauna op de kamer. Wellness begint bij jou aan de deur — geen gedeelde ruimte."
- Features: Eigen infraroodsauna, Meer ruimte, Dubbel bed, Douche, Zithoek, Koffiezetapparaat, Airco

**Junior Suite:**
- Beschrijving: "Het extra formaat dat een wellness-avond echt luxe maakt: kingsize bed, een bad en een ruime zithoek."
- Features: Kingsize bed, Bad, Ruime zithoek met slaapbank, Koelkastje, Koffiezetapparaat, Airco

**Suite:**
- Beschrijving: "Het beste van beide werelden: een ruime suite met eigen infraroodsauna en toegang tot het gedeelde wellness-centrum."
- Features: Kingsize bed, Eigen infraroodsauna, Ruime zithoek met slaapbank, Koelkastje, Airco

**Bruidssuite:**
- Beschrijving: "Vrijstaand bad, ruime inloopdouche en de meest romantische sfeer van het hotel. Voor een onvergetelijke avond."
- Features: Kingsize bed, Vrijstaand bad, Ruime inloopdouche, Zithoek, Koelkastje, Airco

---

## Foto's

Converteren naar WebP (quality 72, max 2000px breed) in `fotos/`.

| Kamer | Bron | Output |
|-------|------|--------|
| Comfort | `Interieur/_O0A9528-HDR.jpg` | `fotos/kamer-comfort.webp` (check bestaande) |
| Royale | `Interieur/_O0A9337-HDR.jpg` | `fotos/kamer-royale.webp` |
| Deluxe | `Interieur/_O0A9134-HDR.jpg` | `fotos/kamer-deluxe.webp` |
| Junior Suite | `Interieur/_O0A9507-HDR.jpg` | `fotos/kamer-junior-suite.webp` |
| Suite | bestaande `kamer-suite.webp` | hergebruik |
| Bruidssuite | `Interieur/_O0A9432-HDR.jpg` | `fotos/kamer-bruidssuite.webp` |

---

## Technisch

- Alles in `wellness-arr-c.html`: CSS in `<style>`, HTML tussen wellness-blok en diner-blok, JS in `<script>`
- Geen externe dependencies
- Popup JS-structuur: `ROOMS` object met data per kamer, `openPopup(key)` rendert dynamisch
- A/B toggle: `URLSearchParams` check → fallback `Math.random()` → `sessionStorage.setItem('rooms-variant', ...)`
- Desktop toont altijd de volledige lijst (geen A/B verschil op desktop)
