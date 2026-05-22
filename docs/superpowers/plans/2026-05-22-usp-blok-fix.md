# USP Blok Redesign — lander-google.html

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Het USP-blok op lander-google.html vervangen door een split-layout met Asteria-branding: grote koptekst links, gestapelde USP-items met linkerborder-accent + mini-thumbnail rechts. Mobile: accordion met uitklapbare foto's.

**Architecture:** De bestaande `.usp-blok` sectie (CSS + HTML) wordt volledig vervangen. Geen externe dependencies. Foto's uit `fotos/` repo.

**Tech Stack:** Vanilla HTML/CSS/JS in één bestand. Accordion via checkbox-hack of minimale inline JS.

---

## Design spec (gebaseerd op inspo + Asteria branding)

### Desktop
```
┌─────────────────────────────────────────────────────────┐
│  [Sticky left]          │  [Stacked USP items right]    │
│                         │                               │
│  Waarom kiezen          │  ┃ Locatie & bereik           │
│  voor Asteria?          │    Direct aan de A73 ...      │
│                         │    [mini foto: buitenkant]    │
│  (Electrolize, groot,   │                               │
│   uppercase)            │  ┃ Wellness op de Top Floor   │
│                         │    300 m² met vier sauna's .. │
│                         │    [mini foto: sauna]         │
│                         │                               │
│                         │  ┃ Uitgebreid ontbijtbuffet   │
│                         │    Elke ochtend vers ...      │
│                         │    [mini foto: ontbijt]       │
└─────────────────────────────────────────────────────────┘
```
- Left: 40% breed, sticky tijdens scroll van de items
- Right: 60%, items gestapeld met `border-left: 3px solid #c23435`
- Mini-thumbnail: 80×80px, border-radius 8px, rechts uitgelijnd per item
- Achtergrond: #f8f7f5 (ongewijzigd)

### Mobile (375px)
- Accordion: koptekst altijd zichtbaar, tap opent foto + omschrijving
- Standaard eerste item open
- Accordion-chevron (▼) rechts, draait bij open

---

## Foto's per USP item

| USP | Foto |
|-----|------|
| Locatie & bereik | `fotos/hero-buitenkant.webp` |
| Wellness Top Floor | `fotos/arr-c-wellness.webp` |
| Ontbijtbuffet | `fotos/restaurant-ontbijt.webp` |

---

## Content per item

**Sectie-koptekst (links):**
```
WAAROM
HOTEL ASTERIA?
```
*(Electrolize uppercase, twee regels, groot — ~2.5rem desktop)*

**Item 1 — Locatie & bereik**
- Titel: `Locatie & bereik`
- Body: `Direct aan de A73, midden in Noord-Limburg. Gratis parkeren bij het hotel. Op fietsafstand van de Maasduinen.`

**Item 2 — Wellness op de Top Floor**
- Titel: `Wellness op de Top Floor`
- Body: `300 m² met vier sauna's, stoomcabine, kruidenbad en relaxruimte. Inclusief bij arrangementen, ook beschikbaar voor dagbezoek.`

**Item 3 — Uitgebreid ontbijtbuffet**
- Titel: `Uitgebreid ontbijtbuffet`
- Body: `Elke ochtend vers en uitgebreid. Inbegrepen bij alle arrangementen. Ook à la carte beschikbaar.`

---

## Bestand

- Modify: `lander-google.html`
  - CSS: vervang alles tussen `/* USP BLOK */` en `/* SFEER BLOK */` (~regels 1766–1819)
  - HTML: vervang de volledige `<section class="usp-blok">` (~regels 1980–2020)
  - Positie in de pagina: verplaatsen naar ná kamertypes, vóór footer (zie Task 3)

---

## Task 1: CSS — split-layout + accordion stijlen

**Files:**
- Modify: `lander-google.html` (CSS sectie ~regels 1766–1819)

