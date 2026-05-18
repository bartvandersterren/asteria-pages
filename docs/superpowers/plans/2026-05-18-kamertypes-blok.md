# Kamertypes Blok Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kamertypes blok toevoegen aan wellness-arr-c.html — OTA room list desktop, A/B compact text vs mini thumbnail op mobile, met popup per kamer.

**Architecture:** Alles in wellness-arr-c.html (CSS + HTML + JS). Desktop: verticale lijst met foto links + delta's rechts. Mobile: twee varianten via CSS class toggle (`.rooms--compact` vs `.rooms--thumb`), random 50/50 of via URL param. Popup met foto + features + CTA.

**Tech Stack:** Vanilla HTML/CSS/JS · cwebp voor fotoconversie · Playwright voor visuele verificatie

---

## Context

- **Bestand:** `/Users/bartvandersterren/Projects/asteria-pages/wellness-arr-c.html` (2142 regels)
- **Spec:** `docs/superpowers/specs/2026-05-18-kamertypes-blok-design.md`
- **CSS invoegpunt:** lijn 1188 — direct vóór het diner blok comment in `<style>`
- **HTML invoegpunt:** lijn 1699 — direct vóór `<!-- ══ DINER`
- **JS invoegpunt:** lijn 2138 — direct vóór `</script>`
- **Mews boekingslink:** `https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS`
- **Fotobank:** `~/Documents/Asteria Fotobank/Interieur/`
- **Deploy:** push naar `main` → Cloudflare deployt automatisch → visit.asteria.nl/wellness-arr-c

---

## Task 1: Foto's converteren

**Files:**
- Add: `fotos/kamer-royale.webp`
- Add: `fotos/kamer-deluxe.webp`
- Add: `fotos/kamer-junior-suite.webp`
- Add: `fotos/kamer-bruidssuite.webp`

Bestaande `fotos/kamer-comfort.webp` (2000×1333) en `fotos/kamer-suite.webp` (2000×1333) worden hergebruikt.

- [ ] **Stap 1: Converteer 4 ontbrekende kamerfoto's**

```bash
cd ~/Projects/asteria-pages
cwebp -q 72 -m 6 -resize 2000 0 ~/Documents/Asteria\ Fotobank/Interieur/_O0A9337-HDR.jpg -o fotos/kamer-royale.webp
cwebp -q 72 -m 6 -resize 2000 0 ~/Documents/Asteria\ Fotobank/Interieur/_O0A9134-HDR.jpg -o fotos/kamer-deluxe.webp
cwebp -q 72 -m 6 -resize 2000 0 ~/Documents/Asteria\ Fotobank/Interieur/_O0A9507-HDR.jpg -o fotos/kamer-junior-suite.webp
cwebp -q 72 -m 6 -resize 2000 0 ~/Documents/Asteria\ Fotobank/Interieur/_O0A9432-HDR.jpg -o fotos/kamer-bruidssuite.webp
```

- [ ] **Stap 2: Controleer output**

```bash
ls -lh fotos/kamer-royale.webp fotos/kamer-deluxe.webp fotos/kamer-junior-suite.webp fotos/kamer-bruidssuite.webp
```

Verwacht: 4 bestanden, elk < 400KB.

- [ ] **Stap 3: Commit**

```bash
git add fotos/kamer-royale.webp fotos/kamer-deluxe.webp fotos/kamer-junior-suite.webp fotos/kamer-bruidssuite.webp
git commit -m "assets: kamerfoto's voor royale, deluxe, junior suite, bruidssuite"
```

---

## Task 2: CSS toevoegen

**Files:**
- Modify: `wellness-arr-c.html` lijn ~1188 (in `<style>`, vóór diner blok CSS)

- [ ] **Stap 1: Voeg CSS toe**

Zoek de regel `/* ══` ... `DINER BLOK` (lijn 1189-1190). Voeg het volgende toe direct **erboven**:

