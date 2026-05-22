# Booking Popup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Voeg een 2-staps booking popup toe aan `wellness-arr-c.html` die datum + kamer verzamelt en de bezoeker via een Mews deeplink naar de juiste beschikbaarheidspagina stuurt.

**Architecture:** Alle code (HTML, CSS, JS) zit in één bestand `wellness-arr-c.html`. De popup is een nieuw overlay-element dat naast de bestaande `room-popup-overlay` wordt geplaatst. Flatpickr (range mode) verzorgt de datumpicker. Een IIFE-module beheert de volledige popup-state.

**Tech Stack:** Vanilla JS (ES5-compatibel, conform bestaande code), Flatpickr 4.x (CDN), CSS transitions (conform bestaande animatiestijl)

---

## Bestandskaart

Alle wijzigingen zitten in één bestand:

| Locatie in bestand | Wat verandert |
|---|---|
| `<head>` (na regel 9) | Flatpickr CSS CDN link |
| `</body>` vóór laatste `</script>` | Flatpickr JS CDN script |
| `ROOMS` object (regel 2718–2761) | `mewsCategoryId` + `shortDesc` toevoegen per kamer |
| Na regel 2761 (na ROOMS definitie) | `window.selectedRoomId = null` initialisatie |
| `openPopup()` functie (regel 2777) | `window.selectedRoomId = key` instellen bij openen kamerpopup |
| Na `<!-- Kamerpopup -->` div (regel 2231) | Nieuw `#bookingPopup` overlay HTML |
| `<style>` sectie | `.booking-popup-*` CSS (stap 1 + stap 2) |
| Onderaan `<script>` sectie | Nieuwe booking popup IIFE |
| Sticky FAB `<a>` (regel 1761–1773) | Omzetten naar `<button>` |
| Sticky card btn `<a>` (regel 1779–1784) | Omzetten naar `<button>` |
| Hero CTA `<a>` (regel 1843–1848) | Omzetten naar `<button>` |
| Arr-c CTA `<a>` (regel 2053–2065) | Omzetten naar `<button>` |
| Diner CTA `<a>` (regel 2242–2245) | Omzetten naar `<button>` |
| `room-popup__cta` in `openPopup()` JS (regel 2809) | `<a>` vervangen door `<button>` met data-key |

---

## Task 1: ROOMS data uitbreiden + selectedRoomId state

**Files:**
- Modify: `wellness-arr-c.html:2718-2761` (ROOMS object)
- Modify: `wellness-arr-c.html:2777` (openPopup functie)

- [ ] **Stap 1: Voeg `mewsCategoryId` en `shortDesc` toe aan elk ROOMS-object**

Vervang het volledige `var ROOMS = { ... };` blok (regels 2718–2761):

