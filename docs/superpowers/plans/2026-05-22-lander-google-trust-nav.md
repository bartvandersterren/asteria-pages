# lander-google.html — Nav + Trust Bar + vipStatus

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Drie aanpassingen aan `lander-google.html`: nav terugbrengen naar logo + boek-nu, hero trust badges vervangen door een witte kaart-balk onderin de hero, en vipStatus corrigeren.

**Architecture:** Alle wijzigingen in één bestand (`lander-google.html`). CSS en JS zijn inline. Geen nieuwe bestanden. Taken zijn onafhankelijk van elkaar.

**Tech Stack:** Vanilla HTML/CSS/JS · Cloudflare Pages (auto-deploy na push naar `main`)

**Wat NIET aanpassen:** Sticky card (niet aanraken).

---

## Bestandswijzigingen

- Modify: `lander-google.html` — CSS nav-sectie (regels ~86–149), HTML nav (regels ~2223–2264), HTML hero (regels ~2267–2294), CSS hero-sectie, JS hamburger-handler

---

### Task 1: vipStatus fix (2 minuten)

**Files:**
- Modify: `lander-google.html` — zoek op `Wellness nieuwsbrief`

- [ ] **Stap 1: Pas de waarde aan**

  Zoek in `lander-google.html`:
  ```html
  <input type="text" name="vipStatus" value="Wellness nieuwsbrief">
  ```
  Verander naar:
  ```html
  <input type="text" name="vipStatus" value="Google Lander">
  ```

- [ ] **Stap 2: Commit**

  ```bash
  cd ~/Projects/asteria-pages
  git add lander-google.html
  git commit -m "fix: vipStatus Revinate form — Google Lander ipv Wellness nieuwsbrief"
  ```

---

### Task 2: Nav vereenvoudigen

**Doel:** Verwijder de top-bar (e-mail, telefoon, taalschakelaar) en alle menu-items. Houd over: logo links + "Boek nu" knop rechts — op zowel desktop als mobile. Geen hamburger-menu meer. Hero `padding-top` omlaag van `110px` naar `90px` want de nav wordt een stuk lager.

**Files:**
- Modify: `lander-google.html` — nav HTML (~2223–2264), CSS nav-sectie (~86–149), JS hamburger (~3344–3359), hero CSS regel `padding-top: 110px`

#### HTML — verwijder top-bar

- [ ] **Stap 1: Verwijder .top-bar blok**

  Zoek in `<!-- ══ NAV -->` het volgende blok en verwijder het volledig:
  ```html
  <div class="top-bar">
    <a href="mailto:info@asteria.nl">...</a>
    <a href="tel:0031478511466">...</a>
    <span class="lang-wrapper">...</span>
  </div>
  ```

#### HTML — verwijder menu-items

- [ ] **Stap 2: Verwijder `<ul>` met links uit .nav-content**

  Binnen `<div class="nav-content">` staat een `<ul>` met alle paginalinks. Verwijder die `<ul>` volledig:
  ```html
  <!-- verwijder dit: -->
  <ul>
    <li class="menu-close" id="menuClose">&#10005;</li>
    <li><a href="https://www.asteria.nl/kamers">Kamers en Suites</a></li>
    <li><a href="https://www.asteria.nl/hotel">Hotel</a></li>
    <li><a href="https://www.asteria.nl/restaurant">Restaurant</a></li>
    <li><a href="https://www.asteria.nl/wellness">Wellness</a></li>
    <li><a href="https://www.asteria.nl/omgeving">Omgeving</a></li>
    <li><a href="https://www.asteria.nl/contact">Contact</a></li>
  </ul>
  ```
  De `<button class="button book-now">Boek nu</button>` die daarna staat: **laat staan**.

#### HTML — vervang hamburger door Boek nu op mobile

- [ ] **Stap 3: Vervang .mobile-nav-buttons**

  Zoek:
  ```html
  <div class="mobile-nav-buttons">
    <span class="menu-button button" id="menuOpen">...</span>
    <a href="tel:..." class="button">...</a>
  </div>
  ```
  Vervang door:
  ```html
  <div class="mobile-nav-buttons">
    <button class="button book-now" onclick="window.openBookingPopup()">Boek nu</button>
  </div>
  ```

#### CSS — ruim top-bar en menu op

- [ ] **Stap 4: Verwijder .top-bar CSS**

  Verwijder in de `/* NAV */` sectie:
  - Het blok `.top-bar { display: flex; justify-content: flex-end; ... }`
  - `.top-bar { display: none; }` in de `@media (max-width: 880px)` override
  - `.top-bar a { color: #f2f2f2; ... }` en `.top-bar a:hover { ... }`
  - `.top-bar .nav-icon { ... }`
  - `.lang-nav { ... }`, `.lang-wrapper { ... }`, `.lang-arrow { ... }`