```css
  /* ══════════════════════════════════════════════════════════
     KAMERTYPES
  ══════════════════════════════════════════════════════════ */
  .rooms {
    background: #fff;
    padding: 80px 40px;
  }
  .rooms__inner { max-width: 1100px; margin: 0 auto; }
  .rooms__eyebrow {
    font-family: 'Electrolize', sans-serif;
    font-size: 10px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #c23435;
    display: block;
    margin-bottom: 10px;
  }
  .rooms__title {
    font-family: 'Electrolize', sans-serif;
    font-size: clamp(22px, 3vw, 36px);
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #0f172a;
    margin-bottom: 8px;
  }
  .rooms__sub {
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 300;
    color: #64748b;
    margin-bottom: 40px;
  }

  /* ── Comfort baseline ── */
  .rooms__base {
    background: #f8f7f5;
    border-radius: 12px;
    border: 1px solid #e8e5e0;
    display: flex;
    overflow: hidden;
    margin-bottom: 16px;
  }
  .rooms__base-img {
    width: 200px;
    flex-shrink: 0;
    object-fit: cover;
    display: block;
  }
  .rooms__base-body {
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .rooms__base-badge {
    display: inline-block;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;
    background: #f1f5f9;
    color: #64748b;
    margin-bottom: 8px;
    align-self: flex-start;
  }
  .rooms__base-name {
    font-family: 'Electrolize', sans-serif;
    font-size: 15px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #0f172a;
    margin-bottom: 6px;
  }
  .rooms__base-feats {
    font-size: 12px;
    color: #64748b;
    line-height: 1.6;
  }

  /* ── Upgrade cards (desktop: OTA list) ── */
  .rooms__list { display: flex; flex-direction: column; gap: 12px; }

  .room-row {
    display: flex;
    align-items: center;
    border-radius: 12px;
    border: 1px solid #f1f5f9;
    overflow: hidden;
    cursor: pointer;
    transition: box-shadow 0.22s ease, transform 0.22s ease;
    background: #fff;
    -webkit-tap-highlight-color: transparent;
  }
  .room-row:hover {
    box-shadow: 0 6px 24px rgba(0,0,0,0.08);
    transform: translateY(-1px);
  }
  .room-row__img {
    width: 200px;
    aspect-ratio: 4/3;
    object-fit: cover;
    display: block;
    flex-shrink: 0;
  }
  .room-row__body {
    flex: 1;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-width: 0;
  }
  .room-row__info { flex: 1; min-width: 0; }
  .room-row__badge {
    display: inline-block;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 6px;
  }
  .badge--upgrade { background: #fff7ed; color: #c2450a; border: 1px solid #fed7aa; }
  .badge--sauna   { background: #c23435; color: #fff; }
  .badge--premium { background: #1e1e1e; color: #fff; }

  .room-row__name {
    font-family: 'Electrolize', sans-serif;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #0f172a;
    margin-bottom: 4px;
  }
  .room-row__deltas {
    font-size: 12px;
    color: #64748b;
    line-height: 1.5;
  }
  .room-row__deltas .plus { color: #c23435; font-weight: 600; }
  .room-row__chevron {
    color: #cbd5e1;
    font-size: 20px;
    margin-left: 16px;
    flex-shrink: 0;
  }

  /* ── Popup ── */
  .room-popup-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.6);
    z-index: 1100;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.25s ease;
  }
  .room-popup-overlay.is-open {
    opacity: 1;
    pointer-events: auto;
  }
  .room-popup {
    background: #fff;
    border-radius: 16px;
    max-width: 640px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    transform: translateY(20px);
    transition: transform 0.25s cubic-bezier(0.16,1,0.3,1);
  }
  .room-popup-overlay.is-open .room-popup { transform: translateY(0); }
  .room-popup__hero {
    width: 100%;
    height: 240px;
    object-fit: cover;
    display: block;
    border-radius: 16px 16px 0 0;
  }
  .room-popup__body { padding: 24px 28px 28px; }
  .room-popup__close {
    float: right;
    background: none;
    border: none;
    font-size: 22px;
    cursor: pointer;
    color: #94a3b8;
    line-height: 1;
    padding: 0;
    margin: -4px -4px 0 0;
  }
  .room-popup__close:hover { color: #0f172a; }
  .room-popup__name {
    font-family: 'Electrolize', sans-serif;
    font-size: 20px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #0f172a;
    margin: 8px 0 6px;
  }
  .room-popup__desc {
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    font-weight: 300;
    color: #64748b;
    line-height: 1.6;
    margin-bottom: 16px;
  }
  .room-popup__features {
    list-style: none;
    display: flex;
    flex-wrap: wrap;
    gap: 6px 16px;
    margin-bottom: 20px;
  }
  .room-popup__feature {
    font-family: 'Montserrat', sans-serif;
    font-size: 12px;
    color: #475569;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .room-popup__feature::before { content: '\2713'; color: #c23435; font-weight: 700; }
  .room-popup__cta {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    min-height: 50px;
    background: #c23435;
    color: #fff;
    font-family: 'Montserrat', sans-serif;
    font-weight: 600;
    font-size: 14px;
    text-decoration: none;
    border-radius: 4px;
    transition: background 200ms ease;
  }
  .room-popup__cta:hover { background: #a82c2c; }

  /* ── Mobile ── */
  @media (max-width: 768px) {
    .rooms { padding: 56px 20px; }

    /* Hide desktop elements on mobile */
    .rooms__base-img { display: none; }
    .rooms__base { border-radius: 12px; }
    .rooms__base-body { padding: 16px; }

    .room-row__img { display: none; }
    .room-row { border-radius: 0; border-left: none; border-right: none; border-radius: 0; }
    .room-row__body { padding: 14px 0; }
    .rooms__list { gap: 0; }

    /* ── Variant A: Compact text (default on mobile) ── */
    /* room-row already works as compact text when img is hidden */

    /* ── Variant B: Mini thumbnail ── */
    .rooms--thumb .rooms__base-img {
      display: block;
      width: 100%;
      height: 140px;
      border-radius: 12px 12px 0 0;
    }
    .rooms--thumb .rooms__base {
      flex-direction: column;
    }
    .rooms--thumb .room-row__img {
      display: block;
      width: 72px;
      height: 56px;
      border-radius: 8px;
      flex-shrink: 0;
      aspect-ratio: auto;
    }
    .rooms--thumb .room-row {
      border-radius: 0;
      gap: 12px;
    }
    .rooms--thumb .room-row__body {
      padding: 12px 0;
    }

    .room-popup__hero { height: 180px; }
    .room-popup__body { padding: 18px 20px 22px; }
  }
```