```javascript
var ROOMS = {
  'comfort': {
    badge: '<span class="room-row__badge badge--included">Standaard inbegrepen</span>',
    name: 'Comfort Kamer',
    imgs: ['fotos/kamer-comfort.webp'],
    desc: 'Een comfortabele kamer voor twee personen met alles wat u nodig hebt voor een ontspannen verblijf.',
    features: ['~22 m²', 'Tweepersoons bed', 'Douche', 'Zithoek', 'Airco', 'WiFi'],
    upgrade: 'basis',
    shortDesc: '~22 m\u00b2 \u00b7 tweepersoons bed \u00b7 douche',
    mewsCategoryId: '98900f3b-e5e2-49c9-9776-af1d00ffc315'
  },
  'royale': {
    badge: '<span class="room-row__badge badge--upgrade">Upgrade</span>',
    name: 'Royale Kamer',
    imgs: ['fotos/kamer-royale.webp', 'fotos/kamer-royale-2.webp', 'fotos/kamer-royale-3.webp'],
    desc: 'Meer ruimte om te ademen \u2014 en de keuze voor een bad als u na de wellness ook op de kamer wilt ontspannen.',
    features: ['Ruimer dan Comfort', 'Bad of douche', 'Zithoek', 'Koffiezetapparaat', 'Airco'],
    upgrade: '+\u20ac10 p.p.',
    shortDesc: 'Ruimer \u00b7 bad of douche \u00b7 koffiezetapparaat',
    mewsCategoryId: 'a8fd7310-0d61-422f-89e6-af1d00ffc315'
  },
  'deluxe': {
    badge: '<span class="room-row__badge badge--sauna">+ Eigen sauna</span>',
    name: 'Deluxe Kamer',
    imgs: ['fotos/kamer-deluxe.webp', 'fotos/kamer-deluxe-2.webp', 'fotos/kamer-deluxe-3.webp'],
    desc: 'Een priv\u00e9 infraroodsauna op de kamer. Wellness begint bij u aan de deur \u2014 geen gedeelde ruimte.',
    features: ['Eigen infraroodsauna', 'Meer ruimte', 'Dubbel bed', 'Douche', 'Zithoek', 'Koffiezetapparaat', 'Airco'],
    upgrade: '+\u20ac20 p.p.',
    shortDesc: '~25 m\u00b2 \u00b7 priv\u00e9 infraroodsauna \u00b7 kingsize bed',
    mewsCategoryId: 'c737de50-e41e-4c8d-a818-af1d00ffc315'
  },
  'junior-suite': {
    badge: '<span class="room-row__badge badge--upgrade">Upgrade</span>',
    name: 'Junior Suite',
    imgs: ['fotos/kamer-junior-suite.webp', 'fotos/kamer-junior-suite-2.webp'],
    desc: 'Het extra formaat dat een wellness-avond \u00e9cht luxe maakt: kingsize bed, een bad en een ruime zithoek.',
    features: ['Kingsize bed', 'Bad', 'Ruime zithoek met slaapbank', 'Koelkastje', 'Koffiezetapparaat', 'Airco'],
    upgrade: '+\u20ac30 p.p.',
    shortDesc: 'Kingsize bed \u00b7 bad \u00b7 ruime zithoek',
    mewsCategoryId: '27ea8deb-ded5-4856-8fdd-af1d00ffc315'
  },
  'suite': {
    badge: '<span class="room-row__badge badge--sauna">+ Eigen sauna</span>',
    name: 'Suite',
    imgs: ['fotos/kamer-suite.webp', 'fotos/kamer-suite-2.webp', 'fotos/kamer-suite-3.webp'],
    desc: 'Het beste van beide werelden: een ruime suite met eigen infraroodsauna \u00e9n toegang tot het gedeelde wellness-centrum.',
    features: ['Kingsize bed', 'Eigen infraroodsauna', 'Ruime zithoek met slaapbank', 'Koelkastje', 'Airco'],
    upgrade: '+\u20ac40 p.p.',
    shortDesc: 'Kingsize bed \u00b7 eigen infraroodsauna \u00b7 ruime suite',
    mewsCategoryId: '4a642b66-68e6-444c-beeb-af1d00ffc315'
  },
  'bruidssuite': {
    badge: '<span class="room-row__badge badge--premium">Premium</span>',
    name: 'Bruidssuite',
    imgs: ['fotos/kamer-bruidssuite.webp', 'fotos/kamer-bruidssuite-2.webp', 'fotos/kamer-bruidssuite-3.webp'],
    desc: 'Vrijstaand bad, ruime inloopdouche en de meest romantische sfeer van het hotel. Voor een onvergetelijke avond.',
    features: ['Kingsize bed', 'Vrijstaand bad', 'Ruime inloopdouche', 'Zithoek', 'Koelkastje', 'Airco'],
    upgrade: '+\u20ac60 p.p.',
    shortDesc: 'Kingsize bed \u00b7 vrijstaand bad \u00b7 romantische sfeer',
    mewsCategoryId: 'a9f18d18-561b-47a9-8ba7-b2a800cfd0e2'
  }
};
```

- [ ] **Stap 2: Voeg `window.selectedRoomId` toe direct na het ROOMS object (na regel 2761)**

```javascript
// Bijhouden welke kamer de gast via de kamerpopup heeft bekeken
window.selectedRoomId = null;
```

- [ ] **Stap 3: Stel `window.selectedRoomId` in bij het openen van de kamerpopup**

In de `openPopup(key)` functie (regel 2777), voeg toe als eerste regel in de functie body:

```javascript
function openPopup(key) {
    window.selectedRoomId = key;   // ← nieuw
    var r = ROOMS[key];
    // ... rest ongewijzigd
```

- [ ] **Stap 4: Reset `window.selectedRoomId` bij het sluiten van de kamerpopup**

Zoek de `closePopup` functie (zoek op `function closePopup`). Voeg toe:

```javascript
function closePopup() {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
    window.selectedRoomId = null;   // ← nieuw
}
```

- [ ] **Stap 5: Verificeer — open browser, klik op een kamertype, check in console: `window.selectedRoomId` geeft de kamernaam. Sluit popup, check: `window.selectedRoomId` is `null`.**

