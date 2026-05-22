# Diner Blok Implementatie Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Voeg een restaurant/diner sfeerblok toe aan `wellness-arr-c.html` direct vóór de footer — een gecontaineerde banner-card met restaurantfoto, overlay en gecentreerde tekst.

**Architecture:** Één HTML-sectie + CSS in het bestaande `<style>` blok. Geen JS. Desktop: gecontaineerde card met border-radius, zweeft op #f0efed pagina-achtergrond. Mobile: full-bleed, aspect-ratio 4:3, subtekst verborgen.

**Tech Stack:** Vanilla HTML/CSS · WebP foto · Playwright voor visuele verificatie

---

## Context

- **Bestand:** `/Users/bartvandersterren/Projects/asteria-pages/wellness-arr-c.html`
- **Spec:** `docs/superpowers/specs/2026-05-18-diner-blok-design.md`
- **Invoegpunt HTML:** lijn 1577 — direct vóór `<!-- ══ FOOTER`
- **Invoegpunt CSS:** in de `<style>`-tag, ná de bestaande `.wp-section` styles (rond lijn 1290)
- **Primaire kleur:** `#c23435` | **Fonts:** Electrolize + Montserrat
- **Deploy:** `git push` → Cloudflare deployt automatisch → visit.asteria.nl/wellness-arr-c
- **Preview lokaal:** `python3 -m http.server 8765` vanuit `~/Projects/asteria-pages/`

---

## Task 1: Foto converteren naar WebP

**Files:**
- Add: `fotos/restaurant-sfeer.webp`

- [ ] **Stap 1: Converteer de foto**

```bash
cd ~/Projects/asteria-pages
cwebp -q 82 ~/Documents/Asteria\ Fotobank/P1046742.jpg -o fotos/restaurant-sfeer.webp
```

Verwacht output: `Saving file 'fotos/restaurant-sfeer.webp'` + bestandsgrootte.

- [ ] **Stap 2: Controleer het resultaat**

```bash
ls -lh fotos/restaurant-sfeer.webp
```

Verwacht: bestand bestaat, kleiner dan ~300KB.

---

## Task 2: CSS toevoegen

**Files:**
- Modify: `wellness-arr-c.html` (in de `<style>`-tag, ná de `.wp-section` block, rond lijn 1290)

- [ ] **Stap 1: Voeg de CSS toe**

Zoek in de `<style>`-tag naar de regel die begint met `</style>` (de sluitende tag van het stijlblok). Voeg het volgende toe direct daarvóór:

```css
/* ══════════════════════════════════════════════════════════
   DINER BLOK
══════════════════════════════════════════════════════════ */
.diner {
  background: #f0efed;
  padding: 40px 20px;
}

.diner__card {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  max-width: 960px;
  margin: 0 auto;
  min-height: 420px;
  border-radius: 20px;
  box-shadow: 0 8px 48px rgba(0,0,0,0.13);
}

.diner__bg {
  position: absolute;
  inset: 0;
  background-image: url('fotos/restaurant-sfeer.webp');
  background-size: cover;
  background-position: 70% center;
}

.diner__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(8,6,4,0.22) 0%, rgba(8,6,4,0.52) 100%);
}

.diner__content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 72px 48px;
  max-width: 520px;
  width: 100%;
}

.diner__eyebrow {
  font-family: 'Electrolize', sans-serif;
  font-size: 10px;
  letter-spacing: 0.26em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.6);
  display: block;
  margin-bottom: 14px;
}

.diner__title {
  font-family: 'Electrolize', sans-serif;
  font-size: clamp(28px, 4vw, 42px);
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #fff;
  line-height: 1.15;
  margin-bottom: 18px;
}

.diner__sub {
  font-family: 'Montserrat', sans-serif;
  font-size: 14px;
  font-weight: 300;
  color: rgba(255,255,255,0.68);
  line-height: 1.75;
  margin-bottom: 36px;
  max-width: 320px;
  margin-left: auto;
  margin-right: auto;
}

.diner__cta {
  display: inline-block;
  background: #c23435;
  color: #fff;
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.04em;
  text-decoration: none;
  padding: 14px 36px;
  border-radius: 8px;
  transition: background 200ms ease;
}

.diner__cta:hover { background: #a82c2c; }

@media (max-width: 768px) {
  .diner {
    padding: 0;
  }
  .diner__card {
    border-radius: 0;
    box-shadow: none;
    min-height: unset;
    aspect-ratio: 4/3;
    max-width: 100%;
  }
  .diner__content {
    padding: 24px 28px;
    max-width: 100%;
  }
  .diner__title {
    font-size: 22px;
    margin-bottom: 10px;
  }
  .diner__eyebrow {
    margin-bottom: 10px;
  }
  .diner__sub {
    display: none;
  }
  .diner__cta {
    font-size: 12px;
    padding: 11px 22px;
  }
}
```

