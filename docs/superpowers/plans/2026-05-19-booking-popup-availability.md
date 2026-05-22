# Booking Popup — Availability & UX Fixes

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Haal live beschikbaarheid op uit Mews zodra de gebruiker datums selecteert in de booking popup, toon prijzen en grijs vol-kamers uit in stap 2. Fix daarnaast de bug dat stap 2 niet overgeslagen wordt als de gebruiker al een kamer heeft gekozen via de kamertypes popup.

**Architecture:** De bestaande Cloudflare Functions proxy `/mews/[[path]].js` stuurt POST-requests door naar `https://api.mews.com`. We roepen `/mews/api/distributor/v1/hotels/getAvailability` aan vanuit de booking popup IIFE in `wellness-arr-c.html`. Resultaat wordt gecached per datum-paar zodat schakelen tussen stap 1 en 2 geen extra requests triggert.

**Tech Stack:** Vanilla JS (geen extra dependencies), bestaande `/mews/[[path]].js` proxy, Mews Booking Engine API v1.

---

## IDs & constanten (hardcoded in wellness-arr-c.html)

```
ConfigurationId: 9fc01bd9-bc04-49f2-83cf-b44400835224
HotelId:         65a522c9-4828-413d-9ad8-af1d00ffb83f
Client:          "Asteria Pages 1.0.0"
VoucherCode:     "WELLNESS"
```

Category IDs per kamertype (al aanwezig in `ROOMS`):
```
comfort:       98900f3b-e5e2-49c9-9776-af1d00ffc315
royale:        a8fd7310-0d61-422f-89e6-af1d00ffc315
deluxe:        c737de50-e41e-4c8d-a818-af1d00ffc315
junior-suite:  27ea8deb-ded5-4856-8fdd-af1d00ffc315
suite:         4a642b66-68e6-444c-beeb-af1d00ffc315
bruidssuite:   a9f18d18-561b-47a9-8ba7-b2a800cfd0e2
```

---

## Task 1: Fix — sla stap 2 over als kamer al geselecteerd

**Probleem:** `btnToStep2` handler checkt `window.selectedRoomId`, maar die wordt op `null` gezet door `closePopup()` van de kamer-popup vóórdat de check uitgevoerd wordt. De lokale variabele `selectedRoomKey` (gezet via `openBookingPopup(preselectedRoomKey)`) is correct.

**Files:**
- Modify: `wellness-arr-c.html` — `btnToStep2.addEventListener` handler (zoek op `window.selectedRoomId`)

- [ ] **Stap 1: Zoek de bug op**

```bash
grep -n "selectedRoomId\|selectedRoomKey" /Users/bartvandersterren/Projects/asteria-pages/wellness-arr-c.html
```

Verwacht: `window.selectedRoomId` in de `btnToStep2` handler, `selectedRoomKey` als lokale var.

- [ ] **Stap 2: Vervang de check**

Zoek in `btnToStep2.addEventListener` dit blok:
```javascript
    // Als er al een kamer geselecteerd is, sla stap 2 over
    if (window.selectedRoomId) {
      window.open(buildBookingUrl(selectedDates[0], selectedDates[1], window.selectedRoomId), '_blank', 'noopener');
      closeBookingPopup();
      return;
    }
```

Vervang door:
```javascript
    // Als er al een kamer geselecteerd is (via kamerpopup), sla stap 2 over
    if (selectedRoomKey) {
      window.open(buildBookingUrl(selectedDates[0], selectedDates[1], selectedRoomKey), '_blank', 'noopener');
      closeBookingPopup();
      return;
    }
```

- [ ] **Stap 3: Test**

1. Open `wellness-arr-c.html` in browser (of live URL)
2. Klik op een kamertype → popup opent → klik "Boek dit arrangement"
3. Booking popup opent op stap 1 (datum)
4. Selecteer een datum range → klik "Volgende stap"
5. Verwacht: Mews opent direct in nieuw tabblad, stap 2 wordt NIET getoond

- [ ] **Stap 4: Commit**

```bash
cd /Users/bartvandersterren/Projects/asteria-pages
git add wellness-arr-c.html
git commit -m "fix: booking-popup — sla stap 2 over bij pre-geselecteerde kamer"
```

---

## Task 2: Update buildBookingUrl met mewsRoute

**Files:**
- Modify: `wellness-arr-c.html` — functie `buildBookingUrl`

- [ ] **Stap 1: Vervang buildBookingUrl**

Zoek:
```javascript
  function buildBookingUrl(checkin, checkout, roomKey) {
    var url = MEWS_BASE + '?mewsStart=' + toYMD(checkin)
      + '&mewsEnd='   + toYMD(checkout);
    if (roomKey && window.ROOMS && window.ROOMS[roomKey] && window.ROOMS[roomKey].mewsCategoryId) {
      url += '&mewsCategories[0]=' + window.ROOMS[roomKey].mewsCategoryId;
    }
    return url;
  }
```

