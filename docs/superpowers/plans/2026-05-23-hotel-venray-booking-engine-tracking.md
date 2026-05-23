# hotel-venray: Mews Widget + Google Ads Tracking

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vervang de deeplink `window.open` aanpak door de Mews inline widget in `hotel-venray.html` (en sync naar `lander-google.html`), plus voeg Google Ads conversion tracking toe.

**Architecture:** De Mews widget wordt geladen via een async script in `<head>`. Een `launchMews()` functie vervangt alle `window.open(buildBookingUrl(...))` calls. Bij het openen van Mews wordt een GA4 + Google Ads conversion event gestuurd. `lander-google.html` is bijna identiek aan `hotel-venray.html` (4 regels verschil) en krijgt dezelfde patch.

**Tech Stack:** Vanilla JS, Mews Distributor JS API, Google Ads gtag.js

---

## Voorkennis — exacte locaties in hotel-venray.html

| Wat | Regel |
|-----|-------|
| `</head>` (waar Mews snippet voor komt) | ~lijn 50 (voor structured data) |
| Booking IIFE start | ~lijn 3774 |
| `MEWS_BASE` var | lijn 3775 |
| `buildBookingUrl()` | lijn 3862 |
| `window.open` #1 — stap 1→Mews (kamer pregeselecteerd) | lijn 3970 |
| `window.open` #2 — "Boek direct zonder kamerkeuze" | lijn 4003 |
| `window.open` #3 — stap 2 confirm | lijn 4124 |
| Einde booking IIFE | lijn 4128 |

**Mews widget API (beschikbare methodes):**
- `api.setStartDate(Date)`
- `api.setEndDate(Date)`
- `api.setVoucherCode(string)`
- `api.open()`

**Voucher in hotel-venray:** Geen vaste VOUCHER — de pagina heeft `pendingVoucherCode` als variabele (gevuld bij arrangement-CTAs zoals 2026WELLNESS). Dit wordt doorgegeven aan `setVoucherCode`.

---

## File Map

| Bestand | Actie |
|---------|-------|
| `hotel-venray.html` | Modify — Mews widget snippet + `launchMews()` + tracking |
| `lander-google.html` | Modify — zelfde patch (sync) |

---

## Task 1: Mews widget snippet toevoegen aan hotel-venray.html

**Files:**
- Modify: `hotel-venray.html` (~lijn 48, voor `<!-- Revinate Contact API -->`)

- [ ] **Step 1: Lees de huidige head sectie**

```bash
sed -n '48,55p' hotel-venray.html
```

Verwachte output: Revinate script tag + structured data start.

- [ ] **Step 2: Voeg Mews widget snippet in vóór de Revinate tag**

Zoek in hotel-venray.html naar:

```html
  <!-- Revinate Contact API -->
```

Vervang door:

```html
  <!-- Mews BookingEngine widget -->
  <script>
  (function(m,e,w,s){c=m.createElement(e);c.onload=function(){
    Mews.Distributor({configurationIds:[s]},function(api){
      window.mewsApi=api;
      if(window._mewsPending){window._mewsPending();window._mewsPending=null;}
    });
  };c.async=1;c.src=w;t=m.getElementsByTagName(e)[0];t.parentNode.insertBefore(c,t);
  })(document,'script','https://app.mews.com/distributor/distributor.min.js','6dc9094c-76e3-4fd8-83a7-af1d00ffc556');
  </script>
  <!-- End Mews BookingEngine -->

  <!-- Revinate Contact API -->
```

- [ ] **Step 3: Verifieer de snippet staat op de juiste plek**

```bash
grep -n "mewsApi\|Revinate\|Mews.Distributor" hotel-venray.html | head -10
```

Verwacht: `Mews.Distributor` op een lagere regel dan `mewsApi`, beide vóór lijn 60.

---

## Task 2: `launchMews()` toevoegen en `window.open` vervangen in hotel-venray.html

**Files:**
- Modify: `hotel-venray.html` (booking IIFE, ~lijn 3774–4128)

- [ ] **Step 1: Voeg `launchMews()` toe vóór de eerste `window.open` in de booking IIFE**

Zoek in hotel-venray.html naar:

```javascript
  function buildBookingUrl(checkin, checkout, roomKey) {
```