---

## Task 3: HTML toevoegen

**Files:**
- Modify: `wellness-arr-c.html` lijn 1577 (direct vóór `<!-- ══ FOOTER`)

- [ ] **Stap 1: Voeg de HTML toe**

Zoek de regel `<!-- ══ FOOTER ════` (lijn ~1577) en plak het volgende er direct vóór:

```html
<!-- ══ DINER ════════════════════════════════════════════ -->
<section class="diner" aria-label="Drie-gangen diner — inbegrepen in het arrangement">
  <div class="diner__card">
    <div class="diner__bg" role="img" aria-label="Restaurant Hotel Asteria — intiem dineren met uitzicht op het groen"></div>
    <div class="diner__overlay"></div>
    <div class="diner__content">
      <span class="diner__eyebrow">Inbegrepen in het arrangement</span>
      <h2 class="diner__title">Een heerlijk<br>drie-gangen diner</h2>
      <p class="diner__sub">Na een avond in de wellness schuift u aan in ons restaurant. Vers bereid, seizoensgebonden, geen haast.</p>
      <a class="diner__cta"
         href="https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS"
         target="_blank"
         rel="noopener">Boek het arrangement</a>
    </div>
  </div>
</section>

```

---

## Task 4: Visueel testen

**Files:** geen wijzigingen

- [ ] **Stap 1: Start lokale server** (als nog niet actief)

```bash
cd ~/Projects/asteria-pages && python3 -m http.server 8765
```

- [ ] **Stap 2: Desktop screenshot (1440px)**

```js
// Playwright — browser_run_code_unsafe
await page.setViewportSize({ width: 1440, height: 900 });
await page.goto('http://localhost:8765/wellness-arr-c.html');
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await page.waitForTimeout(400);
```

Dan `browser_take_screenshot`. Controleer:
- Card gecentreerd, afgeronde hoeken zichtbaar
- Foto laadt (P1046742, ramen rechts)
- Witte tekst leesbaar over overlay
- Rode CTA zichtbaar

- [ ] **Stap 3: Mobile screenshot (375px)**

```js
await page.setViewportSize({ width: 375, height: 812 });
await page.goto('http://localhost:8765/wellness-arr-c.html');
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await page.waitForTimeout(400);
```

Dan `browser_take_screenshot`. Controleer:
- Blok full-bleed (geen witruimte links/rechts)
- Aspect-ratio ~4:3 (geen portrait)
- Subtekst NIET zichtbaar
- Titel + CTA passen zonder overflow

- [ ] **Stap 4: QA-check in console**

```js
// browser_run_code_unsafe
() => {
  const section = document.querySelector('.diner');
  const bg = document.querySelector('.diner__bg');
  const cta = document.querySelector('.diner__cta');
  const sub = document.querySelector('.diner__sub');
  return {
    sectionExists: !!section,
    bgHasImage: bg ? getComputedStyle(bg).backgroundImage !== 'none' : false,
    ctaHref: cta ? cta.href : null,
    subHiddenMobile: sub ? getComputedStyle(sub).display : null,
    ariaLabel: section ? section.getAttribute('aria-label') : null
  };
}
```

Verwacht bij 375px viewport: `subHiddenMobile: "none"`.

---

## Task 5: Commit en push

**Files:**
- `wellness-arr-c.html`
- `fotos/restaurant-sfeer.webp`

- [ ] **Stap 1: Commit**

```bash
cd ~/Projects/asteria-pages
git add wellness-arr-c.html fotos/restaurant-sfeer.webp
git commit -m "feat: diner sfeerblok — banner-card met restaurantfoto vóór footer"
```

- [ ] **Stap 2: Push**

```bash
git push
```

- [ ] **Stap 3: Wacht ~35 seconden, test live**

Open `https://visit.asteria.nl/wellness-arr-c` en scroll naar beneden. Controleer desktop én mobile.

