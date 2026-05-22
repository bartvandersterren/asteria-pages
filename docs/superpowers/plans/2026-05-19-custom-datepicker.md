# Custom Datepicker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vervang Flatpickr door een custom vanilla JS datepicker die altijd volledig breed rendert en twee maanden toont (naast elkaar op desktop, gestapeld op mobile).

**Architecture:** Één zelfstandige IIFE in wellness-arr-c.html die zijn eigen state beheert (`viewMonth`, `selectedStart`, `selectedEnd`, `hoverDate`). Bij elke state-wijziging volledige innerHTML-rerender van `#bkCalendar`. Integreert via `window.initCustomCalendar(callback)` en `window.clearCustomCalendar()` met de bestaande booking popup IIFE.

**Tech Stack:** Vanilla JS (ES5), CSS in bestaande `<style>` block, geen externe dependencies.

---

## Bestandswijzigingen

- **Modify:** `wellness-arr-c.html`
  - Verwijder: Flatpickr CDN link (regel 26), Flatpickr script (regel 2870)
  - Verwijder: CSS block `/* ── Flatpickr overrides ── */` (regels 1870–1984)
  - Vervang: CSS block door `/* ── Custom Datepicker ── */`
  - Verwijder: `var fpInstance`, `initFlatpickr()` (regels 3591–3618)
  - Vervang: `setTimeout(initFlatpickr, 50)` (regel 3651) door `initCustomCalendar(...)` aanroep
  - Voeg toe: custom datepicker IIFE vóór de booking popup script tag

---

## Task 1: Verwijder Flatpickr

**Files:**
- Modify: `wellness-arr-c.html`

- [ ] **Stap 1: Verwijder Flatpickr CSS CDN (regel 26)**

Verwijder deze twee regels uit de `<head>`:
```html
  <!-- Flatpickr date picker -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
```

- [ ] **Stap 2: Verwijder Flatpickr JS CDN (regel 2870)**

Verwijder:
```html
<script src="https://cdn.jsdelivr.net/npm/flatpickr" defer></script>
```

- [ ] **Stap 3: Verwijder de Flatpickr CSS overrides block**

Verwijder alles van `/* ── Flatpickr overrides ── */` t/m `.flatpickr-day.today:not(.selected) { border-color: #c23435; }` (regels 1869–1984, inclusief de lege regel ervoor).

- [ ] **Stap 4: Verwijder fpInstance en initFlatpickr()**

Verwijder uit de booking popup IIFE:
```js
  // Flatpickr init (wordt pas aangemaakt bij eerste openPopup)
  var fpInstance = null;

  function initFlatpickr() {
    if (fpInstance) { fpInstance.clear(); fpInstance.jumpToDate(new Date()); return; }
    if (typeof flatpickr !== 'function') { return; }
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
    // Flatpickr zet inline styles op .flatpickr-days en .dayContainer;
    // die overrulen CSS — forceer volledige breedte via JS.
    var calContainer = document.getElementById('bkCalendar');
    var calEl  = calContainer.querySelector('.flatpickr-calendar');
    var daysEl = calContainer.querySelector('.flatpickr-days');
    var dayContEl = calContainer.querySelector('.dayContainer');
    if (calEl)    { calEl.style.width = '100%'; }
    if (daysEl)   { daysEl.style.width = '100%'; daysEl.style.maxWidth = '100%'; }
    if (dayContEl){ dayContEl.style.width = '100%'; dayContEl.style.minWidth = '0'; dayContEl.style.maxWidth = '100%'; }
  }
```

- [ ] **Stap 5: Vervang setTimeout aanroep (tijdelijk placeholder)**

Vervang in `openBookingPopup()`:
```js
    // Flatpickr wordt geïnitialiseerd na de CSS-transitie
    setTimeout(initFlatpickr, 50);
```
Door (tijdelijk, wordt ingevuld in Task 3):
```js
    // Custom datepicker — wordt ingevuld in Task 3
    if (window.initCustomCalendar) {
      window.initCustomCalendar(function(start, end) {
        selectedDates = start && end ? [start, end] : [];
        updateSummary();
      });
    }
```

- [ ] **Stap 6: Controleer in browser dat pagina laadt zonder JS-errors**

