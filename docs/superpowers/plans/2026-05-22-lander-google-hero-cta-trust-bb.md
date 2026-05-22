# lander-google — Hero CTA+Trust merge & Logies/Ontbijt kaart

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** (1) Trust bar samenvoegen met de CTA in de hero; (2) Weekend arrangement vervangen door een Logies & Ontbijt kaart met dynamisch opgehaalde prijs via de Mews API.

**Architecture:** Beide wijzigingen zitten volledig in `lander-google.html`. Taak 1 is puur CSS/HTML: de absolute-positioned trust bar verdwijnt en de trust items komen als micro-strip direct onder de CTA. Taak 2 is HTML + JS: de Weekend kaart wordt Logies & Ontbijt, bij page load wordt via `fetch` de beschikbaarheidsprijs opgehaald voor de Comfort kamer (volgende dag, 1 nacht) en getoond als afgerond bedrag p.p.

**Tech Stack:** Vanilla HTML/CSS/JS, Mews distributor API via Cloudflare proxy (`/mews/api/distributor/v1/hotels/getAvailability`)

---

## Files

- Modify: `lander-google.html`
  - CSS sectie HERO: `.hero__trust-bar` display:none, nieuwe `.hero__trust-micro` stijlen
  - HTML hero sectie (~r2668): verwijder `.hero__trust-bar` div, voeg `.hero__trust-micro` toe binnen `.hero__content`
  - CSS sectie ARRANGEMENTEN: geen wijzigingen nodig
  - HTML arrangementen sectie (~r2919): vervang Weekend kaart door Logies & Ontbijt
  - JS IIFE arrangementen (~r4304): update `ARR_DATA.weekend` object naar `logiebb` data
  - Nieuwe JS IIFE onderaan: fetch Mews prijs + update kaart DOM

---

## Task 1: Hero CTA + Trust bar samenvoegen

**Files:**
- Modify: `lander-google.html` (CSS ~r247–r299, HTML ~r2661–r2681)

- [ ] **Stap 1: Verwijder de trust bar uit de HTML**

Zoek de sectie (rond r2668):
```html
  <div class="hero__trust-bar" aria-label="Kwaliteitsgaranties">
    <div class="hero__trust-card">
      ...
    </div>
  </div>
</section>
```
Vervang door:
```html
</section>
```
(De volledige `.hero__trust-bar` div eruit.)

- [ ] **Stap 2: Voeg trust micro-strip toe binnen hero__content**

Zoek (rond r2661):
```html
    <button
      class="hero__cta"
      onclick="window.openBookingPopup()"
      data-track-cta="hero"
    >Boek uw verblijf</button>
  </div>
```
Vervang door:
```html
    <button
      class="hero__cta"
      onclick="window.openBookingPopup()"
      data-track-cta="hero"
    >Boek uw verblijf</button>
    <div class="hero__trust-micro" aria-label="Kwaliteitsgaranties">
      <span class="hero__trust-micro-item">
        <span class="hero__trust-micro-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
        4,2 &nbsp;&middot;&nbsp; 2.219 reviews
      </span>
      <span class="hero__trust-micro-dot" aria-hidden="true"></span>
      <span class="hero__trust-micro-item">&#10003;&nbsp; Gratis annuleren</span>
      <span class="hero__trust-micro-dot" aria-hidden="true"></span>
      <span class="hero__trust-micro-item">&#10003;&nbsp; Laagste prijs</span>
    </div>
  </div>
```

- [ ] **Stap 3: Vervang de trust bar CSS door micro-strip CSS**

Zoek het blok `/* ── Trust bar ── */` (rond r247) en vervang het volledige blok t/m de afsluitende `}` van de mobile breakpoint (r299):

```css
    /* ── Trust micro-strip ── */
    .hero__trust-micro {
      display: flex;
      align-items: center;
      justify-content: center;
      flex-wrap: wrap;
      gap: 6px 16px;
      margin-top: 18px;
      font-family: 'Montserrat', sans-serif;
      font-size: 11px;
      font-weight: 500;
      color: rgba(255,255,255,0.60);
      animation: fadeUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.75s both;
    }
    .hero__trust-micro-stars {
      color: #f59e0b;
      font-size: 10px;
      letter-spacing: 0.5px;
      margin-right: 2px;
    }
    .hero__trust-micro-item {
      display: flex;
      align-items: center;
      white-space: nowrap;
    }
    .hero__trust-micro-dot {
      width: 3px;
      height: 3px;
      border-radius: 50%;
      background: rgba(255,255,255,0.28);
      flex-shrink: 0;
    }
    @media (max-width: 600px) {
      .hero__trust-micro { font-size: 10px; gap: 4px 10px; margin-top: 14px; }
      .hero__trust-micro-dot { display: none; }
    }
```

