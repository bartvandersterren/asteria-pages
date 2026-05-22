# USP Blok Mobile A/B Test — Implementatieplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vervang het scroll-snap USP blok op mobile door twee visueel sterke varianten (Magazine Mosaic en Feature Stack) met een 50/50 A/B test.

**Architecture:** Eén bestand (`lander-google.html`). Desktop layout blijft volledig ongewijzigd. Op mobile worden de twee nieuwe varianten via CSS verborgen/getoond op basis van `data-usp-variant` op het `<html>` element, gezet door een vroeg-geladen JS IIFE in `<head>`.

**Tech Stack:** Vanilla HTML/CSS/JS, geen dependencies. Asteria fonts: Electrolize (headings) + Montserrat 300 (body). Primaire kleur: `#c23435`.

---

## Bestandsoverzicht

| Bestand | Actie | Wat |
|---------|-------|-----|
| `lander-google.html` | Modify | JS snippet in `<head>`, mobile CSS vervangen, twee HTML blokken toevoegen |

Foto's die gebruikt worden (al aanwezig in `fotos/`):
- `fotos/hero-buitenkant.webp` — Locatie USP
- `fotos/arr-c-wellness.webp` — Wellness USP
- `fotos/restaurant-ontbijt.webp` — Ontbijt USP

---

## Task 1: A/B variant JS snippet in `<head>`

**Files:**
- Modify: `lander-google.html` (rond regel 30, na `brand.css` link)

Het snippet moet zo vroeg mogelijk staan zodat `data-usp-variant` op `<html>` gezet is vóór de browser de CSS parsed. Dit voorkomt een flash waarbij de verkeerde variant even zichtbaar is.

- [ ] **Stap 1: Voeg de IIFE toe na regel 30 (na de `brand.css` link)**

Voeg het volgende in na `<link rel="stylesheet" href="brand.css">`:

```html
  <!-- A/B: USP variant toewijzing — zo vroeg mogelijk in <head> -->
  <script>
    (function() {
      var param = new URLSearchParams(location.search).get('usp');
      var valid = ['mosaic', 'stack'];
      var variant;
      if (param && valid.indexOf(param) !== -1) {
        variant = param;
        sessionStorage.setItem('usp_variant', variant);
      } else {
        variant = sessionStorage.getItem('usp_variant')
          || (Math.random() < 0.5 ? 'mosaic' : 'stack');
        sessionStorage.setItem('usp_variant', variant);
      }
      document.documentElement.dataset.uspVariant = variant;
    })();
  </script>
```

- [ ] **Stap 2: Verifieer in browser**

Open `lander-google.html` lokaal. Open DevTools → Console en voer uit:
```js
document.documentElement.dataset.uspVariant
```
Verwacht: `"mosaic"` of `"stack"`.

Test URL override: open `lander-google.html?usp=mosaic` → moet `"mosaic"` zijn.
Test URL override: open `lander-google.html?usp=stack` → moet `"stack"` zijn.

- [ ] **Stap 3: Commit**

```bash
git add lander-google.html
git commit -m "feat: A/B variant JS snippet voor USP blok mobile"
```

---

## Task 2: Mobile CSS vervangen + nieuwe variant CSS

**Files:**
- Modify: `lander-google.html` (CSS block `/* Mobile: scroll-snap */`, regels ~1849–1890)

De huidige mobile CSS gebruikt scroll-snap en `height: 100svh` per item — dat vervangen we volledig. De desktop CSS (`@media (min-width: 769px)`) blijft ongewijzigd.

- [ ] **Stap 1: Vervang het volledige `/* Mobile: scroll-snap */` blok**

Zoek en vervang de CSS van `/* Mobile: scroll-snap */` t/m het sluitende `}` van de `@media (max-width: 768px)` block (inclusief de losse `@media (min-width: 769px)` regel eronder):

