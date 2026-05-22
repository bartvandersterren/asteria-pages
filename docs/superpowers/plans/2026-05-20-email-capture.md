# Email Capture Popup — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Een email capture popup toevoegen aan `wellness-arr-c.html` die nieuwsbriefinschrijvingen verzamelt via Revinate, met een A/B test op trigger-strategie en een succes-flow die de gast aanzet tot het openen van de welkomstmail.

**Architecture:** Volledig vanilla JS IIFE onderaan de pagina, zelfde patroon als de booking popup en datepicker. HTML markup als een `<!-- ══ EMAIL CAPTURE ══ -->` blok direct vóór het cookie banner blok. CSS in de bestaande `<style>` tag. Geen nieuwe bestanden nodig.

**Tech Stack:** Vanilla JS, CSS, Revinate Contact API JS (`contact-api.inguest.com`), `sessionStorage`, `localStorage`.

---

### Handmatige vereisten (vóór of na implementatie)

> Deze stappen zijn buiten de code en moeten handmatig gebeuren:
> 1. **Mews:** vouchercode `WELKOM` aanmaken (los van `WELLNESSARRA`)
> 2. **Revinate:** welkomstautomation instellen die na aanmelding de code `WELKOM` meestuurt

---

### Task 1: Revinate CDN script + verborgen form toevoegen

**Files:**
- Modify: `wellness-arr-c.html` — `<head>` (script) + vóór `</body>` (hidden form)

- [ ] **Stap 1: Revinate CDN script in `<head>` toevoegen**

Zoek de regel met `<!-- ══ COOKIE BANNER` (rond regel 2846). Voeg het Revinate script toe in de `<head>`, direct na de bestaande `<link>` tags:

```html
<!-- Revinate Contact API -->
<script type="text/javascript" src="//contact-api.inguest.com/bundles/revinatecontactapi/js/revinate-form.js?v=1" defer></script>
```

- [ ] **Stap 2: Verborgen Revinate form toevoegen**

Direct vóór `<!-- ══ COOKIE BANNER ══` (vóór de cookie banner div), voeg toe:

```html
<!-- ══ REVINATE HIDDEN FORM ══════════════════════════════ -->
<form id="revinate_contact_api_form"
      token="210bb345-899a-4f69-9b9f-4a00624a2024"
      style="display:none"
      onsubmit="return false;">
  <input type="email" name="email" id="ec_hidden_email">
  <input type="text" name="vipStatus" value="Wellness nieuwsbrief">
</form>
```

- [ ] **Stap 3: Verifieer in browser**

Open `wellness-arr-c.html` lokaal. In DevTools console:
```js
document.getElementById('revinate_contact_api_form')
// → <form> element zichtbaar
typeof revFormOnSubmit
// → "function" (Revinate script geladen)
```

- [ ] **Stap 4: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: voeg Revinate hidden form + CDN script toe"
```

---

### Task 2: CSS voor email capture popup

**Files:**
- Modify: `wellness-arr-c.html` — `<style>` tag (onderaan, vóór `</style>`)

- [ ] **Stap 1: CSS toevoegen onderaan de bestaande `<style>` tag**

Zoek `</style>` (de afsluitende tag van de grote stijlblok, rond regel 2260). Voeg daarvoor in:

```css
/* ══ EMAIL CAPTURE POPUP ══════════════════════════════════ */
.ec-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.65);
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}
.ec-overlay.is-open {
  opacity: 1;
  pointer-events: auto;
}

.ec-modal {
  width: 100%;
  max-width: 400px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 32px 80px rgba(0,0,0,0.55);
  position: relative;
  transform: translateY(12px);
  transition: transform 0.3s ease;
}
.ec-overlay.is-open .ec-modal {
  transform: translateY(0);
}

.ec-modal-inner {
  position: relative;
  min-height: 420px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 40px 32px 36px;
}

/* Foto + gradient overlay */
.ec-modal-bg {
  position: absolute;
  inset: 0;
  background-image: url('fotos/wellness-hero.webp');
  background-size: cover;
  background-position: center;
}
.ec-modal-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.80) 0%, rgba(0,0,0,0.35) 55%, rgba(0,0,0,0.10) 100%);
}