Vervang door:
```javascript
  function buildBookingUrl(checkin, checkout, roomKey) {
    var url = MEWS_BASE + '?mewsStart=' + toYMD(checkin)
      + '&mewsEnd='   + toYMD(checkout);
    if (roomKey && window.ROOMS && window.ROOMS[roomKey] && window.ROOMS[roomKey].mewsCategoryId) {
      var catId = window.ROOMS[roomKey].mewsCategoryId;
      url += '&mewsRoute=rates&mewsRoom=' + catId;
    } else {
      url += '&mewsRoute=rooms';
    }
    return url;
  }
```

- [ ] **Stap 2: Test deeplinks**

Controleer handmatig dat de gegenereerde URLs kloppen:
- Met kamer: `?mewsStart=...&mewsEnd=...&mewsRoute=rates&mewsRoom=<uuid>` → Mews opent op tarieven-stap voor die kamer
- Zonder kamer: `?mewsStart=...&mewsEnd=...&mewsRoute=rooms` → Mews opent op kamerkeuze

- [ ] **Stap 3: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: booking-popup — mewsRoute deeplinks (rates/rooms)"
```

---

## Task 3: Availability fetch functie

**Files:**
- Modify: `wellness-arr-c.html` — booking popup IIFE, nieuwe functie `fetchAvailability`

De Mews Booking Engine API endpoint: `POST https://api.mews.com/api/distributor/v1/hotels/getAvailability`
Via onze proxy: `POST /mews/api/distributor/v1/hotels/getAvailability`

Response bevat `RoomCategoryAvailabilities`: array met per kamer `RoomCategoryId` en `AvailableRoomCount`.

- [ ] **Stap 1: Voeg availability cache en fetch functie toe**

Voeg toe direct ná de `toYMD` functie en vóór `buildBookingUrl` in de booking popup IIFE:

```javascript
  var availabilityCache = {}; // key: "YYYY-MM-DD|YYYY-MM-DD" → { categoryId: { available, lowestPrice } }

  function fetchAvailability(checkin, checkout, callback) {
    var cacheKey = toYMD(checkin) + '|' + toYMD(checkout);
    if (availabilityCache[cacheKey]) { callback(null, availabilityCache[cacheKey]); return; }

    var categoryIds = Object.values(window.ROOMS).map(function (r) { return r.mewsCategoryId; });

    fetch('/mews/api/distributor/v1/hotels/getAvailability', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        Client: 'Asteria Pages 1.0.0',
        ConfigurationId: '9fc01bd9-bc04-49f2-83cf-b44400835224',
        HotelId: '65a522c9-4828-413d-9ad8-af1d00ffb83f',
        StartUtc: toYMD(checkin) + 'T12:00:00Z',
        EndUtc: toYMD(checkout) + 'T12:00:00Z',
        VoucherCode: 'WELLNESS',
        CategoryIds: categoryIds
      })
    })
    .then(function (res) { return res.json(); })
    .then(function (data) {
      var result = {};
      var avails = data.RoomCategoryAvailabilities || [];
      avails.forEach(function (a) {
        // Laagste prijs: eerste Rate van eerste beschikbaarheidsoptie
        var lowestPrice = null;
        if (a.RoomOccupancyAvailabilities && a.RoomOccupancyAvailabilities.length) {
          var firstOcc = a.RoomOccupancyAvailabilities[0];
          if (firstOcc.Pricing && firstOcc.Pricing.length) {
            var pricing = firstOcc.Pricing[0];
            if (pricing.Price && pricing.Price.GrossValue != null) {
              lowestPrice = pricing.Price.GrossValue;
            }
          }
        }
        result[a.RoomCategoryId] = {
          available: a.AvailableRoomCount > 0,
          lowestPrice: lowestPrice
        };
      });
      availabilityCache[cacheKey] = result;
      callback(null, result);
    })
    .catch(function (err) {
      callback(err, null);
    });
  }
```

- [ ] **Stap 2: Test de fetch in de browser console**

Open de pagina, open devtools console, plak dit (pas datums aan op toekomstige beschikbare datum):

```javascript
// Tijdelijk test — roept de echte functie aan
var d1 = new Date('2026-07-01'); var d2 = new Date('2026-07-02');
fetch('/mews/api/distributor/v1/hotels/getAvailability', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    Client: 'Asteria Pages 1.0.0',
    ConfigurationId: '9fc01bd9-bc04-49f2-83cf-b44400835224',
    HotelId: '65a522c9-4828-413d-9ad8-af1d00ffb83f',
    StartUtc: '2026-07-01T12:00:00Z',
    EndUtc: '2026-07-02T12:00:00Z',
    VoucherCode: 'WELLNESS',
    CategoryIds: ['98900f3b-e5e2-49c9-9776-af1d00ffc315']
  })
}).then(r => r.json()).then(console.log);
```