Voeg DIRECT DAARVOOR in:

```javascript
  function launchMews(checkin, checkout, roomKey) {
    closeBookingPopup();
    function doOpen() {
      window.mewsApi.setStartDate(checkin);
      window.mewsApi.setEndDate(checkout);
      if (pendingVoucherCode) window.mewsApi.setVoucherCode(pendingVoucherCode);
      window.mewsApi.open();
    }
    if (window.mewsApi) {
      doOpen();
    } else {
      window._mewsPending = doOpen;
      setTimeout(function() {
        if (window._mewsPending) {
          window._mewsPending = null;
          window.open(buildBookingUrl(checkin, checkout, roomKey), '_blank', 'noopener');
        }
      }, 4000);
    }
  }

```

- [ ] **Step 2: Vervang `window.open` #1 — stap 1 (kamer pregeselecteerd, ~lijn 3970)**

Zoek:

```javascript
      if (window.track) window.track('mews_click', { room_key: selectedRoomKey });
      window.open(buildBookingUrl(selectedDates[0], selectedDates[1], selectedRoomKey), '_blank', 'noopener');
      closeBookingPopup();
      return;
```

Vervang door:

```javascript
      if (window.track) window.track('mews_click', { room_key: selectedRoomKey });
      if (typeof gtag === 'function') gtag('event', 'conversion', { send_to: window.GA_ADS_LABEL });
      launchMews(selectedDates[0], selectedDates[1], selectedRoomKey);
      return;
```

- [ ] **Step 3: Vervang `window.open` #2 — "Boek direct zonder kamerkeuze" (~lijn 4003)**

Zoek:

```javascript
    if (window.track) window.track('mews_click', { room_key: null });
    window.open(buildBookingUrl(selectedDates[0], selectedDates[1], null), '_blank', 'noopener');
    closeBookingPopup();
```

Vervang door:

```javascript
    if (window.track) window.track('mews_click', { room_key: null });
    if (typeof gtag === 'function') gtag('event', 'conversion', { send_to: window.GA_ADS_LABEL });
    launchMews(selectedDates[0], selectedDates[1], null);
```

- [ ] **Step 4: Vervang `window.open` #3 — stap 2 confirm (~lijn 4124)**

Zoek:

```javascript
    if (window.track) window.track('mews_click', { room_key: selectedRoomKey });
    window.open(buildBookingUrl(selectedDates[0], selectedDates[1], selectedRoomKey), '_blank', 'noopener');
    closeBookingPopup();
```

Vervang door:

```javascript
    if (window.track) window.track('mews_click', { room_key: selectedRoomKey });
    if (typeof gtag === 'function') gtag('event', 'conversion', { send_to: window.GA_ADS_LABEL });
    launchMews(selectedDates[0], selectedDates[1], selectedRoomKey);
```

- [ ] **Step 5: Verifieer er geen `window.open` meer is in de booking IIFE**

```bash
grep -n "window\.open" hotel-venray.html
```

Verwacht: 0 resultaten in de booking IIFE (lijn 3774–4128). Alleen in `launchMews` zelf (als fallback) mag `window.open` nog staan.

---

## Task 3: Google Ads tracking toevoegen aan hotel-venray.html

**Files:**
- Modify: `hotel-venray.html` (in `<head>`, vóór Mews snippet)

**Vereiste info (vraag Bart):**
- Google Ads Account ID: formaat `AW-XXXXXXXXXX`
- Conversion label: formaat `XXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXX`
- GA4 Measurement ID (optioneel, als er al een property is): formaat `G-XXXXXXXXXX`

**Totale `send_to` waarde:** `AW-XXXXXXXXXX/CONVERSION_LABEL`

- [ ] **Step 1: Voeg GA4 + Google Ads gtag snippet toe in `<head>` (direct na `<link rel="stylesheet" href="brand.css">`)**

Zoek:

```html
  <link rel="stylesheet" href="brand.css">

  <!-- A/B: USP variant toewijzing
```

Voeg DAARTUSSEN in (vervang `AW-XXXXXXXXXX` en `G-XXXXXXXXXX` met echte IDs):