.ec-close {
  position: absolute;
  top: 14px;
  right: 16px;
  background: none;
  border: none;
  color: rgba(255,255,255,0.45);
  font-size: 22px;
  font-weight: 300;
  cursor: pointer;
  line-height: 1;
  z-index: 2;
  transition: color 0.2s;
  padding: 4px;
  font-family: inherit;
}
.ec-close:hover { color: rgba(255,255,255,0.85); }

.ec-content {
  position: relative;
  z-index: 1;
}

/* Scherm 1 — form */
.ec-title {
  font-family: 'Montserrat', sans-serif;
  font-weight: 300;
  font-size: 24px;
  color: #fff;
  line-height: 1.25;
  margin: 0 0 10px;
  letter-spacing: -0.2px;
}
.ec-sub {
  font-family: 'Montserrat', sans-serif;
  font-weight: 300;
  font-size: 13px;
  color: rgba(255,255,255,0.55);
  line-height: 1.6;
  margin: 0 0 24px;
}
.ec-form-row {
  display: flex;
  margin-bottom: 12px;
}
.ec-email-input {
  flex: 1;
  background: rgba(255,255,255,0.09);
  border: 1px solid rgba(255,255,255,0.20);
  border-right: none;
  border-radius: 3px 0 0 3px;
  padding: 12px 14px;
  font-family: 'Montserrat', sans-serif;
  font-weight: 300;
  font-size: 13px;
  color: #fff;
  outline: none;
  transition: border-color 0.2s, background 0.2s;
  min-width: 0;
}
.ec-email-input::placeholder { color: rgba(255,255,255,0.3); }
.ec-email-input:focus {
  background: rgba(255,255,255,0.13);
  border-color: rgba(255,255,255,0.45);
}
.ec-submit-btn {
  background: #c23435;
  border: none;
  border-radius: 0 3px 3px 0;
  padding: 12px 18px;
  font-family: 'Electrolize', sans-serif;
  font-size: 11px;
  letter-spacing: 2px;
  color: #fff;
  text-transform: uppercase;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}