- [ ] **Stap 4: Pas hero padding aan**

De hero had `padding-bottom: 80px` voor de absolute trust bar. Verander dit:

Zoek (rond r148):
```css
    .hero {
      ...
      padding-top: 90px;
      padding-bottom: 80px;
    }
```
Verander `padding-bottom: 80px;` → `padding-bottom: 56px;`

En de mobile override (rond r305):
```css
    @media (max-width: 600px) {
      .hero { min-height: 100svh; padding-bottom: 60px; }
```
Verander `padding-bottom: 60px;` → `padding-bottom: 40px;`

- [ ] **Stap 5: Verwijder ook de prefers-reduced-motion referentie naar hero__trust-bar**

Zoek (rond r302):
```css
      .hero__content *, .hero__trust-bar { animation: none; opacity: 1; transform: none; transition: none; }
```
Vervang door:
```css
      .hero__content * { animation: none; opacity: 1; transform: none; transition: none; }
```

- [ ] **Stap 6: Screenshot via Playwright (mockup verificatie)**

```javascript
await page.setViewportSize({ width: 1280, height: 800 });
await page.goto('http://localhost:8788/lander-google');
await page.waitForTimeout(1200);
// screenshot desktop hero
```

```javascript
await page.setViewportSize({ width: 375, height: 812 });
await page.goto('http://localhost:8788/lander-google');
await page.waitForTimeout(1200);
// screenshot mobile hero
```

Controleer: trust items zichtbaar direct onder de rode CTA knop, geen witte kaart onderaan. Ziet het er netjes uit? Zo ja, door naar stap 7.

- [ ] **Stap 7: Commit**

```bash
git add lander-google.html
git commit -m "feat: hero trust micro-strip — trust items direct onder CTA"
```

---

## Task 2: Logies & Ontbijt kaart met dynamische prijs

**Files:**
- Modify: `lander-google.html` (HTML ~r2919–r2943, JS ~r4295–r4320, nieuw JS IIFE)

### Stap 2A: HTML Weekend kaart vervangen

- [ ] **Stap 1: Vervang de Weekend kaart HTML**

Zoek de eerste `.arr-card` div (r2919–r2943):
```html
      <div class="arr-card">
        <div class="arr-card__photo">
          ...
        </div>
        <div class="arr-card__body">
          <p class="arr-card__eyebrow">Weekendje weg</p>
          <h3 class="arr-card__title">Weekend</h3>
          ...
          <a class="arr-card__cta" href="...mewsVoucherCode=WEEKEND" ...>Boek direct</a>
          <button class="arr-card__more" data-arr="weekend">Meer informatie →</button>
        </div>
      </div>
```

Vervang door:
```html
      <div class="arr-card arr-card--bb" id="arrBbCard">
        <div class="arr-card__photo">
          <img src="fotos/kamer-comfort.webp" alt="Comfort Kamer Hotel Asteria" loading="lazy">
          <div class="arr-card__photo-overlay"></div>
          <div class="arr-card__photo-bottom"></div>
        </div>
        <div class="arr-card__body">
          <p class="arr-card__eyebrow">Lekker uitslapen</p>
          <h3 class="arr-card__title">Logies &amp; Ontbijt</h3>
          <p class="arr-card__tagline">Gewoon goed slapen — met een uitgebreid ontbijt de volgende ochtend</p>
          <div class="arr-card__price-row">
            <span class="arr-card__price" id="bbPrice">Laden&hellip;</span>
            <span class="arr-card__price-unit" id="bbPriceUnit">p.p. · 1 nacht</span>
          </div>
          <div class="arr-card__divider"></div>
          <p class="arr-card__includes-label">Highlights</p>
          <div class="arr-card__feature"><div class="arr-card__dot"></div><span class="arr-card__feat-text">Comfort Kamer voor 2 personen</span></div>
          <div class="arr-card__feature"><div class="arr-card__dot"></div><span class="arr-card__feat-text">Uitgebreid ontbijtbuffet inbegrepen</span></div>
          <div class="arr-card__feature"><div class="arr-card__dot"></div><span class="arr-card__feat-text">Gratis parkeren &amp; WiFi</span></div>
          <a class="arr-card__cta" id="bbCta" href="https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556?mewsRoute=rooms" target="_blank" rel="noopener">Boek direct</a>
          <button class="arr-card__more" data-arr="logiebb">Meer informatie →</button>
        </div>
      </div>
```

- [ ] **Stap 2: Update ARR_DATA in JS IIFE**