- [ ] **Stap 6: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: booking-popup — ROOMS uitbreiden met mewsCategoryId + selectedRoomId state"
```

---

## Task 2: Flatpickr dependency + booking popup HTML

**Files:**
- Modify: `wellness-arr-c.html` — `<head>` sectie (Flatpickr CSS)
- Modify: `wellness-arr-c.html` — vlak boven `</body>` (Flatpickr JS)
- Modify: `wellness-arr-c.html` — na `<!-- Kamerpopup -->` div (popup HTML)

- [ ] **Stap 1: Voeg Flatpickr CSS toe in `<head>` (na de bestaande `<link rel="preload">` regel)**

```html
<!-- Flatpickr date picker -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
```

- [ ] **Stap 2: Voeg Flatpickr JS toe vlak vóór de sluitende `</body>` tag (vóór de bestaande `<script>` blok)**

```html
<script src="https://cdn.jsdelivr.net/npm/flatpickr" defer></script>
```

- [ ] **Stap 3: Voeg booking popup HTML toe direct ná de `<!-- Kamerpopup -->` div (na de regel `</div>` op ~regel 2231)**

```html
<!-- ══ BOOKING POPUP ════════════════════════════════════════ -->
<div class="bk-overlay" id="bookingPopup" role="dialog" aria-modal="true" aria-label="Verblijf boeken">
  <div class="bk-modal" id="bookingModal">

    <!-- Stap 1: Datum kiezen -->
    <div class="bk-step" id="bkStep1">
      <button class="bk-close" id="bkClose" aria-label="Sluiten">&times;</button>
      <div class="bk-step-indicator" aria-hidden="true">
        <span class="bk-dot bk-dot--active"></span>
        <span class="bk-dot"></span>
      </div>
      <h2 class="bk-title">Kies uw verblijfsdata</h2>
      <div id="bkCalendar"></div>
      <div class="bk-summary" id="bkSummary" aria-live="polite">
        <div class="bk-summary__field">
          <span class="bk-summary__label">Aankomst</span>
          <span class="bk-summary__value" id="bkAankomst">&mdash;</span>
        </div>
        <div class="bk-summary__sep" aria-hidden="true"></div>
        <div class="bk-summary__field">
          <span class="bk-summary__label">Vertrek</span>
          <span class="bk-summary__value" id="bkVertrek">&mdash;</span>
        </div>
        <div class="bk-summary__sep" aria-hidden="true"></div>
        <div class="bk-summary__field">
          <span class="bk-summary__label">Nachten</span>
          <span class="bk-summary__value" id="bkNachten">&mdash;</span>
        </div>
      </div>
      <div class="bk-cta-row">
        <button class="bk-btn-primary" id="bkToStep2" disabled>Volgende: kies kamer &rarr;</button>
        <button class="bk-btn-ghost" id="bkDirectBook">Of boek direct zonder kamerkeuze</button>
      </div>
    </div>

    <!-- Stap 2: Kamer kiezen -->
    <div class="bk-step" id="bkStep2" hidden>
      <button class="bk-back" id="bkBack" aria-label="Terug naar datumkeuze">&larr; Aanpassen</button>
      <div class="bk-step-indicator" aria-hidden="true">
        <span class="bk-dot"></span>
        <span class="bk-dot bk-dot--active"></span>
      </div>
      <h2 class="bk-title">Kies uw kamer</h2>
      <div class="bk-rooms" id="bkRooms" role="radiogroup" aria-label="Kamertype kiezen"></div>
      <div class="bk-cta-row">
        <button class="bk-btn-primary" id="bkConfirm">Bekijk beschikbaarheid &rarr;</button>
      </div>
    </div>

  </div>
</div>
```

- [ ] **Stap 4: Verificeer dat de HTML correct is toegevoegd — laad de pagina en controleer dat er geen console errors zijn. De popup is nog niet zichtbaar (overlay heeft `display:none` nog niet, maar is nog niet `is-open`).**

- [ ] **Stap 5: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: booking-popup — Flatpickr CDN + popup HTML structuur"
```

---

## Task 3: Booking popup CSS

**Files:**
- Modify: `wellness-arr-c.html` — `<style>` sectie, toevoegen aan het einde vóór `</style>`

- [ ] **Stap 1: Voeg alle booking popup CSS toe aan het einde van het `<style>` blok**

