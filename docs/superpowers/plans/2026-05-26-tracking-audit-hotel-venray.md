# Tracking Audit & Fix — hotel-venray.html

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verifieer dat GA4, Google Ads conversies en D1 analytics correct werken op hotel-venray.html, en herstel de gevonden tracking-gaps.

**Architecture:** Twee fases: (1) audit via browser-tools + curl om te bevestigen wat werkt, (2) code-fix voor de tracking-gaps die de code-review al onthulde (ontbrekende `data-track-cta` op nav- en arrangement-CTAs).

**Tech Stack:** gtag.js (GA4 + Google Ads), Cloudflare D1 + `/api/track`, Playwright voor browser-verificatie, curl voor stats-API.

---

## Wat de code-review al laat zien

### ✅ Correct geconfigureerd (code-niveau)
- `gtag.js` laadt voor `AW-998609513` en `G-DPCP945DCG` met cross-domain linker
- `window.GA_ADS_LABEL = 'AW-998609513/t8vbCLm6i7IcEOmkltwD'`
- Conversion events (`gtag('event', 'conversion', ...)`) vuren op 3 correcte plekken: `btnToStep2` (kamer al geselecteerd → direct Mews), `btnDirectBook`, `btnConfirm`
- `popup_open` vuurt bij elke `openBookingPopup()` aanroep
- `page_view`, `step2_reached`, `mews_click`, `email_*` events correct geïmplementeerd

### ❌ Tracking-gaps (code-niveau)
- **Nav "Boek nu" buttons (2×)** — `onclick="window.openBookingPopup()"` maar **geen `data-track-cta`** → `cta_click` event wordt niet verzonden
- **Arrangement CTAs "Boek direct" (3×)** — zelfde probleem: `onclick` zonder `data-track-cta` → bron van popup-opens onbekend in analytics

---

## Files

- **Modify:** `hotel-venray.html`
  - Regel ~2651: nav `<button class="button book-now">` (desktop)
  - Regel ~2654: nav `<button class="button book-now">` (mobile)
  - Regel ~2944: arr-card L&O `<button class="arr-card__cta" id="bbCta">`
  - Regel ~2971: arr-card Wellness `<button class="arr-card__cta">`
  - Regel ~2998: arr-card Asperge `<button class="arr-card__cta">`

---

## Task 1: Controleer D1 events via stats-API

**Files:** geen wijzigingen

- [ ] **Stap 1: Haal huidige event-counts op**

```bash
curl "https://visit.asteria.nl/api/stats?summary=1"
```

Verwacht: JSON met event-tellingen per type. Als D1 werkt, zie je minimaal `page_view` met een count > 0.

- [ ] **Stap 2: Interpreteer de output**

Controleer of deze events aanwezig zijn (elk met count > 0):
- `page_view`
- `cta_click`
- `popup_open`
- `mews_click`

Als `page_view` ontbreekt of count = 0: D1 binding is kapot of pagina heeft geen verkeer gehad. Ga dan naar Task 2 voor browser-test.

Als `cta_click` wel telt maar de source-verdeling niet zichtbaar is: normaal, de stats-API toont alleen totalen. De gaps zijn bevestigd via code-review — ga verder naar Task 3.

---

## Task 2: Browser-test D1 tracking via Playwright

**Files:** geen wijzigingen

- [ ] **Stap 1: Open pagina en observeer netwerk**

```javascript
// Playwright browser_run_code_unsafe
await page.setViewportSize({ width: 1280, height: 800 });
await page.goto('https://visit.asteria.nl/hotel-venray');
await page.waitForTimeout(2000);

// Check of /api/track aangeroepen werd voor page_view
const requests = [];
page.on('request', req => {
  if (req.url().includes('/api/track')) requests.push(req.postData());
});
// Wacht nog even
await page.waitForTimeout(1000);
console.log('Track requests:', requests);
```

Verwacht: minimaal 1 request naar `/api/track` met `{"event":"page_view",...}`.

- [ ] **Stap 2: Klik een CTA aan en verifieer cta_click**

```javascript
// Na stap 1 — klik sticky FAB
await page.click('[data-track-cta="sticky_fab"]');
await page.waitForTimeout(500);
```

Verwacht: een tweede request naar `/api/track` met `{"event":"cta_click","cta":"sticky_fab",...}`.

- [ ] **Stap 3: Verifieer dat D1 de nieuwe event ontvangen heeft**

```bash
curl "https://visit.asteria.nl/api/stats?summary=1"
```

Count van `cta_click` moet 1 hoger zijn dan bij Task 1 Stap 1.

---

## Task 3: Verifieer GA4 in DebugView (handmatig, ~5 minuten)

**Files:** geen wijzigingen

- [ ] **Stap 1: Open GA4 DebugView**

Ga naar: Google Analytics → Property 262565995 → Admin → DebugView
(Of direct: analytics.google.com → jouw property → Beheer → DebugView)