Zoek het `ARR_DATA` object (~r4295). Zoek het `weekend` key-blok:
```javascript
      weekend: {
        title: 'Weekend Aanbieding',
        ...
        url: 'https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556?mewsVoucherCode=WEEKEND'
      },
```

Vervang door:
```javascript
      logiebb: {
        title: 'Logies & Ontbijt',
        eyebrow: 'Lekker uitslapen',
        tagline: 'Gewoon goed slapen — met een uitgebreid ontbijt de volgende ochtend',
        photo: 'fotos/kamer-comfort.webp',
        price: null,
        priceUnit: 'p.p. · 1 nacht',
        includes: [
          'Comfort Kamer voor 2 personen',
          'Uitgebreid ontbijtbuffet inbegrepen',
          'Gratis parkeren & WiFi'
        ],
        highlights: [],
        hint: 'Kies uw datum en kamer rechtstreeks in de booking engine.',
        url: 'https://app.mews.com/distributor/6dc9094c-76e3-4fd8-83a7-af1d00ffc556?mewsRoute=rooms'
      },
```

- [ ] **Stap 3: Mobile CSS order aanpassen**

Zoek (~r2589–r2591):
```css
  .arr-card:nth-child(1) { order: 3; } /* Weekend → laatste */
  .arr-card:nth-child(2) { order: 1; } /* Wellness → eerste */
  .arr-card:nth-child(3) { order: 2; } /* Asperge → tweede */
```

Verander de comment, logica blijft hetzelfde:
```css
  .arr-card:nth-child(1) { order: 3; } /* L&O → laatste */
  .arr-card:nth-child(2) { order: 1; } /* Wellness → eerste */
  .arr-card:nth-child(3) { order: 2; } /* Asperge → tweede */
```

### Stap 2B: Dynamische prijs ophalen

- [ ] **Stap 4: Voeg BB prijs-fetch IIFE toe**

Voeg onderaan het `<script>` blok van de arrangementen IIFE (of als apart script vóór `</body>`) toe:

```javascript
(function() {
  var COMFORT_CATEGORY_ID = '98900f3b-e5e2-49c9-9776-af1d00ffc315';

  function nextDate(offsetDays) {
    var d = new Date();
    d.setDate(d.getDate() + offsetDays);
    return d;
  }

  function toYMD(d) {
    var mm = d.getMonth() + 1;
    var dd = d.getDate();
    return d.getFullYear() + '-' + (mm < 10 ? '0' : '') + mm + '-' + (dd < 10 ? '0' : '') + dd;
  }

  function ceilHalf(price) {
    // Afronden naar boven op €0,50 (bijv. 55.67 → 56.00, 55.25 → 55.50)
    return Math.ceil(price * 2) / 2;
  }

  function formatEuro(amount) {
    // €56,– of €55,50
    var whole = Math.floor(amount);
    var cents = Math.round((amount - whole) * 100);
    if (cents === 0) return '\u20AC\u00A0' + whole + ',\u2013';
    return '\u20AC\u00A0' + whole + ',' + (cents < 10 ? '0' : '') + cents;
  }

  function updateCard(pricePerPerson) {
    var el = document.getElementById('bbPrice');
    var unitEl = document.getElementById('bbPriceUnit');
    if (el) el.textContent = 'vanaf ' + formatEuro(pricePerPerson);
    if (unitEl) unitEl.textContent = 'p.p. \u00B7 1 nacht';
  }

  function fetchBbPrice() {
    // Haal 30 nachten op → geeft per nacht pricing → toon de laagste beschikbare prijs
    var checkin = nextDate(1);
    var checkout = nextDate(31);

    fetch('/mews/api/distributor/v1/hotels/getAvailability', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        Client: 'Asteria Pages 1.0.0',
        ConfigurationId: '6dc9094c-76e3-4fd8-83a7-af1d00ffc556',
        HotelId: '65a522c9-4828-413d-9ad8-af1d00ffb83f',
        StartUtc: toYMD(checkin) + 'T12:00:00Z',
        EndUtc: toYMD(checkout) + 'T12:00:00Z',
        CategoryIds: [COMFORT_CATEGORY_ID]
      })
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
      var avails = data.RoomCategoryAvailabilities || [];
      var comfort = avails.find(function(a) { return a.RoomCategoryId === COMFORT_CATEGORY_ID; });
      if (!comfort) { showFallback(); return; }

      // Probeer 2-persoons occupancy (index 1), anders 1-persoons (index 0)
      var occList = comfort.RoomOccupancyAvailabilities || [];
      var occ = occList.length > 1 ? occList[1] : occList[0];
      if (!occ || !occ.Pricing || !occ.Pricing.length) { showFallback(); return; }

      // Pricing is een array met één entry per nacht in de gevraagde periode.
      // Zoek de laagste GrossValue over alle beschikbare nachten.
      var lowestRoom = null;
      occ.Pricing.forEach(function(p) {
        var v = p.Price && p.Price.GrossValue;
        if (v != null && (lowestRoom === null || v < lowestRoom)) {
          lowestRoom = v;
        }
      });
      if (lowestRoom === null) { showFallback(); return; }

      // Bepaal of dit een kamerprijs of p.p.-prijs is:
      // De Mews distributor API geeft typisch een kamerprijs (voor N personen).
      // Voor 2-persoons occupancy: deel door 2 voor p.p.
      // Voor 1-persoons occupancy (fallback): dat is al p.p.
      var ppPrice = occList.length > 1 ? lowestRoom / 2 : lowestRoom;
      ppPrice = ceilHalf(ppPrice);
      updateCard(ppPrice);
    })
    .catch(function() { showFallback(); });
  }

  function showFallback() {
    var el = document.getElementById('bbPrice');
    if (el) el.textContent = 'Vraag prijs op';
    var unitEl = document.getElementById('bbPriceUnit');
    if (unitEl) unitEl.textContent = '1 nacht · 2 personen';
  }

  // Start fetch zodra DOM gereed is
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fetchBbPrice);
  } else {
    fetchBbPrice();
  }
})();
```