.ec-submit-btn:hover { background: #a82c2c; }
.ec-submit-btn:disabled { background: #888; cursor: default; }

.ec-consent {
  font-family: 'Montserrat', sans-serif;
  font-weight: 300;
  font-size: 10px;
  color: rgba(255,255,255,0.30);
  line-height: 1.6;
}
.ec-consent a { color: rgba(255,255,255,0.42); text-decoration: underline; text-decoration-color: rgba(255,255,255,0.2); }

.ec-error {
  font-size: 11px;
  color: #ff8a8a;
  margin-bottom: 10px;
  display: none;
}
.ec-error.is-visible { display: block; }

/* Scherm 2 — succes */
.ec-success { display: none; }
.ec-success.is-visible { display: flex; flex-direction: column; }
.ec-form-state.is-hidden { display: none; }

.ec-success-icon {
  width: 44px;
  height: 44px;
  border: 1px solid rgba(255,255,255,0.22);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}
.ec-success-icon svg {
  width: 18px;
  height: 18px;
  stroke: rgba(255,255,255,0.6);
  fill: none;
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.ec-success-title {
  font-family: 'Montserrat', sans-serif;
  font-weight: 300;
  font-size: 24px;
  color: #fff;
  line-height: 1.25;
  margin: 0 0 10px;
}
.ec-success-sub {
  font-family: 'Montserrat', sans-serif;
  font-weight: 300;
  font-size: 13px;
  color: rgba(255,255,255,0.55);
  line-height: 1.65;
  margin: 0 0 10px;
}
.ec-spam-note {
  font-family: 'Montserrat', sans-serif;
  font-weight: 300;
  font-size: 10px;
  color: rgba(255,255,255,0.25);
  line-height: 1.6;
}

@media (max-width: 480px) {
  .ec-modal-inner { padding: 36px 24px 32px; min-height: 380px; }
  .ec-title, .ec-success-title { font-size: 21px; }
}
```

- [ ] **Stap 2: Verifieer CSS geladen**

Open pagina in browser. Open DevTools → Elements → zoek naar `.ec-overlay`. Als de class bestaat in de stylesheet is CSS correct geladen.

- [ ] **Stap 3: Commit**

```bash
git add wellness-arr-c.html
git commit -m "style: email capture popup CSS"
```

---

### Task 3: HTML markup voor email capture overlay

**Files:**
- Modify: `wellness-arr-c.html` — nieuw blok vóór `<!-- ══ COOKIE BANNER ══`

- [ ] **Stap 1: HTML markup toevoegen**

Voeg direct vóór `<!-- ══ COOKIE BANNER ══` (en vóór het Revinate hidden form) toe:

```html
<!-- ══ EMAIL CAPTURE ═════════════════════════════════════ -->
<div class="ec-overlay" id="ecOverlay" role="dialog" aria-modal="true" aria-label="Nieuwsbrief aanmelden">
  <div class="ec-modal" id="ecModal">
    <div class="ec-modal-inner">
      <div class="ec-modal-bg"></div>
      <button class="ec-close" id="ecClose" aria-label="Sluiten">&times;</button>
      <div class="ec-content">

        <!-- Scherm 1: form -->
        <div class="ec-form-state" id="ecFormState">
          <h2 class="ec-title">Gratis badjas, handdoek<br>&amp; bubbels op de kamer</h2>
          <p class="ec-sub">Meld u aan voor de nieuwsbrief en ontvang het pakket bij uw eerste verblijf.</p>
          <p class="ec-error" id="ecError">Er ging iets mis. Probeer het opnieuw.</p>
          <div class="ec-form-row">
            <input class="ec-email-input" type="email" id="ecEmail" placeholder="uw e-mailadres" autocomplete="email">
            <button class="ec-submit-btn" id="ecSubmit">Aanmelden</button>
          </div>
          <p class="ec-consent">Door u aan te melden gaat u akkoord met onze <a href="/privacyverklaring" target="_blank">privacyverklaring</a>. Afmelden kan altijd.</p>
        </div>

        <!-- Scherm 2: succes -->
        <div class="ec-success" id="ecSuccess">
          <div class="ec-success-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <rect x="2" y="4" width="20" height="16" rx="2"/>
              <polyline points="2,4 12,13 22,4"/>
            </svg>
          </div>
          <h2 class="ec-success-title">Check uw inbox</h2>
          <p class="ec-success-sub">We hebben u een mail gestuurd. Open hem om uw aanmelding te bevestigen &mdash; uw persoonlijke code staat daarin.</p>
          <p class="ec-spam-note">Geen mail ontvangen? Check uw spamfolder.</p>
        </div>

      </div>
    </div>
  </div>
</div>
```

- [ ] **Stap 2: Verifieer HTML in browser**

Open pagina. In console:
```js
document.getElementById('ecOverlay')
// → <div class="ec-overlay"> element
document.getElementById('ecSuccess')
// → <div class="ec-success"> element
```

- [ ] **Stap 3: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: email capture popup HTML markup"
```

---

### Task 4: JS IIFE — basis, open/close, frequentie guards

**Files:**
- Modify: `wellness-arr-c.html` — onderaan `<script>` tag, direct ná de booking popup IIFE

- [ ] **Stap 1: IIFE toevoegen na de booking popup IIFE**

Zoek het einde van de booking popup IIFE (regel met `window.openBookingPopup = openBookingPopup;` gevolgd door `})()`). Voeg direct daarna toe:

```js
/* ══ EMAIL CAPTURE ══════════════════════════════════════ */
(function () {
  // ── Guards ──────────────────────────────────────────
  if (localStorage.getItem('ec_converted')) return;

  var overlay   = document.getElementById('ecOverlay');
  var modal     = document.getElementById('ecModal');
  var btnClose  = document.getElementById('ecClose');
  var formState = document.getElementById('ecFormState');
  var successEl = document.getElementById('ecSuccess');
  var emailInput = document.getElementById('ecEmail');
  var submitBtn  = document.getElementById('ecSubmit');
  var errorEl    = document.getElementById('ecError');

  var shown = false;

  // ── Open / close ─────────────────────────────────────
  function openPopup() {
    if (shown) return;
    if (sessionStorage.getItem('ec_shown')) return;
    shown = true;
    sessionStorage.setItem('ec_shown', '1');
    overlay.classList.add('is-open');
    setTimeout(function () { emailInput && emailInput.focus(); }, 350);
  }

  function closePopup() {
    overlay.classList.remove('is-open');
  }

  btnClose.addEventListener('click', closePopup);

  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closePopup();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay.classList.contains('is-open')) closePopup();
  });

  window.openEmailCapture = openPopup;

  // ── Triggers worden in volgende task toegevoegd ──────
})();
```

- [ ] **Stap 2: Verifieer open/close in browser console**

```js
window.openEmailCapture()
// → popup verschijnt
// Druk Escape → popup verdwijnt
// Klik backdrop → popup verdwijnt
```

- [ ] **Stap 3: Verifieer frequentie guard**

```js
// Na openEmailCapture():
sessionStorage.getItem('ec_shown') // → "1"
// Herlaad pagina → popup mag niet meer vanzelf openen (ec_shown gezet)
// Test: zet localStorage.ec_converted = "1", herlaad → window.openEmailCapture bestaat NIET
```

- [ ] **Stap 4: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: email capture IIFE — open/close + frequentie guards"
```

---

### Task 5: JS IIFE — A/B trigger (timer vs exit intent + scroll)

**Files:**
- Modify: `wellness-arr-c.html` — binnenin de email capture IIFE (vervang de `// ── Triggers worden...` comment)

- [ ] **Stap 1: A/B split + triggers toevoegen**

Vervang de regel `// ── Triggers worden in volgende task toegevoegd ──────` door:

```js
  // ── A/B split ────────────────────────────────────────
  var variant = sessionStorage.getItem('ec_variant');
  if (!variant) {
    variant = Math.random() < 0.5 ? 'A' : 'B';
    sessionStorage.setItem('ec_variant', variant);
  }

  // ── Variant A: timer 4 seconden ──────────────────────
  if (variant === 'A') {
    setTimeout(openPopup, 4000);
    return;
  }

  // ── Variant B: exit intent (desktop) + scroll (mobile) ──
  var isMobile = window.matchMedia('(max-width: 768px)').matches;

  if (!isMobile) {
    // Exit intent: muis verlaat venster bovenkant
    document.addEventListener('mouseleave', function handler(e) {
      if (e.clientY <= 5) {
        document.removeEventListener('mouseleave', handler);
        openPopup();
      }
    });
  } else {
    // Scroll-depth: 70% van de pagina gescrold
    function onScroll() {
      var scrolled = window.scrollY + window.innerHeight;
      var total = document.documentElement.scrollHeight;
      if (scrolled / total >= 0.70) {
        window.removeEventListener('scroll', onScroll);
        openPopup();
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
  }
```

- [ ] **Stap 2: Verifieer Variant A**

```js
// Forceer variant A:
sessionStorage.setItem('ec_variant', 'A');
sessionStorage.removeItem('ec_shown');
// Herlaad pagina → popup verschijnt na ~4 seconden
```

- [ ] **Stap 3: Verifieer Variant B desktop**

```js
// Forceer variant B:
sessionStorage.setItem('ec_variant', 'B');
sessionStorage.removeItem('ec_shown');
// Herlaad pagina op desktop → beweeg muis naar boven uit venster → popup verschijnt
```

- [ ] **Stap 4: Verifieer Variant B mobile**

Open DevTools → mobile emulatie (375px). Zet `ec_variant = "B"`, `ec_shown` leeg. Herlaad en scroll naar beneden voorbij 70% → popup verschijnt.

- [ ] **Stap 5: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: email capture A/B triggers — timer (A) vs exit-intent+scroll (B)"
```

---

### Task 6: JS IIFE — submit handler, Revinate integratie, succes state

**Files:**
- Modify: `wellness-arr-c.html` — binnenin de email capture IIFE, vóór de A/B split sectie

- [ ] **Stap 1: Submit handler toevoegen**

Voeg toe direct ná de `window.openEmailCapture = openPopup;` regel (vóór de A/B split):

```js
  // ── Submit ───────────────────────────────────────────
  function showSuccess() {
    formState.classList.add('is-hidden');
    successEl.classList.add('is-visible');
    localStorage.setItem('ec_converted', '1');
  }

  function showError() {
    errorEl.classList.add('is-visible');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Aanmelden';
  }

  submitBtn.addEventListener('click', function () {
    var email = emailInput.value.trim();
    if (!email || !emailInput.checkValidity()) {
      emailInput.focus();
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = '...';
    errorEl.classList.remove('is-visible');

    // Kopieer email naar verborgen Revinate form
    var hiddenEmail = document.getElementById('ec_hidden_email');
    if (hiddenEmail) hiddenEmail.value = email;

    // Roep Revinate submit aan
    try {
      if (typeof revFormOnSubmit === 'function') {
        revFormOnSubmit();
        showSuccess();
      } else {
        // Revinate script niet geladen — foutmelding
        showError();
      }
    } catch (e) {
      showError();
    }
  });

  // Enter in email input triggert submit
  emailInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') submitBtn.click();
  });
```

- [ ] **Stap 2: Verifieer succes flow in browser**

```js
window.openEmailCapture();
// Vul een email in, klik Aanmelden
// → formState verdwijnt, succes-scherm verschijnt
localStorage.getItem('ec_converted') // → "1"
// Herlaad pagina → window.openEmailCapture bestaat NIET meer (guard bovenin)
```

- [ ] **Stap 3: Verifieer error flow**

```js
// Tijdelijk: hernoem revFormOnSubmit in console
var orig = window.revFormOnSubmit;
window.revFormOnSubmit = undefined;
// Open popup, submit → rode foutmelding verschijnt
window.revFormOnSubmit = orig; // herstel
```

- [ ] **Stap 4: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: email capture submit handler — Revinate integratie + succes state"
```

---

### Task 7: Branding polish + productie-check

**Files:**
- Modify: `wellness-arr-c.html` — CSS `.ec-*` blok

- [ ] **Stap 1: Controleer foto achtergrond**

Open pagina in browser op desktop (1280px+) en mobile (375px). Verifieer:
- `wellness-hero.webp` laadt als background op `.ec-modal-bg`
- Gradient overlay zorgt dat tekst leesbaar is op de foto
- Als foto niet goed oogt: vervang `wellness-hero.webp` door een andere wellness foto uit `fotos/`

Als de foto niet goed valt op mobile (afsnijding), voeg toe aan CSS:

```css
@media (max-width: 480px) {
  .ec-modal-bg { background-position: center top; }
}
```

- [ ] **Stap 2: Controleer fonts**

Verifieer in browser dat:
- Headline gebruikt Montserrat 300 (niet system font)
- "Aanmelden" knop gebruikt Electrolize
- Lijn in DevTools Computed → font-family bevestigt dit

Als fonts niet laden: controleer dat de Google Fonts `<link>` in `<head>` ook Electrolize en Montserrat:300 bevat (staan al in de pagina).

- [ ] **Stap 3: Controleer z-index stapeling**

Open booking popup (`window.openBookingPopup()`) — verifieer dat z-index 1100 (booking) en 1200 (email capture) correct gestapeld zijn. Email capture mag de booking popup niet bedekken als beide open zijn. In de praktijk zal dat niet voorkomen, maar verifieer dat beide `.is-open` classes correct werken.

- [ ] **Stap 4: Mobile test**

Open DevTools → 375px viewport. Verifieer:
- Modal past binnen viewport (geen overflow)
- Input + knop naast elkaar (geen wrap)
- Tekst leesbaar op foto

- [ ] **Stap 5: Final commit**

```bash
git add wellness-arr-c.html
git commit -m "style: email capture branding polish + mobile check"
git push origin main
```

- [ ] **Stap 6: Live check na deploy (~35 seconden na push)**

```
https://visit.asteria.nl/wellness-arr-c
```

Open in browser. In console:
```js
// Test A variant:
sessionStorage.setItem('ec_variant','A'); sessionStorage.removeItem('ec_shown');
location.reload();
// → popup na 4 seconden
```

---

## Niet in scope

- Revinate welkomstautomation configureren (handmatig in Revinate dashboard)
- Mews vouchercode `WELKOM` aanmaken (handmatig in Mews)
- Analytics tracking op conversie (later iteratie)
