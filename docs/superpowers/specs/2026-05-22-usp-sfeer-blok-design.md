# Design Spec — USP-blok + Sfeerblok
# lander-google.html

**Datum:** 2026-05-22
**Status:** Goedgekeurd, klaar voor implementatie

Referentie-HTML voor sfeerblok: functionhealth.com carousel (zie inspo.rtfd/blok.rtf)

---

## USP-blok

### Concept

Split-layout. Links grote display-titel ("waarom Asteria?"). Rechts lijst van 3 USPs, elk met rode linkerborder, titel, beschrijving en kleine foto-thumbnail.

Referentie: Hears split-feature screenshot (inspo.rtfd/Screenshot 2026-05-22 at 12.34.55.png).

### Desktop layout

2-koloms grid, max-width 1200px, padding 100px 24px, achtergrond #f8f7f5.

**Linkerkolom (~40%):**
- Grote display-headline in Electrolize, ~3rem, kleur #1a1a1a, line-height 1.1
- Bijv. "Uw verblijf in Hotel Asteria"
- Sticky positie (position: sticky, top: 40px) zodat hij meescrollt als de USP-lijst lang is

**Rechterkolom (~60%):**
3 USP-rijen, verticaal gestapeld, gap 40px. Elke rij:
- `display: flex; align-items: flex-start; justify-content: space-between; gap: 24px`
- Links: border-left: 3px solid #c23435, padding-left: 20px
  - Titel: Electrolize, 1rem, uppercase, letter-spacing 0.05em, #1a1a1a
  - Beschrijving: Montserrat 300, 0.9rem, line-height 1.7, #4a4a4a, max 2 regels
- Rechts: thumbnail 80×80px, border-radius 8px, object-fit: cover, flex-shrink: 0

HTML structuur:
```html
<section class="usp-blok">
  <div class="usp-inner">
    <div class="usp-split">
      <div class="usp-headline-col">
        <h2 class="usp-headline">Uw verblijf in Hotel Asteria</h2>
      </div>
      <div class="usp-lijst">
        <div class="usp-row">
          <div class="usp-row-content">
            <h3 class="usp-row-titel">Locatie</h3>
            <p class="usp-row-tekst">...</p>
          </div>
          <img class="usp-row-thumb" src="fotos/blok-natuur.webp" alt="Bosrijke omgeving Hotel Asteria">
        </div>
        <!-- 2x herhalen -->
      </div>
    </div>
  </div>
</section>
```

**Drie USPs (inhoud):**

1. **Locatie** — Bosrijke omgeving in Noord-Limburg, 5 minuten van centrum Venray. Gratis parkeren aanwezig.
   Thumbnail: `fotos/blok-natuur.webp`

2. **Wellness & culinair** — Vier sauna's op de Top Floor (300m², inclusief Finse, Bos en Zoutsteen sauna). Brasserie en restaurant met lokale keuken.
   Thumbnail: `fotos/card-wellness.webp`

3. **Comfort & beoordeling** — Gewaardeerd met een 4,2 op Google op basis van 2.219 beoordelingen. Moderne kamers, vlot inchecken.
   Thumbnail: `fotos/card-kamer.webp`

### Mobile layout

Accordion. Headline staat bovenaan als sectie-kop. Daarna 3 accordion-items.

Elk item:
- Header-button: border-left #c23435 + titel + chevron SVG rechts
- Eerste item standaard open, overige dicht
- Open toestand toont: beschrijving + foto (100% breedte, aspect-ratio 16/9, border-radius 8px)
- Max 1 item tegelijk open

Animatie: `max-height: 0` → `max-height: 400px`, `overflow: hidden`, `transition: max-height 300ms ease`.
Toggle via vanilla JS: klik header → toggle `data-open` attribuut → CSS reageert op `[data-open="true"]`.

```html
<div class="usp-accordion-item" data-open="true">
  <button class="usp-acc-header">
    <span>Locatie</span>
    <svg class="usp-chevron" viewBox="0 0 24 24">...</svg>
  </button>
  <div class="usp-acc-body">
    <p class="usp-row-tekst">...</p>
    <img src="fotos/blok-natuur.webp" alt="...">
  </div>
</div>
```

CSS:
```css
.usp-acc-body { max-height: 0; overflow: hidden; transition: max-height 300ms ease; }
.usp-accordion-item[data-open="true"] .usp-acc-body { max-height: 400px; }
.usp-accordion-item[data-open="true"] .usp-chevron { transform: rotate(180deg); }
```

### Responsive breakpoint

Desktop (>768px): split-layout zichtbaar, accordion verborgen.
Mobile (≤768px): split verborgen, accordion zichtbaar.