Verwacht: JSON response met `RoomCategoryAvailabilities` array. Als de response een 4xx bevat, check of de Client naam geregistreerd moet worden bij Mews (zie troubleshooting hieronder).

**Troubleshooting:** Als de API `401` of `403` geeft, is de `Client` string niet geregistreerd. Gebruik dan tijdelijk `"My Client 1.0.0"` voor demo-omgeving tests, of vraag Mews Support om productie-registratie van `"Asteria Pages 1.0.0"`.

- [ ] **Stap 3: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: booking-popup — fetchAvailability via Mews proxy"
```

---

## Task 4: Loading state op stap 1 + fetch trigger bij datumkeuze

**Files:**
- Modify: `wellness-arr-c.html` — `updateSummary` en `btnToStep2` handler

Zodra de gebruiker twee datums selecteert, start de fetch alvast op de achtergrond. Bij klik op "Volgende stap" wacht de popup op het resultaat (of gaat direct door als al beschikbaar).

- [ ] **Stap 1: Voeg loading state variabele toe**

Voeg toe direct ná `var selectedRoomKey = null;` in de booking popup IIFE:

```javascript
  var availabilityResult = null;   // gevuld door fetchAvailability
  var availabilityLoading = false; // true terwijl fetch loopt
```

- [ ] **Stap 2: Trigger fetch in updateSummary**

Vervang de huidige `updateSummary` functie:

```javascript
  function updateSummary() {
    if (selectedDates.length === 2) {
      var diff = Math.round((selectedDates[1] - selectedDates[0]) / 86400000);
      elAankomst.textContent = formatDate(selectedDates[0]);
      elVertrek.textContent  = formatDate(selectedDates[1]);
      elNachten.textContent  = diff + (diff === 1 ? ' nacht' : ' nachten');
      btnToStep2.disabled    = false;
      btnDirectBook.disabled = false;

      // Start availability fetch alvast op achtergrond
      availabilityResult  = null;
      availabilityLoading = true;
      fetchAvailability(selectedDates[0], selectedDates[1], function (err, result) {
        availabilityLoading = false;
        availabilityResult  = err ? null : result;
      });
    } else {
      elAankomst.textContent = '\u2014';
      elVertrek.textContent  = '\u2014';
      elNachten.textContent  = '\u2014';
      btnToStep2.disabled    = true;
      btnDirectBook.disabled = true;
      availabilityResult  = null;
      availabilityLoading = false;
    }
  }
```

- [ ] **Stap 3: Wacht op fetch bij klik "Volgende stap"**

Vervang in `btnToStep2.addEventListener` het blok dat stap 2 rendert (het `else` pad na de `selectedRoomKey` check):

```javascript
    // Wacht op availability als nog bezig
    if (availabilityLoading) {
      btnToStep2.textContent = 'Laden\u2026';
      btnToStep2.disabled = true;
      var poll = setInterval(function () {
        if (!availabilityLoading) {
          clearInterval(poll);
          btnToStep2.textContent = 'Kies een kamer';
          btnToStep2.disabled = false;
          step1.hidden = true;
          step2.hidden = false;
          renderRoomCards(availabilityResult);
        }
      }, 100);
      return;
    }

    // Availability beschikbaar (of gefaald — dan renderen zonder data)
    step1.hidden = true;
    step2.hidden = false;
    renderRoomCards(availabilityResult);
```

- [ ] **Stap 4: Reset bij popup open**

Voeg toe in `openBookingPopup`, direct ná `selectedDates = [];`:

```javascript
    availabilityResult  = null;
    availabilityLoading = false;
```

- [ ] **Stap 5: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: booking-popup — availability fetch op achtergrond bij datumkeuze"
```

---

## Task 5: Toon beschikbaarheid en prijzen in stap 2

**Files:**
- Modify: `wellness-arr-c.html` — `renderRoomCards` functie + CSS

`renderRoomCards` krijgt nu een `availability` argument (object `{ categoryId: { available, lowestPrice } }` of `null`).

- [ ] **Stap 1: Update renderRoomCards signatuur en logica**

Vervang de huidige `function renderRoomCards()` volledig door:

```javascript
  function renderRoomCards(availability) {
    var ROOM_KEYS = ['comfort', 'royale', 'deluxe', 'junior-suite', 'suite', 'bruidssuite'];
    selectedRoomKey = null;
    var firstAvailableKey = null;

    elRooms.innerHTML = ROOM_KEYS.map(function (key) {
      var r = window.ROOMS[key];
      var avail = availability && r.mewsCategoryId && availability[r.mewsCategoryId];
      var isAvailable  = !availability || !avail || avail.available; // bij null data: alles beschikbaar tonen
      var lowestPrice  = avail && avail.lowestPrice;
      var priceLabel   = lowestPrice ? '\u20ac\u00a0' + Math.round(lowestPrice) : '';
      var volLabel     = availability && avail && !avail.available ? '<span class="bk-room-card__vol">Vol</span>' : '';

      if (isAvailable && !firstAvailableKey) firstAvailableKey = key;

      return '<div class="bk-room-card' + (!isAvailable ? ' is-unavailable' : '') + '" data-key="' + key + '" role="radio" aria-checked="false" tabindex="' + (isAvailable ? '0' : '-1') + '">' +
        '<div class="bk-room-card__header">' +
          '<div class="bk-room-card__radio"></div>' +
          '<span class="bk-room-card__name">' + r.name + '</span>' +
          '<span class="bk-room-card__upgrade">' + r.upgrade + '</span>' +
          (priceLabel ? '<span class="bk-room-card__price">' + priceLabel + '</span>' : '') +
          volLabel +
          '<button class="bk-room-card__toggle" data-key="' + key + '" tabindex="-1" aria-expanded="false">meer info</button>' +
        '</div>' +
        '<div class="bk-room-card__details" id="bk-details-' + key + '">' + r.shortDesc + '</div>' +
      '</div>';
    }).join('');

    // Selecteer eerste beschikbare kamer
    if (firstAvailableKey) {
      var firstCard = elRooms.querySelector('[data-key="' + firstAvailableKey + '"]');
      if (firstCard) { firstCard.classList.add('is-selected'); firstCard.setAttribute('aria-checked', 'true'); }
      selectedRoomKey = firstAvailableKey;
    }

    // Klik op card → selecteer (alleen beschikbare kamers)
    elRooms.querySelectorAll('.bk-room-card:not(.is-unavailable)').forEach(function (card) {
      card.addEventListener('click', function (e) {
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

    // Accordion toggle
    elRooms.querySelectorAll('.bk-room-card__toggle').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var k = btn.getAttribute('data-key');
        var details = document.getElementById('bk-details-' + k);
        var isOpen = details.classList.contains('is-open');
        details.classList.toggle('is-open', !isOpen);
        btn.setAttribute('aria-expanded', String(!isOpen));
        btn.textContent = !isOpen ? 'minder' : 'meer info';
      });
    });
  }
```

- [ ] **Stap 2: Voeg CSS toe voor unavailable en prijs**

Zoek in de `<style>` tag de bestaande `.bk-room-card` CSS. Voeg direct erna toe:

```css
.bk-room-card.is-unavailable {
  opacity: 0.45;
  pointer-events: none;
  cursor: not-allowed;
}
.bk-room-card__vol {
  margin-left: auto;
  font-size: 11px;
  font-weight: 700;
  color: #c23435;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.bk-room-card__price {
  margin-left: auto;
  font-size: 13px;
  font-weight: 700;
  color: #2d2d2d;
}
```

- [ ] **Stap 3: Fix btnConfirm — skip als geen kamer beschikbaar**

In `btnConfirm.addEventListener`, voeg guard toe:

```javascript
  btnConfirm.addEventListener('click', function () {
    if (selectedDates.length < 2 || !selectedRoomKey) return;
    window.open(buildBookingUrl(selectedDates[0], selectedDates[1], selectedRoomKey), '_blank', 'noopener');
    closeBookingPopup();
  });
```

- [ ] **Stap 4: Handmatige test**

1. Open popup → selecteer datums waarbij je weet dat één kamertype vol zit
2. Klik "Kies een kamer" → stap 2 toont kamers
3. Vol-kamers zijn uitgegraad en niet klikbaar
4. Beschikbare kamers tonen prijs + zijn selecteerbaar
5. "Boek dit arrangement" opent Mews op juiste stap

- [ ] **Stap 5: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: booking-popup — beschikbaarheid en prijzen in stap 2"
```

---

## Troubleshooting

**API geeft 401/403:** De `Client` string `"Asteria Pages 1.0.0"` is niet geregistreerd bij Mews. Opties:
1. Mail Mews Support: registreer `"Asteria Pages 1.0.0"` voor productie (`api.mews.com`)
2. Tijdelijk: controleer of de bestaande proxy-headers (`Origin: https://apps.mews.com`) voldoende zijn — die zaten al in de Connector proxy maar zijn mogelijk niet geldig voor de Distributor API

**API geeft lege RoomCategoryAvailabilities:** Datum is vol of te ver in de toekomst. Test met een datum over 2-4 weken.

**Prijzen zijn null:** De response-structuur van `RoomOccupancyAvailabilities[0].Pricing[0].Price.GrossValue` kan per hotel anders zijn. Log de volledige response en pas het pad aan.