Open `wellness-arr-c.html` lokaal of op visit.asteria.nl. Open DevTools console. Verwacht: geen errors over `flatpickr is not defined`. De booking popup opent, stap 1 toont een lege `#bkCalendar` div.

- [ ] **Stap 7: Commit**

```bash
git add wellness-arr-c.html
git commit -m "refactor: verwijder Flatpickr dependency uit booking popup"
```

---

## Task 2: Voeg Custom Datepicker CSS toe

**Files:**
- Modify: `wellness-arr-c.html` (style block)

- [ ] **Stap 1: Voeg CSS toe op de plek van de verwijderde Flatpickr block**

Voeg in het `<style>` block toe op de plek waar `/* ── Flatpickr overrides ── */` stond (na `.bk-dot--active` block, vóór `/* ── Bevestigingsbalk ── */`):

```css
  /* ── Custom Datepicker ── */
  #bkCalendar { width: 100%; }

  .cal-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
  }
  .cal-nav__prev,
  .cal-nav__next {
    background: none;
    border: none;
    font-size: 28px;
    color: #9ca3af;
    cursor: pointer;
    padding: 2px 8px;
    line-height: 1;
    font-family: inherit;
  }
  .cal-nav__prev:hover:not([disabled]),
  .cal-nav__next:hover:not([disabled]) { color: #1a1a1a; }
  .cal-nav__prev[disabled] { color: #e5e7eb; cursor: default; }
  .cal-nav__label {
    font-family: 'Electrolize', sans-serif;
    font-size: 14px;
    color: #1a1a1a;
    text-align: center;
  }
  .cal-grid-wrap {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  @media (min-width: 600px) {
    .cal-grid-wrap { flex-direction: row; }
    .cal-month { flex: 1; min-width: 0; }
  }
  .cal-month-label {
    font-family: 'Electrolize', sans-serif;
    font-size: 13px;
    color: #6b7280;
    text-align: center;
    margin-bottom: 8px;
  }
  .cal-weekdays {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    margin-bottom: 2px;
  }
  .cal-weekdays span {
    font-family: 'Montserrat', sans-serif;
    font-size: 10px;
    font-weight: 700;
    color: #9ca3af;
    text-align: center;
    padding: 4px 0;
  }
  .cal-days {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
  }
  .cal-day {
    font-family: 'Montserrat', sans-serif;
    font-size: 12px;
    font-weight: 400;
    color: #1a1a1a;
    background: none;
    border: 1px solid transparent;
    border-radius: 50%;
    cursor: pointer;
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    width: 100%;
  }
  .cal-day:hover:not(.is-disabled):not(.is-start):not(.is-end) {
    background: #f3f4f6;
  }
  .cal-day.is-disabled {
    color: #d1d5db;
    cursor: default;
    pointer-events: none;
  }
  .cal-day.is-today { border-color: #c23435; }
  .cal-day.is-start,
  .cal-day.is-end {
    background: #c23435;
    border-color: #c23435;
    color: #fff;
    font-weight: 700;
    border-radius: 50%;
  }
  .cal-day.is-in-range,
  .cal-day.is-hover-range {
    background: #fde8e8;
    border-color: #fde8e8;
    border-radius: 0;
    color: #1a1a1a;
  }
```

- [ ] **Stap 2: Controleer visueel (na Task 3 — sla nu over)**

Wordt getest nadat de JS is toegevoegd in Task 3.

- [ ] **Stap 3: Commit**

```bash
git add wellness-arr-c.html
git commit -m "style: custom datepicker CSS — 2 maanden, range-highlight, branded kleuren"
```

---

## Task 3: Voeg Custom Datepicker JS toe

**Files:**
- Modify: `wellness-arr-c.html` (vóór de booking popup `<script>` tag)

- [ ] **Stap 1: Voeg de datepicker IIFE toe**

Voeg de volgende `<script>` block toe **direct vóór** de bestaande `<script>` tag van de booking popup (zoek naar `/* ── Cookie banner ── */` — voeg het blok daarvóór in, vlak na de Flatpickr script tag die je in Task 1 verwijderd hebt):