---

## Task 3: HTML toevoegen

**Files:**
- Modify: `wellness-arr-c.html` lijn 1699 (direct vóór `<!-- ══ DINER`)

- [ ] **Stap 1: Voeg HTML toe**

Zoek de regel `<!-- ══ DINER ════` (lijn 1699). Voeg het volgende toe direct **erboven**:

```html
<!-- ══ KAMERTYPES ═══════════════════════════════════════ -->
<section class="rooms" id="kamertypes" aria-label="Kamertypes">
  <div class="rooms__inner">
    <span class="rooms__eyebrow">Kies je kamer</span>
    <h2 class="rooms__title">Welke kamer past bij jou?</h2>
    <p class="rooms__sub">Upgrade voor meer comfort of privacy</p>

    <!-- Comfort = baseline -->
    <div class="rooms__base">
      <img class="rooms__base-img" src="fotos/kamer-comfort.webp" alt="Comfort Kamer" loading="lazy">
      <div class="rooms__base-body">
        <span class="rooms__base-badge">Standaard inbegrepen</span>
        <span class="rooms__base-name">Comfort Kamer</span>
        <p class="rooms__base-feats">~22 m² · tweepersoons bed · douche · zithoek · airco · WiFi</p>
      </div>
    </div>

    <!-- Upgrades -->
    <div class="rooms__list">

      <div class="room-row" data-room="royale" role="button" tabindex="0">
        <img class="room-row__img" src="fotos/kamer-royale.webp" alt="Royale Kamer" loading="lazy">
        <div class="room-row__body">
          <div class="room-row__info">
            <span class="room-row__badge badge--upgrade">Upgrade</span>
            <div class="room-row__name">Royale Kamer</div>
            <div class="room-row__deltas"><span class="plus">+</span> meer ruimte <span class="plus">+</span> ligbad</div>
          </div>
          <span class="room-row__chevron">›</span>
        </div>
      </div>

      <div class="room-row" data-room="deluxe" role="button" tabindex="0">
        <img class="room-row__img" src="fotos/kamer-deluxe.webp" alt="Deluxe Kamer" loading="lazy">
        <div class="room-row__body">
          <div class="room-row__info">
            <span class="room-row__badge badge--sauna">+ Eigen sauna</span>
            <div class="room-row__name">Deluxe Kamer</div>
            <div class="room-row__deltas"><span class="plus">+</span> meer ruimte <span class="plus">+</span> privé infraroodsauna</div>
          </div>
          <span class="room-row__chevron">›</span>
        </div>
      </div>

      <div class="room-row" data-room="junior-suite" role="button" tabindex="0">
        <img class="room-row__img" src="fotos/kamer-junior-suite.webp" alt="Junior Suite" loading="lazy">
        <div class="room-row__body">
          <div class="room-row__info">
            <span class="room-row__badge badge--upgrade">Upgrade</span>
            <div class="room-row__name">Junior Suite</div>
            <div class="room-row__deltas"><span class="plus">+</span> kingsize bed <span class="plus">+</span> ruime zithoek <span class="plus">+</span> ligbad <span class="plus">+</span> koelkast</div>
          </div>
          <span class="room-row__chevron">›</span>
        </div>
      </div>

      <div class="room-row" data-room="suite" role="button" tabindex="0">
        <img class="room-row__img" src="fotos/kamer-suite.webp" alt="Suite" loading="lazy">
        <div class="room-row__body">
          <div class="room-row__info">
            <span class="room-row__badge badge--sauna">+ Eigen sauna</span>
            <div class="room-row__name">Suite</div>
            <div class="room-row__deltas"><span class="plus">+</span> kingsize bed <span class="plus">+</span> privé infraroodsauna <span class="plus">+</span> ruime zithoek <span class="plus">+</span> koelkast</div>
          </div>
          <span class="room-row__chevron">›</span>
        </div>
      </div>

      <div class="room-row" data-room="bruidssuite" role="button" tabindex="0">
        <img class="room-row__img" src="fotos/kamer-bruidssuite.webp" alt="Bruidssuite" loading="lazy">
        <div class="room-row__body">
          <div class="room-row__info">
            <span class="room-row__badge badge--premium">Premium</span>
            <div class="room-row__name">Bruidssuite</div>
            <div class="room-row__deltas"><span class="plus">+</span> kingsize bed <span class="plus">+</span> vrijstaand bad <span class="plus">+</span> inloopdouche <span class="plus">+</span> koelkast</div>
          </div>
          <span class="room-row__chevron">›</span>
        </div>
      </div>

    </div>
  </div>
</section>

<!-- Kamerpopup -->
<div class="room-popup-overlay" id="roomPopup" role="dialog" aria-modal="true" aria-label="Kamerdetails">
  <div class="room-popup" id="roomPopupInner"></div>
</div>

```

