# Sticky CTA Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vervang de full-width sticky balk in `wellness-arr-c.html` door een floating FAB op mobile en een compact beige kaartje op desktop.

**Architecture:** Alle wijzigingen zitten in één bestand (`wellness-arr-c.html`): CSS vervangen (regels 853–943), HTML vervangen (regels 948–966), JS vervangen (regels 1422–1466). Geen nieuwe bestanden nodig.

**Tech Stack:** Vanilla HTML/CSS/JS, IntersectionObserver, CSS animations, Playwright voor visuele QA.

---

## Bestandskaart

| Bestand | Actie | Regels |
|---------|-------|--------|
| `wellness-arr-c.html` | Modify — CSS | 853–943 |
| `wellness-arr-c.html` | Modify — HTML | 948–966 |
| `wellness-arr-c.html` | Modify — JS | 1422–1466 |

---

### Task 1: Vervang de CSS

**Files:**
- Modify: `wellness-arr-c.html:853-943`

De oude `.sticky-cta`-blok (regels 853–943) bevat stijlen voor de full-width balk, twee varianten, en een mobile-override. Dit wordt volledig vervangen door stijlen voor `.sticky-fab` (mobile) en `.sticky-card` (desktop).

- [ ] **Stap 1: Verwijder de oude sticky-cta CSS en vervang door nieuw blok**

Zoek in `wellness-arr-c.html` het blok dat begint met:
```css
    .sticky-cta {
```
en eindigt met de sluitende `}` van de `@media (max-width: 600px)` override (± regel 943).

Vervang het volledige blok door:

```css
    /* ── Sticky CTA: gedeelde animatie ── */
    @keyframes sticky-appear {
      from { opacity: 0; transform: scale(0.88); }
      to   { opacity: 1; transform: scale(1); }
    }

    /* ── Mobile: floating FAB ── */
    .sticky-fab {
      position: fixed;
      bottom: 20px;
      right: 16px;
      z-index: 900;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #c23435;
      color: #fff;
      font-family: 'Montserrat', sans-serif;
      font-weight: 600;
      font-size: 13px;
      letter-spacing: 0.04em;
      text-decoration: none;
      padding: 12px 20px;
      border-radius: 50px;
      box-shadow: 0 4px 16px rgba(194,52,53,0.45), 0 6px 20px rgba(0,0,0,0.15);
      opacity: 0;
      transform: scale(0.88);
      pointer-events: none;
      transition: background 200ms ease;
    }

    .sticky-fab.is-visible {
      animation: sticky-appear 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s forwards;
      pointer-events: auto;
    }

    .sticky-fab svg { width: 14px; height: 14px; flex-shrink: 0; }
    .sticky-fab:hover { background: #a82c2c; }
    .sticky-fab:focus { outline: 2px solid #fff; outline-offset: 3px; }

    /* ── Desktop: floating kaartje ── */
    .sticky-card { display: none; }

    @media (min-width: 601px) {
      .sticky-fab { display: none; }

      .sticky-card {
        display: flex;
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 900;
        width: 180px;
        background: #f0efed;
        border-radius: 14px;
        padding: 16px 18px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.15), 0 2px 8px rgba(0,0,0,0.07);
        opacity: 0;
        transform: scale(0.88);
        pointer-events: none;
      }

      .sticky-card.is-visible {
        animation: sticky-appear 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s forwards;
        pointer-events: auto;
      }
    }

    .sticky-card__name {
      font-family: 'Electrolize', sans-serif;
      font-size: 7px;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: rgba(19,17,16,0.4);
    }

    .sticky-card__price {
      font-family: 'Montserrat', sans-serif;
      font-size: 22px;
      font-weight: 700;
      color: #131110;
      line-height: 1;
    }

    .sticky-card__price-sub {
      font-family: 'Montserrat', sans-serif;
      font-size: 9px;
      font-weight: 300;
      color: rgba(19,17,16,0.4);
      margin-top: -6px;
    }

    .sticky-card__btn {
      display: block;
      background: #c23435;
      color: #fff;
      font-family: 'Montserrat', sans-serif;
      font-weight: 600;
      font-size: 11px;
      letter-spacing: 0.04em;
      text-decoration: none;
      text-align: center;
      padding: 10px 12px;
      border-radius: 8px;
      transition: background 200ms ease;
    }

    .sticky-card__btn:hover { background: #a82c2c; }
    .sticky-card__btn:focus { outline: 2px solid #c23435; outline-offset: 2px; }

    /* ── Reduced motion ── */
    @media (prefers-reduced-motion: reduce) {
      .sticky-fab, .sticky-card {
        animation: none !important;
        transition: opacity 0.2s ease !important;
        transform: none !important;
      }
      .sticky-fab.is-visible, .sticky-card.is-visible {
        opacity: 1;
      }
    }
```

- [ ] **Stap 2: Commit**

```bash
git add wellness-arr-c.html
git commit -m "refactor: sticky CTA CSS — FAB mobile + kaartje desktop"
```

---

### Task 2: Vervang de HTML

**Files:**
- Modify: `wellness-arr-c.html:948-966`