**Oud (vervang dit volledig):**
```css
/* Mobile: scroll-snap */
@media (max-width: 768px) {
  .usp-blok { padding: 0; }
  .usp-inner { flex-direction: column; gap: 0; height: 100svh; }
  .usp-heading-col { display: none; }
  .usp-items-col {
    height: 100svh;
    overflow-y: scroll;
    scroll-snap-type: y mandatory;
    -webkit-overflow-scrolling: touch;
  }
  .usp-item {
    height: 100svh;
    scroll-snap-align: start;
    flex-direction: column;
    padding: 0;
    border: none;
    cursor: default;
    overflow: hidden;
    flex-shrink: 0;
  }
  .usp-item.is-active { border: none; }
  .usp-item__img {
    width: 100%;
    height: 58svh;
    object-fit: cover;
    flex-shrink: 0;
    display: block;
  }
  .usp-item__body {
    flex: 1;
    padding: 28px 20px;
    border-left: 3px solid #c23435;
    margin: 16px 16px 0;
  }
  .usp-item__title { color: #1a1a1a; }
  .usp-main-img { display: none; }
}

@media (min-width: 769px) {
  .usp-item__img { display: none; }
}
```

**Nieuw (zet dit ervoor in de plaats):**
```css
/* Beide mobile varianten standaard verborgen */
.usp-mosaic,
.usp-stack { display: none; }

/* Mobile: A/B varianten */
@media (max-width: 768px) {
  .usp-blok  { padding: 0; }
  .usp-inner { flex-direction: column; gap: 0; }

  /* Desktop layout verbergen op mobile */
  .usp-heading-col { display: none; }
  .usp-items-col   { display: none; }

  /* Actieve variant tonen */
  [data-usp-variant="mosaic"] .usp-mosaic { display: block; }
  [data-usp-variant="stack"]  .usp-stack  { display: block; }

  /* ── Variant C: Magazine Mosaic ── */
  .usp-mosaic {
    background: #f8f7f5;
    padding: 28px 14px 24px;
    width: 100%;
  }
  .usp-mosaic__heading {
    font-family: 'Electrolize', sans-serif;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: #94a3b8;
    margin: 0 0 12px;
  }
  .usp-mosaic__hero {
    position: relative;
    height: 200px;
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 8px;
  }
  .usp-mosaic__hero-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
  .usp-mosaic__overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.72) 0%, transparent 55%);
  }
  .usp-mosaic__hero-content {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 14px;
  }
  .usp-mosaic__kenmerk {
    font-family: 'Electrolize', sans-serif;
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: #c23435;
    margin: 0 0 3px;
  }
  .usp-mosaic__hero-title {
    font-family: 'Electrolize', sans-serif;
    font-size: 15px;
    color: #fff;
    letter-spacing: 0.04em;
    margin: 0 0 4px;
    line-height: 1.2;
  }
  .usp-mosaic__hero-text {
    font-family: 'Montserrat', sans-serif;
    font-size: 9.5px;
    font-weight: 300;
    color: rgba(255,255,255,0.75);
    line-height: 1.5;
    margin: 0;
  }
  .usp-mosaic__row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .usp-mosaic__small {
    position: relative;
    height: 120px;
    border-radius: 12px;
    overflow: hidden;
  }
  .usp-mosaic__small-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
  .usp-mosaic__small-content {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 10px;
  }
  .usp-mosaic__small-title {
    font-family: 'Electrolize', sans-serif;
    font-size: 10px;
    color: #fff;
    letter-spacing: 0.04em;
    margin: 0;
  }

  /* ── Variant D: Feature Stack ── */
  .usp-stack {
    background: #f8f7f5;
    padding: 28px 14px 8px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
  }
  .usp-stack__heading {
    font-family: 'Electrolize', sans-serif;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: #94a3b8;
    margin: 0 0 4px;
  }
  .usp-stack__card {
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 3px 16px rgba(0,0,0,0.08);
  }
  .usp-stack__photo {
    position: relative;
    height: 130px;
    overflow: hidden;
  }
  .usp-stack__photo img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
  .usp-stack__photo-label {
    position: absolute;
    top: 10px; left: 10px;
    background: rgba(0,0,0,0.45);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 20px;
    padding: 3px 9px;
    font-family: 'Electrolize', sans-serif;
    font-size: 7.5px;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #fff;
  }
  .usp-stack__body {
    padding: 12px 13px 13px;
    border-left: 3px solid #c23435;
    margin: 0 12px 12px;
  }
  .usp-stack__title {
    font-family: 'Electrolize', sans-serif;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #1a1a1a;
    margin: 0 0 4px;
  }
  .usp-stack__text {
    font-family: 'Montserrat', sans-serif;
    font-size: 9.5px;
    font-weight: 300;
    color: #64748b;
    line-height: 1.55;
    margin: 0;
  }
}

/* Desktop: mobile varianten verborgen houden */
@media (min-width: 769px) {
  .usp-mosaic { display: none !important; }
  .usp-stack  { display: none !important; }
}
```