- [ ] **Stap 2: Commit CSS + HTML**

```bash
git add wellness-arr-c.html
git commit -m "feat: kamertypes blok — OTA room list met baseline + upgrade cards"
```

---

## Task 4: JS — popup + A/B toggle

**Files:**
- Modify: `wellness-arr-c.html` vóór `</script>` (lijn ~2138, na toevoegingen verschoven)

- [ ] **Stap 1: Voeg JS toe**

Zoek `</script>` aan het einde van het bestand. Voeg het volgende toe direct **erboven**:

```javascript
/* ── Kamertypes — A/B toggle + popup ── */
(function () {
  var BOOK_URL = 'https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS';

  // A/B toggle: ?rooms=compact | ?rooms=thumb | random 50/50
  var section = document.querySelector('.rooms');
  if (section) {
    var params = new URLSearchParams(window.location.search);
    var variant = params.get('rooms');
    if (variant !== 'compact' && variant !== 'thumb') {
      variant = sessionStorage.getItem('rooms-variant');
      if (!variant) {
        variant = Math.random() < 0.5 ? 'compact' : 'thumb';
        sessionStorage.setItem('rooms-variant', variant);
      }
    }
    if (variant === 'thumb') {
      section.classList.add('rooms--thumb');
    }
  }

  // Room data
  var ROOMS = {
    'royale': {
      badge: '<span class="room-row__badge badge--upgrade">Upgrade</span>',
      name: 'Royale Kamer',
      img: 'fotos/kamer-royale.webp',
      desc: 'Meer ruimte om te ademen \u2014 en de keuze voor een bad als je na de wellness ook op de kamer wil ontspannen.',
      features: ['Ruimer dan Comfort', 'Bad of douche', 'Zithoek', 'Koffiezetapparaat', 'Airco']
    },
    'deluxe': {
      badge: '<span class="room-row__badge badge--sauna">+ Eigen sauna</span>',
      name: 'Deluxe Kamer',
      img: 'fotos/kamer-deluxe.webp',
      desc: 'Een priv\u00e9 infraroodsauna op de kamer. Wellness begint bij jou aan de deur \u2014 geen gedeelde ruimte.',
      features: ['Eigen infraroodsauna', 'Meer ruimte', 'Dubbel bed', 'Douche', 'Zithoek', 'Koffiezetapparaat', 'Airco']
    },
    'junior-suite': {
      badge: '<span class="room-row__badge badge--upgrade">Upgrade</span>',
      name: 'Junior Suite',
      img: 'fotos/kamer-junior-suite.webp',
      desc: 'Het extra formaat dat een wellness-avond \u00e9cht luxe maakt: kingsize bed, een bad en een ruime zithoek.',
      features: ['Kingsize bed', 'Bad', 'Ruime zithoek met slaapbank', 'Koelkastje', 'Koffiezetapparaat', 'Airco']
    },
    'suite': {
      badge: '<span class="room-row__badge badge--sauna">+ Eigen sauna</span>',
      name: 'Suite',
      img: 'fotos/kamer-suite.webp',
      desc: 'Het beste van beide werelden: een ruime suite met eigen infraroodsauna \u00e9n toegang tot het gedeelde wellness-centrum.',
      features: ['Kingsize bed', 'Eigen infraroodsauna', 'Ruime zithoek met slaapbank', 'Koelkastje', 'Airco']
    },
    'bruidssuite': {
      badge: '<span class="room-row__badge badge--premium">Premium</span>',
      name: 'Bruidssuite',
      img: 'fotos/kamer-bruidssuite.webp',
      desc: 'Vrijstaand bad, ruime inloopdouche en de meest romantische sfeer van het hotel. Voor een onvergetelijke avond.',
      features: ['Kingsize bed', 'Vrijstaand bad', 'Ruime inloopdouche', 'Zithoek', 'Koelkastje', 'Airco']
    }
  };

  var overlay = document.getElementById('roomPopup');
  var inner = document.getElementById('roomPopupInner');

  function openPopup(key) {
    var r = ROOMS[key];
    if (!r) return;
    inner.innerHTML =
      '<img class="room-popup__hero" src="' + r.img + '" alt="' + r.name + '" loading="lazy">' +
      '<div class="room-popup__body">' +
        '<button class="room-popup__close" id="popupClose" aria-label="Sluiten">&times;</button>' +
        r.badge +
        '<h3 class="room-popup__name">' + r.name + '</h3>' +
        '<p class="room-popup__desc">' + r.desc + '</p>' +
        '<ul class="room-popup__features">' +
          r.features.map(function (f) { return '<li class="room-popup__feature">' + f + '</li>'; }).join('') +
        '</ul>' +
        '<a href="' + BOOK_URL + '" class="room-popup__cta" target="_blank" rel="noopener">Boek dit arrangement</a>' +
      '</div>';
    overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    document.getElementById('popupClose').addEventListener('click', closePopup);
  }

  function closePopup() {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closePopup();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closePopup();
  });

  document.querySelectorAll('.room-row').forEach(function (row) {
    row.addEventListener('click', function () { openPopup(this.dataset.room); });
    row.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openPopup(this.dataset.room); }
    });
  });
}());
```