```html
<script>
/* ── Custom Datepicker ── */
(function() {
  var MONTH_NAMES = ['Januari','Februari','Maart','April','Mei','Juni',
                     'Juli','Augustus','September','Oktober','November','December'];
  var DAY_NAMES   = ['Ma','Di','Wo','Do','Vr','Za','Zo'];

  var cal = {
    viewYear: 0, viewMonth: 0,
    selectedStart: null, selectedEnd: null,
    hoverDate: null,
    onDateChange: null
  };

  function todayMidnight() {
    var d = new Date();
    return new Date(d.getFullYear(), d.getMonth(), d.getDate());
  }

  function isSameDay(a, b) {
    return a && b &&
      a.getFullYear() === b.getFullYear() &&
      a.getMonth()    === b.getMonth()    &&
      a.getDate()     === b.getDate();
  }

  function isBefore(a, b) { return a.getTime() < b.getTime(); }
  function isAfter(a, b)  { return a.getTime() > b.getTime(); }

  function formatISO(d) {
    var m   = String(d.getMonth() + 1).padStart ? String(d.getMonth() + 1).padStart(2,'0') : (d.getMonth() < 9 ? '0' + (d.getMonth()+1) : String(d.getMonth()+1));
    var day = String(d.getDate()).padStart      ? String(d.getDate()).padStart(2,'0')        : (d.getDate() < 10 ? '0' + d.getDate() : String(d.getDate()));
    return d.getFullYear() + '-' + m + '-' + day;
  }

  function firstWeekdayOfMonth(year, month) {
    // 0 = maandag, 6 = zondag
    var dow = new Date(year, month, 1).getDay(); // 0=zo,1=ma,...6=za
    return dow === 0 ? 6 : dow - 1;
  }

  function daysInMonth(year, month) {
    return new Date(year, month + 1, 0).getDate();
  }

  function renderMonth(year, month) {
    var todayDate  = todayMidnight();
    var daysCount  = daysInMonth(year, month);
    var firstDay   = firstWeekdayOfMonth(year, month);
    var start      = cal.selectedStart;
    var end        = cal.selectedEnd;
    var hover      = cal.hoverDate;

    // Bepaal effectieve range voor in-range highlight
    var rangeA = null, rangeB = null;
    if (start && end) {
      rangeA = isBefore(start, end) ? start : end;
      rangeB = isBefore(start, end) ? end   : start;
    } else if (start && hover && !isSameDay(hover, start)) {
      rangeA = isBefore(start, hover) ? start : hover;
      rangeB = isBefore(start, hover) ? hover : start;
    }

    var html = '<div class="cal-month">';
    html += '<div class="cal-month-label">' + MONTH_NAMES[month] + ' ' + year + '</div>';
    html += '<div class="cal-weekdays">';
    for (var w = 0; w < 7; w++) {
      html += '<span>' + DAY_NAMES[w] + '</span>';
    }
    html += '</div><div class="cal-days">';

    // Lege cellen vóór de eerste dag
    for (var e = 0; e < firstDay; e++) {
      html += '<span class="cal-day-empty"></span>';
    }

    for (var day = 1; day <= daysCount; day++) {
      var date     = new Date(year, month, day);
      var iso      = formatISO(date);
      var disabled = isBefore(date, todayDate);
      var classes  = ['cal-day'];

      if (disabled)              classes.push('is-disabled');
      if (isSameDay(date, todayDate) && !disabled) classes.push('is-today');
      if (isSameDay(date, start))    classes.push('is-start');
      if (isSameDay(date, end))      classes.push('is-end');

      if (rangeA && rangeB && isAfter(date, rangeA) && isBefore(date, rangeB)) {
        classes.push(cal.selectedEnd ? 'is-in-range' : 'is-hover-range');
      }

      var attrs = disabled ? ' disabled aria-disabled="true"' : '';
      html += '<button class="' + classes.join(' ') + '" data-date="' + iso + '"' + attrs + '>' + day + '</button>';
    }

    html += '</div></div>';
    return html;
  }

  function render() {
    var container = document.getElementById('bkCalendar');
    if (!container) return;

    var y1 = cal.viewYear, m1 = cal.viewMonth;
    var y2 = y1, m2 = m1 + 1;
    if (m2 > 11) { m2 = 0; y2++; }

    var todayDate   = todayMidnight();
    var prevDisabled = (y1 < todayDate.getFullYear()) ||
                       (y1 === todayDate.getFullYear() && m1 <= todayDate.getMonth());

    var html = '<div class="cal-nav">';
    html += '<button class="cal-nav__prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>';
    html += '<span class="cal-nav__label">' + MONTH_NAMES[m1] + ' \u2014 ' + MONTH_NAMES[m2] + ' ' + y2 + '</span>';
    html += '<button class="cal-nav__next">&#8250;</button>';
    html += '</div>';
    html += '<div class="cal-grid-wrap">';
    html += renderMonth(y1, m1);
    html += renderMonth(y2, m2);
    html += '</div>';

    container.innerHTML = html;
    attachListeners(container);
  }

  function attachListeners(container) {
    // Navigatie
    var btnPrev = container.querySelector('.cal-nav__prev');
    var btnNext = container.querySelector('.cal-nav__next');

    btnPrev.addEventListener('click', function() {
      cal.viewMonth--;
      if (cal.viewMonth < 0) { cal.viewMonth = 11; cal.viewYear--; }
      render();
    });
    btnNext.addEventListener('click', function() {
      cal.viewMonth++;
      if (cal.viewMonth > 11) { cal.viewMonth = 0; cal.viewYear++; }
      render();
    });

    // Dag-klik
    container.querySelectorAll('.cal-day:not([disabled])').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var date = new Date(btn.dataset.date + 'T00:00:00');
        if (!cal.selectedStart || (cal.selectedStart && cal.selectedEnd)) {
          // Reset: nieuwe start
          cal.selectedStart = date;
          cal.selectedEnd   = null;
        } else {
          if (isSameDay(date, cal.selectedStart)) {
            // Klik op start → wis selectie
            cal.selectedStart = null;
          } else if (isBefore(date, cal.selectedStart)) {
            // Vóór start → swap
            cal.selectedEnd   = cal.selectedStart;
            cal.selectedStart = date;
          } else {
            // Na start → stel end in
            cal.selectedEnd = date;
          }
        }
        cal.hoverDate = null;
        render();
        if (cal.onDateChange) {
          cal.onDateChange(cal.selectedStart, cal.selectedEnd);
        }
      });

      // Hover preview — alleen re-renderen als dag verandert
      btn.addEventListener('mouseenter', function() {
        if (cal.selectedStart && !cal.selectedEnd) {
          var newHover = new Date(btn.dataset.date + 'T00:00:00');
          if (!cal.hoverDate || !isSameDay(newHover, cal.hoverDate)) {
            cal.hoverDate = newHover;
            render();
          }
        }
      });
    });

    // Verlaat kalender → wis hover
    container.addEventListener('mouseleave', function() {
      if (cal.hoverDate) {
        cal.hoverDate = null;
        render();
      }
    });
  }

  window.initCustomCalendar = function(onDateChange) {
    var t = todayMidnight();
    cal.viewYear      = t.getFullYear();
    cal.viewMonth     = t.getMonth();
    cal.selectedStart = null;
    cal.selectedEnd   = null;
    cal.hoverDate     = null;
    cal.onDateChange  = onDateChange || null;
    render();
  };

  window.clearCustomCalendar = function() {
    var t = todayMidnight();
    cal.viewYear      = t.getFullYear();
    cal.viewMonth     = t.getMonth();
    cal.selectedStart = null;
    cal.selectedEnd   = null;
    cal.hoverDate     = null;
    render();
  };
})();
</script>
```