- [ ] **Stap 2: Verifieer dat desktop ongewijzigd is**

Open de pagina op desktop (≥769px). Het USP blok moet er identiek uitzien als voor de wijziging: sticky foto links, items rechts.

- [ ] **Stap 3: Commit**

```bash
git add lander-google.html
git commit -m "feat: USP mobile CSS — vervangt scroll-snap door A/B variant systeem"
```

---

## Task 3: HTML voor Variant C — Magazine Mosaic

**Files:**
- Modify: `lander-google.html` (binnen `<section class="usp-blok">`, na sluitende `</div>` van `.usp-items-col`)

- [ ] **Stap 1: Voeg het `.usp-mosaic` HTML blok toe**

Zoek de regel:
```html
    </div>
  </div>
</section>

<!-- ══ FOOTER
```

En vervang door:
```html
    </div>

    <!-- Mobile Variant C: Magazine Mosaic -->
    <div class="usp-mosaic" aria-hidden="true">
      <p class="usp-mosaic__heading">Waarom Asteria</p>
      <div class="usp-mosaic__hero">
        <img src="fotos/arr-c-wellness.webp" alt="Wellness Top Floor Hotel Asteria" class="usp-mosaic__hero-img" loading="lazy">
        <div class="usp-mosaic__overlay"></div>
        <div class="usp-mosaic__hero-content">
          <p class="usp-mosaic__kenmerk">Wellness</p>
          <h3 class="usp-mosaic__hero-title">Top Floor<br>300 m²</h3>
          <p class="usp-mosaic__hero-text">4 sauna's, stoomcabine, kruidenbad en relaxruimte. Inclusief bij arrangementen.</p>
        </div>
      </div>
      <div class="usp-mosaic__row">
        <div class="usp-mosaic__small">
          <img src="fotos/hero-buitenkant.webp" alt="Hotel Asteria Venray buitenaanzicht" class="usp-mosaic__small-img" loading="lazy">
          <div class="usp-mosaic__overlay"></div>
          <div class="usp-mosaic__small-content">
            <p class="usp-mosaic__kenmerk">Locatie</p>
            <h3 class="usp-mosaic__small-title">Aan de A73</h3>
          </div>
        </div>
        <div class="usp-mosaic__small">
          <img src="fotos/restaurant-ontbijt.webp" alt="Ontbijtbuffet Hotel Asteria Venray" class="usp-mosaic__small-img" loading="lazy">
          <div class="usp-mosaic__overlay"></div>
          <div class="usp-mosaic__small-content">
            <p class="usp-mosaic__kenmerk">Ontbijt</p>
            <h3 class="usp-mosaic__small-title">Uitgebreid buffet</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Variant D: Feature Stack — zie Task 4 -->

  </div>
</section>

<!-- ══ FOOTER
```

- [ ] **Stap 2: Verifieer variant C**

Open `lander-google.html?usp=mosaic` op mobile viewport (375px). Controleer:
- Hero-kaart (wellness foto) zichtbaar, 200px hoog
- Twee mini-kaarten naast elkaar eronder
- Kopje "Waarom Asteria" zichtbaar
- Gradient overlay over foto's aanwezig
- Tekst leesbaar (wit op donkere overlay)

- [ ] **Stap 3: Commit**

```bash
git add lander-google.html
git commit -m "feat: USP mobile variant C — Magazine Mosaic HTML"
```

---

## Task 4: HTML voor Variant D — Feature Stack

**Files:**
- Modify: `lander-google.html` (vervangt de placeholder `<!-- Mobile Variant D: Feature Stack — zie Task 4 -->`)

- [ ] **Stap 1: Vervang de placeholder door het `.usp-stack` blok**

Zoek:
```html
    <!-- Mobile Variant D: Feature Stack — zie Task 4 -->
```