- [ ] **Stap 2: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: kamertypes JS — popup + A/B mobile toggle"
```

---

## Task 5: Visueel testen

**Files:** geen wijzigingen

- [ ] **Stap 1: Start lokale server** (als nog niet actief)

```bash
cd ~/Projects/asteria-pages && python3 -m http.server 8765 &
```

- [ ] **Stap 2: Desktop screenshot (1440px)**

```js
// Playwright — browser_run_code_unsafe
await page.setViewportSize({ width: 1440, height: 900 });
await page.goto('http://localhost:8765/wellness-arr-c.html#kamertypes');
await page.waitForTimeout(500);
```

Dan `browser_take_screenshot`. Controleer:
- Sectie-header zichtbaar (eyebrow + titel + subtitel)
- Comfort baseline-blok met foto links
- 5 upgrade-rijen met foto links, badge + naam + delta's midden, chevron rechts
- Geen horizontale overflow

- [ ] **Stap 3: Desktop popup test**

```js
// Playwright — browser_run_code_unsafe
await page.click('[data-room="bruidssuite"]');
await page.waitForTimeout(400);
```

Dan `browser_take_screenshot`. Controleer:
- Popup zichtbaar met foto + badge + naam + beschrijving + features + CTA
- Overlay donker achter popup
- Close-button zichtbaar

- [ ] **Stap 4: Mobile A screenshot (375px, compact)**

```js
// Playwright — browser_run_code_unsafe
await page.setViewportSize({ width: 375, height: 812 });
await page.goto('http://localhost:8765/wellness-arr-c.html?rooms=compact#kamertypes');
await page.waitForTimeout(500);
```

Dan `browser_take_screenshot`. Controleer:
- Comfort baseline zonder foto (tekst only)
- Upgrade-rijen zonder foto's, badge + naam + delta's + chevron
- Compact, weinig verticale ruimte per rij

- [ ] **Stap 5: Mobile B screenshot (375px, thumb)**

```js
// Playwright — browser_run_code_unsafe
await page.setViewportSize({ width: 375, height: 812 });
await page.goto('http://localhost:8765/wellness-arr-c.html?rooms=thumb#kamertypes');
await page.waitForTimeout(500);
```

Dan `browser_take_screenshot`. Controleer:
- Comfort baseline met grote foto bovenaan
- Upgrade-rijen met mini thumbnail (72px) links
- Thumbnail-formaat correct (niet vervormd)

- [ ] **Stap 6: Mobile popup test**

```js
// Playwright — browser_run_code_unsafe
await page.click('[data-room="suite"]');
await page.waitForTimeout(400);
```

Dan `browser_take_screenshot`. Controleer:
- Popup neemt volle breedte, scrollbaar
- Foto 180px hoog
- CTA zichtbaar en klikbaar

---

## Task 6: Push en live test

**Files:** geen wijzigingen

- [ ] **Stap 1: Push**

```bash
git push
```

- [ ] **Stap 2: Wacht ~35 seconden, test live**

```js
// Playwright — browser_run_code_unsafe
await page.setViewportSize({ width: 1440, height: 900 });
await page.goto('https://visit.asteria.nl/wellness-arr-c#kamertypes');
await page.waitForTimeout(1000);
```

Dan `browser_take_screenshot`. Bevestig dat het live hetzelfde werkt als lokaal.

- [ ] **Stap 3: Live mobile test**

```js
// Playwright — browser_run_code_unsafe
await page.setViewportSize({ width: 375, height: 812 });
await page.goto('https://visit.asteria.nl/wellness-arr-c?rooms=thumb#kamertypes');
await page.waitForTimeout(1000);
```

Dan `browser_take_screenshot`.