```css
/* ══════════════════════════════════════════════════════════
   BOOKING POPUP
══════════════════════════════════════════════════════════ */

/* ── Overlay ── */
.bk-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.55);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
}
.bk-overlay.is-open {
  opacity: 1;
  pointer-events: auto;
}

/* ── Modal ── */
.bk-modal {
  background: #fff;
  border-radius: 20px 20px 0 0;
  width: 100%;
  max-width: 480px;
  max-height: 92vh;
  overflow-y: auto;
  padding: 28px 24px 32px;
  transform: translateY(40px);
  transition: transform 0.3s cubic-bezier(0.16,1,0.3,1);
}
.bk-overlay.is-open .bk-modal {
  transform: translateY(0);
}

@media (min-width: 600px) {
  .bk-overlay {
    align-items: center;
  }
  .bk-modal {
    border-radius: 20px;
    max-height: 88vh;
  }
}

/* ── Sluit & terug knoppen ── */
.bk-close {
  position: absolute;
  top: 16px;
  right: 20px;
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  line-height: 1;
  padding: 4px;
}
.bk-close:hover { color: #0f172a; }

.bk-back {
  background: none;
  border: none;
  font-family: 'Montserrat', sans-serif;
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.bk-back:hover { color: #0f172a; }

/* ── Stap indicator ── */
.bk-step-indicator {
  display: flex;
  gap: 6px;
  justify-content: center;
  margin-bottom: 16px;
}
.bk-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #e5e7eb;
}
.bk-dot--active { background: #c23435; }

/* ── Titel ── */
.bk-title {
  font-family: 'Electrolize', sans-serif;
  font-size: 18px;
  font-weight: 400;
  color: #1a1a1a;
  margin: 0 0 20px;
  text-align: center;
}

/* ── Flatpickr overrides ── */
#bkCalendar .flatpickr-calendar {
  box-shadow: none;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  width: 100%;
}
.flatpickr-day.selected,
.flatpickr-day.startRange,
.flatpickr-day.endRange {
  background: #c23435 !important;
  border-color: #c23435 !important;
}
.flatpickr-day.inRange {
  background: #fde8e8 !important;
  border-color: #fde8e8 !important;
  box-shadow: -5px 0 0 #fde8e8, 5px 0 0 #fde8e8;
}
.flatpickr-day.today { border-color: #c23435; }

/* ── Bevestigingsbalk ── */
.bk-summary {
  display: flex;
  align-items: center;
  gap: 0;
  background: #f8f7f5;
  border-radius: 12px;
  padding: 14px 16px;
  margin: 16px 0;
}
.bk-summary__field {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.bk-summary__sep {
  width: 1px;
  height: 32px;
  background: #e5e7eb;
}
.bk-summary__label {
  font-family: 'Montserrat', sans-serif;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #9ca3af;
}
.bk-summary__value {
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  font-weight: 700;
  color: #1a1a1a;
}

/* ── CTA rij ── */
.bk-cta-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 4px;
}
.bk-btn-primary {
  background: #c23435;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-family: 'Montserrat', sans-serif;
  font-size: 14px;
  font-weight: 700;
  padding: 14px 20px;
  cursor: pointer;
  transition: background 200ms ease;
  width: 100%;
}
.bk-btn-primary:hover:not(:disabled) { background: #a82c2c; }
.bk-btn-primary:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}
.bk-btn-ghost {
  background: none;
  border: none;
  font-family: 'Montserrat', sans-serif;
  font-size: 12px;
  color: #6b7280;
  text-decoration: underline;
  cursor: pointer;
  padding: 4px 0;
  text-align: center;
}
.bk-btn-ghost:hover { color: #1a1a1a; }

/* ── Kamerkeuze cards (stap 2) ── */
.bk-rooms {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  max-height: 360px;
  overflow-y: auto;
}
.bk-room-card {
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 200ms ease;
}
.bk-room-card.is-selected {
  border-color: #c23435;
  background: #fff8f8;
}
.bk-room-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  gap: 8px;
}
.bk-room-card__name {
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  font-weight: 700;
  color: #1a1a1a;
  flex: 1;
}
.bk-room-card__upgrade {
  font-family: 'Montserrat', sans-serif;
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
}
.bk-room-card.is-selected .bk-room-card__upgrade { color: #c23435; }
.bk-room-card__toggle {
  background: none;
  border: none;
  font-size: 11px;
  color: #9ca3af;
  cursor: pointer;
  padding: 2px 4px;
  flex-shrink: 0;
}
.bk-room-card__toggle:hover { color: #1a1a1a; }
.bk-room-card__details {
  font-family: 'Montserrat', sans-serif;
  font-size: 12px;
  color: #6b7280;
  padding: 0 14px 12px;
  display: none;
}
.bk-room-card__details.is-open { display: block; }

/* ── Radio indicator ── */
.bk-room-card__radio {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid #d1d5db;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 200ms;
}
.bk-room-card.is-selected .bk-room-card__radio {
  border-color: #c23435;
}
.bk-room-card__radio::after {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: transparent;
  transition: background 200ms;
}
.bk-room-card.is-selected .bk-room-card__radio::after {
  background: #c23435;
}

/* ── Stap animatie ── */
.bk-step[hidden] { display: none; }
```

- [ ] **Stap 2: Verifieer in browser — laad pagina, open DevTools, zoek `#bookingPopup` element. Styles zijn geladen. Geen layout-errors zichtbaar.**

