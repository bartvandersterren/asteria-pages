# Booking Popup Polish — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Drie UX-verbeteringen aan de booking popup op `wellness-arr-c.html`: (1) calendar visueel opschonen, (2) slimmere flow als kamer al geselecteerd is, (3) "meer info" knop in stap 2 opent een room detail sub-view.

**Architecture:** Alle wijzigingen in één bestand (`wellness-arr-c.html`). CSS-blok uitbreiden met Flatpickr overrides. HTML: twee extra elementen toevoegen aan booking popup (`#bkSelectedRoom`, `#bkStep3`). JS: `openBookingPopup`, `renderRoomCards` en een nieuwe `goToRoomDetail` functie aanpassen.

**Tech Stack:** Vanilla HTML/CSS/JS, Flatpickr (CDN, al aanwezig)

---

## File map

- Modify: `wellness-arr-c.html:1871-1888` — Flatpickr CSS-overrides uitbreiden
- Modify: `wellness-arr-c.html:1765-2071` — booking popup CSS-blok uitbreiden (selected room badge + room detail styles)
- Modify: `wellness-arr-c.html:2562-2610` — booking popup HTML: badge + step 3 toevoegen
- Modify: `wellness-arr-c.html:3268-3560` — booking popup IIFE: `openBookingPopup`, `renderRoomCards`, `closeBookingPopup` aanpassen + `goToRoomDetail` toevoegen

---

## Task 1: Flatpickr calendar — CSS redesign

**Doel:** De native-looking maand/jaar selects en generieke opmaak vervangen door een branded, clean kalender die bij de rest van de popup past.

**Huidige situatie (regel 1871-1888):** Alleen kleur-overrides. Header (`flatpickr-months`) en weekdag-labels (`flatpickr-weekday`) zijn volledig unstyled.

**Files:**
- Modify: `wellness-arr-c.html:1871-1888`

- [ ] **Stap 1: vervang de bestaande Flatpickr CSS-overrides**

Zoek het blok dat begint met `/* ── Flatpickr overrides ── */` (rond regel 1870) en vervang alles t/m `.flatpickr-day.today` door:

```css
/* ── Flatpickr overrides ── */
#bkCalendar .flatpickr-calendar {
  box-shadow: none;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  width: 100%;
  font-family: 'Montserrat', sans-serif;
}
/* Header: maand + jaar */
#bkCalendar .flatpickr-months {
  padding: 10px 4px 6px;
  align-items: center;
}
#bkCalendar .flatpickr-month {
  height: auto;
  line-height: 1;
}
#bkCalendar .flatpickr-current-month {
  font-size: 15px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  position: static;
  width: auto;
  left: auto;
  transform: none;
}
/* Maand select + jaar input: styled als plain tekst */
#bkCalendar .flatpickr-monthDropdownContainer select,
#bkCalendar .numInputWrapper input {
  font-family: 'Electrolize', sans-serif;
  font-size: 15px;
  font-weight: 400;
  color: #1a1a1a;
  background: none;
  border: none;
  outline: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  cursor: pointer;
  padding: 0;
  width: auto;
}
#bkCalendar .numInputWrapper { width: 56px; }
#bkCalendar .numInputWrapper span { display: none; } /* verberg up/down pijltjes */
/* Navigatie pijlen */
#bkCalendar .flatpickr-prev-month,
#bkCalendar .flatpickr-next-month {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 14px;
  height: auto;
  top: 8px;
  fill: #9ca3af;
  color: #9ca3af;
}
#bkCalendar .flatpickr-prev-month:hover,
#bkCalendar .flatpickr-next-month:hover { fill: #1a1a1a; color: #1a1a1a; }
/* Weekdag labels */
#bkCalendar .flatpickr-weekdays { background: none; padding: 4px 0; }
#bkCalendar .flatpickr-weekday {
  font-family: 'Montserrat', sans-serif;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #9ca3af;
  background: none;
}
/* Dag cellen */
#bkCalendar .flatpickr-day {
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  font-weight: 400;
  border-radius: 8px;
  color: #1a1a1a;
  border: 1.5px solid transparent;
}
#bkCalendar .flatpickr-day.flatpickr-disabled,
#bkCalendar .flatpickr-day.prevMonthDay,
#bkCalendar .flatpickr-day.nextMonthDay { color: #d1d5db; }
#bkCalendar .flatpickr-day:hover:not(.flatpickr-disabled):not(.selected):not(.startRange):not(.endRange) {
  background: #f3f4f6;
  border-color: #f3f4f6;
}
.flatpickr-day.selected,
.flatpickr-day.startRange,
.flatpickr-day.endRange {
  background: #c23435 !important;
  border-color: #c23435 !important;
  color: #fff !important;
  font-weight: 700;
}
.flatpickr-day.inRange {
  background: #fde8e8 !important;
  border-color: #fde8e8 !important;
  box-shadow: -5px 0 0 #fde8e8, 5px 0 0 #fde8e8;
}
.flatpickr-day.today:not(.selected) { border-color: #c23435; }
```

