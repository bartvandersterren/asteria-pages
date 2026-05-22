# Session Notes — 2026-05-22

## Wat gedaan

**Task 1 van lander-google plan — Strippen — AFGEROND**

`lander-google.html` aangemaakt als fork van `wellness-arr-c.html`. Live op `visit.asteria.nl/lander-google`.

Verwijderd:
- arr-c arrangement blok + CSS
- Wellness plattegrond + hotspot blok + CSS
- Diner blok + CSS
- A/B price test IIFE
- arr-c feature-interactie IIFE
- Taaldetectie/redirect script (geen -en/-de versies voor lander-google)
- Voucher codes (WELLNESSARRA, WELLNESS124)

Aangepast:
- `buildBookingUrl()` — geen `mewsVoucherCode` parameter
- Canonical + OG URLs → `/lander-google`
- Meta description generiek

**Bug gevonden en gefixed:**
Bij het verwijderen brak `button.hero__cta,` (hangende komma) de CSS-parser. Gefixed.

## Open / te verifiëren

- Bart moet de live pagina nog visueel controleren — Playwright screenshots hingen (marquee-animatie).
- Paginatitel is nog "Wellness Arrangement | Hotel Asteria Venray" — wordt Task 2

## Volgende sessie — Task 2: Hero aanpassen

- Generieke hotel hero-foto kiezen uit `foto-index.md`
- Hero headline + subline → hotel-first copy (max 8 woorden)
- Trust badges → generieke hotel USPs
- Sticky CTA: "Boek het Wellness Arrangement" → "Boek uw verblijf"
- Paginatitel aanpassen
- Plan: `docs/superpowers/plans/2026-05-22-lander-google.md` — Task 2 sectie