- [ ] **Stap 3: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: booking-popup — CSS volledig"
```

---

## Task 4: JS core — buildBookingUrl, open/close, stap 1 flatpickr

**Files:**
- Modify: `wellness-arr-c.html` — onderaan het `<script>` blok (vóór de afsluitende `</script>` tag)

- [ ] **Stap 1: Voeg de booking popup IIFE toe onderaan het script blok**

Voeg het volgende toe als laatste blok vóór `</script>`:

```javascript
/* ══ BOOKING POPUP ══════════════════════════════════════════ */
(function () {
  var MEWS_BASE = 'https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76';
  var VOUCHER   = 'WELLNESS';

  var overlay   = document.getElementById('bookingPopup');
  var modal     = document.getElementById('bookingModal');
  var step1     = document.getElementById('bkStep1');
  var step2     = document.getElementById('bkStep2');
  var btnClose  = document.getElementById('bkClose');
  var btnBack   = document.getElementById('bkBack');
  var btnToStep2    = document.getElementById('bkToStep2');
  var btnDirectBook = document.getElementById('bkDirectBook');
  var btnConfirm    = document.getElementById('bkConfirm');
  var elAankomst = document.getElementById('bkAankomst');
  var elVertrek  = document.getElementById('bkVertrek');
  var elNachten  = document.getElementById('bkNachten');
  var elRooms    = document.getElementById('bkRooms');

  var selectedDates = [];   // [Date aankomst, Date vertrek]
  var selectedRoomKey = null; // kamersleutel voor stap 2

  var DAYS_NL = ['zo','ma','di','wo','do','vr','za'];
  var MONTHS_NL = ['jan','feb','mrt','apr','mei','jun','jul','aug','sep','okt','nov','dec'];

  function formatDate(d) {
    return DAYS_NL[d.getDay()] + ' ' + d.getDate() + ' ' + MONTHS_NL[d.getMonth()];
  }

  function toYMD(d) {
    var mm = d.getMonth() + 1;
    var dd = d.getDate();
    return d.getFullYear() + '-' + (mm < 10 ? '0' : '') + mm + '-' + (dd < 10 ? '0' : '') + dd;
  }

  function buildBookingUrl(checkin, checkout, roomKey) {
    var url = MEWS_BASE + '?mewsVoucherCode=' + VOUCHER
      + '&mewsStart=' + toYMD(checkin)
      + '&mewsEnd='   + toYMD(checkout);
    if (roomKey && ROOMS[roomKey] && ROOMS[roomKey].mewsCategoryId) {
      url += '&mewsCategories[0]=' + ROOMS[roomKey].mewsCategoryId;
    }
    return url;
  }

  function updateSummary() {
    if (selectedDates.length === 2) {
      var diff = Math.round((selectedDates[1] - selectedDates[0]) / 86400000);
      elAankomst.textContent = formatDate(selectedDates[0]);
      elVertrek.textContent  = formatDate(selectedDates[1]);
      elNachten.textContent  = diff + (diff === 1 ? ' nacht' : ' nachten');
      btnToStep2.disabled    = false;
      btnDirectBook.disabled = false;
    } else {
      elAankomst.textContent = '\u2014';
      elVertrek.textContent  = '\u2014';
      elNachten.textContent  = '\u2014';
      btnToStep2.disabled    = true;
      btnDirectBook.disabled = true;
    }
  }

  // Flatpickr init (wordt pas aangemaakt bij eerste openPopup)
  var fpInstance = null;

  function initFlatpickr() {
    if (fpInstance) { fpInstance.jumpToDate(new Date()); return; }
    fpInstance = flatpickr(document.getElementById('bkCalendar'), {
      inline: true,
      mode: 'range',
      minDate: 'today',
      locale: {
        rangeSeparator: ' \u2014 '
      },
      onChange: function (dates) {
        selectedDates = dates.length === 2 ? dates : [];
        updateSummary();
      }
    });
  }

  function openBookingPopup(preselectedRoomKey) {
    selectedRoomKey = preselectedRoomKey || null;
    selectedDates   = [];
    updateSummary();

    // Altijd stap 1 tonen bij openen
    step1.hidden = false;
    step2.hidden = true;

    overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';

    // Flatpickr wordt geïnitialiseerd na de CSS-transitie
    setTimeout(initFlatpickr, 50);
  }

  function closeBookingPopup() {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  // Sluit via overlay klik (buiten modal)
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closeBookingPopup();
  });

  btnClose.addEventListener('click', closeBookingPopup);

  btnToStep2.addEventListener('click', function () {
    if (selectedDates.length < 2) return;

    // Als er al een kamer geselecteerd is, sla stap 2 over
    if (window.selectedRoomId) {
      window.open(buildBookingUrl(selectedDates[0], selectedDates[1], window.selectedRoomId), '_blank', 'noopener');
      closeBookingPopup();
      return;
    }

    // Anders stap 2 tonen
    step1.hidden = true;
    step2.hidden = false;
    renderRoomCards();
  });

  btnDirectBook.addEventListener('click', function () {
    if (selectedDates.length < 2) return;
    window.open(buildBookingUrl(selectedDates[0], selectedDates[1], null), '_blank', 'noopener');
    closeBookingPopup();
  });

  btnBack.addEventListener('click', function () {
    step1.hidden = false;
    step2.hidden = true;
  });

  // Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay.classList.contains('is-open')) closeBookingPopup();
  });

  // Exporteer openBookingPopup zodat andere scripts het kunnen aanroepen
  window.openBookingPopup = openBookingPopup;

  // Stap 2: kamers renderen (wordt gevuld in Task 5)
  function renderRoomCards() {
    // Zie Task 5
  }

  btnConfirm.addEventListener('click', function () {
    if (selectedDates.length < 2) return;
    window.open(buildBookingUrl(selectedDates[0], selectedDates[1], selectedRoomKey), '_blank', 'noopener');
    closeBookingPopup();
  });

}());
```

- [ ] **Stap 2: Verificeer in browser-console:**

```javascript
window.openBookingPopup();
```

De popup opent, de kalender is zichtbaar, de bevestigingsbalk toont streepjes. Klik twee data aan — de balk update correct. "Volgende" knop blijft disabled tot twee data geselecteerd zijn.

- [ ] **Stap 3: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: booking-popup — JS core: buildBookingUrl, open/close, stap 1 datepicker"
```