- [ ] **Stap 5: Verwijder link-stijlen en mobile menu CSS**

  Verwijder uit de `/* NAV */` sectie:
  - `.nav-bar a:not(.button):not(.logo) { color: #f2f2f2; ... }`
  - `.nav-bar a:not(.button):not(.logo):hover { ... }`
  - `.main-nav ul { position: fixed; inset: 0; background: #444; ... }` (fullscreen overlay)
  - `.main-nav.show-mobile-nav ul:not(.submenu) { display: block; }`
  - `.main-nav.show-mobile-nav.delay ul { opacity: 1; }`
  - `.main-nav ul li { width: 100%; display: block; }`
  - `.main-nav ul li a { font-size: 20px; ... }`
  - `.menu-close { display: block !important; ... }` in de media query

- [ ] **Stap 6: Stijl mobile Boek nu knop**

  Voeg toe aan het `@media (max-width: 880px)` blok in de nav-sectie:
  ```css
  .mobile-nav-buttons .book-now {
    background: #c23435;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 600;
    padding: 10px 18px;
    cursor: pointer;
    white-space: nowrap;
  }
  .mobile-nav-buttons .book-now:hover { background: #a82c2c; }
  ```

#### CSS — pas hero padding-top aan

- [ ] **Stap 7: Verlaag hero padding-top**

  Zoek in `.hero` CSS:
  ```css
  padding-top: 110px;
  ```
  Verander naar:
  ```css
  padding-top: 90px;
  ```
  (Nav zonder top-bar is ~86px hoog op desktop; 90px geeft 4px ruimte.)

#### JS — verwijder hamburger handler

- [ ] **Stap 8: Verwijder hamburger event-listener**

  Zoek in het script-blok onderaan (circa `var btnOpen = document.getElementById('menuOpen')`):
  ```js
  var nav      = document.querySelector('.main-nav');
  var btnOpen  = document.getElementById('menuOpen');
  var btnClose = document.getElementById('menuClose');
  if (btnOpen) {
    btnOpen.addEventListener('click', function () {
      nav.classList.add('show-mobile-nav');
      setTimeout(function () { nav.classList.add('delay'); }, 10);
    });
  }
  if (btnClose) {
    btnClose.addEventListener('click', function () {
      nav.classList.remove('delay');
      setTimeout(function () { nav.classList.remove('show-mobile-nav'); }, 400);
    });
  }
  ```
  Verwijder dit blok. Als `var nav` nergens anders wordt gebruikt, verwijder die regel ook.

- [ ] **Stap 9: Commit**

  ```bash
  git add lander-google.html
  git commit -m "feat: vereenvoudig nav — logo + boek-nu, geen menu of top-bar"
  ```

---

### Task 3: Trust bar in hero

**Doel:** Vervang de huidige `.hero__trust` (kleine doorzichtige tekstbadges, gecentreerd onder de CTA) door een witte kaart-balk die **absoluut onderin de hero** staat. Hero hoogte blijft `100svh`. De scroll-indicator (`.hero__scroll`) valt weg want die overlapt met de trust bar.

**Sticky card: niet aanraken.**

**Inhoud trust bar:**
- ★ 4,2 · 2.219 Google reviews
- ✓ Gratis annuleren
- ✓ Gratis parkeren
- ✓ Laagste prijs

**Files:**
- Modify: `lander-google.html` — HTML hero (~2267–2294), CSS hero-sectie

#### HTML

- [ ] **Stap 1: Verwijder .hero__trust**

  Zoek in het `<!-- ══ HERO -->` blok:
  ```html
  <div class="hero__trust">
    <span>&#9733; 4,2/5 op Google (2.219 reviews)</span>
    <span>&#10003; Gratis parkeren</span>
    <span>&#10003; Wellness op de Top Floor</span>
  </div>
  ```
  Verwijder dit volledig.

- [ ] **Stap 2: Verwijder .hero__scroll**

  Zoek en verwijder:
  ```html
  <div class="hero__scroll" aria-hidden="true">
    <div class="hero__scroll-dot"></div>
    <div class="hero__scroll-track"></div>
  </div>
  ```

- [ ] **Stap 3: Voeg .hero__trust-bar toe**

  Voeg direct vóór `</section>` (afsluitende tag van `.hero`) toe:
  ```html
  <div class="hero__trust-bar" aria-label="Kwaliteitsgaranties">
    <div class="hero__trust-card">
      <span class="hero__trust-item hero__trust-google">
        <span class="hero__trust-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
        <span>4,2 &nbsp;&middot;&nbsp; 2.219 Google reviews</span>
      </span>
      <span class="hero__trust-divider" aria-hidden="true"></span>
      <span class="hero__trust-item">&#10003;&nbsp; Gratis annuleren</span>
      <span class="hero__trust-divider" aria-hidden="true"></span>
      <span class="hero__trust-item">&#10003;&nbsp; Gratis parkeren</span>
      <span class="hero__trust-divider" aria-hidden="true"></span>
      <span class="hero__trust-item">&#10003;&nbsp; Laagste prijs</span>
    </div>
  </div>
  ```

