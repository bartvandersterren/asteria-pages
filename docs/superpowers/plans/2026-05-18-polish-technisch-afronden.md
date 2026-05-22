# Polish & Technisch Afronden — wellness-arr-c Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** De wellness-arr-c landingspagina technisch afronden: favicon, meta-tags, preload, footer fix, Font Awesome verwijderen, cookie banner, Schema.org, en robots.txt.

**Architecture:** Alle wijzigingen in `wellness-arr-c.html` (head + footer + cookie banner) plus twee nieuwe bestanden (`robots.txt`, `favicon.svg`). Font Awesome CDN wordt vervangen door 4 inline SVG iconen in de nav. Cookie banner is een lichtgewicht vanilla JS implementatie zonder externe library.

**Tech Stack:** Vanilla HTML/CSS/JS · Cloudflare Pages · SVG favicon

---

## Context (lees dit vóór elke task)

- **Bestand:** `/Users/bartvandersterren/Projects/asteria-pages/wellness-arr-c.html`
- **Live URL:** `https://visit.asteria.nl/wellness-arr-c`
- **Deploy:** push naar `main` → Cloudflare deployt automatisch
- **Kennisbank:** `hotel-content.md`, `design-dna.md`, `brand.css`
- **Primaire kleur:** `#c23435`
- **Fonts:** Electrolize (headings) + Montserrat 300/400/600/700
- **Correct adres:** Maasheseweg 80a, 5804 AD Venray
- **Mews booking URL:** `https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS`

---

## Task 1: Favicon toevoegen

**Doel:** SVG favicon met de Asteria primaire kleur, plus fallback PNG link.

**Files:**
- Create: `favicon.svg`
- Modify: `wellness-arr-c.html` regel 6-7 (in `<head>`)

- [ ] **Stap 1: SVG favicon aanmaken**

Maak `favicon.svg` in de repo-root — een simpel "A" in Asteria-stijl:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="#c23435"/>
  <text x="16" y="23" font-family="Arial,sans-serif" font-size="22" font-weight="bold" fill="#fff" text-anchor="middle">A</text>
</svg>
```

- [ ] **Stap 2: Favicon link toevoegen in `<head>`**

Voeg toe ná regel 6 (`<title>`) in `wellness-arr-c.html`:

```html
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
```

- [ ] **Stap 3: Commit**

```bash
git add favicon.svg wellness-arr-c.html
git commit -m "feat: favicon toevoegen (SVG)"
```

---

## Task 2: Meta-tags — OG, canonical, preload

**Doel:** Open Graph tags voor social sharing, canonical URL, en hero-afbeelding preloaden voor snellere LCP.

**Files:**
- Modify: `wellness-arr-c.html` — in `<head>` sectie (regels 6-13)

- [ ] **Stap 1: Meta-tags toevoegen**

Voeg toe in `<head>`, ná de favicon-link en vóór de `<link rel="preconnect">` regels:

```html
  <!-- Canonical -->
  <link rel="canonical" href="https://visit.asteria.nl/wellness-arr-c">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="Wellness Arrangement — Hotel Asteria Venray">
  <meta property="og:description" content="Wellness arrangement met overnachting, drie-gangen diner en ontbijtbuffet bij Hotel Asteria Venray. Vier unieke sauna's op de Top Floor. Vanaf €139,50 p.p.">
  <meta property="og:image" content="https://visit.asteria.nl/fotos/wellness-hero.webp">
  <meta property="og:url" content="https://visit.asteria.nl/wellness-arr-c">
  <meta property="og:locale" content="nl_NL">
  <meta property="og:site_name" content="Hotel Asteria Venray">
```

- [ ] **Stap 2: Hero-afbeelding preloaden**

Voeg toe direct ná de OG-tags, vóór de Google Fonts preconnects:

```html
  <!-- Preload hero image (LCP) -->
  <link rel="preload" as="image" href="fotos/wellness-hero.webp" type="image/webp">
```

- [ ] **Stap 3: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: OG tags, canonical URL, hero preload"
```

---

## Task 3: Font Awesome verwijderen → inline SVG

**Doel:** De Font Awesome CDN (80KB) verwijderen en de 4 gebruikte iconen vervangen door inline SVG.

**Files:**
- Modify: `wellness-arr-c.html` — CDN link verwijderen (regel 13), CSS aanpassen (regels 48-49), nav HTML aanpassen (regels 1642-1676)