---

## Task 5: JS stap 2 — kamerkeuze cards renderen

**Files:**
- Modify: `wellness-arr-c.html` — de `renderRoomCards()` functie in de booking popup IIFE (Task 4)

- [ ] **Stap 1: Vervang de lege `renderRoomCards()` functie met de volledige implementatie**

Zoek de regel `// Zie Task 5` in de `renderRoomCards` functie en vervang de volledige functie:

```javascript
function renderRoomCards() {
    var ROOM_KEYS = ['comfort', 'royale', 'deluxe', 'junior-suite', 'suite', 'bruidssuite'];
    selectedRoomKey = null; // reset bij elke render

    elRooms.innerHTML = ROOM_KEYS.map(function (key) {
      var r = ROOMS[key];
      var isDefault = key === 'comfort';
      return '<div class="bk-room-card' + (isDefault ? ' is-selected' : '') + '" data-key="' + key + '" role="radio" aria-checked="' + (isDefault ? 'true' : 'false') + '" tabindex="0">' +
        '<div class="bk-room-card__header">' +
          '<div class="bk-room-card__radio"></div>' +
          '<span class="bk-room-card__name">' + r.name + '</span>' +
          '<span class="bk-room-card__upgrade">' + r.upgrade + '</span>' +
          '<button class="bk-room-card__toggle" data-key="' + key + '" tabindex="-1" aria-expanded="false">meer info</button>' +
        '</div>' +
        '<div class="bk-room-card__details" id="bk-details-' + key + '">' + r.shortDesc + '</div>' +
      '</div>';
    }).join('');

    // Comfort standaard geselecteerd
    selectedRoomKey = 'comfort';

    // Klik op card → selecteer
    elRooms.querySelectorAll('.bk-room-card').forEach(function (card) {
      card.addEventListener('click', function (e) {
        // Voorkom dubbel togglen als toggle-knop geklikt is
        if (e.target.classList.contains('bk-room-card__toggle')) return;

        elRooms.querySelectorAll('.bk-room-card').forEach(function (c) {
          c.classList.remove('is-selected');
          c.setAttribute('aria-checked', 'false');
        });
        card.classList.add('is-selected');
        card.setAttribute('aria-checked', 'true');
        selectedRoomKey = card.getAttribute('data-key');
      });
    });

    // Klik op "meer info" → accordion toggle
    elRooms.querySelectorAll('.bk-room-card__toggle').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var key = btn.getAttribute('data-key');
        var details = document.getElementById('bk-details-' + key);
        var isOpen = details.classList.contains('is-open');
        details.classList.toggle('is-open', !isOpen);
        btn.setAttribute('aria-expanded', !isOpen ? 'true' : 'false');
        btn.textContent = !isOpen ? 'minder' : 'meer info';
      });
    });
  }
```

- [ ] **Stap 2: Verificeer in browser:**

```javascript
window.openBookingPopup();
```

Selecteer twee data, klik "Volgende: kies kamer". Stap 2 toont 6 kamers. Comfort is standaard geselecteerd (rode rand). Klik op Deluxe — selectie wisselt. Klik "meer info" op een kamer — accordion opent. Klik "Bekijk beschikbaarheid" — Mews opent in nieuw tabblad met de juiste `mewsStart`, `mewsEnd` en `mewsCategories[0]` parameters in de URL.

