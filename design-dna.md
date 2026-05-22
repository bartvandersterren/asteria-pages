# Design DNA — Asteria Landingspagina's

_Referentiekader voor de design agent. Lees dit vóór je ook maar één regel schrijft._

---

## Visuele referenties

**Bezoek deze URLs met Playwright en analyseer ze voor je begint:**

1. `https://visit.asteria.nl/wellness-arr-c` — Beste interne referentie (mei 2026). Let op: interactive split-layout (foto links / features rechts), mobile kaart-treatment, prijs+CTA altijd zichtbaar onderaan.

2. `https://pura.com` — Externe referentie. Let specifiek op: hoe klein de hero-tekst is t.o.v. de foto, hoeveel padding tussen secties, hoe spaarzaam de merkkleur (#c23435 equivalent) ingezet wordt, het vertrouwen waarmee ze weinig zeggen.

---

## Brand constraints (niet onderhandelbaar)

- **Primaire kleur:** `#c23435` — uitsluitend voor CTA-knoppen en minimale accenten
- **Heading font:** Electrolize (Google Fonts) — uppercase, ruime letter-spacing
- **Body font:** Montserrat 300/400/600/700 (Google Fonts)
- **Logo:** `https://www.asteria.nl/images/logo-hotel-asteria.png`
- **brand.css** altijd laden vóór eigen styles
- **Aanspreekvorm:** altijd "u" (niet "je/jij")

---

## Wat dit design moet zijn

- **Editoriaal** — grote koppen, kleine bodytekst, veel witruimte
- **Confident** — weinig woorden, vertrouw op de foto
- **Spaarzaam** — één idee per blok, nooit meer
- **Fotografie-gedreven** — de foto verkoopt, de tekst ondersteunt

---

## Anti-patronen — doe dit NOOIT

- Tekst midden op een foto met zware donkere overlay
- Meer dan één gedachte per sectie
- Opsommingslijsten met uitleg (gebruik checkmarks/streepjes spaarzaam)
- Donkere sectie-achtergronden (anders dan de nav en een subtiele footer)
- Merkkleur (#c23435) voor decoratieve elementen — alleen CTA's
- Generieke "hotel template" indeling: hero → USP balk → 3 kaartjes → reviews → footer
- Meer dan 2-3 zinnen bodytekst per blok
- Padding onder 100px tussen secties

---

## Ruimte en typografie

- Sectie padding: minimaal 100px, liever 120-140px
- H1: minimaal 56px desktop / 36px mobile
- H2 als editoriale anker: minimaal 40px desktop
- Bodytekst: 15-16px, Montserrat 300 of 400, kleur `#475569`
- Line-height body: 1.7

---

## Motion

- Eén goed gecoördineerd laadmoment (hero elementen staggered) > tien micro-interacties
- Scroll-triggered fade-up: subtiel (20px translate, 0.6s)
- Hover states: 200ms, subtiele schaduw-upgrade
- `prefers-reduced-motion` altijd respecteren

---

## Foto's beschikbaar

| Bestand | Gebruik |
|---------|---------|
| `fotos/wellness-spa.webp` | Hero, arrangement achtergrond |
| `fotos/wellness-sauna.webp` | Accordeon item 1 (Finse sauna) |
| `fotos/wellness-sauna2.webp` | Accordeon item 2 (Zoutsteen sauna) |
| `fotos/card-wellness.webp` | Accordeon item 3 (Stoombad) |
| `fotos/kamer-comfort.webp` | Kamer in arrangement blok |
| `fotos/restaurant-diner.webp` | Diner in arrangement blok |

---

_Versie 1.0 — 16 mei 2026_
