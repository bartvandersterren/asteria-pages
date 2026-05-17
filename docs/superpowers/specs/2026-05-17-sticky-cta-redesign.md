# Sticky CTA Redesign — Design Spec

_Datum: 2026-05-17_

---

## Samenvatting

De bestaande sticky CTA (een full-width donkere balk onderin) wordt vervangen door twee aparte gedragspatronen: een minimale floating knop op mobile, en een compact floating kaartje op desktop. Geen full-width balk meer op enige viewport.

---

## Mobile — Floating FAB

**Vorm:** Afgeronde pill (border-radius: 50px), rechtsonder in het scherm.

**Inhoud:** Alleen "Boek direct" + pijl-icoon. Geen prijs, geen subtitel.

**Kleur:** Achtergrond `#c23435`, witte tekst. Rode gloed-schaduw (`box-shadow: 0 4px 16px rgba(194,52,53,0.45)`).

**Positie:** `bottom: 20px; right: 16px; position: fixed;`

**Entry-animatie:** Fade + scale — verschijnt ter plekke vanuit 88% → 100% grootte, opacity 0 → 1. Timing: 0.4s, easing `cubic-bezier(0.34, 1.56, 0.64, 1)` (lichte spring). Delay: 0.2s na trigger.

**Trigger:** Zodra de reviews-sectie (`#reviews`) in beeld komt (IntersectionObserver, threshold 0) — zelfde logica als huidig. Verdwijnt als gebruiker terug scrolt naar vóór het arrangement-blok.

---

## Desktop — Floating kaartje

**Breakpoint:** `min-width: 601px`

**Vorm:** Compact kaartje rechtsonder, `border-radius: 14px`, geen border.

**Inhoud:**
- Label: "Wellness Arrangement" (Electrolize, 7px, uppercase, 0.2em letter-spacing)
- Prijs: "€139,50" (Montserrat 700, 22px)
- Subtitel: "per persoon" (Montserrat 300, 9px)
- Knop: "Boek direct →" (Montserrat 600, rood `#c23435`, border-radius: 8px)

**Kleur:** Achtergrond `#f0efed` (zelfde als body). Geen border. Schaduw: `0 8px 40px rgba(0,0,0,0.15), 0 2px 8px rgba(0,0,0,0.07)`.

**Positie:** `bottom: 24px; right: 24px; position: fixed; width: 180px;`

**Entry-animatie:** Zelfde als mobile — fade + scale, `cubic-bezier(0.34, 1.56, 0.64, 1)`, 0.4s, delay 0.2s.

**Trigger:** Zelfde IntersectionObserver op `#reviews`.

---

## Gedeeld gedrag

- `prefers-reduced-motion`: animatie uitschakelen, direct tonen (opacity: 1, transform: none).
- Klik op knop: navigeer naar bookinglink (Mews Distributor), zelfde als huidig.
- Geen sluitknop in initiële versie — staat op de A/B test lijst.
- De huidige A/B test (variant A prijs / variant B tekst) vervalt. De nieuwe CTA heeft één vaste variant.

---

## A/B test ideeën (toekomstig)

| Variant | Wat | Hypothese |
|---------|-----|-----------|
| Sluitknop | Kaartje/FAB wegklikken | Minder irritatie → hogere kwaliteit clicks |
| Prijs op mobile | FAB met prijs erbij | Meer context → hogere conversie |
| Trigger eerder | Na hero ipv na arrangement | Meer impressies → meer clicks |
| Knoptekst | "Bekijk beschikbaarheid" vs "Boek direct" | Lagere drempel → hogere CTR |

---

## Wat vervalt

- De huidige `.sticky-cta` met `flex-direction: column` op mobile.
- De twee HTML-varianten (`#stickyVariantA`, `#stickyVariantB`).
- De A/B test logica in `sessionStorage`.
- De `border-top: 2px solid rgba(194,52,53,0.5)` balk-stijl.

---

## Implementatie scope

Alleen `wellness-arr-c.html` — andere pagina's hebben geen sticky CTA.