De 4 iconen die gebruikt worden:
1. `fa-envelope` (top-bar, email)
2. `fa-phone` (top-bar + mobile nav)
3. `fa-globe` (top-bar, taalkeuze)
4. `fa-bars` (mobile hamburger menu)

- [ ] **Stap 1: CDN link verwijderen**

Verwijder regel 13:
```html
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
```

- [ ] **Stap 2: CSS voor Font Awesome iconen aanpassen**

Vervang de bestaande regels 48-49:
```css
    .top-bar .far, .top-bar .fas { margin: 0 4px 0 5px; color: #f2f2f2; font-size: 12px; }
    .top-bar .fa-globe, .top-bar .fa-phone { margin: 0 4px 0 8px; }
```

Door:
```css
    .top-bar .nav-icon { width: 14px; height: 14px; margin: 0 5px 0 8px; vertical-align: -2px; fill: none; stroke: #f2f2f2; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
    .mobile-nav-buttons .nav-icon { width: 18px; height: 18px; margin-right: 4px; vertical-align: -3px; fill: none; stroke: #fff; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
```

- [ ] **Stap 3: HTML iconen vervangen in top-bar (regels 1642-1645)**

Vervang:
```html
      <a href="mailto:info@asteria.nl"><i class="far fa-envelope"></i>info@asteria.nl</a>
      <a href="tel:0031478511466"><i class="fas fa-phone"></i>0478 511 466</a>
      <span class="lang-wrapper">
        <i class="fas fa-globe"></i>
```

Door:
```html
      <a href="mailto:info@asteria.nl"><svg class="nav-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 4l10 9 10-9"/></svg>info@asteria.nl</a>
      <a href="tel:0031478511466"><svg class="nav-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6A19.79 19.79 0 012.12 4.18 2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.362 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.338 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg>0478 511 466</a>
      <span class="lang-wrapper">
        <svg class="nav-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10A15.3 15.3 0 0112 2z"/></svg>
```

- [ ] **Stap 4: HTML iconen vervangen in mobile-nav-buttons (regels 1675-1676)**

Vervang:
```html
        <span class="menu-button button" id="menuOpen"><i class="fas fa-bars"></i> Menu</span>
        <a href="tel:0031478511466" class="button"><i class="fas fa-phone"></i> Bel</a>
```

Door:
```html
        <span class="menu-button button" id="menuOpen"><svg class="nav-icon" viewBox="0 0 24 24" aria-hidden="true"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg> Menu</span>
        <a href="tel:0031478511466" class="button"><svg class="nav-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6A19.79 19.79 0 012.12 4.18 2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.362 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.338 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg> Bel</a>
```

- [ ] **Stap 5: Visueel verifiëren**

Open `wellness-arr-c.html` lokaal in browser, check:
- Desktop: envelope + phone + globe iconen zichtbaar in top-bar
- Mobile (375px): hamburger + phone iconen zichtbaar

- [ ] **Stap 6: Commit**

```bash
git add wellness-arr-c.html
git commit -m "perf: Font Awesome CDN verwijderd, inline SVG iconen"
```

---

## Task 4: Footer fixen — adres + content matchen met asteria.nl

**Doel:** Footer updaten met correct adres (Maasheseweg 80a) en content matchen met de echte asteria.nl footer: social media links, privacy/voorwaarden links.

**Files:**
- Modify: `wellness-arr-c.html` — footer sectie (regels 2101-2122)

- [ ] **Stap 1: Footer HTML vervangen**

Vervang de volledige footer (regels 2101-2122) door:

```html
<!-- ══ FOOTER ════════════════════════════════════════════════ -->
<footer class="footer">
  <div class="footer__inner">
    <div class="footer__logo">
      <a href="https://www.asteria.nl">
        <img src="https://www.asteria.nl/images/logo-hotel-asteria.png" alt="Hotel Asteria" loading="lazy">
      </a>
    </div>
    <div class="footer__info">
      <p class="footer__name">Hotel Asteria</p>
      Maasheseweg 80a &nbsp;&middot;&nbsp; 5804 AD Venray<br>
      <a href="tel:0031478511466">0478 511 466</a> &nbsp;&middot;&nbsp;
      <a href="mailto:info@asteria.nl">info@asteria.nl</a><br>
      <a href="https://www.asteria.nl" target="_blank" rel="noopener">www.asteria.nl</a>
    </div>
    <div class="footer__social">
      <a href="https://www.facebook.com/AsteriaVenray" target="_blank" rel="noopener" aria-label="Facebook">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg>
      </a>
      <a href="https://www.instagram.com/hotelasteriavenray" target="_blank" rel="noopener" aria-label="Instagram">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="5"/><circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none"/></svg>
      </a>
      <a href="https://www.linkedin.com/company/hotel-asteria-venray" target="_blank" rel="noopener" aria-label="LinkedIn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-4 0v7h-4v-7a6 6 0 016-6zM2 9h4v12H2zM4 2a2 2 0 110 4 2 2 0 010-4z"/></svg>
      </a>
    </div>
    <div class="footer__links">
      <a href="https://www.asteria.nl/privacy" target="_blank" rel="noopener">Privacy</a>
      <a href="https://www.asteria.nl/algemene-voorwaarden" target="_blank" rel="noopener">Algemene voorwaarden</a>
    </div>
    <div class="footer__copy">
      &copy; 2026 Hotel Asteria &nbsp;&middot;&nbsp; Onderdeel van Van der Sterren Hotels
    </div>
  </div>
</footer>
```

