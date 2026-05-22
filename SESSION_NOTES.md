# Session Notes — 2026-05-22 (update 2)

## Wat gedaan

### USP blok mobile A/B test — lander-google.html (volledig live)
- Scroll-snap vervangen door Magazine Mosaic (C) + Feature Stack (D)
- A/B test: sessionStorage + URL override (?usp=mosaic / ?usp=stack)
- Desktop fixes: gelijke kolomhoogte, heading op één regel
- Bug fixes: beide varianten toonden tegelijk → display:flex verplaatst naar activatie-selector

### URLs
- https://visit.asteria.nl/lander-google?usp=mosaic
- https://visit.asteria.nl/lander-google?usp=stack

### Open voor volgende sessie
- Visuele QA op echte mobile device
- Eventueel gradient/overlay mosaic mini-kaarten finetunen

---

### USP blok — lander-google.html (sessie eerder)

Redesign van het USP-blok op basis van inspo (split-layout, Hears.com stijl).

**Desktop:**
- Split-layout: linker kolom = heading "WAAROM HOTEL ASTERIA?" + grote foto (aspect-ratio 4/5, border-radius 16px)
- Rechter kolom: 3 gestapelde items met `border-left: 3px solid #c23435`
- Hover op item → foto in linker kolom wisselt (fade-out/in 200ms) + `is-active` class
- Niet-actieve items: titel grijs (#94a3b8), actief item: titel zwart

**Mobile:**
- Elk item = 100svh hoog
- .usp-items-col = scroll-container met scroll-snap-type: y mandatory
- Per item: foto (58svh) bovenaan, titel + tekst eronder met border-left accent
- Heading-kolom verborgen op mobile

**Items:**
1. Locatie & bereik → fotos/hero-buitenkant.webp
2. Wellness op de Top Floor → fotos/arr-c-wellness.webp
3. Uitgebreid ontbijtbuffet → fotos/restaurant-ontbijt.webp

**Positie in pagina:** na kamertypes, voor footer

## Wat open staat

### Inspo 1 — Sfeerblok redesign (volgende sessie)
Inspo: slider met afwisselend "tekst boven / foto onder" en "foto boven / tekst onder".
Inspo bestand: /Users/bartvandersterren/Downloads/inspo.rtfd/
- Screenshot 12.30.49.png → referentie
- TXT.rtf beschrijving: "Slider met afwisselend boven tekst onder foto en daarna boven foto onder tekst"
Huidig sfeerblok: section.sfeer-blok in lander-google.html

## Technische notities

- lander-google.html ~regel 1765: USP CSS
- lander-google.html ~regel 2301: USP HTML  
- JS image-switcher: zoek op 'uspMainImg' in script-blok
- Alles live op visit.asteria.nl/lander-google
