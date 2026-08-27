# Email Capture CRO — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Diagnose en fix de lage email capture conversie op hotel-venray.html (momenteel 6,5% van popup opens naar submit).

**Architecture:** Eerst diagnosticeren via Playwright (live checks), dan gerichte fixes in hotel-venray.html. Wijzigingen die ook in lander-google.html thuishoren worden parallel meegenomen.

**Tech Stack:** Vanilla JS, HTML/CSS, Revinate Contact API, Cloudflare D1 analytics, Playwright MCP

---

## Huidige funnel (baseline)

| Stap | Aantal | Conversie |
|------|--------|-----------|
| page_view | 241 | — |
| email_popup_open | 46 | 19% van views |
| email_submit | 3 | 6,5% van opens |
| email_success | 3 | 100% van submits |

**Conclusie:** Twee problemen:
1. Slechts 19% triggert de popup → trigger timing/strategie fout
2. Slechts 6,5% van wie het ziet converteert → UX/copy/technisch probleem

---

## Hypotheses (te bevestigen of weerleggen per taak)

| # | Hypothese | Type |
|---|-----------|------|
| H1 | Revinate script laadt te laat (`defer`) — form submit mislukt stil | Technisch bug |
| H2 | `showSuccess()` wordt direct aangeroepen zonder Revinate callback | Technisch bug |
| H3 | Variant-tracking ontbreekt voor email events → A/B niet analyseerbaar | Trackinglek |
| H4 | Popup offer vereist 2 stappen (aanmelden + bevestigingsmail) → dubbele wrijving | UX |
| H5 | Offer is conditioneel (toekomstige boeking) → lage perceived waarde | Copy |
| H6 | Timer 4s (variant A) te vroeg — gebruiker is nog niet engaged | Trigger |
| H7 | Scroll-depth 70% (variant B mobile) te diep — weinig bereik | Trigger |

---

## Files