- [ ] **Stap 3: Verificeer pre-selected room flow:**

```javascript
window.selectedRoomId = 'deluxe';
window.openBookingPopup('deluxe');
```

Selecteer twee data, klik "Volgende" — popup sluit direct en Mews opent met de Deluxe category ID (geen stap 2 getoond).

- [ ] **Stap 4: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: booking-popup — stap 2 kamerkeuze cards + accordion"
```

---

## Task 6: Alle CTAs koppelen aan de popup

**Files:**
- Modify: `wellness-arr-c.html` — HTML van 5 booking CTAs + room popup CTA in JS

- [ ] **Stap 1: Zet de sticky FAB om van `<a>` naar `<button>` (regel ~1761–1773)**

Vervang:
```html
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
```

Door:
```html
<button
  class="sticky-fab"
  id="stickyFab"
  aria-label="Boek direct: Wellness Arrangement"
  onclick="window.openBookingPopup()"
>
  Boek direct
  <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <path d="M3 8h10M9 4l4 4-4 4" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</button>
```

- [ ] **Stap 2: Zet de sticky card knop om (regel ~1779–1784)**

Vervang:
```html
  <a
    href="https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS"
    class="sticky-card__btn"
    target="_blank"
    rel="noopener"
  >Boek direct &rarr;</a>
```

Door:
```html
  <button
    class="sticky-card__btn"
    onclick="window.openBookingPopup()"
  >Boek direct &rarr;</button>
```

- [ ] **Stap 3: Zet de hero CTA om (regel ~1843–1848)**

Vervang:
```html
    <a
      href="https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS"
      class="hero__cta"
      target="_blank"
      rel="noopener"
    >Boek het arrangement</a>
```

Door:
```html
    <button
      class="hero__cta"
      onclick="window.openBookingPopup()"
    >Boek het arrangement</button>
```

- [ ] **Stap 4: Zet de arr-c CTA om (zoek op `class="button book-now"` — regel ~2053)**

Vervang:
```html
        <a href="https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS"
           class="button book-now" target="_blank" rel="noopener">Boek nu</a>
```

Door:
```html
        <button class="button book-now" onclick="window.openBookingPopup()">Boek nu</button>
```

- [ ] **Stap 5: Zet de arr-c sectie CTA om (zoek op `Boek het arrangement` in de arr-c sectie — regel ~2057)**

Vervang de `<a>` tag die "Boek het arrangement" bevat in de arr-c sectie:
```html
      <a
        class="arr-c__cta"
        href="https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS"
        target="_blank"
        rel="noopener"
      >
        Boek het arrangement
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </a>
```

Door:
```html
      <button
        class="arr-c__cta"
        onclick="window.openBookingPopup()"
      >
        Boek het arrangement
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </button>
```

- [ ] **Stap 6: Zet de diner CTA om (zoek op `class="diner__cta"` — regel ~2242)**

Vervang:
```html
      <a class="diner__cta"
         href="https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS"
         target="_blank"
         rel="noopener">Boek het arrangement</a>
```

Door:
```html
      <button class="diner__cta" onclick="window.openBookingPopup()">Boek het arrangement</button>
```

- [ ] **Stap 7: Pas de CSS aan voor `<a>` → `<button>` waar nodig**

De bestaande CTA-stijlen zijn geschreven voor `<a>` tags. Voeg per CTA toe dat de stijl ook op `button` werkt. Zoek in de `<style>` sectie naar de volgende regels en voeg `button` toe als selector:

```css
/* hero__cta — voeg button variant toe */
button.hero__cta {
  cursor: pointer;
  font-family: inherit;
  border: none;
}

/* arr-c__cta — voeg button variant toe */
button.arr-c__cta {
  cursor: pointer;
  font-family: inherit;
  border: none;
}

/* diner__cta — voeg button variant toe */
button.diner__cta {
  cursor: pointer;
  font-family: inherit;
  border: none;
}