- [ ] **Stap 2: Open hotel-venray met debug-parameter**

Open in browser:
```
https://visit.asteria.nl/hotel-venray?gtag_debug=1
```

Na ~5-10 seconden moeten events verschijnen in DebugView.

- [ ] **Stap 3: Controleer deze events**

Verifieer aanwezigheid in DebugView:
- `page_view` (automatisch door GA4 config)
- `session_start`

Als deze ontbreken: gtag.js laadt niet correct. Controleer browser-console op errors.

- [ ] **Stap 4: Test conversion event**

Klik in de browser op "Boek uw verblijf" (hero CTA), kies een datum, klik "Boek direct zonder kamerkeuze".

Verwacht in DebugView: `conversion` event met `send_to: AW-998609513/t8vbCLm6i7IcEOmkltwD`.

---

## Task 4: Fix — voeg `data-track-cta` toe aan ontbrekende CTAs

**Files:** Modify `hotel-venray.html`

- [ ] **Stap 1: Fix nav "Boek nu" desktop**

Zoek op (rond regel 2651):
```html
<button class="button book-now" onclick="window.openBookingPopup()">Boek nu</button>
```

Eerste instantie (desktop nav): vervang door:
```html
<button class="button book-now" data-track-cta="nav_desktop" onclick="window.openBookingPopup()">Boek nu</button>
```

- [ ] **Stap 2: Fix nav "Boek nu" mobile**

Tweede instantie (mobile nav, ~2 regels lager):
```html
<button class="button book-now" onclick="window.openBookingPopup()">Boek nu</button>
```

Vervang door:
```html
<button class="button book-now" data-track-cta="nav_mobile" onclick="window.openBookingPopup()">Boek nu</button>
```

- [ ] **Stap 3: Fix arr-card L&O CTA**

Zoek op (rond regel 2944):
```html
<button class="arr-card__cta" id="bbCta" onclick="window.openBookingPopup()">Boek direct</button>
```

Vervang door:
```html
<button class="arr-card__cta" id="bbCta" data-track-cta="arr_logies" onclick="window.openBookingPopup()">Boek direct</button>
```

- [ ] **Stap 4: Fix arr-card Wellness CTA**

Zoek op (rond regel 2971):
```html
<button class="arr-card__cta" onclick="window.openBookingPopup(null, '2026WELLNESS')">Boek direct</button>
```

Vervang door:
```html
<button class="arr-card__cta" data-track-cta="arr_wellness" onclick="window.openBookingPopup(null, '2026WELLNESS')">Boek direct</button>
```

- [ ] **Stap 5: Fix arr-card Asperge CTA**

Zoek op (rond regel 2998):
```html
<button class="arr-card__cta" onclick="window.openBookingPopup(null, 'ASPERGE')">Boek direct</button>
```

Vervang door:
```html
<button class="arr-card__cta" data-track-cta="arr_asperge" onclick="window.openBookingPopup(null, 'ASPERGE')">Boek direct</button>
```

- [ ] **Stap 6: Commit**

```bash
cd ~/Projects/asteria-pages
git add hotel-venray.html
git commit -m "fix: add data-track-cta to nav and arr-card CTAs for complete cta_click tracking"
git push
```

---

## Task 5: Verifieer de fix live

**Files:** geen wijzigingen

Na ~35 seconden (Cloudflare deploy):

- [ ] **Stap 1: Browser-test via Playwright — klik een arr-card CTA**

```javascript
await page.setViewportSize({ width: 1280, height: 800 });
await page.goto('https://visit.asteria.nl/hotel-venray');
await page.waitForTimeout(2000);

// Verifieer dat arr_wellness track request verstuurd wordt
const trackBodies = [];
page.on('request', req => {
  if (req.url().includes('/api/track')) trackBodies.push(JSON.parse(req.postData()));
});

// Klik op Wellness arr CTA
await page.click('[data-track-cta="arr_wellness"]');
await page.waitForTimeout(1000);
console.log('Track requests:', JSON.stringify(trackBodies, null, 2));
```

Verwacht: een request met `{"event":"cta_click","cta":"arr_wellness",...}`.

- [ ] **Stap 2: Controleer stats-API**

```bash
curl "https://visit.asteria.nl/api/stats?summary=1"
```

`cta_click` count moet hoger zijn dan vóór de fix.

---

## Samenvatting verwachte uitkomsten

| Check | Verwacht resultaat |
|---|---|
| D1 `page_view` count > 0 | ✅ D1 werkt |
| D1 `cta_click` wordt verzonden na sticky_fab klik | ✅ cta_click tracking werkt |
| GA4 DebugView toont `page_view` + `session_start` | ✅ GA4 ontvangt events |
| Conversion event verschijnt na datum kiezen + boek klik | ✅ Google Ads conversies werken |
| Na fix: `arr_wellness` cta_click in D1 | ✅ Arrangement CTAs getrackt |
