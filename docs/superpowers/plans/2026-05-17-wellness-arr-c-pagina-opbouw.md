# wellness-arr-c Pagina-opbouw Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** De landingspagina wellness-arr-c uitbreiden van 2 blokken (hero + arrangement) naar een volledige conversiepagina met sticky CTA, reviews, wellness-sfeer, kamertypes en restaurant.

**Architecture:** Alle blokken worden toegevoegd aan het bestaande `wellness-arr-c.html` bestand. Elke task is onafhankelijk en kan in een aparte sessie gebouwd worden — lees de task volledig voordat je begint. De Google Reviews API vereist een Cloudflare Function als proxy.

**Tech Stack:** Vanilla HTML/CSS/JS · Cloudflare Pages + Functions · Google Places API · Eigen WebP fotobank

---

## Context (lees dit vóór elke task)

- **Bestand:** `/Users/bartvandersterren/Projects/asteria-pages/wellness-arr-c.html`
- **Spec:** `docs/superpowers/specs/2026-05-17-wellness-arr-c-pagina-structuur-design.md`
- **Kennisbank:** `hotel-content.md`, `foto-index.md`, `design-dna.md`, `brand.css`
- **Mews boekingslink wellness:** `https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS`
- **Primaire kleur:** `#c23435` | **Fonts:** Electrolize (headings) + Montserrat 300/400/600/700
- **Deploy:** push naar `main` → Cloudflare deployt automatisch naar visit.asteria.nl
- **Volgorde blokken in HTML** (van boven naar beneden):
  1. NAV ✅
  2. HERO ✅
  3. Sticky CTA (task 1) — *zweeft over alles*
  4. ARRANGEMENT arr-c met rating (task 2) ✅ + kleine aanpassing
  5. REVIEWS (task 3+4)
  6. WELLNESS (task 5)
  7. KAMERTYPES (task 6)
  8. RESTAURANT (task 7)
  9. FOOTER ✅

---

## Task 1: Sticky CTA met A/B test

**Doel:** Een balk die verschijnt zodra de hero uit beeld scrolt. Twee varianten worden 50/50 getoond.

**Files:**
- Modify: `wellness-arr-c.html` — CSS-sectie uitbreiden + HTML vóór `</body>` + JS-blok uitbreiden

**Variant A:** Arrangementsnaam + prijs + "Boek nu"-knop
**Variant B:** Knop met context "Boek het arrangement" + subtekst "Incl. wellness, diner & ontbijt" (geen prijs)

- [ ] **Stap 1: CSS toevoegen** — plak dit in de `<style>`-tag, ná de bestaande footer-styles:

```css
/* ══════════════════════════════════════════════════════════
   STICKY CTA
══════════════════════════════════════════════════════════ */
.sticky-cta {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  z-index: 900;
  background: #1a1a1a;
  border-top: 1px solid rgba(255,255,255,0.08);
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  transform: translateY(100%);
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: transform;
}
.sticky-cta.is-visible { transform: translateY(0); }

/* Variant A */
.sticky-cta__info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.sticky-cta__name {
  font-family: 'Electrolize', sans-serif;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.45);
}
.sticky-cta__price {
  font-family: 'Montserrat', sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}
.sticky-cta__price-sub {
  font-family: 'Montserrat', sans-serif;
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

/* Variant B */
.sticky-cta__sub {
  font-family: 'Montserrat', sans-serif;
  font-size: 11px;
  font-weight: 300;
  color: rgba(255,255,255,0.5);
  margin-top: 2px;
}

/* Knop (beide varianten) */
.sticky-cta__btn {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #c23435;
  color: #fff;
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
  padding: 12px 24px;
  border-radius: 4px;
  transition: background 200ms ease;
  white-space: nowrap;
}
.sticky-cta__btn:hover { background: #a82c2c; }

@media (max-width: 600px) {
  .sticky-cta { padding: 10px 16px; gap: 12px; }
  .sticky-cta__price { font-size: 17px; }
  .sticky-cta__btn { font-size: 13px; padding: 11px 18px; }
}
```

- [ ] **Stap 2: HTML toevoegen** — plak dit direct ná `<body>` (vóór de NAV):

```html
<!-- ══ STICKY CTA ════════════════════════════════════════ -->
<div class="sticky-cta" id="stickyCta" role="complementary" aria-label="Snel boeken">
  <!-- Variant A: prijs zichtbaar -->
  <div class="sticky-cta__info" id="stickyVariantA">
    <span class="sticky-cta__name">Wellness Arrangement</span>
    <strong class="sticky-cta__price">&euro;139,50</strong>
    <span class="sticky-cta__price-sub">per persoon &middot; 2-persoonskamer</span>
  </div>
  <!-- Variant B: inbegrepen zichtbaar, geen prijs -->
  <div class="sticky-cta__info" id="stickyVariantB" style="display:none">
    <span class="sticky-cta__name">Boek het arrangement</span>
    <span class="sticky-cta__sub">Incl. wellness, diner &amp; ontbijt</span>
  </div>
  <a
    href="https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS"
    class="sticky-cta__btn"
    id="stickyCtaBtn"
    target="_blank"
    rel="noopener"
  >Boek nu</a>
</div>
```

- [ ] **Stap 3: JS toevoegen** — voeg toe aan het bestaande `<script>`-blok onderaan, binnen de IIFE-structuur:

```javascript
/* ── Sticky CTA + A/B test ── */
(function () {
  var bar      = document.getElementById('stickyCta');
  var hero     = document.getElementById('hero');
  var footer   = document.querySelector('.footer');
  var variantA = document.getElementById('stickyVariantA');
  var variantB = document.getElementById('stickyVariantB');
  var btn      = document.getElementById('stickyCtaBtn');

  // A/B split: 50/50, persistent per sessie
  var variant = sessionStorage.getItem('sticky_ab');
  if (!variant) {
    variant = Math.random() < 0.5 ? 'A' : 'B';
    sessionStorage.setItem('sticky_ab', variant);
  }
  if (variant === 'B') {
    variantA.style.display = 'none';
    variantB.style.display = '';
    btn.textContent = 'Bekijk beschikbaarheid';
  }

  // Klik tracken (custom event — koppel later aan analytics)
  btn.addEventListener('click', function () {
    var ev = new CustomEvent('sticky_cta_click', { detail: { variant: variant } });
    document.dispatchEvent(ev);
    // console.log('sticky_cta_click', variant); // debug
  });

  // Toon/verberg op scroll
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.target === hero)   { bar.classList.toggle('is-visible', !e.isIntersecting); }
      if (e.target === footer) { bar.classList.toggle('is-visible', !e.isIntersecting); }
    });
  }, { threshold: 0.1 });

  if (hero)   io.observe(hero);
  if (footer) io.observe(footer);
}());
```

- [ ] **Stap 4: Testen in browser**
  - Open `wellness-arr-c.html` lokaal of op `visit.asteria.nl` na deploy
  - Scroll voorbij de hero → sticky balk verschijnt
  - Scroll naar de footer → balk verdwijnt
  - Open in nieuw tabblad: andere variant verschijnt (of dezelfde, afhankelijk van de 50/50)
  - Controleer op mobiel (375px): balk past in beeld, tekst niet afgekapt