- [ ] **Stap 1: Vervang de bestaande USP CSS volledig**

  Zoek de blok tussen `/* USP BLOK */` en `/* SFEER BLOK */` en vervang alles daartussen door:

  ```css
  /* ══════════════════════════════════════════════════════════
     USP BLOK — split layout
  ══════════════════════════════════════════════════════════ */
  .usp-blok {
    background: #f8f7f5;
    padding: 100px 24px;
  }
  .usp-inner {
    max-width: 1100px;
    margin: 0 auto;
    display: flex;
    gap: 80px;
    align-items: flex-start;
  }

  /* Linker kolom: koptekst sticky */
  .usp-heading-col {
    flex: 0 0 38%;
    position: sticky;
    top: 120px;
  }
  .usp-heading {
    font-family: 'Electrolize', sans-serif;
    font-size: clamp(1.8rem, 3vw, 2.8rem);
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    line-height: 1.1;
    color: #1a1a1a;
  }
  .usp-heading em {
    font-style: normal;
    color: #c23435;
  }

  /* Rechter kolom: gestapelde items */
  .usp-items-col {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0;
  }
  .usp-item {
    display: flex;
    align-items: flex-start;
    gap: 20px;
    padding: 32px 0;
    border-bottom: 1px solid rgba(0,0,0,0.08);
    border-left: 3px solid #c23435;
    padding-left: 24px;
  }
  .usp-item:first-child {
    padding-top: 0;
  }
  .usp-item__body {
    flex: 1;
  }
  .usp-item__title {
    font-family: 'Electrolize', sans-serif;
    font-size: 1rem;
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #1a1a1a;
    margin: 0 0 10px;
  }
  .usp-item__text {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.9rem;
    font-weight: 300;
    color: #475569;
    line-height: 1.7;
    margin: 0;
  }
  .usp-item__thumb {
    flex-shrink: 0;
    width: 88px;
    height: 88px;
    border-radius: 10px;
    object-fit: cover;
  }

  /* Mobile: accordion */
  @media (max-width: 768px) {
    .usp-blok { padding: 64px 16px; }
    .usp-inner {
      flex-direction: column;
      gap: 32px;
    }
    .usp-heading-col {
      position: static;
      flex: none;
    }
    .usp-heading { font-size: 1.6rem; }
    .usp-items-col { gap: 0; }

    /* accordion */
    .usp-item {
      flex-direction: column;
      padding: 0;
      border-left: none;
      border-bottom: 1px solid rgba(0,0,0,0.1);
      overflow: hidden;
    }
    .usp-item__trigger {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 18px 0;
      cursor: pointer;
      border-left: 3px solid #c23435;
      padding-left: 16px;
      background: none;
      border-top: none;
      border-right: none;
      border-bottom: none;
      width: 100%;
      text-align: left;
    }
    .usp-item__trigger-title {
      font-family: 'Electrolize', sans-serif;
      font-size: 0.95rem;
      font-weight: 400;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #1a1a1a;
    }
    .usp-item__chevron {
      width: 18px;
      height: 18px;
      color: #c23435;
      transition: transform 0.3s ease;
      flex-shrink: 0;
    }
    .usp-item.is-open .usp-item__chevron {
      transform: rotate(180deg);
    }
    .usp-item__drawer {
      display: none;
      padding: 0 0 20px 19px;
    }
    .usp-item.is-open .usp-item__drawer {
      display: block;
    }
    .usp-item__drawer-img {
      width: 100%;
      height: 180px;
      object-fit: cover;
      border-radius: 10px;
      margin-bottom: 14px;
    }
    /* verberg desktop elementen op mobile */
    .usp-item__body,
    .usp-item__thumb { display: none; }
  }

  @media (min-width: 769px) {
    /* verberg mobile-only elementen op desktop */
    .usp-item__trigger,
    .usp-item__drawer { display: none; }
  }
  ```

- [ ] **Stap 2: Commit**
  ```bash
  git add lander-google.html
  git commit -m "feat: usp blok — split-layout CSS + mobile accordion stijlen"
  ```

---

## Task 2: HTML — sectie herschrijven

**Files:**
- Modify: `lander-google.html` (HTML ~regels 1980–2020)

- [ ] **Stap 1: Vervang de volledige `<section class="usp-blok">` door:**

  ```html
  <!-- ══ USP ════════════════════════════════════════════════ -->
  <section class="usp-blok" id="usp" aria-label="Waarom Hotel Asteria">
    <div class="usp-inner">

      <!-- Linker kolom: koptekst -->
      <div class="usp-heading-col">
        <h2 class="usp-heading">Waarom<br>Hotel<br><em>Asteria?</em></h2>
      </div>

      <!-- Rechter kolom: items -->
      <div class="usp-items-col">

        <!-- Item 1: Locatie -->
        <div class="usp-item is-open">
          <!-- Mobile trigger -->
          <button class="usp-item__trigger" aria-expanded="true">
            <span class="usp-item__trigger-title">Locatie &amp; bereik</span>
            <svg class="usp-item__chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <!-- Mobile drawer -->
          <div class="usp-item__drawer">
            <img src="fotos/hero-buitenkant.webp" alt="Hotel Asteria Venray — buitenaanzicht" class="usp-item__drawer-img" loading="lazy">
            <p class="usp-item__text">Direct aan de A73, midden in Noord-Limburg. Gratis parkeren bij het hotel. Op fietsafstand van de Maasduinen.</p>
          </div>
          <!-- Desktop body -->
          <div class="usp-item__body">
            <h3 class="usp-item__title">Locatie &amp; bereik</h3>
            <p class="usp-item__text">Direct aan de A73, midden in Noord-Limburg. Gratis parkeren bij het hotel. Op fietsafstand van de Maasduinen.</p>
          </div>
          <img src="fotos/hero-buitenkant.webp" alt="Hotel Asteria Venray — buitenaanzicht" class="usp-item__thumb" loading="lazy">
        </div>

        <!-- Item 2: Wellness -->
        <div class="usp-item">
          <button class="usp-item__trigger" aria-expanded="false">
            <span class="usp-item__trigger-title">Wellness op de Top Floor</span>
            <svg class="usp-item__chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <div class="usp-item__drawer">
            <img src="fotos/arr-c-wellness.webp" alt="Wellness Top Floor Hotel Asteria" class="usp-item__drawer-img" loading="lazy">
            <p class="usp-item__text">300 m² met vier sauna's, stoomcabine, kruidenbad en relaxruimte. Inclusief bij arrangementen, ook beschikbaar voor dagbezoek.</p>
          </div>
          <div class="usp-item__body">
            <h3 class="usp-item__title">Wellness op de Top Floor</h3>
            <p class="usp-item__text">300 m² met vier sauna's, stoomcabine, kruidenbad en relaxruimte. Inclusief bij arrangementen, ook beschikbaar voor dagbezoek.</p>
          </div>
          <img src="fotos/arr-c-wellness.webp" alt="Wellness Top Floor Hotel Asteria" class="usp-item__thumb" loading="lazy">
        </div>

        <!-- Item 3: Ontbijt -->
        <div class="usp-item">
          <button class="usp-item__trigger" aria-expanded="false">
            <span class="usp-item__trigger-title">Uitgebreid ontbijtbuffet</span>
            <svg class="usp-item__chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <div class="usp-item__drawer">
            <img src="fotos/restaurant-ontbijt.webp" alt="Ontbijtbuffet Hotel Asteria Venray" class="usp-item__drawer-img" loading="lazy">
            <p class="usp-item__text">Elke ochtend vers en uitgebreid. Inbegrepen bij alle arrangementen. Ook à la carte beschikbaar.</p>
          </div>
          <div class="usp-item__body">
            <h3 class="usp-item__title">Uitgebreid ontbijtbuffet</h3>
            <p class="usp-item__text">Elke ochtend vers en uitgebreid. Inbegrepen bij alle arrangementen. Ook à la carte beschikbaar.</p>
          </div>
          <img src="fotos/restaurant-ontbijt.webp" alt="Ontbijtbuffet Hotel Asteria Venray" class="usp-item__thumb" loading="lazy">
        </div>

      </div>
    </div>
  </section>
  ```