Vervang door:
```html
    <!-- Mobile Variant D: Feature Stack -->
    <div class="usp-stack" aria-hidden="true">
      <p class="usp-stack__heading">Waarom Asteria</p>
      <div class="usp-stack__card">
        <div class="usp-stack__photo">
          <img src="fotos/hero-buitenkant.webp" alt="Hotel Asteria Venray — buitenaanzicht" loading="lazy">
          <span class="usp-stack__photo-label">Locatie</span>
        </div>
        <div class="usp-stack__body">
          <h3 class="usp-stack__title">Direct aan de A73</h3>
          <p class="usp-stack__text">Gratis parkeren bij het hotel. Op fietsafstand van de Maasduinen. Midden in Noord-Limburg.</p>
        </div>
      </div>
      <div class="usp-stack__card">
        <div class="usp-stack__photo">
          <img src="fotos/arr-c-wellness.webp" alt="Wellness Top Floor Hotel Asteria" loading="lazy">
          <span class="usp-stack__photo-label">Wellness</span>
        </div>
        <div class="usp-stack__body">
          <h3 class="usp-stack__title">Wellness op de Top Floor</h3>
          <p class="usp-stack__text">300 m² met vier sauna's, stoomcabine, kruidenbad en relaxruimte. Inclusief bij arrangementen.</p>
        </div>
      </div>
      <div class="usp-stack__card">
        <div class="usp-stack__photo">
          <img src="fotos/restaurant-ontbijt.webp" alt="Ontbijtbuffet Hotel Asteria Venray" loading="lazy">
          <span class="usp-stack__photo-label">Ontbijt</span>
        </div>
        <div class="usp-stack__body">
          <h3 class="usp-stack__title">Uitgebreid ontbijtbuffet</h3>
          <p class="usp-stack__text">Elke ochtend vers en uitgebreid. Inbegrepen bij alle arrangementen. Ook à la carte beschikbaar.</p>
        </div>
      </div>
    </div>
```

- [ ] **Stap 2: Verifieer variant D**

Open `lander-google.html?usp=stack` op mobile viewport (375px). Controleer:
- 3 kaarten gestapeld, elk met grote foto bovenin (130px hoog)
- Glassmorphism label linksboven in elke foto
- Rode accentlijn links naast de tekst
- Titel in Electrolize uppercase, bodytekst Montserrat 300

- [ ] **Stap 3: Commit**

```bash
git add lander-google.html
git commit -m "feat: USP mobile variant D — Feature Stack HTML"
```

---

## Task 5: QA — alle scenario's doornemen

**Files:**
- Geen codewijzigingen. Alleen verificatie.

- [ ] **Stap 1: A/B random toewijzing**

Open `lander-google.html` in incognito (geen sessionStorage). Ververs 6x. Controleer via DevTools → Application → Session Storage dat `usp_variant` afwisselend `mosaic` en `stack` is (~50/50).

- [ ] **Stap 2: SessionStorage persistentie**

Open `lander-google.html` (geen URL param). Noteer welke variant getoond wordt. Ververs de pagina — dezelfde variant moet getoond worden (sessionStorage bewaard binnen sessie).

- [ ] **Stap 3: URL overrides**

- `?usp=mosaic` → Magazine Mosaic zichtbaar, `usp_variant` in sessionStorage = `"mosaic"`
- `?usp=stack` → Feature Stack zichtbaar, `usp_variant` in sessionStorage = `"stack"`
- `?usp=invalid` → random toewijzing (invalid param genegeerd)

- [ ] **Stap 4: Desktop ongewijzigd**

Open pagina op 1200px breedte. Controleer:
- Sticky foto links aanwezig
- Items rechts met hover-effect (foto wisselt)
- Geen `.usp-mosaic` of `.usp-stack` zichtbaar

- [ ] **Stap 5: aria-hidden correctheid**

De actieve mobile variant heeft `aria-hidden="true"`. Dat is correct omdat dezelfde content ook beschikbaar is in `.usp-items-col` (die op desktop getoond wordt). Verifieer in DevTools → Accessibility dat de heading structuur logisch is.

> **Optioneel:** Als je `aria-hidden` wilt togglen naar `false` op de actieve variant, voeg dan in de IIFE toe:
> ```js
> // na het zetten van data-usp-variant:
> document.addEventListener('DOMContentLoaded', function() {
>   var active = document.querySelector('.usp-' + variant);
>   if (active) active.removeAttribute('aria-hidden');
> });
> ```

- [ ] **Stap 6: Push naar main**

```bash
git push
```

Wacht ~35 seconden en verifieer op `https://visit.asteria.nl/lander-google?usp=mosaic` en `?usp=stack`.