- [ ] **Stap 2: Footer CSS updaten**

Zoek de bestaande footer CSS-sectie en vervang/breid uit:

```css
/* ══════════════════════════════════════════════════════════
   FOOTER
══════════════════════════════════════════════════════════ */
.footer {
  background: #1a1a1a;
  color: rgba(255,255,255,0.6);
  font-family: 'Montserrat', sans-serif;
  font-size: 14px;
  padding: 60px 24px 40px;
  text-align: center;
}
.footer__inner {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}
.footer__logo img { width: 60px; opacity: 0.8; }
.footer__name {
  font-family: 'Electrolize', sans-serif;
  font-size: 16px;
  color: #fff;
  margin-bottom: 4px;
}
.footer__info { line-height: 1.8; }
.footer__info a { color: rgba(255,255,255,0.6); text-decoration: none; }
.footer__info a:hover { color: #fff; }
.footer__social { display: flex; gap: 16px; }
.footer__social a { color: rgba(255,255,255,0.5); transition: color 0.2s; }
.footer__social a:hover { color: #fff; }
.footer__links { display: flex; gap: 20px; font-size: 13px; }
.footer__links a { color: rgba(255,255,255,0.4); text-decoration: none; }
.footer__links a:hover { color: #fff; }
.footer__copy { font-size: 12px; color: rgba(255,255,255,0.3); }
```

- [ ] **Stap 3: Verifiëren**

Check visueel: logo, adres (Maasheseweg 80a), social icons, privacy/voorwaarden links.

- [ ] **Stap 4: Commit**

```bash
git add wellness-arr-c.html
git commit -m "fix: footer — correct adres + social links + privacy/voorwaarden"
```

---

## Task 5: Cookie-consent banner

**Doel:** Lichtgewicht cookie-consent banner. Geen externe library. Slaat keuze op in localStorage zodat de banner niet terugkomt.

**Files:**
- Modify: `wellness-arr-c.html` — CSS toevoegen + HTML vóór `</body>` + JS toevoegen

- [ ] **Stap 1: CSS toevoegen**

Voeg toe in de `<style>`-tag, ná de footer-styles:

```css
/* ══════════════════════════════════════════════════════════
   COOKIE BANNER
══════════════════════════════════════════════════════════ */
.cookie-banner {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  z-index: 9999;
  background: #1a1a1a;
  color: rgba(255,255,255,0.8);
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  line-height: 1.6;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
  box-shadow: 0 -2px 12px rgba(0,0,0,0.3);
}
.cookie-banner[hidden] { display: none; }
.cookie-banner__text { max-width: 600px; }
.cookie-banner__text a { color: #fff; text-decoration: underline; }
.cookie-banner__btn {
  background: #c23435;
  color: #fff;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
}
.cookie-banner__btn:hover { background: #a82c2c; }
```

- [ ] **Stap 2: HTML toevoegen**

Voeg toe vóór de `<script>` tag (vóór regel 2127):

```html
<!-- ══ COOKIE BANNER ═════════════════════════════════════ -->
<div class="cookie-banner" id="cookieBanner" role="dialog" aria-label="Cookiemelding">
  <p class="cookie-banner__text">
    Deze website gebruikt cookies voor een optimale ervaring.
    <a href="https://www.asteria.nl/privacy" target="_blank" rel="noopener">Meer info</a>
  </p>
  <button class="cookie-banner__btn" id="cookieAccept">Akkoord</button>
</div>
```

- [ ] **Stap 3: JS toevoegen**

Voeg toe aan het begin van het `<script>` blok (direct na `<script>`):

