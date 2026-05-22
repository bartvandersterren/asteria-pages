# Spec: USP Blok Mobile A/B Test
**Datum:** 2026-05-22
**Bestand:** `lander-google.html`
**Status:** Goedgekeurd — klaar voor implementatieplan

---

## Probleem

Het huidige mobile USP-blok gebruikt `scroll-snap-type: y mandatory` met `height: 100svh` per panel. Dit blokkeert de verticale scroll van de pagina, geeft geen indicatie dat er meer panels zijn, en verbergt de rest van de pagina (reviews, kamertypes, CTA) totdat alle 4 panels doorlopen zijn. Dit schaadt de conversie.

---

## Oplossing

Twee visueel sterke varianten als A/B test, random 50/50 toegewezen op pageload. Desktop blijft ongewijzigd.

---

## Variant C — Magazine Mosaic

### Layout
- Sectie-achtergrond: `#f8f7f5`
- Padding: `28px 14px 24px`
- Kopje: "Waarom Asteria" — Electrolize, uppercase, 10px, letter-spacing 0.16em, kleur `#94a3b8`

### Hero-kaart (bovenste, volledige breedte)
- De wellness-USP is altijd de hero (visueel sterkste foto: `arr-c-wellness.webp`)
- Hoogte: `200px`, `border-radius: 14px`, `overflow: hidden`
- Foto: `object-fit: cover`, volledige breedte
- Gradient overlay: `linear-gradient(to top, rgba(0,0,0,0.72) 0%, transparent 55%)`
- Content onderaan foto (absolute):
  - Kenmerk-label: Electrolize, 8px, uppercase, `#c23435`
  - Titel: Electrolize, 15px, wit, `letter-spacing: 0.04em`
  - Subtekst: 9.5px, `rgba(255,255,255,0.7)`, gewicht 300

### Mini-kaarten (2 naast elkaar)
- Grid: `grid-template-columns: 1fr 1fr`, gap 8px
- Kaarthoogte: `120px`, `border-radius: 12px`, `overflow: hidden`
- Foto: `object-fit: cover`, volledige breedte en hoogte
- Gradient overlay: zelfde patroon als hero maar compacter
- Content onderaan (absolute): kenmerk-label + titel
- Volgorde: locatie links, ontbijt rechts

### Foto-toewijzing
- Hero: `fotos/arr-c-wellness.webp`
- Mini links: `fotos/hero-buitenkant.webp`
- Mini rechts: `fotos/restaurant-ontbijt.webp`

---

## Variant D — Feature Stack

### Layout
- Sectie-achtergrond: `#f8f7f5`
- Padding: `28px 14px 8px`
- Kopje: zelfde als variant C
- Kaarten gestapeld, gap `10px`

### Kaart-structuur (per USP)
- `background: #fff`, `border-radius: 16px`, `overflow: hidden`
- `box-shadow: 0 3px 16px rgba(0,0,0,0.08)`

**Foto-zone (boven)**
- Hoogte: `130px`, `overflow: hidden`
- `<img>` met `object-fit: cover`, volledige breedte
- Glassmorphism label linksboven: `background: rgba(0,0,0,0.45)`, `backdrop-filter: blur(8px)`, `border-radius: 20px`, padding `3px 9px`, Electrolize 7.5px uppercase

**Tekst-zone (onder)**
- Padding: `12px 13px 13px`
- Rode accentlijn links: `border-left: 3px solid #c23435`, margin `0 12px 12px`
- Titel: Electrolize, 11px, uppercase, `letter-spacing: 0.06em`, `#1a1a1a`
- Tekst: Montserrat 300, 9.5px, `#64748b`, `line-height: 1.55`

### Volgorde kaarten
1. Locatie & bereik — `fotos/hero-buitenkant.webp`
2. Wellness op de Top Floor — `fotos/arr-c-wellness.webp`
3. Uitgebreid ontbijtbuffet — `fotos/restaurant-ontbijt.webp`

---

## A/B Test Logica

### Toewijzing
```js
// Zo vroeg mogelijk in <head> plaatsen (vóór eerste render) om flash te voorkomen
(function() {
  const param = new URLSearchParams(location.search).get('usp');
  const valid = ['mosaic', 'stack'];
  let variant;
  if (param && valid.includes(param)) {
    variant = param;
    sessionStorage.setItem('usp_variant', variant);
  } else {
    variant = sessionStorage.getItem('usp_variant')
      || (Math.random() < 0.5 ? 'mosaic' : 'stack');
    sessionStorage.setItem('usp_variant', variant);
  }
  document.documentElement.dataset.uspVariant = variant;
})();
```

### URL override
`?usp=mosaic` of `?usp=stack` — overschrijft sessionStorage. Handig voor preview/QA.

### CSS activering
```css
/* Standaard: beide varianten verborgen op mobile */
@media (max-width: 768px) {
  .usp-mosaic { display: none; }
  .usp-stack  { display: none; }

  [data-usp-variant="mosaic"] .usp-mosaic { display: block; }
  [data-usp-variant="stack"]  .usp-stack  { display: block; }
}

/* Desktop: originele layout, geen varianten */
@media (min-width: 769px) {
  .usp-mosaic { display: none; }
  .usp-stack  { display: none; }
}
```

### HTML structuur
Het bestaande `.usp-items-col` (desktop) blijft staan. Twee extra `<div>`s worden toegevoegd binnen `.usp-inner`, alleen zichtbaar op mobile:

```html
<div class="usp-inner">
  <!-- Desktop (ongewijzigd) -->
  <div class="usp-heading-col">...</div>
  <div class="usp-items-col">...</div>

  <!-- Mobile variant C -->
  <div class="usp-mosaic">...</div>

  <!-- Mobile variant D -->
  <div class="usp-stack">...</div>
</div>
```

---

## Wat blijft ongewijzigd

- Desktop layout: sticky foto links + items rechts — volledig ongewijzigd
- Bestaande JS voor desktop hover (foto wisselt) — ongewijzigd
- Foto's: alle drie zijn al aanwezig in `fotos/`
- Sectie-wrapper, aria-labels, anchor `#usp` — ongewijzigd

---

## Niet in scope

- Analytics/conversie-meting (geen GTM of dataLayer events)
- Animaties of scroll-triggered effecten
- Meer dan 3 USPs
- Wijzigingen aan andere pagina's dan `lander-google.html`