```css
@media (max-width: 768px) {
  .usp-split { display: none; }
  .usp-mobile { display: block; }
}
@media (min-width: 769px) {
  .usp-mobile { display: none; }
}
```

---

## Sfeerblok

### Concept

Horizontale draggable carousel/slider. Kaarten wisselen af:
- **Odd (1e, 3e):** foto boven, label + tekst onder
- **Even (2e):** label + tekst boven, foto onder

Afwisseling via CSS `nth-child(even)` + flexbox `order`. Gebaseerd op functionhealth.com carousel patroon (zie blok.rtf referentie-HTML).

### Desktop + Mobile layout

Max-width 1200px, padding 80px 0 (geen zijdelingse padding op slider zelf zodat kaarten tot rand lopen).
Achtergrond sectie: #fff.

Slider container:
```css
.sfeer-slider {
  display: flex;
  flex-direction: row;
  gap: 20px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  cursor: grab;
  padding: 0 24px;
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.sfeer-slider::-webkit-scrollbar { display: none; }
.sfeer-slider:active { cursor: grabbing; }
```

Elke kaart:
```css
.sfeer-kaart {
  flex: 0 0 auto;
  width: 360px;          /* desktop */
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
  border-radius: 20px;
  overflow: hidden;
  background: #f8f7f5;
}
@media (max-width: 768px) {
  .sfeer-kaart { width: calc(100vw - 48px); }
}
```

Foto-wrapper per kaart:
```css
.sfeer-foto-wrap {
  aspect-ratio: 3/4;
  overflow: hidden;
}
.sfeer-foto-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
```

**Alternerende layout via CSS:**
```css
.sfeer-kaart:nth-child(even) .sfeer-foto-wrap {
  order: 999;   /* foto naar onder op even kaarten */
}
```

Tekst-blok per kaart:
```css
.sfeer-tekst-blok {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.sfeer-label {
  font-family: 'Electrolize', sans-serif;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #1a1a1a;
}
.sfeer-desc {
  font-family: 'Montserrat', sans-serif;
  font-weight: 300;
  font-size: 0.9rem;
  line-height: 1.6;
  color: #4a4a4a;
}
```

### Drag-to-scroll JS (vanilla, geen library)

```js
(function() {
  const slider = document.querySelector('.sfeer-slider');
  if (!slider) return;
  let isDown = false, startX, scrollLeft;
  slider.addEventListener('mousedown', e => {
    isDown = true;
    startX = e.pageX - slider.offsetLeft;
    scrollLeft = slider.scrollLeft;
  });
  slider.addEventListener('mouseleave', () => isDown = false);
  slider.addEventListener('mouseup', () => isDown = false);
  slider.addEventListener('mousemove', e => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - slider.offsetLeft;
    slider.scrollLeft = scrollLeft - (x - startX) * 1.5;
  });
})();
```

### Kaartinhoud (3 kaarten)

```html
<section class="sfeer-blok">
  <div class="sfeer-inner">
    <div class="sfeer-slider">

      <!-- Kaart 1: foto boven (odd) -->
      <div class="sfeer-kaart">
        <div class="sfeer-foto-wrap">
          <img src="fotos/intro-lobby.webp" alt="Lobby Hotel Asteria" loading="lazy">
        </div>
        <div class="sfeer-tekst-blok">
          <p class="sfeer-label">Hotel & Comfort</p>
          <p class="sfeer-desc">Moderne kamers, warm ontvangen.</p>
        </div>
      </div>

      <!-- Kaart 2: tekst boven, foto onder (even — via CSS order) -->
      <div class="sfeer-kaart">
        <div class="sfeer-foto-wrap">
          <img src="fotos/card-wellness.webp" alt="Wellness Top Floor" loading="lazy">
        </div>
        <div class="sfeer-tekst-blok">
          <p class="sfeer-label">Wellness op de Top Floor</p>
          <p class="sfeer-desc">Vier sauna's, 300m².</p>
        </div>
      </div>

      <!-- Kaart 3: foto boven (odd) -->
      <div class="sfeer-kaart">
        <div class="sfeer-foto-wrap">
          <img src="fotos/card-restaurant.webp" alt="Restaurant Asteria" loading="lazy">
        </div>
        <div class="sfeer-tekst-blok">
          <p class="sfeer-label">Restaurant & Brasserie</p>
          <p class="sfeer-desc">Lokale keuken, terras, à la carte.</p>
        </div>
      </div>

    </div>
  </div>
</section>
```

### Sectie-heading

Geen sectie-heading boven de slider — de kaarten spreken voor zich.