- [ ] **Stap 5: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: sticky CTA met A/B test — variant A prijs / variant B inbegrepen"
```

---

## Task 2: Mini Google-rating in arr-c blok

**Doel:** Kleine Google-rating (4,2 ★ · 2.219 reviews) toevoegen aan het bestaande arrangement-blok, met anchor-link naar de reviews-sectie.

**Files:**
- Modify: `wellness-arr-c.html` — één HTML-regel + kleine CSS-toevoeging

- [ ] **Stap 1: CSS toevoegen** — in de `<style>`-tag, ná de arr-c styles:

```css
/* Mini rating in arr-c */
.arr-c__rating {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  margin-bottom: 14px;
  color: inherit;
}
.arr-c__rating-stars {
  color: #f59e0b;
  font-size: 12px;
  letter-spacing: 1px;
}
.arr-c__rating-score {
  font-family: 'Montserrat', sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: #0f172a;
}
.arr-c__rating-count {
  font-family: 'Montserrat', sans-serif;
  font-size: 11px;
  color: #94a3b8;
}
.arr-c__rating:hover .arr-c__rating-count { color: #64748b; }
```

- [ ] **Stap 2: HTML toevoegen** — in `wellness-arr-c.html`, direct vóór `<span class="arr-c__eyebrow">`:

```html
<a href="#reviews" class="arr-c__rating" aria-label="4,2 van 5 sterren · 2.219 Google reviews">
  <span class="arr-c__rating-stars" aria-hidden="true">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
  <span class="arr-c__rating-score">4,2</span>
  <span class="arr-c__rating-count">· 2.219 reviews</span>
</a>
```

**Let op:** de anchor `#reviews` verwijst naar de reviews-sectie die in task 4 gebouwd wordt. De link werkt pas volledig na task 4.

- [ ] **Stap 3: Testen**
  - Rating zichtbaar boven de eyebrow-tekst "Wellness Arrangement"
  - Klik op rating scrollt naar `#reviews` (werkt pas na task 4)
  - Op mobiel: rating past naast de andere elementen

- [ ] **Stap 4: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: mini Google-rating in arr-c blok met anchor naar reviews"
```

---

## Task 3: Cloudflare Function — Google Places API proxy

**Doel:** Een serverless functie die Google Places reviews ophaalt zonder de API-key in de frontend bloot te stellen.

**Files:**
- Create: `functions/api/google-reviews.js`

**Vereisten vóór deze task:**
1. Google Cloud Console → Places API inschakelen
2. API key aanmaken (beperken tot Places API + jouw domein)
3. Key toevoegen als Cloudflare Pages secret: `wrangler secret put GOOGLE_PLACES_API_KEY` (of via Cloudflare dashboard → Settings → Environment variables)
4. Asteria Place ID opzoeken via: `https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=Hotel+Asteria+Venray&inputtype=textquery&key=JOUW_KEY` — sla het `place_id` op

- [ ] **Stap 1: Function aanmaken**

```javascript
// functions/api/google-reviews.js
export async function onRequest(context) {
  const PLACE_ID = 'VERVANG_MET_ECHTE_PLACE_ID'; // bijv. ChIJ...
  const API_KEY  = context.env.GOOGLE_PLACES_API_KEY;

  if (!API_KEY) {
    return new Response(JSON.stringify({ error: 'API key niet geconfigureerd' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const url = `https://maps.googleapis.com/maps/api/place/details/json`
    + `?place_id=${PLACE_ID}`
    + `&fields=rating,user_ratings_total,reviews`
    + `&reviews_sort=most_relevant`
    + `&language=nl`
    + `&key=${API_KEY}`;

  const resp = await fetch(url);
  const data = await resp.json();

  if (data.status !== 'OK') {
    return new Response(JSON.stringify({ error: data.status }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const result = data.result;
  const payload = {
    rating: result.rating,
    total:  result.user_ratings_total,
    reviews: (result.reviews || []).map(function (r) {
      return {
        author:   r.author_name,
        avatar:   r.profile_photo_url,
        rating:   r.rating,
        text:     r.text,
        time:     r.relative_time_description,
        url:      r.author_url
      };
    })
  };

  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=3600' // 1 uur cachen
    }
  });
}
```

- [ ] **Stap 2: PLACE_ID invullen** — vervang `VERVANG_MET_ECHTE_PLACE_ID` met het echte place_id van Hotel Asteria Venray

- [ ] **Stap 3: Lokaal testen** (optioneel, vereist Wrangler)

```bash
npx wrangler pages dev . --binding GOOGLE_PLACES_API_KEY=JOUW_KEY
# Bezoek: http://localhost:8788/api/google-reviews
# Verwacht: JSON met rating, total, reviews array
```

- [ ] **Stap 4: Deploy en testen**

```bash
git add functions/api/google-reviews.js
git commit -m "feat: Cloudflare Function als proxy voor Google Places reviews"
git push
# Wacht op Cloudflare deploy, dan:
# curl https://visit.asteria.nl/api/google-reviews
```

---

## Task 4: Reviews blok

**Doel:** Reviews-sectie toevoegen die live data ophaalt via de proxy uit task 3. Authentieke Google-stijl kaarten.

**Files:**
- Modify: `wellness-arr-c.html` — CSS + HTML-sectie + JS

**Voeg de reviews-sectie toe in `wellness-arr-c.html` direct ná het `arr-c`-blok (na `</section>`) en vóór de footer.**

- [ ] **Stap 1: CSS toevoegen** — in `<style>`, ná arr-c styles:

```css
/* ══════════════════════════════════════════════════════════
   REVIEWS
══════════════════════════════════════════════════════════ */
.reviews {
  background: #f8f7f5;
  padding: 80px 40px;
}
.reviews__inner {
  max-width: 1100px;
  margin: 0 auto;
}
.reviews__header {
  display: flex;
  align-items: flex-end;
  gap: 24px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}
.reviews__score-block { display: flex; align-items: center; gap: 16px; }
.reviews__score {
  font-family: 'Electrolize', sans-serif;
  font-size: 56px;
  font-weight: 400;
  color: #0f172a;
  line-height: 1;
}
.reviews__score-meta { display: flex; flex-direction: column; gap: 4px; }
.reviews__stars { color: #f59e0b; font-size: 18px; letter-spacing: 2px; }
.reviews__total {
  font-family: 'Montserrat', sans-serif;
  font-size: 12px;
  color: #94a3b8;
}
.reviews__google-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'Montserrat', sans-serif;
  font-size: 12px;
  color: #94a3b8;
  margin-left: auto;
}
.reviews__google-logo {
  width: 18px; height: 18px;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E%3Cpath fill='%23EA4335' d='M24 9.5c3.5 0 6.3 1.2 8.4 3.1l6.3-6.3C34.8 3 29.8 1 24 1 14.8 1 6.9 6.6 3.1 14.6l7.4 5.7C12.4 13.5 17.7 9.5 24 9.5z'/%3E%3Cpath fill='%234285F4' d='M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v8.5h12.7c-.5 2.9-2.2 5.3-4.7 6.9l7.3 5.7c4.3-4 6.8-9.9 6.8-16.6z'/%3E%3Cpath fill='%23FBBC05' d='M10.5 28.6A14.7 14.7 0 0 1 9.5 24c0-1.6.3-3.1.7-4.6L2.8 13.7A23.9 23.9 0 0 0 1 24c0 3.8.9 7.4 2.5 10.6l7-5.4-.1-.6z'/%3E%3Cpath fill='%2334A853' d='M24 47c5.8 0 10.7-1.9 14.3-5.2l-7.3-5.7c-2 1.3-4.4 2.1-7 2.1-6.3 0-11.6-4-13.5-9.6l-7.4 5.7C6.8 41.4 14.8 47 24 47z'/%3E%3C/svg%3E") center / contain no-repeat;
  flex-shrink: 0;
}

/* Kaarten grid */
.reviews__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.review-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.review-card__top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.review-card__avatar {
  width: 38px; height: 38px;
  border-radius: 50%;
  background: #e2e8f0;
  flex-shrink: 0;
  object-fit: cover;
  font-family: 'Montserrat', sans-serif;
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  text-transform: uppercase;
}
.review-card__meta { flex: 1; min-width: 0; }
.review-card__name {
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.review-card__date {
  font-family: 'Montserrat', sans-serif;
  font-size: 11px;
  color: #94a3b8;
}
.review-card__stars { color: #f59e0b; font-size: 12px; letter-spacing: 1px; }
.review-card__text {
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  font-weight: 300;
  color: #475569;
  line-height: 1.65;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.reviews__loading {
  text-align: center;
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  color: #94a3b8;
  padding: 40px 0;
}

@media (max-width: 900px) {
  .reviews__grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .reviews { padding: 56px 20px; }
  .reviews__grid { grid-template-columns: 1fr; }
  .reviews__score { font-size: 44px; }
}
```

- [ ] **Stap 2: HTML toevoegen** — direct ná `</section>` van het arr-c blok:

```html
<!-- ══ REVIEWS ══════════════════════════════════════════ -->
<section class="reviews" id="reviews" aria-label="Gastbeoordelingen">
  <div class="reviews__inner">

    <div class="reviews__header">
      <div class="reviews__score-block">
        <span class="reviews__score" id="reviewsScore">4,2</span>
        <div class="reviews__score-meta">
          <span class="reviews__stars" id="reviewsStars">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
          <span class="reviews__total" id="reviewsTotal">2.219 beoordelingen</span>
        </div>
      </div>
      <div class="reviews__google-badge">
        <div class="reviews__google-logo" aria-hidden="true"></div>
        Google Reviews
      </div>
    </div>

    <div class="reviews__grid" id="reviewsGrid">
      <p class="reviews__loading">Reviews worden geladen&hellip;</p>
    </div>

  </div>
</section>
```

- [ ] **Stap 3: JS toevoegen** — in het `<script>`-blok onderaan:

```javascript
/* ── Reviews laden ── */
(function () {
  var grid  = document.getElementById('reviewsGrid');
  var score = document.getElementById('reviewsScore');
  var total = document.getElementById('reviewsTotal');

  // Kleur per initiaal
  var colors = ['#c23435','#1e88e5','#43a047','#8e24aa','#fb8c00'];
  function colorFor(name) {
    var i = (name.charCodeAt(0) || 0) % colors.length;
    return colors[i];
  }
  function starsHtml(n) {
    return '&#9733;'.repeat(Math.round(n)) + (n < 5 ? '&#9734;'.repeat(5 - Math.round(n)) : '');
  }

  fetch('/api/google-reviews')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.error) throw new Error(data.error);

      // Update totaalscore
      if (score) score.textContent = data.rating ? data.rating.toFixed(1).replace('.', ',') : '4,2';
      if (total) total.textContent = (data.total ? data.total.toLocaleString('nl-NL') : '2.219') + ' beoordelingen';

      var reviews = (data.reviews || []).slice(0, 6);
      if (!reviews.length) { grid.innerHTML = '<p class="reviews__loading">Geen reviews beschikbaar.</p>'; return; }

      grid.innerHTML = reviews.map(function (r) {
        var initials = r.author.split(' ').map(function (w) { return w[0]; }).slice(0, 2).join('');
        var avatarHtml = r.avatar
          ? '<img class="review-card__avatar" src="' + r.avatar + '" alt="" loading="lazy">'
          : '<div class="review-card__avatar" style="background:' + colorFor(r.author) + '">' + initials + '</div>';
        return '<article class="review-card">'
          + '<div class="review-card__top">'
          + avatarHtml
          + '<div class="review-card__meta">'
          + '<span class="review-card__name">' + r.author + '</span>'
          + '<span class="review-card__date">' + r.time + '</span>'
          + '</div>'
          + '<span class="review-card__stars">' + starsHtml(r.rating) + '</span>'
          + '</div>'
          + '<p class="review-card__text">' + r.text + '</p>'
          + '</article>';
      }).join('');
    })
    .catch(function () {
      // Fallback: toon statische reviews uit hotel-content.md
      grid.innerHTML = [
        { author: 'Rob', time: '24 december 2025', rating: 5, text: 'Ruime kamers met heerlijke sauna. Ontbijt super en diner zeer goed!' },
        { author: 'Danielle', time: '14 augustus 2025', rating: 5, text: 'We hebben 2 heerlijke dagen Venray gehad met 1 overnachting, diner, ontbijt en late check out. Het diner was top en het ontbijt ook. Personeel heel vriendelijk. Wij komen hier zeker nog eens terug.' },
        { author: 'Cornelia O.', time: '10 juni 2024', rating: 5, text: 'Was super goed fijne bedden. Koffie apparaat op je kamer. Top hotel.' }
      ].map(function (r) {
        var initials = r.author.split(' ').map(function (w) { return w[0]; }).slice(0, 2).join('');
        return '<article class="review-card">'
          + '<div class="review-card__top">'
          + '<div class="review-card__avatar" style="background:' + colorFor(r.author) + '">' + initials + '</div>'
          + '<div class="review-card__meta">'
          + '<span class="review-card__name">' + r.author + '</span>'
          + '<span class="review-card__date">' + r.time + '</span>'
          + '</div>'
          + '<span class="review-card__stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span>'
          + '</div>'
          + '<p class="review-card__text">' + r.text + '</p>'
          + '</article>';
      }).join('');
    });
}());
```

- [ ] **Stap 4: Testen**
  - Reviews-sectie zichtbaar onder arr-c blok
  - Anchor-link van rating in arr-c scrollt naar `#reviews`
  - Fallback zichtbaar als API niet bereikbaar is (open DevTools → Network → block `/api/google-reviews`)
  - Kaarten zien er authentiek uit: initiaal-avatar of profielfoto, naam, datum, sterren

- [ ] **Stap 5: Commit**

```bash
git add wellness-arr-c.html
git commit -m "feat: reviews blok met Google Places API en fallback"
git push
```

---

## Task 5: Wellness Top Floor blok

**Doel:** Foto-dominant sfeerblok dat alle faciliteiten van de wellness laat zien.

**Faciliteiten:** 4 sauna's (infrarood, zoutsteen, + 2 anderen), stoomcabine, dompelbad, kruidenbad, belevenisdouches, 4 voetenbaden, relaxruimte — 300m² Top Floor.

**Fotoselectie:** Raadpleeg `foto-index.md` vóór het bouwen. Zoek op termen als "sauna", "wellness", "stoom", "relaxatie", "Top Floor". Selecteer:
- 1 grote sfeerfoto (hoofd)
- 5–8 detailbeelden per faciliteit
Converteer gebruikte foto's naar WebP (quality=72, max 2000px breed) en zet ze in `fotos/`.

**Files:**
- Modify: `wellness-arr-c.html`
- Add: WebP-foto's in `fotos/wellness-*.webp`

- [ ] **Stap 1: Fotoselectie** — lees `foto-index.md`, kies de sfeerfoto en detailbeelden, converteer naar WebP:

```bash
# Voorbeeld conversie (pas paden aan op basis van foto-index.md):
cwebp -q 72 -m 6 ~/Documents/Asteria\ Fotobank/[pad-naar-foto].jpg -o fotos/wellness-sfeer.webp
```

- [ ] **Stap 2: CSS toevoegen** — in `<style>`:

```css
/* ══════════════════════════════════════════════════════════
   WELLNESS BLOK
══════════════════════════════════════════════════════════ */
.wellness {
  background: #0d0c0b;
  color: #fff;
  overflow: hidden;
}
.wellness__hero {
  position: relative;
  height: 55vw;
  max-height: 680px;
  min-height: 320px;
}
.wellness__hero-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  opacity: 0.85;
}
.wellness__hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 40%, rgba(13,12,11,0.9) 100%);
}
.wellness__hero-text {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  width: 100%;
  padding: 0 24px;
}
.wellness__eyebrow {
  font-family: 'Electrolize', sans-serif;
  font-size: 10px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #c23435;
  display: block;
  margin-bottom: 10px;
}
.wellness__title {
  font-family: 'Electrolize', sans-serif;
  font-size: clamp(28px, 4vw, 52px);
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #fff;
  line-height: 1.1;
}

/* Grid faciliteiten */
.wellness__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2px;
  background: #0d0c0b;
}
.wellness__item {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  background: #1a1a1a;
}
.wellness__item-img {
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.6s cubic-bezier(0.16,1,0.3,1);
}
.wellness__item:hover .wellness__item-img { transform: scale(1.06); }
.wellness__item-label {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 20px 14px 14px;
  background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 100%);
  font-family: 'Electrolize', sans-serif;
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.8);
}

.wellness__tagline {
  text-align: center;
  padding: 40px 24px;
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  font-weight: 300;
  color: rgba(255,255,255,0.45);
  letter-spacing: 0.04em;
}

@media (max-width: 768px) {
  .wellness__grid { grid-template-columns: repeat(2, 1fr); }
  .wellness__hero { height: 70vw; max-height: 400px; }
}
```

- [ ] **Stap 3: HTML toevoegen** — direct ná de reviews-sectie. Vervang de `src`-paden met de werkelijke fotos uit stap 1:

```html
<!-- ══ WELLNESS ═════════════════════════════════════════ -->
<section class="wellness" aria-label="Wellness Top Floor">

  <div class="wellness__hero">
    <img class="wellness__hero-img"
         src="fotos/wellness-sfeer.webp"
         alt="Wellness Top Floor Hotel Asteria"
         loading="lazy">
    <div class="wellness__hero-overlay"></div>
    <div class="wellness__hero-text">
      <span class="wellness__eyebrow">Top Floor &middot; 300 m²</span>
      <h2 class="wellness__title">Ontspan op een andere verdieping</h2>
    </div>
  </div>

  <div class="wellness__grid">
    <div class="wellness__item">
      <img class="wellness__item-img" src="fotos/wellness-infrarood.webp" alt="Infraroodsauna" loading="lazy">
      <span class="wellness__item-label">Infraroodsauna</span>
    </div>
    <div class="wellness__item">
      <img class="wellness__item-img" src="fotos/wellness-zoutsteen.webp" alt="Zoutsteen sauna" loading="lazy">
      <span class="wellness__item-label">Zoutsteen sauna</span>
    </div>
    <div class="wellness__item">
      <img class="wellness__item-img" src="fotos/wellness-stoom.webp" alt="Stoomcabine" loading="lazy">
      <span class="wellness__item-label">Stoomcabine</span>
    </div>
    <div class="wellness__item">
      <img class="wellness__item-img" src="fotos/wellness-dompelbad.webp" alt="Dompelbad" loading="lazy">
      <span class="wellness__item-label">Dompelbad</span>
    </div>
    <div class="wellness__item">
      <img class="wellness__item-img" src="fotos/wellness-kruiden.webp" alt="Kruidenbad" loading="lazy">
      <span class="wellness__item-label">Kruidenbad</span>
    </div>
    <div class="wellness__item">
      <img class="wellness__item-img" src="fotos/wellness-douche.webp" alt="Belevenisdouches" loading="lazy">
      <span class="wellness__item-label">Belevenisdouches</span>
    </div>
    <div class="wellness__item">
      <img class="wellness__item-img" src="fotos/wellness-voeten.webp" alt="Voetenbaden" loading="lazy">
      <span class="wellness__item-label">Voetenbaden</span>
    </div>
    <div class="wellness__item">
      <img class="wellness__item-img" src="fotos/wellness-relax.webp" alt="Relaxruimte" loading="lazy">
      <span class="wellness__item-label">Relaxruimte</span>
    </div>
  </div>

  <p class="wellness__tagline">Vrij toegankelijk &middot; inbegrepen in het arrangement</p>

</section>
```

- [ ] **Stap 4: Controleer fotonamen** — alle `src`-paden moeten overeenkomen met de werkelijk aangemaakte WebP-bestanden in `fotos/`

- [ ] **Stap 5: Testen**
  - Alle foto's laden zonder 404
  - Hover-zoom werkt op desktop
  - Grid op mobiel: 2 kolommen
  - Grote sfeerfoto vult de volle breedte

- [ ] **Stap 6: Commit**

```bash
git add wellness-arr-c.html fotos/wellness-*.webp
git commit -m "feat: wellness Top Floor blok — foto-grid met alle faciliteiten"
git push
```

---

## Task 6: Kamertypes blok

**Doel:** Ecommerce-stijl kaartjes per kamertype. Comfort = standaard, 5 upgrades. Klik op kaartje opent een popup met foto's en faciliteiten.

**Upgrade-redenen per kamertype:**

| Kamer | Badge | Upgrade-reden |
|-------|-------|---------------|
| Comfort | Standaard inbegrepen | — |
| Royale | Upgrade | Meer ruimte, keuze bad of douche |
| Deluxe | Upgrade + eigen sauna | Privé infraroodsauna op de kamer |
| Junior Suite | Upgrade | Kingsize bed, ruime zithoek, bad |
| Suite | Upgrade + eigen sauna | Kingsize bed + privé infraroodsauna |
| Bruidssuite | Upgrade premium | Vrijstaand bad, inloopdouche — meest romantisch |

**Fotoselectie:** Raadpleeg `foto-index.md`. Zoek per kamertype op "suite", "kingsize", "badkamer", "zithoek", "tweepersoonsbed". Elke popup krijgt 2-3 foto's. Converteer naar WebP in `fotos/kamer-*.webp`.

**Files:**
- Modify: `wellness-arr-c.html`
- Add: `fotos/kamer-*.webp`

- [ ] **Stap 1: Fotoselectie en conversie** — zie instructie task 5 stap 1, nu voor kamerfoto's

- [ ] **Stap 2: CSS toevoegen**

```css
/* ══════════════════════════════════════════════════════════
   KAMERTYPES
══════════════════════════════════════════════════════════ */
.rooms {
  background: #fff;
  padding: 80px 40px;
}
.rooms__inner { max-width: 1100px; margin: 0 auto; }
.rooms__eyebrow {
  font-family: 'Electrolize', sans-serif;
  font-size: 10px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #c23435;
  display: block;
  margin-bottom: 10px;
}
.rooms__title {
  font-family: 'Electrolize', sans-serif;
  font-size: clamp(22px, 3vw, 36px);
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #0f172a;
  margin-bottom: 8px;
}
.rooms__sub {
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  font-weight: 300;
  color: #64748b;
  margin-bottom: 40px;
}
.rooms__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.room-card {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #f1f5f9;
  cursor: pointer;
  transition: box-shadow 0.22s ease, transform 0.22s ease;
  background: #fff;
  -webkit-tap-highlight-color: transparent;
}
.room-card:hover {
  box-shadow: 0 8px 32px rgba(0,0,0,0.10);
  transform: translateY(-2px);
}
.room-card__img {
  width: 100%;
  aspect-ratio: 4/3;
  object-fit: cover;
  display: block;
}
.room-card__body { padding: 16px 18px 20px; }
.room-card__badge {
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 4px;
  margin-bottom: 8px;
}
.badge-base    { background: #f1f5f9; color: #64748b; }
.badge-upgrade { background: #fff7ed; color: #c2450a; border: 1px solid #fed7aa; }
.badge-sauna   { background: #c23435; color: #fff; }
.badge-premium { background: #1e1e1e; color: #fff; }
.room-card__name {
  font-family: 'Electrolize', sans-serif;
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #0f172a;
  display: block;
  margin-bottom: 6px;
}
.room-card__why {
  font-family: 'Montserrat', sans-serif;
  font-size: 12px;
  font-weight: 300;
  color: #64748b;
  line-height: 1.5;
}
.room-card__cta {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 12px;
  font-family: 'Montserrat', sans-serif;
  font-size: 12px;
  font-weight: 600;
  color: #c23435;
}

/* Popup */
.room-popup-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease;
}
.room-popup-overlay.is-open {
  opacity: 1;
  pointer-events: auto;
}
.room-popup {
  background: #fff;
  border-radius: 16px;
  max-width: 640px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  transform: translateY(20px);
  transition: transform 0.25s cubic-bezier(0.16,1,0.3,1);
}
.room-popup-overlay.is-open .room-popup { transform: translateY(0); }
.room-popup__imgs {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 3px;
  height: 240px;
}
.room-popup__img {
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
}
.room-popup__imgs--single .room-popup__img { grid-column: 1 / -1; }
.room-popup__body { padding: 24px 28px 28px; }
.room-popup__close {
  float: right;
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: #94a3b8;
  line-height: 1;
  padding: 0;
  margin: -4px -4px 0 0;
}
.room-popup__close:hover { color: #0f172a; }
.room-popup__badge { /* hergebruik .room-card__badge */ }
.room-popup__name {
  font-family: 'Electrolize', sans-serif;
  font-size: 20px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #0f172a;
  margin: 8px 0 6px;
}
.room-popup__why {
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  font-weight: 300;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 16px;
}
.room-popup__features {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 6px 16px;
  margin-bottom: 20px;
}
.room-popup__feature {
  font-family: 'Montserrat', sans-serif;
  font-size: 12px;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 5px;
}
.room-popup__feature::before { content: '✓'; color: #c23435; font-weight: 700; }
.room-popup__cta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  min-height: 50px;
  background: #c23435;
  color: #fff;
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
  border-radius: 4px;
  transition: background 200ms ease;
}
.room-popup__cta:hover { background: #a82c2c; }

@media (max-width: 900px) { .rooms__grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px) {
  .rooms { padding: 56px 20px; }
  .rooms__grid { grid-template-columns: 1fr; }
  .room-popup__imgs { height: 180px; }
  .room-popup__body { padding: 18px 20px 22px; }
}
```

- [ ] **Stap 3: HTML toevoegen** — direct ná het wellness-blok. Pas de `src`-paden aan op basis van de gekozen fotos:

```html
<!-- ══ KAMERTYPES ═══════════════════════════════════════ -->
<section class="rooms" aria-label="Kamertypes">
  <div class="rooms__inner">
    <span class="rooms__eyebrow">Kies je kamer</span>
    <h2 class="rooms__title">Welke kamer past bij jou?</h2>
    <p class="rooms__sub">Het arrangement is inbegrepen in elke kamer. Upgrade voor meer comfort of privacy.</p>

    <div class="rooms__grid">

      <!-- Comfort — standaard -->
      <div class="room-card" data-room="comfort" role="button" tabindex="0">
        <img class="room-card__img" src="fotos/kamer-comfort.webp" alt="Comfort Kamer" loading="lazy">
        <div class="room-card__body">
          <span class="room-card__badge badge-base">Standaard inbegrepen</span>
          <span class="room-card__name">Comfort Kamer</span>
          <p class="room-card__why">Ca. 22 m² · zithoek · douche · koffiezetapparaat</p>
          <span class="room-card__cta">Bekijk kamer &rsaquo;</span>
        </div>
      </div>

      <!-- Royale -->
      <div class="room-card" data-room="royale" role="button" tabindex="0">
        <img class="room-card__img" src="fotos/kamer-royale.webp" alt="Royale Kamer" loading="lazy">
        <div class="room-card__body">
          <span class="room-card__badge badge-upgrade">Upgrade</span>
          <span class="room-card__name">Royale Kamer</span>
          <p class="room-card__why">Meer ruimte — keuze tussen bad of douche</p>
          <span class="room-card__cta">Bekijk kamer &rsaquo;</span>
        </div>
      </div>

      <!-- Deluxe -->
      <div class="room-card" data-room="deluxe" role="button" tabindex="0">
        <img class="room-card__img" src="fotos/kamer-deluxe.webp" alt="Deluxe Kamer" loading="lazy">
        <div class="room-card__body">
          <span class="room-card__badge badge-sauna">Upgrade &middot; eigen infraroodsauna</span>
          <span class="room-card__name">Deluxe Kamer</span>
          <p class="room-card__why">Privé infraroodsauna op de kamer — wellness begint bij jou aan de deur</p>
          <span class="room-card__cta">Bekijk kamer &rsaquo;</span>
        </div>
      </div>

      <!-- Junior Suite -->
      <div class="room-card" data-room="junior-suite" role="button" tabindex="0">
        <img class="room-card__img" src="fotos/kamer-junior-suite.webp" alt="Junior Suite" loading="lazy">
        <div class="room-card__body">
          <span class="room-card__badge badge-upgrade">Upgrade</span>
          <span class="room-card__name">Junior Suite</span>
          <p class="room-card__why">Kingsize bed · ruime zithoek · bad</p>
          <span class="room-card__cta">Bekijk kamer &rsaquo;</span>
        </div>
      </div>

      <!-- Suite -->
      <div class="room-card" data-room="suite" role="button" tabindex="0">
        <img class="room-card__img" src="fotos/kamer-suite.webp" alt="Suite" loading="lazy">
        <div class="room-card__body">
          <span class="room-card__badge badge-sauna">Upgrade &middot; eigen infraroodsauna</span>
          <span class="room-card__name">Suite</span>
          <p class="room-card__why">Kingsize bed + privé infraroodsauna — maximale ontspanning</p>
          <span class="room-card__cta">Bekijk kamer &rsaquo;</span>
        </div>
      </div>

      <!-- Bruidssuite -->
      <div class="room-card" data-room="bruidssuite" role="button" tabindex="0">
        <img class="room-card__img" src="fotos/kamer-bruidssuite.webp" alt="Bruidssuite" loading="lazy">
        <div class="room-card__body">
          <span class="room-card__badge badge-premium">Upgrade premium</span>
          <span class="room-card__name">Bruidssuite</span>
          <p class="room-card__why">Vrijstaand bad · inloopdouche · meest romantisch</p>
          <span class="room-card__cta">Bekijk kamer &rsaquo;</span>
        </div>
      </div>

    </div>
  </div>
</section>

<!-- Kamerpopup -->
<div class="room-popup-overlay" id="roomPopup" role="dialog" aria-modal="true" aria-label="Kamerdetails">
  <div class="room-popup" id="roomPopupInner">
    <!-- wordt dynamisch gevuld door JS -->
  </div>
</div>
```

- [ ] **Stap 4: JS toevoegen** — in `<script>`-blok:

```javascript
/* ── Kamertypes popup ── */
(function () {
  var BOOK_URL = 'https://app.mews.com/distributor/bee2f902-f30f-4977-b9f7-af5d00e4ab76?&mewsVoucherCode=WELLNESS';

  var rooms = {
    'comfort': {
      badge: '<span class="room-card__badge badge-base">Standaard inbegrepen</span>',
      name: 'Comfort Kamer',
      why: 'Alles wat je nodig hebt voor een ontspannen wellness-avond.',
      features: ['Ca. 22 m²', '2 personen', 'Douche', 'Zithoek', 'Koffiezetapparaat', 'Airco', 'LCD-tv', 'Gratis WiFi'],
      imgs: ['fotos/kamer-comfort.webp']
    },
    'royale': {
      badge: '<span class="room-card__badge badge-upgrade">Upgrade</span>',
      name: 'Royale Kamer',
      why: 'Meer ruimte om te ademen — en de keuze voor een bad als je na de wellness ook op de kamer wil ontspannen.',
      features: ['Ruimer dan Comfort', 'Bad of douche', 'Zithoek', 'Koffiezetapparaat', 'Airco'],
      imgs: ['fotos/kamer-royale.webp']
    },
    'deluxe': {
      badge: '<span class="room-card__badge badge-sauna">Upgrade &middot; eigen infraroodsauna</span>',
      name: 'Deluxe Kamer',
      why: 'Een privé infraroodsauna op de kamer. Wellness begint bij jou aan de deur — geen gedeelde ruimte.',
      features: ['Eigen infraroodsauna', 'Dubbel bed', 'Douche', 'Zithoek', 'Koffiezetapparaat', 'Airco'],
      imgs: ['fotos/kamer-deluxe.webp']
    },
    'junior-suite': {
      badge: '<span class="room-card__badge badge-upgrade">Upgrade</span>',
      name: 'Junior Suite',
      why: 'Het extra formaat dat een wellness-avond écht luxe maakt: kingsize bed, een bad en een ruime zithoek.',
      features: ['Kingsize bed', 'Bad', 'Ruime zithoek met slaapbank', 'Koelkastje', 'Koffiezetapparaat', 'Airco'],
      imgs: ['fotos/kamer-junior-suite.webp']
    },
    'suite': {
      badge: '<span class="room-card__badge badge-sauna">Upgrade &middot; eigen infraroodsauna</span>',
      name: 'Suite',
      why: 'Het beste van beide werelden: een ruime suite met eigen infraroodsauna én toegang tot het gedeelde wellness-centrum.',
      features: ['Kingsize bed', 'Eigen infraroodsauna', 'Ruime zithoek met slaapbank', 'Koelkastje', 'Airco'],
      imgs: ['fotos/kamer-suite.webp']
    },
    'bruidssuite': {
      badge: '<span class="room-card__badge badge-premium">Upgrade premium</span>',
      name: 'Bruidssuite',
      why: 'Vrijstaand bad, ruime inloopdouche en de meest romantische sfeer van het hotel. Voor een onvergetelijke avond.',
      features: ['Kingsize bed', 'Vrijstaand bad', 'Ruime inloopdouche', 'Zithoek', 'Koelkastje', 'Airco'],
      imgs: ['fotos/kamer-bruidssuite.webp']
    }
  };

  var overlay = document.getElementById('roomPopup');
  var inner   = document.getElementById('roomPopupInner');

  function openPopup(key) {
    var r = rooms[key];
    if (!r) return;
    var imgsHtml = r.imgs.length === 1
      ? '<div class="room-popup__imgs room-popup__imgs--single"><img class="room-popup__img" src="' + r.imgs[0] + '" alt="' + r.name + '" loading="lazy"></div>'
      : '<div class="room-popup__imgs">' + r.imgs.map(function (s, i) { return '<img class="room-popup__img" src="' + s + '" alt="' + r.name + ' ' + (i+1) + '" loading="lazy">'; }).join('') + '</div>';
    inner.innerHTML = imgsHtml
      + '<div class="room-popup__body">'
      + '<button class="room-popup__close" id="popupClose" aria-label="Sluiten">&times;</button>'
      + r.badge
      + '<h3 class="room-popup__name">' + r.name + '</h3>'
      + '<p class="room-popup__why">' + r.why + '</p>'
      + '<ul class="room-popup__features">' + r.features.map(function (f) { return '<li class="room-popup__feature">' + f + '</li>'; }).join('') + '</ul>'
      + '<a href="' + BOOK_URL + '" class="room-popup__cta" target="_blank" rel="noopener">Boek dit arrangement</a>'
      + '</div>';
    overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    document.getElementById('popupClose').addEventListener('click', closePopup);
  }

  function closePopup() {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  overlay.addEventListener('click', function (e) { if (e.target === overlay) closePopup(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closePopup(); });

  document.querySelectorAll('.room-card').forEach(function (card) {
    card.addEventListener('click', function () { openPopup(this.dataset.room); });
    card.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openPopup(this.dataset.room); }
    });
  });
}());
```

- [ ] **Stap 5: Testen**
  - Alle 6 kaartjes zichtbaar in 3-koloms grid (desktop) / 2 kolommen (tablet) / 1 kolom (mobiel)
  - Klik op kaartje → popup opent met foto, faciliteiten en CTA
  - Popup sluit met ✕-knop, Escape-toets en klik buiten popup
  - Badges correct per type (rood voor sauna, zwart voor premium)

- [ ] **Stap 6: Commit**

```bash
git add wellness-arr-c.html fotos/kamer-*.webp
git commit -m "feat: kamertypes blok met popup per kamer — upsell logica"
git push
```

---

## Task 7: Restaurant / Diner blok

**Doel:** Sfeerblok dat het 3-gangen diner — inbegrepen in het arrangement — concreet en aantrekkelijk maakt.

**Fotoselectie:** Raadpleeg `foto-index.md`. Zoek op "restaurant", "diner", "bord", "gerecht", "tafel". Selecteer 1 grote sfeershot + optioneel 1 gerecht-detail. Converteer naar WebP in `fotos/restaurant-*.webp`.

**Files:**
- Modify: `wellness-arr-c.html`
- Add: `fotos/restaurant-*.webp`

- [ ] **Stap 1: Fotoselectie en conversie**

- [ ] **Stap 2: CSS toevoegen**

```css
/* ══════════════════════════════════════════════════════════
   RESTAURANT BLOK
══════════════════════════════════════════════════════════ */
.diner {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 480px;
}
.diner__photo {
  background: #111 center / cover no-repeat;
  min-height: 320px;
}
.diner__content {
  background: #1a1a1a;
  padding: 64px 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: #fff;
}
.diner__eyebrow {
  font-family: 'Electrolize', sans-serif;
  font-size: 10px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #c23435;
  display: block;
  margin-bottom: 14px;
}
.diner__title {
  font-family: 'Electrolize', sans-serif;
  font-size: clamp(22px, 3vw, 34px);
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #fff;
  line-height: 1.15;
  margin-bottom: 16px;
}
.diner__text {
  font-family: 'Montserrat', sans-serif;
  font-size: 14px;
  font-weight: 300;
  color: rgba(255,255,255,0.55);
  line-height: 1.75;
  max-width: 360px;
  margin-bottom: 28px;
}
.diner__included {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 32px;
}
.diner__included li {
  font-family: 'Montserrat', sans-serif;
  font-size: 13px;
  color: rgba(255,255,255,0.7);
  display: flex;
  align-items: center;
  gap: 10px;
}
.diner__included li::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c23435;
  flex-shrink: 0;
}
.diner__note {
  font-family: 'Montserrat', sans-serif;
  font-size: 11px;
  color: rgba(255,255,255,0.3);
  font-style: italic;
}

@media (max-width: 768px) {
  .diner { grid-template-columns: 1fr; }
  .diner__photo { min-height: 260px; }
  .diner__content { padding: 44px 28px; }
}
```

- [ ] **Stap 3: HTML toevoegen** — direct ná het kamertypes-blok, vóór de footer:

```html
<!-- ══ DINER ════════════════════════════════════════════ -->
<section class="diner" aria-label="Drie-gangen diner">
  <div class="diner__photo"
       style="background-image:url('fotos/restaurant-sfeer.webp')"
       role="img"
       aria-label="Restaurant Hotel Asteria"></div>
  <div class="diner__content">
    <span class="diner__eyebrow">Inbegrepen in het arrangement</span>
    <h2 class="diner__title">Een heerlijk<br>drie-gangen diner</h2>
    <p class="diner__text">
      Na een avond in de wellness schuift u aan in ons restaurant op de begane grond.
      Vers bereid, geen haast.
    </p>
    <ul class="diner__included">
      <li>Drie gangen naar keuze</li>
      <li>Vers bereid door onze keuken</li>
      <li>Inclusief in de arrangementsprijs</li>
    </ul>
    <p class="diner__note">Het restaurant bevindt zich op de begane grond van het hotel.</p>
  </div>
</section>
```

- [ ] **Stap 4: Testen**
  - Foto links, tekst rechts (desktop) / foto boven tekst (mobiel)
  - Foto laadt zonder 404

- [ ] **Stap 5: Commit**

```bash
git add wellness-arr-c.html fotos/restaurant-*.webp
git commit -m "feat: restaurant/diner blok — sfeer en inbegrepen elementen"
git push
```

---

## Afrondende check (na alle tasks)

- [ ] Alle blokken in de juiste volgorde: hero → sticky CTA → arr-c → reviews → wellness → kamertypes → diner → footer
- [ ] Sticky CTA verdwijnt bij de footer
- [ ] Anchor `#reviews` in arr-c rating werkt
- [ ] Google Reviews laden live (of fallback zichtbaar)
- [ ] Alle afbeeldingen laden (geen 404's), alle WebP
- [ ] Pagina werkt op 375px, 430px en desktop
- [ ] `git push` → Cloudflare deployt → controleer op `visit.asteria.nl/wellness-arr-c`