- [ ] **Stap 2: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: custom vanilla JS datepicker — 2 maanden, range-selectie, hover-preview"
```

---

## Task 4: Integreer met booking popup

**Files:**
- Modify: `wellness-arr-c.html` (booking popup IIFE)

- [ ] **Stap 1: Controleer dat de tijdelijke aanroep uit Task 1 correct staat**

In `openBookingPopup()` moet staan (toegevoegd in Task 1, stap 5):
```js
    if (window.initCustomCalendar) {
      window.initCustomCalendar(function(start, end) {
        selectedDates = start && end ? [start, end] : [];
        updateSummary();
      });
    }
```

Als dat er nog niet staat, voeg het nu toe ter vervanging van de `setTimeout(initFlatpickr, 50)` regel.

- [ ] **Stap 2: Voeg clearCustomCalendar toe bij popup close**

Zoek de `closeBookingPopup()` functie:
```js
  function closeBookingPopup() {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
    btnDirectBook.hidden = false;
    document.getElementById('bookingModal').classList.remove('has-preselected');
  }
```

Voeg `window.clearCustomCalendar && window.clearCustomCalendar();` toe aan het einde:
```js
  function closeBookingPopup() {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
    btnDirectBook.hidden = false;
    document.getElementById('bookingModal').classList.remove('has-preselected');
    if (window.clearCustomCalendar) window.clearCustomCalendar();
  }