#### CSS — verwijder oude trust en scroll

- [ ] **Stap 4: Verwijder .hero__trust CSS**

  Verwijder in de hero CSS-sectie:
  ```css
  .hero__trust { display: flex; flex-wrap: wrap; justify-content: center; gap: 4px 20px; margin-top: 14px; animation: ...; }
  .hero__trust span { font-family: ...; font-size: 11px; ... }
  ```

- [ ] **Stap 5: Verwijder .hero__scroll CSS**

  Verwijder:
  ```css
  .hero__scroll { position: absolute; bottom: 36px; left: 50%; ... }
  .hero__scroll-dot { ... }
  .hero__scroll-track { ... }
  .hero__scroll-track::after { ... }
  @keyframes scrollDown { ... }
  @keyframes scrollPulse { ... }
  ```

  En pas de `prefers-reduced-motion` regel aan — verwijder `.hero__scroll` eruit:
  ```css
  /* was: */
  .hero__content *, .hero__scroll { animation: none; opacity: 1; transform: none; transition: none; }
  /* wordt: */
  .hero__content * { animation: none; opacity: 1; transform: none; transition: none; }
  ```

#### CSS — voeg trust bar CSS toe

- [ ] **Stap 6: Voeg .hero__trust-bar CSS toe**

  Voeg toe direct ná het `.hero__cta:focus` blok (en vóór het `@media (prefers-reduced-motion)` blok):

  ```css
  /* ── Trust bar ── */
  .hero__trust-bar {
    position: absolute;
    bottom: 24px;
    left: 0;
    right: 0;
    z-index: 3;
    display: flex;
    justify-content: center;
    padding: 0 20px;
    animation: fadeUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.9s both;
  }
  .hero__trust-card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.18), 0 1px 4px rgba(0,0,0,0.08);
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px 20px;
    padding: 14px 24px;
    font-family: 'Montserrat', sans-serif;
    font-size: 12px;
    font-weight: 500;
    color: #1a1a1a;
    max-width: 700px;
    width: 100%;
    justify-content: center;
  }
  .hero__trust-item {
    display: flex;
    align-items: center;
    gap: 5px;
    white-space: nowrap;
    color: #2a2a2a;
  }
  .hero__trust-google { gap: 8px; }
  .hero__trust-stars {
    color: #f59e0b;
    font-size: 11px;
    letter-spacing: 1px;
  }
  .hero__trust-divider {
    width: 1px;
    height: 16px;
    background: rgba(0,0,0,0.12);
    flex-shrink: 0;
  }
  @media (max-width: 600px) {
    .hero__trust-bar { bottom: 16px; padding: 0 12px; }
    .hero__trust-card { padding: 12px 16px; font-size: 11px; gap: 6px 14px; }
    .hero__trust-divider { display: none; }
  }
  ```

- [ ] **Stap 7: Controleer hero padding-bottom**

  De trust bar staat op `bottom: 24px` met hoogte ~52px → occupeert tot `bottom: 76px`.
  De hero heeft `padding-bottom: 80px` (mobile: `60px`). Dit creëert voldoende ruimte zodat `.hero__content` (de gecentreerde titel + CTA) niet overlapt met de trust bar.

  Als na visuele check op mobile 375×667px (iPhone SE) overlap blijkt: verander `padding-bottom` in de mobile media query van `60px` naar `100px`.

- [ ] **Stap 8: Commit**

  ```bash
  git add lander-google.html
  git commit -m "feat: vervang hero trust badges door witte trust bar onderin hero"
  ```

---

### Task 4: Push en verifieer live

- [ ] **Stap 1: Push naar main**

  ```bash
  git push origin main
  ```

- [ ] **Stap 2: Wacht ~35 seconden op Cloudflare deploy**

- [ ] **Stap 3: Verifieer desktop en mobile**

  Check op `https://visit.asteria.nl/lander-google`:
  - **Desktop 1280px:** logo links, "Boek nu" rechts in nav, geen menu-items, geen top-bar. Hero: witte trust bar zichtbaar onderin, volledig binnen 100svh.
  - **Mobile 375px:** logo links, rode "Boek nu" knop rechts in nav, geen hamburger. Hero: trust card zichtbaar, dividers verborgen, tekst past op één rij per item.
  - **Sticky card:** ongewijzigd.