De oude HTML heeft een `<div class="sticky-cta">` met twee variant-divs en een knop. Dit wordt vervangen door een `<a class="sticky-fab">` voor mobile en een `<div class="sticky-card">` voor desktop.

- [ ] **Stap 1: Vervang het oude sticky-cta HTML-blok**

Zoek in `wellness-arr-c.html` het blok:
```html
<!-- ══ STICKY CTA ════════════════════════════════════════ -->
<div class="sticky-cta" id="stickyCta" role="complementary" aria-label="Snel boeken">
  ...
</div>
```
(regels 948–966, tot en met de sluitende `</div>`)

Vervang het door:

```html
<!-- ══ STICKY CTA ════════════════════════════════════════ -->
<a
  href="https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS"
  class="sticky-fab"
  id="stickyFab"
  target="_blank"
  rel="noopener"
  aria-label="Boek direct: Wellness Arrangement"
>
  Boek direct
  <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <path d="M3 8h10M9 4l4 4-4 4" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</a>

<div class="sticky-card" id="stickyCard" role="complementary" aria-label="Snel boeken">
  <span class="sticky-card__name">Wellness Arrangement</span>
  <strong class="sticky-card__price">&euro;139,50</strong>
  <span class="sticky-card__price-sub">per persoon</span>
  <a
    href="https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS"
    class="sticky-card__btn"
    target="_blank"
    rel="noopener"
  >Boek direct &rarr;</a>
</div>
```

- [ ] **Stap 2: Commit**

```bash
git add wellness-arr-c.html
git commit -m "refactor: sticky CTA HTML — FAB + kaartje, A/B markup verwijderd"
```

---

### Task 3: Vervang de JavaScript

**Files:**
- Modify: `wellness-arr-c.html:1422-1466`

De oude JS bevat A/B test logica (`sessionStorage`, twee varianten, custom event). Dit vervalt volledig. De nieuwe JS doet alleen: `#reviews` observeren → `.is-visible` toevoegen/verwijderen op beide elementen.

- [ ] **Stap 1: Vervang het JS-blok**

Zoek in `wellness-arr-c.html` het blok dat begint met:
```js
  /* ── Sticky CTA + A/B test ── */
  (function () {
```
en eindigt met de sluitende `}());` van dat IIFE.

Vervang het volledige blok door:

```js
  /* ── Sticky CTA ── */
  (function () {
    var fab  = document.getElementById('stickyFab');
    var card = document.getElementById('stickyCard');
    var reviews = document.getElementById('reviews');
    if (!fab || !card || !reviews) return;

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var show;
        if (e.isIntersecting) {
          show = true;                        // reviews in beeld → arrangement voorbij
        } else if (e.boundingClientRect.top > 0) {
          show = false;                       // reviews nog onder viewport
        } else {
          show = true;                        // reviews al boven viewport (ver gescrolld)
        }
        fab.classList.toggle('is-visible', show);
        card.classList.toggle('is-visible', show);
      });
    }, { threshold: 0 });

    io.observe(reviews);
  }());
```

- [ ] **Stap 2: Commit**

```bash
git add wellness-arr-c.html
git commit -m "refactor: sticky CTA JS — A/B test verwijderd, FAB + kaartje trigger"
```

---

### Task 4: Visuele QA

**Files:**
- Read: `wellness-arr-c.html` (geen wijziging)

Controleer het resultaat op mobile (375px) en desktop (1280px) via Playwright.

- [ ] **Stap 1: Push naar main en wacht op Cloudflare deploy**

```bash
git push
```

Wacht ~35 seconden.

- [ ] **Stap 2: Mobile QA — FAB zichtbaar na scrollen**

Gebruik `browser_run_code_unsafe` met:

```js
await page.setViewportSize({ width: 375, height: 812 });
await page.goto('https://visit.asteria.nl/wellness-arr-c');
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await new Promise(r => setTimeout(r, 600));
```

Daarna `browser_take_screenshot`. Verwacht: rode FAB rechtsonder zichtbaar, geen balk over de volle breedte.

- [ ] **Stap 3: Desktop QA — kaartje zichtbaar na scrollen**

Gebruik `browser_run_code_unsafe` met:

```js
await page.setViewportSize({ width: 1280, height: 800 });
await page.goto('https://visit.asteria.nl/wellness-arr-c');
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await new Promise(r => setTimeout(r, 600));
```

Daarna `browser_take_screenshot`. Verwacht: beige kaartje rechtsonder, prijs zichtbaar, geen volle-breedte balk.

- [ ] **Stap 4: Mobile QA — FAB verborgen bij hero**

```js
await page.setViewportSize({ width: 375, height: 812 });
await page.goto('https://visit.asteria.nl/wellness-arr-c');
// Niet scrollen
```

Daarna `browser_take_screenshot`. Verwacht: geen FAB zichtbaar.

- [ ] **Stap 5: Commit als alles klopt**

```bash
git add wellness-arr-c.html
git commit -m "fix: sticky CTA QA — visuele controle geslaagd" --allow-empty
```

Of als er toch kleine fixes nodig zijn, fix → commit met beschrijving van de fix.