```

- [ ] **Stap 3: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: integreer custom datepicker met booking popup — open/close lifecycle"
```

---

## Task 5: Handmatig testen via Playwright

**Files:** geen wijzigingen

- [ ] **Stap 1: Push naar main en wacht op deploy**

```bash
git push origin main
# Wacht ~35 seconden
```

- [ ] **Stap 2: Open popup op desktop en controleer breedte**

Gebruik Playwright browser_navigate naar `https://visit.asteria.nl/wellness-arr-c` en klik een CTA. Verwacht:
- Kalender vult volledige modal breedte
- Twee maanden naast elkaar zichtbaar
- Navigatiepijlen tonen huidige en volgende maand

- [ ] **Stap 3: Test datum-selectie**

Klik op een aankomstdatum (bijv. 31e van de lopende maand). Verwacht:
- Dag krijgt rode achtergrond (`is-start`)
- Samenvatting toont aankomstdatum
- "Volgende" knop blijft disabled

Klik dan op een vertrekdatum. Verwacht:
- Vertrekdag rood, tussenliggende dagen lichtroze (`is-in-range`)
- Samenvatting toont beide datums + aantal nachten
- "Volgende" knop wordt enabled

- [ ] **Stap 4: Test maand-grens gebruik case**

Selecteer aankomst op de 31e van de lopende maand en vertrek op de 2e van de volgende maand (zichtbaar in de rechtermaand). Verwacht: range overspant de maandgrens, highlight doorloopt beide maandkolommen.

- [ ] **Stap 5: Test hover preview**

Selecteer een aankomstdatum en beweeg over andere dagen. Verwacht: lichtroze hover-range zichtbaar tijdens zweefbeweging. Verlaat de kalender → hover-range verdwijnt.

- [ ] **Stap 6: Test mobile (375px)**

```js
// In browser_run_code_unsafe:
await page.setViewportSize({ width: 375, height: 812 });
await page.goto('https://visit.asteria.nl/wellness-arr-c');
```

Klik een CTA. Verwacht:
- Twee maanden gestapeld (onder elkaar)
- Elke maand volledige breedte
- Modal scrollt verticaal om tweede maand te bereiken

- [ ] **Stap 7: Test heropenen popup**

Sluit de popup en open opnieuw. Verwacht: kalender reset naar huidige maand, geen selectie meer.

- [ ] **Stap 8: Commit (geen code — alleen als er kleine fixes zijn)**

```bash
git add wellness-arr-c.html
git commit -m "fix: datepicker — kleine correcties na manuele test"
```

---

## Zelf-review notities

**Spec dekking:**
- ✅ Twee maanden naast elkaar desktop / gestapeld mobile
- ✅ Maand-grens use case (31e aankomst)
- ✅ Range-selectie: start, end, swap, reset
- ✅ Hover preview
- ✅ Disabled verleden datums
- ✅ Navigatie prev/next
- ✅ Integratie met `selectedDates` en `updateSummary()`
- ✅ Verwijdering Flatpickr dependency
- ✅ `clearCustomCalendar()` bij sluiten popup

**Type consistency:**
- `initCustomCalendar(callback)` — consistent in Task 3 (definitie) en Task 1+4 (gebruik)
- `clearCustomCalendar()` — consistent in Task 3 (definitie) en Task 4 (gebruik)
- `selectedDates` — array van `Date` objecten, gevoed via callback, matches bestaand gebruik in `updateSummary()`, `buildBookingUrl()`, `btnToStep2`, `btnDirectBook`, `btnConfirm`
- `isBefore(a, b)` / `isSameDay(a, b)` — consistent door heel de IIFE