```html
  <!-- Google tag (gtag.js) — GA4 + Google Ads -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=AW-XXXXXXXXXX"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){ dataLayer.push(arguments); }
    gtag('js', new Date());
    gtag('config', 'AW-XXXXXXXXXX');   // Google Ads
    gtag('config', 'G-XXXXXXXXXX');    // GA4 (optioneel)

    // Conversion label — ingesteld als globale var zodat launchMews het kan lezen
    window.GA_ADS_LABEL = 'AW-XXXXXXXXXX/CONVERSION_LABEL';
  </script>

```

- [ ] **Step 2: Verifieer gtag aanwezig is**

```bash
grep -n "gtag\|GA_ADS_LABEL\|googletagmanager" hotel-venray.html | head -10
```

Verwacht: gtag definitie op ~lijn 32–45, `GA_ADS_LABEL` op ~lijn 45, `GA_ADS_LABEL` referentie op 3 plekken in de booking IIFE.

---

## Task 4: Zelfde wijzigingen toepassen op lander-google.html

`lander-google.html` is bijna identiek aan `hotel-venray.html`. De regelnummers zijn gelijk.

- [ ] **Step 1: Pas exact dezelfde drie wijzigingen toe**

Herhaal Task 1 (Mews snippet), Task 2 (launchMews + window.open vervangen), Task 3 (gtag) — maar dan in `lander-google.html`.

- [ ] **Step 2: Verifieer geen `window.open` in de booking IIFE van lander-google.html**

```bash
grep -n "window\.open" lander-google.html
```

Verwacht: alleen in de `launchMews` fallback.

---

## Task 5: Commit en deploy

- [ ] **Step 1: Commit**

```bash
git add hotel-venray.html lander-google.html
git commit -m "feat: Mews inline widget + Google Ads conversion tracking op hotel-venray + lander-google"
git push
```

- [ ] **Step 2: Wacht op Cloudflare deploy (~35 seconden)**

- [ ] **Step 3: Test booking flow op hotel-venray**

Open `https://visit.asteria.nl/hotel-venray` → klik "Boek nu" → selecteer datum → klik "Volgende" of "Boek direct" → verwacht: Mews widget opent IN de pagina (niet nieuw tabblad).

- [ ] **Step 4: Verifieer Google Ads conversion in browser console**

Open DevTools → Console → filter op `gtag`. Nadat je op "Boek nu" klikt en doorgaat tot Mews, verwacht:

```
gtag called with: conversion { send_to: 'AW-XXXXXXXXXX/CONVERSION_LABEL' }
```

Of zie in Network tab een request naar `https://www.google.com/pagead/...` na de booking click.

---

## Google Ads setup — wat Bart moet doen in de Google Ads interface

Dit is buiten de code. Zodra de tracking code live staat:

1. **Ga naar:** Google Ads → Doelen → Conversies → Nieuwe conversieactie
2. **Type:** Website
3. **Categorie:** Aankoop / Reservering
4. **Naam:** "Mews widget geopend" (of "Boeking gestart")
5. **Waarde:** Gebruik een vaste waarde (bijv. €15 als gemiddelde commissiebesparing) of geen waarde
6. **Tag instelling:** Gebruik bestaande Google-tag — kies de tag die je in Task 3 hebt toegevoegd
7. **Event naam:** `conversion` (dat is wat de code stuurt)
8. **Kopieer het Conversion Label** dat Google Ads genereert → vul in bij `GA_ADS_LABEL` in de code

### Google Ads campagne koppelen (branded search)

- Campagne type: Zoek
- Zoekwoorden: "hotel asteria", "hotel venray", "hotel venray boeken" (branded)
- Final URL: `https://visit.asteria.nl/hotel-venray`
- Tracking template (optioneel): `{lpurl}?utm_source=google&utm_medium=cpc&utm_campaign=branded`
- Conversie: koppel aan de conversieactie die je net aangemaakt hebt

---

## Bekende risico's

- `pendingVoucherCode` is `null` bij normale boeking — `setVoucherCode(null)` is onschadelijk in de Mews API
- Als de Mews widget niet laadt binnen 4s (traag netwerk), valt de code terug op `window.open` deeplink — booking gaat door
- Google Ads conversion ID/label zijn placeholders — pagina functioneert normaal zonder, tracking werkt pas na invullen
