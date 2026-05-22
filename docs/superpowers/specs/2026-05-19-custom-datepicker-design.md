# Spec: Custom Vanilla JS Datepicker voor Booking Popup

**Datum:** 2026-05-19
**Pagina:** wellness-arr-c.html
**Vervangt:** Flatpickr (CDN dependency, inline-style breedte-conflict)

---

## Probleemstelling

Flatpickr injecteert `style="width: 273px"` als inline stijl op `.flatpickr-days` en `.dayContainer` na elke render. CSS `!important` en JS-overrides verliezen het van inline styles. De kalender is smaller dan de popup en links uitgelijnd. Meerdere fix-pogingen mislukten.

---

## Oplossing

Vervang Flatpickr door een custom vanilla JS datepicker. Geen externe dependency, volledige controle over HTML/CSS, geen inline-stijl strijd.

---

## HTML-structuur (gegenereerd door JS)

```html
<div id="bkCalendar">
  <div class="cal-nav">
    <button class="cal-nav__prev">&#8249;</button>
    <span class="cal-nav__label"><!-- "januari — februari 2026" --></span>
    <button class="cal-nav__next">&#8250;</button>
  </div>
  <div class="cal-grid-wrap">
    <div class="cal-month">
      <div class="cal-month-label">Januari 2026</div>
      <div class="cal-weekdays">
        <span>Ma</span><span>Di</span>...<span>Zo</span>
      </div>
      <div class="cal-days">
        <button class="cal-day" data-date="2026-01-01">1</button>
        <!-- ... -->
      </div>
    </div>
    <div class="cal-month">
      <!-- tweede maand, zelfde structuur -->
    </div>
  </div>
</div>
```

Elk `.cal-day` krijgt data-states als CSS-klassen:
- `is-disabled` — verleden of vóór minDate
- `is-other-month` — visueel gedimde opvulling (eerste/laatste week)
- `is-start` — geselecteerde aankomstdatum
- `is-end` — geselecteerde vertrekdatum
- `is-in-range` — dagen tussen start en end
- `is-hover-range` — preview-range tijdens zweefbeweging (start gezet, end nog niet)
- `is-today` — visuele markering huidige dag

---

## Layout

### Desktop (≥600px)
`.cal-grid-wrap` — `display: flex; flex-direction: row; gap: 24px`
Beide maanden naast elkaar, elk ~50% breedte.

### Mobile (<600px)
`.cal-grid-wrap` — `display: flex; flex-direction: column; gap: 24px`
Maanden gestapeld. De modal heeft al `overflow-y: auto` — geen aanpassing nodig.

---

## Navigatie

- `cal-nav__prev` en `cal-nav__next` wijzigen `viewMonth` met ±1
- `viewMonth` is de eerste zichtbare maand (0-gebaseerd: jaar + maandindex)
- Minimale viewMonth: huidige maand (vorige maand-knop disabled als viewMonth === huidige maand)
- Na navigatie: volledige re-render van `#bkCalendar` innerHTML

---

## Selectie-logica

```
Klik op een dag:
  if dag is disabled → negeer
  if geen start geselecteerd → stel start in, wis end
  if start gezet maar geen end:
    if klik === start → reset (wis beide)
    if klik < start → swap: nieuwe start = klik, nieuwe end = oude start
    else → stel end in
  if beide gezet → reset: nieuwe start = klik, wis end
```

Na elke klik: re-render + roep `onDateChange(start, end)` aan.

---

## Hover-preview

Terwijl start gezet is maar end nog niet: toon `is-hover-range` klasse op alle dagen tussen start en hoverDate. Update bij `mouseover` / `touchmove` op `.cal-day` elementen.

Mobile (touch): hover-preview is optioneel — touch triggert direct `click`, geen `mouseover`. Eerste tap = start, tweede tap = end.

---

## Datum-utilities (puur JS, geen library)

```js
function today() // Date object op middernacht lokale tijd
function addMonths(date, n) // nieuwe Date, n maanden later
function isSameDay(a, b) // boolean
function isBefore(a, b) // boolean
function isAfter(a, b) // boolean
function formatDate(date) // "vr 31 jan" voor summary-balk
function formatISO(date) // "2026-01-31" voor Mews deeplink
function daysInMonth(year, month) // integer
function firstWeekdayOfMonth(year, month) // 0=ma … 6=zo
```

---

## CSS-stijlen

Alle stijlen staan in de `<style>` block van wellness-arr-c.html, onder het label `/* ── Custom Datepicker ── */`. Geen inline stijlen vanuit JS.

| Element | Stijl |
|---|---|
| `.cal-day` | Montserrat 13px, `width: 100%`, `aspect-ratio: 1`, border-radius 50% |
| `.cal-day.is-start`, `.is-end` | `background: #c23435`, `color: #fff`, `font-weight: 700` |
| `.cal-day.is-in-range`, `.is-hover-range` | `background: #fde8e8`, border-radius 0 |
| `.cal-day.is-start` | border-radius: 50% 0 0 50% (links afgerond) |
| `.cal-day.is-end` | border-radius: 0 50% 50% 0 (rechts afgerond) |
| `.cal-day.is-today` | `border: 1px solid #c23435` |
| `.cal-day.is-disabled` | `color: #d1d5db`, `cursor: default`, `pointer-events: none` |
| `.cal-month-label` | Electrolize 15px, margin-bottom 8px |
| `.cal-weekdays span` | Montserrat 10px, `font-weight: 700`, `color: #9ca3af`, tekst gecentreerd |
| `.cal-days` | `display: grid; grid-template-columns: repeat(7, 1fr)` |
| `.cal-nav` | flex, space-between, Electrolize 14px |

---

## Integratie in booking popup

### Verwijderen
- `<link rel="stylesheet" href=".../flatpickr.min.css">`
- `<script src=".../flatpickr" defer>`
- Alle CSS-overrides onder `/* ── Flatpickr overrides ── */`
- `fpInstance` variabele en `initFlatpickr()` functie

### Toevoegen / aanpassen
- `initCustomCalendar()` — rendert kalender in `#bkCalendar`, zet event listeners
- `clearCustomCalendar()` — reset state, re-render
- `onDateChange(start, end)` callback — roept bestaande `updateSummary()` aan

### Bestaande koppelingen (ongewijzigd)
- `selectedDates` array — wordt gevoed door `onDateChange`
- `updateSummary()` — leest `selectedDates`, geen aanpassing nodig
- `buildBookingUrl(checkin, checkout, roomKey)` — verwacht `Date` objecten, geen aanpassing nodig

---

## Scope — buiten deze spec

- Availability highlighting (kamerbeschikbaarheid per dag) — aparte taak
- Blackout dates — niet van toepassing (Mews regelt beschikbaarheid)
- Taalondersteuning EN/DE — aparte taak
- Minimale verblijfsduur (bijv. min 2 nachten) — niet geïmplementeerd tenzij Mews dit vereist