- [ ] **Stap 2: visueel testen**

Open `visit.asteria.nl/wellness-arr-c` in de browser, klik op "Boek nu" en verifieer:
- Maand en jaar tonen als plain Electrolize-tekst (geen native select-box look)
- Weekdagen tonen als kleine caps Montserrat
- Prev/next pijlen zijn zichtbaar en clickable
- Geselecteerde range is rood (#c23435), inRange lichtroze

- [ ] **Stap 3: commit**

```bash
git add wellness-arr-c.html
git commit -m "style: booking popup — flatpickr calendar redesign"
```

---

## Task 2: Smart popup flow — kamer al geselecteerd

**Doel:** Wanneer `openBookingPopup(key)` wordt aangeroepen met een pre-geselecteerde kamer (via de kamerpopup), moet stap 2 worden overgeslagen én moet de UI dat communiceren: toon welke kamer geselecteerd is, verberg "Of boek direct zonder kamerkeuze".

**Huidige situatie:** `openBookingPopup(key)` zet `selectedRoomKey = key` en slaat stap 2 over in de `btnToStep2` click handler. Maar visueel ziet de popup er hetzelfde uit als zonder pre-selectie.

**Files:**
- Modify: `wellness-arr-c.html:1926-1962` — CSS uitbreiden met badge + has-preselected class
- Modify: `wellness-arr-c.html:2590-2595` — HTML stap 1 CTA-rij
- Modify: `wellness-arr-c.html:3411-3427` — `openBookingPopup` functie

### Stap 2a: CSS toevoegen

- [ ] **Stap 1: voeg CSS toe na de `.bk-btn-ghost:hover` regel (na regel ~1962)**

```css
/* ── Pre-geselecteerde kamer badge ── */
.bk-selected-room {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fff8f8;
  border: 1.5px solid #fca5a5;
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 8px;
}
.bk-selected-room__label {
  font-family: 'Montserrat', sans-serif;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #9ca3af;
  display: block;
  margin-bottom: 2px;
}
.bk-selected-room__name {
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  font-weight: 700;
  color: #c23435;
}
.bk-selected-room__change {
  margin-left: auto;
  background: none;
  border: none;
  font-family: 'Montserrat', sans-serif;
  font-size: 11px;
  color: #9ca3af;
  text-decoration: underline;
  cursor: pointer;
  flex-shrink: 0;
  padding: 0;
}
.bk-selected-room__change:hover { color: #1a1a1a; }
```

### Stap 2b: HTML aanpassen

- [ ] **Stap 2: voeg de badge toe aan stap 1, vóór `.bk-cta-row`**

Zoek in de HTML het blok met `<div class="bk-cta-row">` in `#bkStep1` (rond regel 2590) en voeg er direct boven toe:

```html
<div class="bk-selected-room" id="bkSelectedRoom" hidden>
  <div>
    <span class="bk-selected-room__label">Geselecteerde kamer</span>
    <span class="bk-selected-room__name" id="bkSelectedRoomName"></span>
  </div>
  <button class="bk-selected-room__change" id="bkChangeRoom">wijzig</button>
</div>
```

### Stap 2c: JS aanpassen

- [ ] **Stap 3: voeg variabelen toe bovenaan de booking popup IIFE**

Voeg toe na de bestaande variabeledeclaraties (na `var elRooms = ...`):

```js
var elSelectedRoom     = document.getElementById('bkSelectedRoom');
var elSelectedRoomName = document.getElementById('bkSelectedRoomName');
var btnChangeRoom      = document.getElementById('bkChangeRoom');
```

- [ ] **Stap 4: pas `openBookingPopup` aan**

Vervang de functie (zoek `function openBookingPopup(preselectedRoomKey)`) door:

```js
function openBookingPopup(preselectedRoomKey) {
  selectedRoomKey = preselectedRoomKey || null;
  selectedDates   = [];
  availabilityResult  = null;
  availabilityLoading = false;
  updateSummary();

  // Stap 1 tonen, stap 2 en 3 verbergen
  step1.hidden = false;
  step2.hidden = true;
  step3.hidden = true;

  // Pre-selectie UI
  var modal = document.getElementById('bookingModal');
  if (selectedRoomKey && window.ROOMS && window.ROOMS[selectedRoomKey]) {
    modal.classList.add('has-preselected');
    elSelectedRoomName.textContent = window.ROOMS[selectedRoomKey].name;
    elSelectedRoom.hidden = false;
    btnToStep2.textContent = 'Bekijk beschikbaarheid \u2192';
    btnDirectBook.hidden = true;
  } else {
    modal.classList.remove('has-preselected');
    elSelectedRoom.hidden = true;
    btnToStep2.textContent = 'Volgende: kies kamer \u2192';
    btnDirectBook.hidden = false;
  }

  overlay.classList.add('is-open');
  document.body.style.overflow = 'hidden';
  setTimeout(initFlatpickr, 50);
}
```

- [ ] **Stap 5: voeg "wijzig" handler toe (na de `btnBack` listener)**

```js
btnChangeRoom.addEventListener('click', function () {
  selectedRoomKey = null;
  var modal = document.getElementById('bookingModal');
  modal.classList.remove('has-preselected');
  elSelectedRoom.hidden = true;
  btnToStep2.textContent = 'Volgende: kies kamer \u2192';
  btnDirectBook.hidden = false;
});
```

- [ ] **Stap 6: reset `btnDirectBook.hidden` in `closeBookingPopup`**

Voeg toe in `closeBookingPopup`:

```js
function closeBookingPopup() {
  overlay.classList.remove('is-open');
  document.body.style.overflow = '';
  btnDirectBook.hidden = false;
  document.getElementById('bookingModal').classList.remove('has-preselected');
}
```

- [ ] **Stap 7: visueel testen**

Test scenario A: klik op een kamer in de kamertypes sectie → "Boek dit arrangement" → popup toont kamerbadge (bv. "Royale Kamer"), alleen 1 rode knop "Bekijk beschikbaarheid", geen ghost-knop.

Test scenario B: klik op "Boek nu" in de nav → popup toont normale 2-stappen flow, ghost-knop zichtbaar.

Test scenario C: klik in scenario A op "wijzig" → popup wisselt naar normale 2-stappen flow.

- [ ] **Stap 8: commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: booking popup — slim flow bij pre-geselecteerde kamer"
```

---

## Task 3: "Meer info" in stap 2 → room detail sub-view

**Doel:** De "meer info" knop in elke kamer-card in stap 2 navigeert naar een sub-view (stap 3) binnen dezelfde modal met: kamerfoto, badge, naam, beschrijving, features en een "Selecteer deze kamer" knop.

**Huidige situatie:** Klikken op "meer info" toggle-t inline `.bk-room-card__details` (alleen `r.shortDesc` tekst). Dit is onvoldoende info voor een upgradebeslissing.

**Files:**
- Modify: `wellness-arr-c.html:~2071` — CSS toevoegen voor room detail sub-view
- Modify: `wellness-arr-c.html:2606-2609` — HTML: `#bkStep3` toevoegen na `#bkStep2`
- Modify: `wellness-arr-c.html:3493-3553` — `renderRoomCards`: toggle vervangen + `goToRoomDetail` toevoegen

### Stap 3a: CSS toevoegen

- [ ] **Stap 1: voeg CSS toe na `.bk-step[hidden]` (na regel ~2071)**

```css
/* ── Room detail sub-view (stap 3) ── */
.bk-room-detail__img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 16px;
  display: block;
}
.bk-room-detail__name {
  font-family: 'Electrolize', sans-serif;
  font-size: 18px;
  font-weight: 400;
  color: #1a1a1a;
  margin: 8px 0 10px;
}
.bk-room-detail__desc {
  font-family: 'Montserrat', sans-serif;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.65;
  margin-bottom: 16px;
}
.bk-room-detail__features {
  list-style: none;
  padding: 0;
  margin: 0 0 24px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.bk-room-detail__feature {
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 8px;
}
.bk-room-detail__feature::before {
  content: '\2713';
  color: #c23435;
  font-weight: 700;
  flex-shrink: 0;
}
```

### Stap 3b: HTML toevoegen

- [ ] **Stap 2: voeg `#bkStep3` toe direct na het sluitende `</div>` van `#bkStep2`**

```html
<div class="bk-step" id="bkStep3" hidden>
  <button class="bk-back" id="bkBackToRooms" aria-label="Terug naar kamerkeuze">&larr; Terug</button>
  <div id="bkRoomDetail"></div>
</div>
```

### Stap 3c: JS aanpassen

- [ ] **Stap 3: declareer `step3` en `btnBackToRooms` bovenaan de IIFE**

Voeg toe bij de andere variabeledeclaraties:

```js
var step3           = document.getElementById('bkStep3');
var btnBackToRooms  = document.getElementById('bkBackToRooms');
```

- [ ] **Stap 4: voeg `goToRoomDetail` functie toe, vóór `renderRoomCards`**

```js
function goToRoomDetail(key) {
  var r = window.ROOMS && window.ROOMS[key];
  if (!r) return;
  var detailEl = document.getElementById('bkRoomDetail');
  detailEl.innerHTML =
    '<img class="bk-room-detail__img" src="' + r.imgs[0] + '" alt="' + r.name + '" loading="lazy">' +
    r.badge +
    '<h3 class="bk-room-detail__name">' + r.name + '</h3>' +
    '<p class="bk-room-detail__desc">' + r.desc + '</p>' +
    '<ul class="bk-room-detail__features">' +
      r.features.map(function (f) { return '<li class="bk-room-detail__feature">' + f + '</li>'; }).join('') +
    '</ul>' +
    '<button class="bk-btn-primary" data-select-key="' + key + '">Selecteer deze kamer</button>';

  detailEl.querySelector('[data-select-key]').addEventListener('click', function () {
    var k = this.dataset.selectKey;
    selectedRoomKey = k;
    step3.hidden = true;
    step2.hidden = false;
    // Update selectie in de kamercards
    elRooms.querySelectorAll('.bk-room-card').forEach(function (c) {
      var isThis = c.getAttribute('data-key') === k;
      c.classList.toggle('is-selected', isThis);
      c.setAttribute('aria-checked', isThis ? 'true' : 'false');
    });
  });

  step2.hidden = true;
  step3.hidden = false;
}
```

- [ ] **Stap 5: vervang de toggle-handler in `renderRoomCards`**

Zoek het blok dat begint met `elRooms.querySelectorAll('.bk-room-card__toggle').forEach` en vervang de volledige forEach door:

```js
elRooms.querySelectorAll('.bk-room-card__toggle').forEach(function (btn) {
  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    goToRoomDetail(this.dataset.key);
  });
});
```

- [ ] **Stap 6: voeg `btnBackToRooms` handler toe (bij de andere knoppen-listeners)**

```js
btnBackToRooms.addEventListener('click', function () {
  step3.hidden = true;
  step2.hidden = false;
});
```

- [ ] **Stap 7: verberg `.bk-room-card__details` div (inline expand niet meer nodig)**

In `renderRoomCards`, in de HTML-string: verwijder de `<div class="bk-room-card__details" ...>` regel volledig. De inline details worden niet meer gebruikt.

De regel om te verwijderen:
```js
'<div class="bk-room-card__details" id="bk-details-' + key + '">' + r.shortDesc + '</div>' +
```

- [ ] **Stap 8: visueel testen**

Test stap 2 → klik "meer info" op een kamer → stap 3 toont foto, badge, naam, beschrijving en features.
Klik "← Terug" → terug naar stap 2, geselecteerde kamer ongewijzigd.
Klik "Selecteer deze kamer" → terug naar stap 2, die kamer is geselecteerd.
Klik daarna "Bekijk beschikbaarheid" → Mews deeplink opent met de geselecteerde kamer.

- [ ] **Stap 9: commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: booking popup — meer info opent room detail sub-view"
```

---

## Task 4: Push naar main

- [ ] **Stap 1: push**

```bash
git push origin main
```

- [ ] **Stap 2: wacht ~35 seconden en test live op `visit.asteria.nl/wellness-arr-c`**

Controleer alle drie de flows op desktop en mobile (375px).