```js
/* ── Cookie banner ── */
(function () {
  if (localStorage.getItem('cookie-consent')) {
    document.getElementById('cookieBanner').hidden = true;
    return;
  }
  document.getElementById('cookieAccept').addEventListener('click', function () {
    localStorage.setItem('cookie-consent', '1');
    document.getElementById('cookieBanner').hidden = true;
  });
}());
```

- [ ] **Stap 4: Verifiëren**

Open pagina → banner verschijnt onderaan. Klik "Akkoord" → banner verdwijnt. Herlaad → banner komt niet terug. Verwijder `cookie-consent` uit localStorage → banner verschijnt weer.

- [ ] **Stap 5: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: cookie-consent banner"
```

---

## Task 6: Schema.org JSON-LD

**Doel:** Structured data toevoegen voor Google rich results: Hotel + Offer (arrangement).

**Files:**
- Modify: `wellness-arr-c.html` — JSON-LD script toevoegen in `<head>`

- [ ] **Stap 1: JSON-LD toevoegen**

Voeg toe aan het einde van `<head>`, vóór `</head>` en de `<style>` tag:

```html
  <!-- Structured Data -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Hotel",
    "name": "Hotel Asteria",
    "url": "https://www.asteria.nl",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "Maasheseweg 80a",
      "postalCode": "5804 AD",
      "addressLocality": "Venray",
      "addressCountry": "NL"
    },
    "telephone": "+31478511466",
    "email": "info@asteria.nl",
    "image": "https://visit.asteria.nl/fotos/wellness-hero.webp",
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "4.2",
      "reviewCount": "2219",
      "bestRating": "5"
    },
    "makesOffer": {
      "@type": "Offer",
      "name": "Wellness Arrangement",
      "description": "Overnachting, welkomstdrankje, badjas en slippers, vrije toegang wellness, drie-gangen diner en ontbijtbuffet.",
      "price": "139.50",
      "priceCurrency": "EUR",
      "priceSpecification": {
        "@type": "UnitPriceSpecification",
        "price": "139.50",
        "priceCurrency": "EUR",
        "unitText": "per persoon"
      },
      "url": "https://visit.asteria.nl/wellness-arr-c",
      "availability": "https://schema.org/InStock"
    }
  }
  </script>
```

- [ ] **Stap 2: Valideren**

Test de JSON-LD door de pagina-URL in te voeren op https://search.google.com/test/rich-results (na deploy).

- [ ] **Stap 3: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: Schema.org JSON-LD (Hotel + Offer)"
```

---

## Task 7: robots.txt

**Doel:** Basis robots.txt voor Cloudflare Pages.

**Files:**
- Create: `robots.txt`

- [ ] **Stap 1: robots.txt aanmaken**

```
User-agent: *
Allow: /

Sitemap: https://visit.asteria.nl/sitemap.xml
```

Opmerking: de sitemap.xml bestaat nog niet, maar de verwijzing is standaardpraktijk en doet geen kwaad.

- [ ] **Stap 2: Commit**

```bash
git add robots.txt
git commit -m "feat: robots.txt"
```

---

## Task 8: Adres fixen in CLAUDE.md

**Doel:** Het foutieve adres in CLAUDE.md corrigeren zodat toekomstige sessies het juiste adres gebruiken.

**Files:**
- Modify: `CLAUDE.md` — regel met "Leunseweg" aanpassen

- [ ] **Stap 1: Adres corrigeren**

Zoek in `CLAUDE.md` naar "Leunseweg 2" en vervang door "Maasheseweg 80a, 5804 AD Venray".

- [ ] **Stap 2: Commit**

```bash
git add CLAUDE.md
git commit -m "fix: correct adres in CLAUDE.md"
```

---

## Samenvatting volgorde

| Task | Wat | Geschatte omvang |
|------|-----|------------------|
| 1 | Favicon | Klein — 1 nieuw bestand + 1 regel in head |
| 2 | OG + canonical + preload | Klein — ~15 regels in head |
| 3 | Font Awesome → inline SVG | Medium — CDN weg, CSS+HTML aanpassen |
| 4 | Footer fixen | Medium — HTML + CSS vervangen |
| 5 | Cookie banner | Medium — CSS + HTML + JS |
| 6 | Schema.org JSON-LD | Klein — 1 script block in head |
| 7 | robots.txt | Klein — 1 nieuw bestand |
| 8 | Adres fix CLAUDE.md | Klein — 1 regel |

Alle tasks zijn onafhankelijk en kunnen in willekeurige volgorde uitgevoerd worden.