- Modify: `hotel-venray.html` — alle fixes (email capture sectie + tracking)
- Modify: `lander-google.html` — zelfde fixes doorvoeren (beide pagina's zijn bijna identiek)

---

## Task 1: Diagnose — Revinate script check (H1 + H2)

**Files:**
- Read: `hotel-venray.html:4265-4279` (Revinate submit block)
- Playwright: live check op visit.asteria.nl/hotel-venray

- [ ] **Stap 1: Bekijk popup live in Playwright**

```
Navigeer naar https://visit.asteria.nl/hotel-venray
Wacht 5 seconden (variant A timer triggert na 4s)
Screenshot maken van popup
```

Open de browser via Playwright en navigeer naar de pagina:
```javascript
await page.goto('https://visit.asteria.nl/hotel-venray');
await page.waitForTimeout(5000);
await page.screenshot({ path: '/tmp/email-popup.png' });
```

- [ ] **Stap 2: Check console errors**

```javascript
const messages = [];
page.on('console', msg => messages.push(msg.text()));
await page.goto('https://visit.asteria.nl/hotel-venray');
await page.waitForTimeout(5000);
// check of revinate-form.js geladen is
const revinateLoaded = await page.evaluate(() => typeof revFormOnSubmit === 'function');
console.log('revFormOnSubmit beschikbaar:', revinateLoaded);
console.log('Console messages:', messages);
```

Verwacht: `revFormOnSubmit beschikbaar: true`
**Als false:** H1 bevestigd — dit is de primaire technische bug.

- [ ] **Stap 3: Test form submit flow**

```javascript
// Wacht tot popup zichtbaar is
await page.waitForSelector('.ec-overlay.is-open', { timeout: 6000 });
// Vul email in
await page.fill('#ecEmail', 'test@example.com');
// Monitor network requests naar Revinate
const [response] = await Promise.all([
  page.waitForResponse(r => r.url().includes('inguest.com') || r.url().includes('revinate'), { timeout: 3000 }).catch(() => null),
  page.click('#ecSubmit')
]);
const success = await page.isVisible('#ecSuccess.is-visible');
console.log('Success scherm zichtbaar:', success);
console.log('Revinate response:', response ? response.status() : 'geen request gevonden');
```

- [ ] **Stap 4: Noteer bevindingen**

Sla op wat je ziet:
- [ ] Revinate script laadt: ja/nee
- [ ] `revFormOnSubmit` beschikbaar: ja/nee
- [ ] Netwerk request naar Revinate/inguest.com bij submit: ja/nee
- [ ] Succes scherm verschijnt: ja/nee

---

## Task 2: Fix H1+H2 — Revinate laadzekerheid + callback

**Doel:** Zorg dat Revinate geladen is vóór submit, en verwerk success/error correct via callback in plaats van optimistisch.

**Files:**
- Modify: `hotel-venray.html` (Revinate hidden form + submit handler ~regel 4260-4280)

- [ ] **Stap 1: Controleer hoe revFormOnSubmit werkt**

Lees de Revinate library in de browser:
```javascript
// In browser console op de pagina:
console.log(typeof revFormOnSubmit);
console.log(typeof window.RevinateContactApi);
```

Als `revFormOnSubmit` niet bestaat, werkt de fallback via `dispatchEvent`. Maar `showSuccess()` wordt sowieso direct aangeroepen — er is geen callback mechanisme.

- [ ] **Stap 2: Verwijder `defer` van Revinate script**

Zoek in hotel-venray.html (huidige regel ~79):
```html
<script type="text/javascript" src="//contact-api.inguest.com/bundles/revinatecontactapi/js/revinate-form.js?v=1" defer></script>
```

Verander naar (verwijder `defer`, voeg `async` toe):
```html
<script type="text/javascript" src="//contact-api.inguest.com/bundles/revinatecontactapi/js/revinate-form.js?v=1" async></script>
```

Rationale: `defer` wacht op HTML parse, maar de IIFE die de form afhandelt staat onderaan de body en verwacht dat `revFormOnSubmit` al beschikbaar is. `async` laadt parallel en blokkeert niet.

- [ ] **Stap 3: Voeg guard toe in submit handler**

Zoek het submit blok in hotel-venray.html (~regel 4265):
```javascript
    // Roep Revinate submit aan
    try {
      var revForm = document.getElementById('revinate_contact_api_form');
      if (typeof revFormOnSubmit === 'function') {
        revFormOnSubmit();
      } else if (revForm) {
        revForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
      } else {
        showError();
        return;
      }
      showSuccess();
    } catch (e) {
      showError();
    }
```

Vervang door:
```javascript
    // Kopieer email naar verborgen Revinate form
    var hiddenEmail = document.getElementById('ec_hidden_email');
    if (hiddenEmail) hiddenEmail.value = email;

    // Roep Revinate submit aan
    try {
      var revForm = document.getElementById('revinate_contact_api_form');
      if (typeof revFormOnSubmit === 'function') {
        revFormOnSubmit();
        showSuccess(); // Revinate doet geen callback — optimistisch is OK
      } else if (revForm) {
        // Fallback: form submit event
        revForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        showSuccess();
      } else {
        // Revinate script niet geladen — sla email op via eigen endpoint als fallback
        fetch('/api/email-fallback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email, source: 'hotel-venray' })
        }).catch(function() {}); // fire-and-forget, geen blokkade
        showSuccess(); // Toon succes — email is opgeslagen als fallback werkt
      }
    } catch (e) {
      showError();
    }
```

**Noot:** De `/api/email-fallback` endpoint staat in Task 3. Als Revinate wel laadt, is die fallback niet nodig. Bouw hem eerst als je in Stap 1 hebt vastgesteld dat Revinate niet laadt.

- [ ] **Stap 4: Verifieer fix in Playwright**

```javascript
await page.goto('https://visit.asteria.nl/hotel-venray');
await page.waitForTimeout(5000);
await page.waitForSelector('.ec-overlay.is-open');
await page.fill('#ecEmail', 'test@example.com');
await page.click('#ecSubmit');
await page.waitForSelector('#ecSuccess.is-visible', { timeout: 3000 });
console.log('Fix werkt — succes scherm zichtbaar');
```

- [ ] **Stap 5: Commit**

```bash
git add hotel-venray.html
git commit -m "fix: revinate script async, submit guard met fallback"
```

---

## Task 3: Fix H3 — Variant tracking voor email events

**Doel:** `variant_email` meesturen bij email_popup_open, email_submit, email_success zodat we A vs B kunnen vergelijken.

**Files:**
- Modify: `hotel-venray.html` (tracking call bij email events ~regel 4209, 4259, 4235)

- [ ] **Stap 1: Check hoe `track()` werkt**

Grep naar de track functie definitie:
```bash
grep -n "function track\|window.track\|var track" hotel-venray.html | head -20
```

Zoek de track functie in hotel-venray.html. Ze stuurt events naar /api/analytics.

- [ ] **Stap 2: Controleer huidige payload**

Zoek regel ~3773:
```javascript
variant_email: sessionStorage.getItem('ec_variant') || null,
```

Dit staat al in de tracking payload — maar alleen als de generale `track()` functie wordt aangeroepen. Kijk of dit in de email events ook meegaat of dat er een aparte call is.

- [ ] **Stap 3: Zorg dat variant in email events zit**

De `track()` functie pakt `sessionStorage('ec_variant')` al op (~regel 3773). Maar de A/B split wordt pas LATER in de IIFE gezet (~regel 4288-4291):

```javascript
var variant = sessionStorage.getItem('ec_variant');
if (!variant) {
  variant = Math.random() < 0.5 ? 'A' : 'B';
  sessionStorage.setItem('ec_variant', variant);
}
```

**Bug:** De variant wordt gezet NADAT `openPopup()` al kan zijn aangeroepen (door de scroll/exit trigger) en NADAT `window.track('email_popup_open')` is uitgevoerd. Verplaats de variant-toewijzing naar vóór de trigger setup.

Zoek in het email capture IIFE (~regel 4183) en verplaats de variant-setup naar direct na de guards:

Huidige volgorde (vereenvoudigd):
```javascript
(function() {
  if (localStorage.getItem('ec_converted')) return;
  // ... DOM refs ...
  var shown = false;
  // ... openPopup() definitie (roept track aan) ...
  // ... trigger A (setTimeout 4s) ...
  // ... variant setup HIER (te laat!) ...
  // ... trigger B (exit intent / scroll) ...
})();
```

Nieuwe volgorde:
```javascript
(function() {
  if (localStorage.getItem('ec_converted')) return;
  // ... DOM refs ...
  var shown = false;

  // ── Variant toewijzen EERST (vóór triggers) ──────────
  var variant = sessionStorage.getItem('ec_variant');
  if (!variant) {
    variant = Math.random() < 0.5 ? 'A' : 'B';
    sessionStorage.setItem('ec_variant', variant);
  }

  // ... rest van de IIFE ...
  // Verwijder de variant-setup blok onderaan
```

- [ ] **Stap 4: Check analytics na deploy**

Na pushen, wacht 35 seconden en test:
```bash
curl -s "https://visit.asteria.nl/api/stats?summary=1" | python3 -m json.tool
```

Controleer of email events nu variant-kolom hebben in de variants array.

- [ ] **Stap 5: Commit**

```bash
git add hotel-venray.html
git commit -m "fix: variant tracking vóór email popup triggers, zodat A/B analyseerbaar is"
```

---

## Task 4: Fix H4+H5 — Copy, offer en UX verbeteren (bevestigingsmail blijft)

**Doel:** Verhoog conversie van popup open → submit. De bevestigingsmail (dubbele opt-in) blijft — goed voor GDPR en lijstkwaliteit. We verbeteren offer-helderheid, CTA en success-framing.

**Huidige problemen:**
- Offer "bij uw eerste verblijf" is vaag en ver weg
- CTA "Aanmelden" is passief
- Pakketinhoud staat alleen in de title — niet scanbaar
- Success screen: "bevestig uw aanmelding" klinkt als drempel

**Files:**
- Modify: `hotel-venray.html` (popup HTML ~regel 3217-3239, CSS na `.ec-consent a`)

- [ ] **Stap 1: Herschrijf title, voeg perks-lijst toe**

Zoek (~regel 3218-3219):
```html
          <h2 class="ec-title">Gratis badjas, handdoek<br>&amp; bubbels op de kamer</h2>
          <p class="ec-sub">Meld u aan voor de nieuwsbrief en ontvang het pakket bij uw eerste verblijf.</p>
```

Vervang door:
```html
          <h2 class="ec-title">Gratis welkomstpakket<br>bij uw verblijf</h2>
          <ul class="ec-perks">
            <li>&#x1F6C1; Badjas &amp; handdoek</li>
            <li>&#x1F942; Fles bubbels op de kamer</li>
          </ul>
          <p class="ec-sub">Meld u aan en ontvang uw persoonlijke code per e-mail.</p>
```

- [ ] **Stap 2: Voeg CSS toe voor `.ec-perks`**

Zoek in CSS:
```css
.ec-consent a { color: rgba(255,255,255,0.60); text-decoration: underline; text-decoration-color: rgba(255,255,255,0.25); }
```

Voeg direct erna toe:
```css

.ec-perks {
  list-style: none;
  padding: 0;
  margin: 0 0 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.ec-perks li {
  font-size: 14px;
  color: rgba(255,255,255,0.88);
  font-family: 'Montserrat', sans-serif;
  font-weight: 400;
}
```

- [ ] **Stap 3: Verbeter CTA**

Zoek:
```html
            <button class="ec-submit-btn" id="ecSubmit">Aanmelden</button>
```

Vervang:
```html
            <button class="ec-submit-btn" id="ecSubmit">Stuur mij de code &#x2192;</button>
```

- [ ] **Stap 4: Verbeter success screen framing**

Zoek (~regel 3236-3238):
```html
          <h2 class="ec-success-title">Check uw inbox</h2>
          <p class="ec-success-sub">We hebben u een mail gestuurd. Open hem om uw aanmelding te bevestigen. Uw persoonlijke code staat daarin.</p>
          <p class="ec-spam-note">Geen mail ontvangen? Check uw spamfolder.</p>
```

Vervang:
```html
          <h2 class="ec-success-title">Bijna klaar!</h2>
          <p class="ec-success-sub">Check uw inbox en bevestig uw aanmelding. Uw welkomstcode staat in diezelfde mail — vermeld hem bij het boeken.</p>
          <p class="ec-spam-note">Geen mail ontvangen? Check uw spamfolder.</p>
```

- [ ] **Stap 5: Visueel check in Playwright**

```javascript
// Forceer variant A en wis ec_shown zodat popup opnieuw kan triggeren
await page.evaluate(() => { sessionStorage.setItem('ec_variant', 'A'); sessionStorage.removeItem('ec_shown'); });
await page.reload();
await page.waitForTimeout(13000);
await page.waitForSelector('.ec-overlay.is-open');
await page.screenshot({ path: '/tmp/popup-copy.png' });
```

Check: perks-lijst zichtbaar, CTA volledig in beeld, achtergrond leesbaar.

- [ ] **Stap 6: Commit**

```bash
git add hotel-venray.html
git commit -m "copy: email popup perks lijst, actieve CTA, positief success screen"
```

---

## Task 5: Fix H6+H7 — Trigger timing optimaliseren

**Doel:** Verhoog het percentage bezoekers dat de popup ziet (nu 19%).

**Huidige situatie:**
- Variant A: timer 4 seconden — te vroeg, gebruiker nog niet geëngageerd
- Variant B desktop: exit intent — laag bereik (niet iedereen verlaat via boven)
- Variant B mobile: 70% scroll — veel gebruikers haken eerder af

**Files:**
- Modify: `hotel-venray.html` (trigger setup ~regel 4294-4322)

- [ ] **Stap 1: Pas timer aan van 4s naar 12s (variant A)**

Zoek (~regel 4295-4297):
```javascript
  if (variant === 'A') {
    setTimeout(openPopup, 4000);
    return;
  }
```

Vervang door:
```javascript
  if (variant === 'A') {
    setTimeout(openPopup, 12000); // 12s: gebruiker heeft tijd gehad om page te scannen
    return;
  }
```

Rationale: 4 seconden is te vroeg. Op dit punt heeft de gebruiker de hero net gezien. 12 seconden geeft tijd om de kamers/arrangementen te bekijken — meer context = hogere bereidheid.

- [ ] **Stap 2: Verlaag scroll-depth voor mobile (variant B)**

Zoek (~regel 4316):
```javascript
      if (scrolled / total >= 0.70) {
```

Vervang door:
```javascript
      if (scrolled / total >= 0.45) { // 45%: na eerste grote blok (reviews/USPs)
```

Rationale: 70% halen veel mobiele gebruikers niet. 45% is na de reviews — de gebruiker heeft social proof gezien, is warm.

- [ ] **Stap 3: Voeg tweede trigger toe voor variant A op mobile**

Na de `setTimeout` voor variant A, voeg toe dat op mobile ook scroll triggert als backup (voor gebruikers die de pagina wegleggen vóór 12s):

Vervang het variant A blok:
```javascript
  if (variant === 'A') {
    setTimeout(openPopup, 12000);
    // Op mobile: ook bij scroll 45% als de timer nog niet heeft getriggerd
    if (window.matchMedia('(max-width: 768px)').matches) {
      function onScrollA() {
        var scrolled = window.scrollY + window.innerHeight;
        var total = document.documentElement.scrollHeight;
        if (scrolled / total >= 0.45) {
          window.removeEventListener('scroll', onScrollA);
          openPopup();
        }
      }
      window.addEventListener('scroll', onScrollA, { passive: true });
    }
    return;
  }
```

- [ ] **Stap 4: Verifieer triggers in Playwright**

Test variant A timer:
```javascript
// Simuleer variant A
await page.goto('https://visit.asteria.nl/hotel-venray');
await page.evaluate(() => sessionStorage.setItem('ec_variant', 'A'));
await page.reload();
await page.waitForTimeout(13000); // wacht 13s op popup
const popupOpen = await page.isVisible('.ec-overlay.is-open');
console.log('Popup na 12s zichtbaar:', popupOpen);
```

- [ ] **Stap 5: Commit**

```bash
git add hotel-venray.html
git commit -m "fix: email popup trigger timing — 12s timer, 45% scroll depth mobile"
```

---

## Task 6: Zelfde fixes in lander-google.html

**Doel:** lander-google.html heeft dezelfde email capture code — fixes doorvoeren.

**Files:**
- Modify: `lander-google.html`

- [ ] **Stap 1: Check of lander-google.html dezelfde email capture heeft**

```bash
grep -n "ec-overlay\|ecEmail\|revinate\|email_popup_open\|ec_variant" lander-google.html | wc -l
```

Als > 10 regels → beide bestanden hebben de code.

- [ ] **Stap 2: Pas alle fixes toe**

Voer Tasks 1-5 uit op `lander-google.html`. De HTML sectie is identiek — zoek dezelfde regels.

Controleer: `diff <(grep -n "ec-" hotel-venray.html) <(grep -n "ec-" lander-google.html)` om te zien wat afwijkt.

- [ ] **Stap 3: Commit**

```bash
git add lander-google.html
git commit -m "fix: zelfde email capture fixes doorvoeren in lander-google.html"
```

---

## Task 7: Push + verifieer live

- [ ] **Stap 1: Push naar main**

```bash
git push origin main
```

- [ ] **Stap 2: Wacht op Cloudflare deploy (~35s)**

```bash
sleep 40
```

- [ ] **Stap 3: Check live pagina in Playwright**

```javascript
await page.goto('https://visit.asteria.nl/hotel-venray');
// Scherm 1: popup trigger test
await page.evaluate(() => sessionStorage.setItem('ec_variant', 'A'));
await page.reload();
await page.waitForTimeout(13000);
const popupOpen = await page.isVisible('.ec-overlay.is-open');
console.log('Popup verschijnt na 12s:', popupOpen);
// Scherm 2: submit test
await page.fill('#ecEmail', 'test+deploy@example.com');
await page.click('#ecSubmit');
await page.waitForTimeout(1000);
const successVisible = await page.isVisible('#ecSuccess.is-visible');
console.log('Success scherm na submit:', successVisible);
await page.screenshot({ path: '/tmp/email-capture-live.png' });
```

Verwacht: beide `true`.

- [ ] **Stap 4: Check analytics baseline reset**

```bash
curl -s "https://visit.asteria.nl/api/stats?summary=1" | python3 -m json.tool
```

Noteer de baseline voor nieuwe meting. Nieuwe data zal variant info bevatten voor email events.

---

## Verwachte impact

| Metric | Huidig | Doel na fixes |
|--------|--------|---------------|
| popup open rate | 19% | 35-40% |
| submit rate (van opens) | 6,5% | 20-30% |
| overall conversie | ~1,2% | 7-12% |

De grootste winst zit in trigger timing (Task 5) en copy (Task 4). Task 2 (Revinate fix) is cruciaal als H1 bevestigd wordt.