/* sticky-card__btn — voeg button variant toe */
button.sticky-card__btn {
  cursor: pointer;
  font-family: inherit;
  border: none;
  width: 100%;
}
```

- [ ] **Stap 8: Koppel de kamer popup CTA aan de booking popup**

In de `openPopup(key)` JS functie, zoek de regel (regel ~2809):
```javascript
'<a href="' + BOOK_URL + '" class="room-popup__cta" target="_blank" rel="noopener">Boek dit arrangement</a>'
```

Vervang door:
```javascript
'<button class="room-popup__cta" onclick="window.openBookingPopup(\'' + key + '\')">Boek dit arrangement</button>'
```

En voeg aan het einde van de CSS voor `.room-popup__cta:hover` (regel ~1565) toe:
```css
button.room-popup__cta {
  cursor: pointer;
  font-family: inherit;
  border: none;
  width: 100%;
  text-align: center;
}
```

- [ ] **Stap 9: Verwijder de `var BOOK_URL` variabele bovenaan de kamertypes IIFE (nu ongebruikt)**

Zoek en verwijder regel:
```javascript
var BOOK_URL = 'https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS';
```

- [ ] **Stap 10: Verificeer alle 5 CTAs:**

```
1. Sticky FAB (mobile) → popup opent
2. Sticky card (desktop) → popup opent
3. Hero CTA → popup opent
4. Arr-c "Boek het arrangement" → popup opent
5. Diner "Boek het arrangement" → popup opent
6. Kamera popup "Boek dit arrangement" → popup opent met selectedRoomId ingesteld,
   na datumkeuze wordt stap 2 overgeslagen
```

- [ ] **Stap 11: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: booking-popup — alle CTAs gekoppeld aan popup"
```

---

## Task 7: End-to-end verificatie + deploy

**Files:**
- Geen codewijzigingen — verificatie en push

- [ ] **Stap 1: Lokale verificatie — open wellness-arr-c.html in browser**

Test het volledige happy path:
1. Klik sticky FAB → popup opent op stap 1
2. Selecteer aankomst + vertrek datum → bevestigingsbalk update
3. Klik "Volgende: kies kamer" → stap 2 toont 6 kamers
4. Klik "meer info" op Deluxe → accordion opent
5. Selecteer Suite → rode rand
6. Klik "Bekijk beschikbaarheid" → Mews opent in nieuw tab met URL:
   `https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?mewsVoucherCode=WELLNESS&mewsStart=YYYY-MM-DD&mewsEnd=YYYY-MM-DD&mewsCategories[0]=4a642b66-68e6-444c-beeb-af1d00ffc315`

- [ ] **Stap 2: Test "boek direct zonder kamerkeuze"**

1. Open popup, selecteer data
2. Klik "Of boek direct zonder kamerkeuze"
3. Mews opent zonder `mewsCategories` parameter

- [ ] **Stap 3: Test pre-selected flow via kamerpopup**

1. Scroll naar kamertypes blok
2. Klik op "Junior Suite" card → kamerpopup opent
3. Klik "Boek dit arrangement" → booking popup opent
4. Selecteer data, klik "Volgende"
5. Stap 2 wordt NIET getoond — Mews opent direct met Junior Suite category ID

- [ ] **Stap 4: Test mobile (375px)**

Resize browser naar 375px breed. Controleer:
- Popup is full-width bottom sheet (border-radius alleen boven)
- Kalender past binnen de popup
- Bevestigingsbalk past horizontaal

- [ ] **Stap 5: Push naar main**

```bash
git push origin main
```

- [ ] **Stap 6: Wacht 35 seconden, test live op `https://visit.asteria.nl/wellness-arr-c`**

Herhaal de verificatie uit Stap 1 op de live URL.

---

## Self-review — spec coverage check

| Spec-eis | Task |
|---|---|
| 4 booking CTAs openen popup | Task 6 stap 1–6 |
| Kamerpopup "Boek" opent popup met pre-selected kamer | Task 6 stap 8 |
| Stap 1: inline kalender (Flatpickr range) | Task 4 |
| Stap 1: bevestigingsbalk met live update | Task 4 |
| Stap 1: "Volgende" disabled tot beide data geselecteerd | Task 4 |
| Stap 1: "Boek direct zonder kamerkeuze" | Task 4 |
| Stap 2: 6 kamercards radio-stijl | Task 5 |
| Stap 2: accordion per kamer met shortDesc | Task 5 |
| Stap 2 overgeslagen als selectedRoomId gezet | Task 4 (`btnToStep2` handler) |
| Mews deeplink met correcte parameters | Task 4 (`buildBookingUrl`) |
| `mewsVoucherCode=WELLNESS` altijd aanwezig | Task 4 |
| `mewsCategories[0]` alleen bij kamerkeuze | Task 4 |
| Verleden datums disabled in kalender | Task 4 (Flatpickr `minDate: 'today'`) |
| `window.selectedRoomId` reset bij sluiten kamerpopup | Task 1 stap 4 |
| Popup sluit bij Escape en overlay-klik | Task 4 |
| `buildBookingUrl()` is één te vervangen functie voor fase 2 | Task 4 |
| `window.selectedRoomId = null` (geen localStorage) | Task 1 |
| Comfort, Royale, Deluxe, Junior, Suite, Bruidssuite zichtbaar | Task 5 |
| Comfort 3-persoons + Intern NIET zichtbaar | Task 5 (niet in ROOM_KEYS) |
