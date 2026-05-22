# Diner Blok — Design Spec

**Datum:** 2026-05-18
**Bestand:** `wellness-arr-c.html`
**Positie:** direct vóór de footer, ná het kamertypes-blok

---

## Doel

Sfeerblok dat het drie-gangen diner — inbegrepen in het wellness arrangement — concreet en aantrekkelijk maakt. Laatste inhoudelijke blok vóór de footer, sluit de pagina af met een warme, eetlustige indruk.

---

## Layout

### Desktop (> 768px)
- Gecontaineerde card, max-width 960px, gecentreerd in de sectie
- Sectie-achtergrond: `#f0efed` (body-kleur) — geen nieuwe achtergrondkleur
- Card zweeft op de pagina: `border-radius: 20px`, `box-shadow: 0 8px 48px rgba(0,0,0,0.13)`
- Min-height: 420px
- Content gecentreerd in de card

### Mobile (≤ 768px)
- Full-bleed: geen margin, `border-radius: 0`
- Aspect-ratio: `4/3` (375px breed → ~281px hoog)
- Geen box-shadow

---

## Foto

- **Bestand:** `fotos/restaurant-sfeer.webp`
- **Bron:** `~/Documents/Asteria Fotobank/P1046742.jpg`
- **Conversie:** `cwebp -q 82 P1046742.jpg -o fotos/restaurant-sfeer.webp`
- **Crop:** `background-position: 70% center` — toont de rechterkant van de foto (ramen, groen buiten, rustige sfeer)
- **Overlay:** `linear-gradient(to bottom, rgba(8,6,4,0.22) 0%, rgba(8,6,4,0.52) 100%)` — subtiel, alleen voor leesbaarheid

---

## Content

### Desktop + Mobile
- **Eyebrow:** `INBEGREPEN IN HET ARRANGEMENT` — Electrolize, 10px, letter-spacing 0.26em, `rgba(255,255,255,0.6)`
- **H2:** `EEN HEERLIJK / DRIE-GANGEN DINER` — Electrolize, 42px desktop / 22px mobile, uppercase, wit
- **CTA:** `Boek het arrangement` — Montserrat 600, `#c23435`, padding 14px 36px desktop / 11px 22px mobile, border-radius 8px

### Desktop only
- **Subtekst:** "Na een avond in de wellness schuift u aan in ons restaurant. Vers bereid, seizoensgebonden, geen haast." — Montserrat 300, 14px, `rgba(255,255,255,0.68)`, max-width 320px gecentreerd

### Mobile
- Subtekst weggelaten (te weinig ruimte bij 4:3)

---

## CSS-klassen

```
.diner               — sectie wrapper, background #f0efed, padding 0 (mobile) / 40px 20px (desktop)
.diner__card         — de card zelf, border-radius 20px desktop / 0 mobile
.diner__bg           — absolute, inset 0, background-image, cover, position 70% center
.diner__overlay      — absolute, inset 0, gradient overlay
.diner__content      — relative, z-index 1, text-align center
.diner__eyebrow
.diner__title
.diner__sub          — verborgen op mobile (display:none ≤ 768px)
.diner__cta
```

---

## Link

CTA linkt naar de Mews boekingslink:
`https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS`

---

## Wat dit blok NIET doet

- Geen lijst met inbegrepen items (dat staat al in het arr-c blok bovenaan)
- Geen openingstijden
- Geen donkere sectie-achtergrond