- [ ] **Stap 2: Commit**
  ```bash
  git add lander-google.html
  git commit -m "feat: usp blok — split-layout HTML, 3 items met thumbnail + accordion markup"
  ```

---

## Task 3: JS — accordion gedrag

**Files:**
- Modify: `lander-google.html` (script sectie onderaan, voor `</body>`)

- [ ] **Stap 1: Voeg accordion JS toe**

  Voeg dit toe direct vóór de afsluitende `</body>` tag (of aan het einde van het bestaande script-blok):

  ```js
  // ── USP accordion (mobile) ──────────────────────────────
  (function() {
    var triggers = document.querySelectorAll('.usp-item__trigger');
    triggers.forEach(function(btn) {
      btn.addEventListener('click', function() {
        var item = btn.closest('.usp-item');
        var isOpen = item.classList.contains('is-open');
        // sluit alle items
        document.querySelectorAll('.usp-item').forEach(function(el) {
          el.classList.remove('is-open');
          el.querySelector('.usp-item__trigger').setAttribute('aria-expanded', 'false');
        });
        // open dit item als het gesloten was
        if (!isOpen) {
          item.classList.add('is-open');
          btn.setAttribute('aria-expanded', 'true');
        }
      });
    });
  })();
  ```

- [ ] **Stap 2: Commit**
  ```bash
  git add lander-google.html
  git commit -m "feat: usp blok — accordion JS"
  ```

---

## Task 4: Positie — USP verplaatsen naar na kamertypes

**Files:**
- Modify: `lander-google.html` (HTML volgorde)

Huidige volgorde: Hero → USP → Reviews → Sfeer → Kamertypes → Footer
Doelvolgorde:     Hero → Reviews → Sfeer → Kamertypes → **USP** → Footer

- [ ] **Stap 1: Knip de `<section class="usp-blok">` uit zijn huidige positie** (direct na hero)

- [ ] **Stap 2: Plak hem direct vóór `<footer class="footer">`**

- [ ] **Stap 3: Commit en push**
  ```bash
  git add lander-google.html
  git commit -m "feat: usp blok — positie na kamertypes"
  git push origin main
  ```

---

## Task 5: Verificatie

- [ ] **Stap 1: Wacht ~35s na push, open `visit.asteria.nl/lander-google`**

- [ ] **Stap 2: Desktop check**
  - Split-layout zichtbaar: koptekst links, 3 items rechts
  - Rode linker-border per item (#c23435)
  - Mini-thumbnails 88×88px zichtbaar rechts per item
  - Koptekst "sticky" tijdens scrollen langs de items
  - Accordion triggers (`<button>`) zijn NIET zichtbaar op desktop

- [ ] **Stap 3: Mobile check (375px via Playwright)**

  ```js
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto('https://visit.asteria.nl/lander-google#usp');
  ```

  - Accordion zichtbaar: item 1 standaard open met foto
  - Tap op item 2 → opent foto + tekst, item 1 sluit
  - Chevron draait bij open/sluiten
  - Desktop thumbnails en body-tekst zijn verborgen op mobile

- [ ] **Stap 4: Klaar — meld af**