- [ ] **Stap 5: Lokaal testen**

Start de dev server:
```bash
cd ~/Projects/asteria-pages && npx wrangler pages dev . --port 8788
```

Open `http://localhost:8788/lander-google` en controleer:
1. "Laden..." verdwijnt en wordt vervangen door een bedrag (bijv. "vanaf € 89,–")
2. Browser DevTools → Network: check de `/mews/api/distributor/v1/hotels/getAvailability` response — log `grossValue` en het aantal `RoomOccupancyAvailabilities` items om te bevestigen of deling door 2 correct is
3. Prijs heeft geen decimalen zoals €55,67 — alleen hele euros of .50 cent

Als de prijs onrealistisch is (bijv. €5,– of €500,–): open DevTools Console en log de ruwe API response:
```javascript
// Plak in console:
fetch('/mews/api/distributor/v1/hotels/getAvailability', {
  method: 'POST',
  headers: {'Content-Type':'application/json'},
  body: JSON.stringify({
    Client:'test', ConfigurationId:'6dc9094c-76e3-4fd8-83a7-af1d00ffc556',
    HotelId:'65a522c9-4828-413d-9ad8-af1d00ffb83f',
    StartUtc: new Date(Date.now()+86400000).toISOString().slice(0,10)+'T12:00:00Z',
    EndUtc: new Date(Date.now()+86400000*31).toISOString().slice(0,10)+'T12:00:00Z',
    CategoryIds:['98900f3b-e5e2-49c9-9776-af1d00ffc315']
  })
}).then(r=>r.json()).then(d=>console.log(JSON.stringify(d,null,2)));
```
Pas `ppPrice` logica aan als nodig.

- [ ] **Stap 6: Screenshot mobile + desktop**

```javascript
// Desktop
await page.setViewportSize({ width: 1280, height: 900 });
await page.goto('http://localhost:8788/lander-google');
await page.waitForTimeout(2000); // wacht op API fetch
await page.evaluate(() => document.getElementById('arrBbCard').scrollIntoView());
// screenshot
```

```javascript
// Mobile
await page.setViewportSize({ width: 375, height: 812 });
await page.goto('http://localhost:8788/lander-google');
await page.waitForTimeout(2000);
// screenshot
```

- [ ] **Stap 7: Commit & push**

```bash
git add lander-google.html
git commit -m "feat: logies & ontbijt kaart — dynamische Mews prijs, vervangt weekend arrangement"
git push
```

Na ~35 sec live testen op `https://visit.asteria.nl/lander-google`.

---

## Self-review

**Spec coverage:**
- [x] Trust bar samenvoegen met CTA in hero → Taak 1
- [x] Mockup stap opgenomen → Stap 6 van Taak 1 (Playwright screenshot vóór commit)
- [x] Weekend arrangement vervangen door Logies & Ontbijt → Taak 2
- [x] Dynamische prijs via Mews API → Stap 2B
- [x] Netjes afronden (geen €55,67) → `ceilHalf()` functie
- [x] Mobile CSS order bijgewerkt → Stap 3
- [x] ARR_DATA popup data bijgewerkt → Stap 2

**Placeholder scan:** Geen TBD of vage instructies — alle code volledig uitgeschreven.

**Type consistency:** `bbPrice`, `bbPriceUnit`, `bbCta` ID's consistent in HTML en JS. `logiebb` key consistent in `data-arr` attribuut en `ARR_DATA`.
